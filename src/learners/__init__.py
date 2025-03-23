from .q_learner import QLearner
from .dmaq_qatten_learner import DMAQ_qattenLearner
from .nq_learner import NQLearner
from .ppo_learner import PPOLearner
from .coma_learner import COMALearner
from .nq_learner_data_augmentation import NQLearnerDataAugmentation

REGISTRY = {}

REGISTRY["nq_learner"] = NQLearner
REGISTRY["dmaq_qatten_learner"] = DMAQ_qattenLearner
REGISTRY["q_learner_data_augmentation"] = NQLearnerDataAugmentation
REGISTRY["q_learner"] = QLearner
REGISTRY["ppo_learner"] = PPOLearner
REGISTRY["coma_learner"] = COMALearner