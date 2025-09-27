import datetime
import os
import pprint
import time
import threading
import torch as th
from types import SimpleNamespace as SN
from utils.logging import Logger
from utils.timehelper import time_left, time_str
from os.path import dirname, abspath
from gym import spaces
import numpy as np

from learners import REGISTRY as le_REGISTRY
from runners import REGISTRY as r_REGISTRY
from controllers import REGISTRY as mac_REGISTRY
from components.episode_buffer import ReplayBuffer
from components.transforms import OneHot


def run(_run, _config, _log):
    # check args sanity
    _config = args_sanity_check(_config, _log)

    args = SN(**_config)

    th.set_num_threads(args.thread_num)
    # th.set_num_interop_threads(8)

    args.device = "cuda" if args.use_cuda else "cpu"

    # setup loggers
    logger = Logger(_log)

    _log.info("Experiment Parameters:")
    experiment_params = pprint.pformat(_config,
                                       indent=4,
                                       width=1)
    _log.info("\n\n" + experiment_params + "\n")

    # configure tensorboard logger
    unique_token = "{}__{}".format(args.name, datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    args.unique_token = unique_token

    env_name = args.env
    logdir = env_name
    if env_name in ["sc2", "sc2_v2", ]:
        logdir = os.path.join("{}_{}-obs_aid={}-obs_act={}".format(
            logdir,
            args.env_args["map_name"],
            int(args.obs_agent_id),
            int(args.obs_last_action),
        ))
        if env_name == "sc2_v2":
            logdir = logdir + "-conic_fov={}".format(
                "1-change_fov_by_move={}".format(
                    int(args.env_args["change_fov_with_move"])) if args.env_args["conic_fov"] else "0"
            )

    args.log_model_dir = logdir
    if args.use_tensorboard:
        tb_logs_direc = os.path.join(dirname(dirname(dirname(abspath(__file__)))), args.local_results_path, "tb_logs")
        tb_exp_direc = os.path.join(tb_logs_direc, "{}").format(unique_token)
        logger.setup_tb(tb_exp_direc)

    # sacred is on by default
    logger.setup_sacred(_run)

    # Run and train
    run_sequential(args=args, logger=logger)

    # Clean up after finishing
    print("Exiting Main")

    print("Stopping all threads")
    for t in threading.enumerate():
        if t.name != "MainThread":
            print("Thread {} is alive! Is daemon: {}".format(t.name, t.daemon))
            t.join(timeout=1)
            print("Thread joined")

    print("Exiting script")

    # Making sure framework really exits
    os._exit(os.EX_OK)


def evaluate_sequential(args, runner):
    for _ in range(args.test_nepisode):
        runner.run(test_mode=True)

    if args.save_replay:
        runner.save_replay()

    runner.close_env()


def run_sequential(args, logger):
    # Init runner so we can get env info
    runner = r_REGISTRY[args.runner](args=args, logger=logger)

    # Set up schemes and groups here
    env_info = runner.get_env_info()
    args.n_agents = env_info["n_agents"]
    args.n_actions = env_info["n_actions"]
    args.state_shape = env_info["state_shape"]
    args.obs_shape = env_info["obs_shape"]
    args.accumulated_episodes = getattr(args, "accumulated_episodes", None)

    if args.env in ["sc2", "sc2_v2"]:
        args.output_normal_actions = env_info["n_normal_actions"]
        args.n_enemies = env_info["n_enemies"]
        args.n_allies = env_info["n_allies"]
        # args.obs_ally_feats_size = env_info["obs_ally_feats_size"]
        # args.obs_enemy_feats_size = env_info["obs_enemy_feats_size"]
        args.state_ally_feats_size = env_info["state_ally_feats_size"]
        args.state_enemy_feats_size = env_info["state_enemy_feats_size"]
        args.obs_component = env_info["obs_component"]
        args.state_component = env_info["state_component"]
        args.map_type = env_info["map_type"]
        args.agent_own_state_size = env_info["state_ally_feats_size"]

    # Default/Base scheme
    if args.env in ['particle']:  # MPE需要额外处理数据来构造scheme
        env_info = runner.get_env_info()
        args.n_agents = env_info["n_agents"]
        args.n_actions = env_info["n_actions"]
        args.state_shape = env_info["state_shape"]
        args.obs_shape = env_info["obs_shape"]
        args.action_spaces = env_info["action_spaces"]
        args.actions_dtype = env_info["actions_dtype"]
        args.normalise_actions = env_info.get("normalise_actions", False)  # if true, action vectors need to sum to one

        ttype = th.FloatTensor if not args.use_cuda else th.cuda.FloatTensor
        mult_coef_tensor = ttype(args.n_agents, args.n_actions)
        action_min_tensor = ttype(args.n_agents, args.n_actions)
        if all([isinstance(act_space, spaces.Box) for act_space in args.action_spaces]):
            for _aid in range(args.n_agents):
                for _actid in range(args.action_spaces[_aid].shape[0]):
                    _action_min = args.action_spaces[_aid].low[_actid]
                    _action_max = args.action_spaces[_aid].high[_actid]
                    mult_coef_tensor[_aid, _actid] = (_action_max - _action_min).item()
                    action_min_tensor[_aid, _actid] = (_action_min).item()
        elif all([isinstance(act_space, spaces.Tuple) for act_space in args.action_spaces]):
            for _aid in range(args.n_agents):
                for _actid in range(args.action_spaces[_aid].spaces[0].shape[0]):
                    _action_min = args.action_spaces[_aid].spaces[0].low[_actid]
                    _action_max = args.action_spaces[_aid].spaces[0].high[_actid]
                    mult_coef_tensor[_aid, _actid] = (_action_max - _action_min).item()
                    action_min_tensor[_aid, _actid] = (_action_min).item()
                for _actid in range(args.action_spaces[_aid].spaces[1].shape[0]):
                    _action_min = args.action_spaces[_aid].spaces[1].low[_actid]
                    _action_max = args.action_spaces[_aid].spaces[1].high[_actid]
                    tmp_idx = _actid + args.action_spaces[_aid].spaces[0].shape[0]
                    mult_coef_tensor[_aid, tmp_idx] = (_action_max - _action_min).item()
                    action_min_tensor[_aid, tmp_idx] = (_action_min).item()

        args.actions2unit_coef = mult_coef_tensor
        args.actions2unit_coef_cpu = mult_coef_tensor.cpu()
        args.actions2unit_coef_numpy = mult_coef_tensor.cpu().numpy()
        args.actions_min = action_min_tensor
        args.actions_min_cpu = action_min_tensor.cpu()
        args.actions_min_numpy = action_min_tensor.cpu().numpy()

        def actions_to_unit_box(actions):
            if isinstance(actions, np.ndarray):
                return args.actions2unit_coef_numpy * actions + args.actions_min_numpy
            elif actions.is_cuda:
                return args.actions2unit_coef * actions + args.actions_min
            else:
                return args.args.actions2unit_coef_cpu * actions + args.actions_min_cpu

        def actions_from_unit_box(actions):
            if isinstance(actions, np.ndarray):
                return th.div((actions - args.actions_min_numpy), args.actions2unit_coef_numpy)
            elif actions.is_cuda:
                return th.div((actions - args.actions_min), args.actions2unit_coef)
            else:
                return th.div((actions - args.actions_min_cpu), args.actions2unit_coef_cpu)

        # make conversion functions globally available
        args.actions2unit = actions_to_unit_box
        args.unit2actions = actions_from_unit_box

        action_dtype = th.long if not args.actions_dtype == np.float32 else th.float
        if all([isinstance(act_space, spaces.Box) for act_space in args.action_spaces]):
            actions_vshape = 1 if not args.actions_dtype == np.float32 else max(
                [i.shape[0] for i in args.action_spaces])
        elif all([isinstance(act_space, spaces.Tuple) for act_space in args.action_spaces]):
            actions_vshape = 1 if not args.actions_dtype == np.float32 else \
                max([i.spaces[0].shape[0] + i.spaces[1].shape[0] for i in args.action_spaces])
        elif all([isinstance(act_space, spaces.Discrete) for act_space in
                  args.action_spaces]):  # 修改，新增Discrete版本的vshape定义
            actions_vshape = 1

    scheme = {
        "state": {"vshape": env_info["state_shape"]},
        "obs": {"vshape": env_info["obs_shape"], "group": "agents"},
        "actions": {"vshape": (actions_vshape,), "group": "agents", "dtype": action_dtype},
        "avail_actions": {"vshape": (env_info["n_actions"],), "group": "agents", "dtype": th.int},
        "probs": {"vshape": (env_info["n_actions"],), "group": "agents", "dtype": th.float},
        "reward": {"vshape": (1,)},
        "terminated": {"vshape": (1,), "dtype": th.uint8}
    }
    if hasattr(args, "scheme"):  # 如果有指定scheme
        if args.scheme == "differ":  # differ专用的scheme，硬性规定了单位存活标签信息
            scheme = {
                "state": {"vshape": env_info["state_shape"]},
                "obs": {"vshape": env_info["obs_shape"], "group": "agents"},
                "actions": {"vshape": (actions_vshape,), "group": "agents", "dtype": action_dtype},
                "avail_actions": {"vshape": (env_info["n_actions"],), "group": "agents", "dtype": th.int},
                "probs": {"vshape": (env_info["n_actions"],), "group": "agents", "dtype": th.float},
                "reward": {"vshape": (1,)},
                "terminated": {"vshape": (1,), "dtype": th.uint8},
                "indi_terminated": {"vshape": (env_info["n_agents"],), "dtype": th.uint8},  # DIFFER特有的
            }
        if args.scheme == "inspire":  # inspire专用的scheme，硬性规定了单位存活标签信息和可视标签矩阵
            scheme = {
                "state": {"vshape": env_info["state_shape"]},
                "obs": {"vshape": env_info["obs_shape"], "group": "agents"},
                "actions": {"vshape": (actions_vshape,), "group": "agents", "dtype": action_dtype},
                "avail_actions": {"vshape": (env_info["n_actions"],), "group": "agents", "dtype": th.int},
                "probs": {"vshape": (env_info["n_actions"],), "group": "agents", "dtype": th.float},
                "reward": {"vshape": (1,)},
                "terminated": {"vshape": (1,), "dtype": th.uint8},
                "indi_terminated": {"vshape": (env_info["n_agents"],), "dtype": th.uint8},  # 单位存活标签
                "visibility_matrix": {"vshape": (env_info["n_agents"],), "dtype": th.uint8},  # 可视标签
            }
    groups = {
        "agents": args.n_agents
    }
    preprocess = {
        "actions": ("actions_onehot", [OneHot(out_dim=args.n_actions)])
    }

    # [batch, episode_length, n_agents, feature_dim]
    buffer = ReplayBuffer(scheme, groups, args.buffer_size, env_info["episode_limit"] + 1,
                          preprocess=preprocess,
                          device="cpu" if args.buffer_cpu_only else args.device)
    # Setup multiagent controller here
    mac = mac_REGISTRY[args.mac](buffer.scheme, groups, args)

    # Give runner the scheme
    runner.setup(scheme=scheme, groups=groups, preprocess=preprocess, mac=mac)

    # Learner
    learner = le_REGISTRY[args.learner](mac, buffer.scheme, logger, args)

    if args.use_cuda:
        learner.cuda()

    if args.checkpoint_path != "":
        timesteps = []
        timestep_to_load = 0

        if not os.path.isdir(args.checkpoint_path):
            logger.console_logger.info("Checkpoint directiory {} doesn't exist".format(args.checkpoint_path))
            return

        # Go through all files in args.checkpoint_path
        for name in os.listdir(args.checkpoint_path):
            full_name = os.path.join(args.checkpoint_path, name)
            # Check if they are dirs the names of which are numbers
            if os.path.isdir(full_name) and name.isdigit():
                timesteps.append(int(name))

        if args.load_step == 0:
            # choose the max timestep
            timestep_to_load = max(timesteps)
        else:
            # choose the timestep closest to load_step
            timestep_to_load = min(timesteps, key=lambda x: abs(x - args.load_step))

        model_path = os.path.join(args.checkpoint_path, str(timestep_to_load))

        logger.console_logger.info("Loading model from {}".format(model_path))
        learner.load_models(model_path)
        runner.t_env = timestep_to_load

        if args.evaluate or args.save_replay:
            evaluate_sequential(args, runner)
            return

    # start training
    episode = 0
    last_test_T = -args.test_interval - 1
    last_log_T = 0
    model_save_time = 0

    start_time = time.time()
    last_time = start_time

    logger.console_logger.info("Beginning training for {} timesteps".format(args.t_max))

    while runner.t_env <= args.t_max:
        # Run for a whole episode at a time
        with th.no_grad():
            # t_start = time.time()
            episode_batch = runner.run(test_mode=False)
            if episode_batch.batch_size > 0:  # After clearing the batch data, the batch may be empty.
                buffer.insert_episode_batch(episode_batch)
            # print("Sample new batch cost {} seconds.".format(time.time() - t_start))
            episode += args.batch_size_run

        if buffer.can_sample(args.batch_size):
            if args.accumulated_episodes and episode % args.accumulated_episodes != 0:
                continue

            episode_sample = buffer.sample(args.batch_size)

            # Truncate batch to only filled timesteps
            max_ep_t = episode_sample.max_t_filled()
            episode_sample = episode_sample[:, :max_ep_t]

            if episode_sample.device != args.device:
                episode_sample.to(args.device)

            learner.train(episode_sample, runner.t_env, episode)
            del episode_sample

        # Execute test runs once in a while
        n_test_runs = max(1, args.test_nepisode // runner.batch_size)
        if (runner.t_env - last_test_T) / args.test_interval >= 1.0:
            logger.console_logger.info("t_env: {} / {}".format(runner.t_env, args.t_max))
            logger.console_logger.info("Estimated time left: {}. Time passed: {}".format(
                time_left(last_time, last_test_T, runner.t_env, args.t_max), time_str(time.time() - start_time)))
            last_time = time.time()
            last_test_T = runner.t_env
            with th.no_grad():
                for _ in range(n_test_runs):
                    runner.run(test_mode=True)

        if args.save_model and (
                runner.t_env - model_save_time >= args.save_model_interval or runner.t_env >= args.t_max):
            model_save_time = runner.t_env
            save_path = os.path.join(args.local_results_path, "models", args.log_model_dir, args.unique_token,
                                     str(runner.t_env))
            # "results/models/{}".format(unique_token)
            os.makedirs(save_path, exist_ok=True)
            logger.console_logger.info("Saving models to {}".format(save_path))

            # learner should handle saving/loading -- delegate actor save/load to mac,
            # use appropriate filenames to do critics, optimizer states
            learner.save_models(save_path)

        if (runner.t_env - last_log_T) >= args.log_interval:
            logger.log_stat("episode", episode, runner.t_env)
            logger.log_stat("episode_in_buffer", buffer.episodes_in_buffer, runner.t_env)
            logger.print_recent_stats()
            last_log_T = runner.t_env

    runner.close_env()
    logger.console_logger.info("Finished Training")

    # flush
    # sys.stdout.flush()
    # time.sleep(10)


def args_sanity_check(config, _log):
    # set CUDA flags
    # config["use_cuda"] = True # Use cuda whenever possible!
    if config["use_cuda"] and not th.cuda.is_available():
        config["use_cuda"] = False
        _log.warning("CUDA flag use_cuda was switched OFF automatically because no CUDA devices are available!")

    if config["test_nepisode"] < config["batch_size_run"]:
        config["test_nepisode"] = config["batch_size_run"]
    else:
        config["test_nepisode"] = (config["test_nepisode"] // config["batch_size_run"]) * config["batch_size_run"]

    return config
