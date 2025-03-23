# pymarl-smac-smacv2-google-football-
集成了smac，smacv2,和google football的pymarl整合版仓库。只要配置好环境，并放入对应的文件，就可以在本仓库运行MARL算法（或许会有报错）。

thanks to:

1. https://github.com/tjuHaoXiaotian/pymarl3
2. <https://github.com/google-research/football>
3. https://github.com/jidiai/GRF_MARL
4. https://github.com/oxwhirl/pymarl
5. https://github.com/oxwhirl/smac

## 环境配置

您可以通过运行以下指令完成环境配置：

```
sh install_sc2.sh
sh install_gfootball.sh
sh install_dependencies.sh
```

也可以走以下流程人工配置（比较推荐）

### 人工配置流程

1. 创建一个conda环境，python版本为3.8.10（超出3.9版本的话GRF的安装或许会出错）

2. 配置GRF环境：

   1. 安装依赖软件：

      ```
      sudo apt-get install git cmake build-essential libgl1-mesa-dev libsdl2-dev libsdl2-image-dev libsdl2-ttf-dev libsdl2-gfx-dev libboost-all-dev libdirectfb-dev libst-dev mesa-utils xvfb x11vnc python3-pip
      ```

      如果出现报错：The following packages have been kept back:
      linux-generic linux-headers-generic linux-image-generic。执行下面指令以重新安装部分软件：

      ```
      sudo apt-get install linux-generic linux-headers-generic linux-image-generic
      ```

   2. 下载依赖包：

      ```
      python3 -m pip install --upgrade pip setuptools psutil wheel
      
      pip install six 
      
      pip install --upgrade pip==24.0(高版本在下载时会报错)
      ```

   3. 下载GRF的运行环境：

      ```
      git clone https://github.com/google-research/football.git
      cd football
      python3 -m pip install .
      ```

      也可以用pip install gfootball。但是可能报错，上面的方式稳妥一些。

   4. 运行测试：

      ```
      python3 -m gfootball.play_game --action_set=full
      ```

      命令行出现以下内容说明成功：

      ```
       pygame 2.6.0 (SDL 2.28.4, Python 3.8.10)
      Hello from the pygame community. https://www.pygame.org/contribute.html
      ALSA lib confmisc.c:767:(parse_card) cannot find card '0'
      ALSA lib conf.c:4528:(_snd_config_evaluate) function snd_func_card_driver returned error: No such file or directory
      ALSA lib confmisc.c:392:(snd_func_concat) error evaluating strings
      ALSA lib conf.c:4528:(_snd_config_evaluate) function snd_func_concat returned error: No such file or directory
      ALSA lib confmisc.c:1246:(snd_func_refer) error evaluating name
      ALSA lib conf.c:4528:(_snd_config_evaluate) function snd_func_refer returned error: No such file or directory
      ALSA lib conf.c:5007:(snd_config_expand) Evaluate error: No such file or directory
      ALSA lib pcm.c:2495:(snd_pcm_open_noupdate) Unknown PCM default
      No DISPLAY defined, doing off-screen rendering
      ```

   优先配置GRF是因为从个人经验来说，GRF的配置最容易出问题。想运行GRF的话需要把配置SMAC步骤也做完，或者只下载SMAC，把SMAC环境相关的文件/代码删除/注释以防止报错。

   注：如果您想在自己的工程（基于pymarl）中加入GRF环境，除去配置环境外还需要对工程做以下改动：

   1. 复制\src\envs\gfootball文件夹到您的工程，注意路径保持一致

   2. 修改src\envs的init.py：

      ```python
      在src/envs的init.py写入如下：
      try:
          gfootball = True
          from .gfootball import GoogleFootballEnv
      except Exception as e:
          gfootball = False
          print(e)
      
      （这段都有，是分隔段，上面放try段，下面放if段）def env_fn(env, **kwargs) -> MultiAgentEnv:
          return env(**kwargs)
      
      if gfootball:
          REGISTRY["gfootball"] = partial(env_fn, env=GoogleFootballEnv)
      ```

   3. 复制src\config\envs的gfootball.yaml到您的工程，注意路径保持一致。

3. 配置SMAC环境：

   1. 下载SC2游戏体。

      ```
      wget https://blzdistsc2-a.akamaihd.net/Linux/SC2.4.6.2.69232.zip
      ```

      具体版本可以到<https://github.com/Blizzard/s2client-proto?tab=readme-ov-file#downloads>找。点击版本就是下载链接。

      之后unzip指令解压（解压密码iagreetotheeula）。版本号需要注意，要与之后的游戏回放/工程参数的版本号一致，否则无法兼容。

      记住SC2根目录的地址（之后用SC2PATH代指）

   2. 下载MAP。

      ```
      wget https://github.com/oxwhirl/smac/releases/download/v0.1-beta1/SMAC_Maps.zip
      ```

      之后用unzip指令解压获得_MACOSX和SMAC_MAPS两个文件夹，需要拷贝到$SC2PATH/Maps。

   3. 安装依赖包：

      ```
      pip install git+https://github.com/oxwhirl/smac.git
      pip install torch（可以到pytorch官网找对应GPU和环境的下载指令）
      pip install sacred
      pip install PyYAML==3.13
      ```

   4. 检查MAP和SMAC是否配置成功：

      ```
      python -m smac.bin.map_list （输出list为成功）
      python -m smac.examples.random_agents （如果最后输出reward+unable to parse websocker frame结束就成功）
      ```

   5. 在工程中配置SC2软连接：

      ```
      cd pymarl (进入工程目录)
      mkdir 3rdparty
      cd 3rdparty/
      ln -s StarCraftII的根目录 StarCraftII （如ln -s /root/StarCraftII StarCraftII）
      ```

   如果只执行SMAC环境的话，把SMACV2和GRF部分的文件/代码删除即可。配置pymarl本体也可以这么做。

4. 配置SMACV2：

   1. 确认已按照SMAC配置SC2游戏软件和MAPS，确认已按照SMAC配置下载依赖包

   2. 下载依赖包：

      ```
      pip install git+https://github.com/oxwhirl/smacv2.git
      pip install tensorboard tensorboard_logger
      
      以下部分和SMAC重复：
      pip install torch (可以自己到pytorch官网找GPU版本的下载指令)
      pip install sacred
      pip install PyYAML==3.13
      ```

   3. 配置新的地图文件：

      将https://github.com/oxwhirl/smacv2/tree/main/smacv2/env/starcraft2/maps/SMAC_Maps文件夹下的地图下载，并移动到$SC2PATH/Maps。

      这里也可以用src/envs/smac_v2/official/maps的SMAC_MAPS文件夹，打个压缩包复制到$SC2PATH/Maps解压即可。

   4. 确认已按照SMAC配置SC2软连接。

### 运行测试

测试pymarl是否可以跑通：在pymarl目录和虚拟环境下运行

1. SMAC:```python src/main.py --config=qmix --env-config=sc2 with env_args.map_name=2s3z t_max=20000```。
2. SMACV2:```python src/main.py --config=qmix --env-config=sc2_v2_zerg with t_max=20000```
3. GRF：```python3 src/main.py --config=qmix --env-config=gfootball with env_args.map_name=academy_pass_and_shoot_with_keeper t_max=20000```

目前的版本在运行IPPO时可能出现报错，其他版本，特别是基于QMIX的算法，应该没有问题。

#### 实验结果查询

实验结果会统一保存在results中，并按照地图名\算法名进行分类存放。

1. 在SMAC和SMACV2的实验结果中，cout.txt记录了控制台输出，可以看运行时间和剩余时间。info.json中，battle_won_mean记录了两次采样之间的平均胜率，battle_won_mean_T是对应的采样时间点。
2. 在GRF的运行结果中，cout.txt记录了控制台输出，可以看剩余时间和运行时间。info.json中，score_reward_mean记录了两次采样之间的平均得分，score_reward_mean_T记录了对应时间点。注意是得分不是胜率，SCORE是对面进球得-1.我方进球得+1。如果开启了check_points，还会有经过每个区域的得分和扣分，所以出现负分的个例也不稀奇。

### 报错记录

#### GRF部分：

1. 如果出现报错：

   ```
       /tmp/pip-req-build-t41lw446/third_party/gfootball_engine /tmp/pip-req-build-t41lw446
       gfootball/build_game_engine.sh: line 29: cmake: command not found
       gfootball/build_game_engine.sh: 
   
   ```

   cmake不存在或者环境路径未配置导致的。

   执行以下命令：

   sudo apt autoremove cmake

   sudo apt install cmake

   以重新安装cmake即可解决问题。

2. 如果出现报错：

   ```
       /tmp/pip-req-build-t41lw446/third_party/gfootball_engine /tmp/pip-req-build-t41lw446
       gfootball/build_game_engine.sh:  line 30: pushd: third_party/gfootball_engine: No such file or directory
   
   ```

   这个是因为boost-python在ubuntu20.04 LTS 虚拟机中只支持python 3.8及以下，而你可能使用了3.9、3.10这种高版本。目前来说没有很好的解决方案，建议转到python3.8.10重新安装。如执行以下指令以更改环境内python版本：

   conda install python=3.8.10

   注意，更改python版本会导致你需要重新下载python扩展库（pip install指令下载的库）

3. 如果在运行一些地图（比如academy_pass_and_shoot_with_keeper）时发现报错如下：

   ```
     File "/root/miniconda3/lib/python3.8/site-packages/gfootball/env/football_env_core.py", line 314, in _retrieve_observation
    info.left_controllers[i].controlled_player)
      IndexError: Index out of range
   ```

   请按照如下步骤修改gfootball库的代码：

   ```python
   在</你的环境路径/lib/python3.8/site-packages/gfootball/env/football_env_core.py>的第312行开始将被注释的内容换成新的for循环，防止agent数目多于controller数目：
       result['right_agent_controlled_player'] = []
       for i in range(self._env.config.left_agents):
       #for i in range(min(self._env.config.left_agents, len(info.left_controllers))):
         result['left_agent_controlled_player'].append(
             info.left_controllers[i].controlled_player)
         result['left_agent_sticky_actions'].append(
             np.array(self.sticky_actions_state(True, i), dtype=np.uint8))
       for i in range(self._env.config.right_agents):
       #for i in range(min(self._env.config.right_agents, len(info.right_controllers))):
           result['right_agent_controlled_player'].append(
               info.right_controllers[i].controlled_player)
           result['right_agent_sticky_actions'].append(
               np.array(self.sticky_actions_state(False, i), dtype=np.uint8))
   
   ```python
   ```

4. 运行最后一步出现报错：

   ```
   python3(_PyEval_EvalFrameDefault+0x4cb3)[0x5647c2383e33]
   python3(_PyEval_EvalCodeWithName+0x2c2)[0x5647c2367bd2]
   python3(+0x1ae6d7)[0x5647c23696d7]
   python3(_PyEval_EvalFrameDefault+0x1791)[0x5647c2380911]
   Error: signal 11:
   ```

   目前来看应该不需要担心，可以正常运行环境，只是记录不了replay录像。

5. 在运行GRF时，遇到以下报错：

   ```
   File "/home/stu/zjn/smacv2_test/src/run/run.py", line 113, in run_sequential
       args.n_allies = env_info["n_allies"]
   KeyError: 'n_allies'
   ```

   这个是因为pymarl3的run.py针对smac和smacv2多写入了一些参数，将/run/run.py的109行修改为：

   ```python
       if args.env in ["sc2", "sc2_v2", "gfootball"]:
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
   ```

   即可。



#### SMAC部分：

1. 如果报错：

   ```
     Traceback (most recent calls WITHOUT Sacred internals):
    File “src/main.py”, line 33, in my_main
    _config[‘env_args’][‘seed’] = _config[“seed”]
    sacred.utils.SacredError: The configuration is read-only in a captured function!                 
    原文链接：https://blog.csdn.net/Pmkin/article/details/136706935
   ```

   在src/main.py的import语句组后面加入如下语句：

   ```python
        from sacred import SETTINGS
        SETTINGS.CONFIG.READ_ONLY_CONFIG = False
   ```

2. 运行工程报错：

   ```
   TypeError: can‘t convert cuda:0 device type tensor to numpy. Use Tensor.cpu() to copy the tensor to
   ```

   是在GPU运行时候的报错，logger的state存的数据有部分是tensor引起的，进入/pymarl/src/utils/logging.py，修改：

   ```
      #item = "{:.4f}".format(np.mean([x[1] for x in self.stats[k][-window:]]))为
   item = "{:.4f}".format(np.mean(1))
   ```

   这样打印时候的数据都是1，但是不影响info.json的数据

3. 运行报错：
   AttributeError: module 'collections' has no attribute 'Mapping'
   python版本升高之后把collections.Mapping改成了collections.abc.Mapping，可以把python改成3.9或3.8版本。也可以在src.main.py的第59行：

   ```python
      if isinstance(v, collections.Mapping):
            d[k] = recursive_dict_update(d.get(k, {}), v)
      的collections.Mapping改为collections.abc.Mapping
   ```

4. 运行报错：AttributeError: module 'numpy' has no attribute 'bool'.

   numpy高版本把numpy.bool换成了nnumpy.bool_。你可以选择把工程里的numpy.bool全部换掉，或者更改numpy版本：

   pip install numpy==1.23.2

#### SMACV2部分：

1. ValueError: Map SMAC_Maps/32x32_flat.SC2Map not found in /home/stu/zjn/smacv2_test/3rdparty/StarCraftII/Maps.：

   出现这个错误说明SC2的地图导入有问题导致丢了地图。SMACV1有很多地图，SMACV2则默认只要这个32x32_flat.SC2Map。重做地图导入这一步即可

## 添加新算法

1. 将新的learner纳入可选参数：在src/learners下面仿照其他文件编写一一个learner。在src/learners/__init__.py仿照已有写法导入包，并添加参数：REGISTRY["learner模块名"]=learner类名。这里参数筛选用的是字典匹配方式。这里的参数用于src/config/algs中。

2. 如果您有意配置其他模块，可以参考工程的文件夹结果来放置文件：

   1. components：工程运行需要的模块
   2. config/algs：放算法的.yaml文件。文件名对应运行指令时的--config=参数后的名字，用于指定运行算法。config/envs放的是环境的.yaml，修改环境时才用得到。
   3. envs:环境配置文件
   4. controllers:算法与环境交互的控制器
   5. learners:放learner，是算法训练代码的文件
   6. modules：放算法的网络结构模块，包括agent,critic,layer,mixer等。
   7. run,runner,utils：放工程文件，一般不需要动。run是工程实际运行环境和训练算法的主要文件，runner配置与环境交互的细节，utils放运行需要的其他文件（主要是日志记录之类的代码）

3. 将新的训练算法纳入可选参数：在src/config/algs创建一个算法名.yaml存放算法模块设置和超参数，修改参考如下：

   ```yaml
   # --- QMIX_super specific parameters ---
   
    # use epsilon greedy action selector #epsilon选择动作策略的参数
    action_selector: "epsilon_greedy" #名字
    epsilon_start: 1.0 #在第几步启动
    epsilon_finish: 0.05 #随机选择动作的概率
    epsilon_anneal_time: 50000 
   
    runner: "episode" #选择runner，可用参数在/src/runner/__init.py
   
    buffer_size: 5000 #缓冲池长度
   
    # update the target network every {} episodes 每隔多少轮更新一次目标网络
    target_update_interval: 200
   
    # use the Q_Learner to train
    agent_output_type: "q" #agent输出的是值预估q还是动作a
    learner: "q_learner_super" #learner选择。参数在/src/learners/__nint.py
    double_q: True #QMIX特有的参数，这里也可以自定义自己需要的参数
    mixer: "qmix" #mixer选择
    mixing_embed_dim: 32
    hypernet_layers: 2
    hypernet_embed: 64
   
    name: "qmix_super"  #算法名字
   ```

   

## 环境介绍

### SMAC

SMAC是WARL环境，基于SC2为协作多智能体强化学习研究提供实验环境。由暴雪SC2和Pysc2提供支持。

SMAC中每个角色都由一个单独agent控制，每个agent只享有以角色为中心的部分视野。相对于原始版的SC2LE，SMAC更适合MARL的实验。在部分可观察性的MARL特性下，每个agent控制一个角色，进行协作对抗另一支部队。SMAC由22个MAP组成，MAP可供2-27个agent运行，均为一个agent操作一个角色组成战斗小队对抗游戏内置AI控制的另一支部队的模式。每个MAP中，内置游戏AI均会指挥自己的小队攻击agent们扮演的角色，任一支部队全部死亡或者超时的时候结束场景。

MAP的目标均为使MARL的获胜率最大化。丰富的地形，SC2的战术复杂性，使得SMAC具有相当的难度。MAP中有完全同类型角色的场景，也有多类型混编的场景，己方存在对敌方兵种克制、被敌方兵种克制单位的场景，以少打多的场景，存在可利用地形致胜机会的场景。

SMAC的环境特性如下：

1. 完全分散的多agent环境：不同于SC2LE，SMAC中每个agent仅操作一个单位，而不是扮演一个玩家
2. 部分可观察性：每个步长中，agent仅收到其单位固定视野范围（7-70格）的局部观测（范围内敌方我方单位的距离，xy相对坐标，血量，护盾，单位类型 | 视野内友军单位的最后一次行动 | 周围地形特征），对范围外的情况处于未知。 如果采用集中训练模式，在训练的时候可以令agent掌握全图全单位的信息，行动和地形。
3. 动作空间简单：因为仅涉及SC2的小队战斗部分，所以agent1的动作只有四方向move，攻击，治疗，停止
4. 奖励稀疏：可以只对结果进行+1/-1的奖励。也可以根据受伤/造成伤害/击杀/被击杀给奖励。
5. 环境确定性：每次打开地图时，地图的初始设置都是一致的。这比较方便agent的训练，但也可能造成泛化能力的不足或者过拟合的出现

资源站：

       1. 暴雪官方的pysc2库（SC2API接口），linux版本SC2，配套地图和训练数据：https://github.com/Blizzard/s2client-proto
          2. SMAC本体：https://github.com/oxwhirl/smac
             3. pymarl实验框架：https://github.com/oxwhirl/pymarl

下载教程：

1. SMAC：https://developer.aliyun.com/article/1296841
2. Pymarl：https://blog.csdn.net/zhoupingqi2017/article/details/124173208

#### 地图设置

map(按难度分成三个等级)具体等级见<chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://reinholdm.github.io/Homepage/%E5%A4%9A%E6%99%BA%E8%83%BD%E4%BD%93%E5%BC%BA%E5%8C%96%E5%AD%A6%E4%B9%A0%E7%8E%AF%E5%A2%83-%E6%98%9F%E9%99%85%E4%BA%89%E9%9C%B82%E4%BB%8B%E7%BB%8D.pdf>

|       Name        | Ally Units                         | Enemy Units                        | Type                                          | difficulty         |
| :---------------: | ---------------------------------- | ---------------------------------- | --------------------------------------------- | ------------------ |
|        3m         | 3 Marines                          | 3 Marines                          | homogeneous & symmetric                       | Easy               |
|        8m         | 8 Marines                          | 8 Marines                          | homogeneous & symmetric                       | Easy               |
|        25m        | 25 Marines                         | 25 Marines                         | homogeneous & symmetric                       | Hard               |
|       2s3z        | 2 Stalkers & 3 Zealots             | 2 Stalkers & 3 Zealots             | heterogeneous & symmetric                     | Easy               |
|       3s5z        | 3 Stalkers & 5 Zealots             | 3 Stalkers & 5 Zealots             | heterogeneous & symmetric                     | Hard               |
|        MMM        | 1 Medivac, 2 Marauders & 7 Marines | 1 Medivac, 2 Marauders & 7 Marines | heterogeneous & symmetric                     | Easy               |
|     5m_vs_6m      | 5 Marines                          | 6 Marines                          | homogeneous & asymmetric                      | Hard               |
|     8m_vs_9m      | 8 Marines                          | 9 Marines                          | homogeneous & asymmetric                      | Hard               |
|    10m_vs_11m     | 10 Marines                         | 11 Marines                         | homogeneous & asymmetric                      | Hard               |
|    27m_vs_30m     | 27 Marines                         | 30 Marines                         | homogeneous & asymmetric                      | Super Hard         |
|   3s5z_vs_3s6z    | 3 Stalkers & 5 Zealots             | 3 Stalkers & 6 Zealots             | heterogeneous & asymmetric                    | Super Hard         |
|       MMM2        | 1 Medivac, 2 Marauders & 7 Marines | 1 Medivac, 3 Marauders & 8 Marines | heterogeneous & asymmetric                    | Super Hard         |
|     2m_vs_1z      | 2 Marines                          | 1 Zealot                           | micro-trick: alternating fire（考验交替开火） | Easy               |
|     2s_vs_1sc     | 2 Stalkers                         | 1 Spine Crawler                    | micro-trick: alternating fire（考验交替开火） | Easy（实测还挺难） |
|     3s_vs_3z      | 3 Stalkers                         | 3 Zealots                          | micro-trick: kiting（考验风筝战术）           | Easy               |
|     3s_vs_4z      | 3 Stalkers                         | 4 Zealots                          | micro-trick: kiting（考验风筝战术）           | Easy               |
|     3s_vs_5z      | 3 Stalkers                         | 5 Zealots                          | micro-trick: kiting（考验风筝战术）           | Hard               |
|     6h_vs_8z      | 6 Hydralisks                       | 8 Zealots                          | micro-trick: focus fire（考验集中火力）       | Super Hard         |
|     corridor      | 6 Zealots                          | 24 Zerglings                       | micro-trick: wall off（考验分割）             | Super Hard         |
|   bane_vs_bane    | 20 Zerglings & 4 Banelings         | 20 Zerglings & 4 Banelings         | micro-trick: positioning（考验位置选择）      | Easy               |
| so_many_banelings | 7 Zealots                          | 32 Banelings                       | micro-trick: positioning（考验位置选择）      | Easy               |
|    2c_vs_64zg     | 2 Colossi                          | 64 Zerglings                       | micro-trick: positioning（考验位置选择）      | Hard               |
|      1c3s5z       | 1 Colossi & 3 Stalkers & 5 Zealots | 1 Colossi & 3 Stalkers & 5 Zealots | heterogeneous & symmetric                     | Easy               |

注意，地图的智能体个数越多，地图需要的运行内存和显存越大，运行耗时越长。

### GRF

基于谷歌足球的MARL实验环境，每队若干人，通过射门得分。足球比赛对于MARL来说更具有挑战性，因为需要MARL学习短期角色控制，行为逻辑（传球，追球，阻拦对方球员）和全局策略。
地图一览：<https://github.com/google-research/football/tree/master/gfootball/scenarios>
工程：

<https://github.com/google-research/football>

https://github.com/jidiai/GRF_MARL

介绍这个的论文：

<chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://arxiv.org/pdf/1907.11180>

环境特性如下：

1. 环境随机性：每次重启地图时，角色的位置和球的位置都还是随机的。对手AI的行为逻辑也具有随机性。当然也可以改为确定性
2. 针对足球比赛的不同子任务设计了一系列academy地图，也提供5v5和11v11的全局比赛。
3. 部分可观察性：每个角色只能关注其周围一段空间的数据变化
4. 行为简单性：可控制的行为只有多方向移动和踢球。
5. 实时物理引擎：游戏模拟器基本基于物理规则运行，帮助agent在更加真实的环境中理解和适应环境变化

#### 地图设置

可选择地图有：

1. 11_vs_11：11人足球赛，进球得分。我方中后卫在初始时有球。最大持续时间为3000帧。直接运行到时间结束看比分

   11_vs_11_competition（两边都是1.0难度AI。也可以让agent扮演其中一队）

   11_vs_11_easy_stochastic（对方难度0.05）

   11_vs_11_hard_stochastic（对方难度0.95）

   11_vs_11_kaggle（两边都是1.0难度AI，有半场设定）

   11_vs_11_stochastic（对方难度0.6）

2. 1_vs_1_easy：1v1足球赛，进球得分。两边AI难度都是0.0，游戏时长500帧。直接运行到时间结束看比分

3. 5_vs_5:5v5足球赛，进球得分。两边都有一个不可以主动控制的守门员。两边AI难度0.05，游戏时长3000帧。直接运行到时间结束看比分

4. academy_3_vs_1_with_keeper：我方三名球员在禁区边缘试图射门得分。我们在对方球门两个侧方和正前方都有一个球员，对方只有一个守门员和一个球员。初始球在我方中间球员。游戏时间400帧，超时/得分/丢球停止。

5. academy_corner：标准的角球罚球情况，但发角球的人在发球前不能跑动。双方都是标准11人，得分/超时停止。

6. academy_counterattack：球赛的防守反攻情况。我方守门员拿到球，我方4个球员和对方1个球员在球门附近争夺，剩下的球员接近足球。双方都是标准11人，游戏时间400帧，超时/得分/丢球停止。

   academy_counterattack_easy：我方4个球员和对方1个球员在球门附近争夺

   academy_counterattack_hard：我方4个球员和对方2个球员在球门附近争夺

7. academy_empty_goal：我方球员带球进攻。我们两人（守门员+后卫）对方一人（守门员）。游戏时间400帧，超时/得分/丢球停止。

   academy_empty_goal:从中场带球进攻

   academy_empty_goal_close:从对方禁区带球进攻

8. academy_pass_and_shoot_with_keeper：我方两名球员与对方守门员和一名球员在禁区边缘博弈。游戏时间400帧，超时/得分/丢球停止。

   academy_pass_and_shoot_with_keeper：我方1名球员在球边，旁边是对方的1个球员；另一个正对球门，面对对方守门员。

   academy_run_pass_and_shoot_with_keeper：我方一门球员在禁区边缘带着球；我方另一名正对球门，面对对方守门员，旁边是对方一个球员。

9. academy_run_to_score：我方球员在中场带球，后面是五个对方球员。游戏时间400帧，超时/得分/丢球停止。

   academy_run_to_score：对方守门员不存在（被安排到我方球门去了）

   academy_run_to_score_with_keeper：对方守门员存在

10. academy_single_goal_versus_lazy：11人足球赛，但是对方除去守门员外的球员只会拦截自己附近的球，不会移动。游戏时间3000帧，超时/得分/丢球停止。

除此之外还可以按照格式自定义地图。

地图设置详见https://github.com/google-research/football/tree/master/gfootball/scenarios

### SMACV2

在SMAC的基础上，继续基于星际争霸2的一些单位对战场景、SMAC机器学习API和PySC2实现实验环境。

github库：https://github.com/oxwhirl/smacv2/tree/main

运行工程：https://github.com/tjuHaoXiaotian/pymarl3（疑似可以同时跑SMACV1和SMACV2）



注意：

1. SMACV2和SMAC的地图彼此不兼容。SMACV2只能从那三个文件里面自己选单位数目和单位比例，甚至不能实现不同种族之间的对战。

SMACV2的环境特性如下：

1. 随机性：SMACV2增加了随机化初始位置，随机化单位类型两种随机设置，加大了地图的难度。

   1. 随机化初始位置：有两种情形，各自有0.5概率生成（这个概率可以自己调整）。第一种是surround，我方在地图中间生成并被敌方包围。另一种是reflect场景，随机选择盟军单位的位置进行生成

   2. 随机单位类型：同种族下的单位会根据预先固定规定概率随机生成。

      | Race    | Unit      | Generation Probability |
      | ------- | --------- | ---------------------- |
      | Terran  | Marine    | 0.45                   |
      |         | Marauder  | 0.45                   |
      |         | Medivac   | 0.1                    |
      | Protoss | Stalker   | 0.45                   |
      |         | Zealot    | 0.45                   |
      |         | Colossus  | 0.1                    |
      | Zerg    | Zergling  | 0.45                   |
      |         | Hydralisk | 0.45                   |
      |         | Baneling  | 0.1                    |

      这个是可以在地图文件里改的，但是乱改可能导致很难或者更简单的场景出现。

2. 更多的可更改值：增加了对单位视野范围和攻击范围的更改选项。

#### 地图设置

SMACV2给出了不同种族之间对战的地图设计，具体的双方单位数和生成概率可以在config里自己调。

可选择地图如下：

1. 10gen_protoss：sc2_v2_protoss.yaml，神族对战
2. 10gen_terran：sc2_v2_terran,yaml，人族对战
3. 10gen_zerg：sc2_v2_zerg.yaml，虫族对战

以sc2_gen_protoss.yaml为例：

```yaml
env: sc2wrapped

env_args:
  continuing_episode: False
  difficulty: "7"
  game_version: null
  map_name: "10gen_protoss" #地图名，可以自己改一个新名字以便并行多个地图
  move_amount: 2
  obs_all_health: True
  obs_instead_of_state: False
  obs_last_action: False
  obs_own_health: True
  obs_pathing_grid: False
  obs_terrain_height: False
  obs_timestep_number: False
  reward_death_value: 10 #击杀得分，如果改奖励稀疏改为0
  reward_defeat: 0
  reward_negative_scale: 0.5
  reward_only_positive: True
  reward_scale: True
  reward_scale_rate: 20
  reward_sparse: False  #如果改奖励稀疏改为true
  reward_win: 200
  replay_dir: ""
  replay_prefix: ""
  conic_fov: False
  use_unit_ranges: True
  min_attack_range: 2 #最低攻击距离
  obs_own_pos: True
  num_fov_actions: 12 #视野范围
  capability_config:
    n_units: 5 #我方单位数
    n_enemies: 5 #敌方单位数
    team_gen:
      dist_type: "weighted_teams"
      unit_types: 
        - "stalker"
        - "zealot"
        - "colossus"
      weights: #三种类型敌人的生成比例，一般不需要改
        - 0.45
        - 0.45
        - 0.1
      observe: True
    start_positions:
      dist_type: "surrounded_and_reflect"
      p: 0.5
      map_x: 32
      map_y: 32
    
    # enemy_mask:
    #   dist_type: "mask"
    #   mask_probability: 0.5
    #   n_enemies: 5
  state_last_action: True
  state_timestep_number: False
  step_mul: 8
  heuristic_ai: False
  # heuristic_rest: False
  debug: False
  prob_obs_enemy: 1.0
  action_mask: True

test_nepisode: 32
test_interval: 10000
log_interval: 2000
runner_log_interval: 2000
learner_log_interval: 2000
t_max: 10050000
```

注：

1. 修改 n_units: 5 和n_enemies: 5 会引起运行时间和难度的变化。总单位数越多运行时间越长。敌方单位多于我方单位会引起难度的增加。
2. 修改奖励稀疏会导致难度明显上升
3. 减少视野范围会导致难度明显上升

#### SMACV2推荐人数设置
| 设想               | 配置文件             | `n_units` | `n_enemies` |
| ------------------ | -------------------- | --------- | ----------- |
| `protoss_5_vs_5`   | sc2_gen_protoss.yaml | 5         | 5           |
| `zerg_5_vs_5`      | sc2_gen_zerg.yaml    | 5         | 5           |
| `terran_5_vs_5`    | sc2_gen_terran.yaml  | 5         | 5           |
| `protoss_10_vs_10` | sc2_gen_protoss.yaml | 10        | 10          |
| `zerg_10_vs_10`    | sc2_gen_zerg.yaml    | 10        | 10          |
| `terran_10_vs_10`  | sc2_gen_terran.yaml  | 10        | 10          |
| `protoss_20_vs_20` | sc2_gen_protoss.yaml | 20        | 20          |
| `zerg_20_vs_20`    | sc2_gen_zerg.yaml    | 20        | 20          |
| `terran_20_vs_20`  | sc2_gen_terran.yaml  | 20        | 20          |
| `protoss_10_vs_11` | sc2_gen_protoss.yaml | 10        | 11          |
| `zerg_10_vs_11`    | sc2_gen_zerg.yaml    | 10        | 11          |
| `terran_10_vs_11`  | sc2_gen_terran.yaml  | 10        | 11          |
| `protoss_20_vs_23` | sc2_gen_protoss.yaml | 20        | 23          |
| `zerg_20_vs_23`    | sc2_gen_zerg.yaml    | 20        | 23          |
| `terran_20_vs_23`  | sc2_gen_terran.yaml  | 20        | 23          |

来自https://github.com/oxwhirl/smacv2/tree/main
