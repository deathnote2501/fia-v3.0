"""
FIA v3.0 - Infrastructure Models Package
SQLAlchemy models for database tables
"""

# Import all models to ensure proper relationship resolution
from .trainer_model import TrainerModel
from .training_model import TrainingModel
from .training_session_model import TrainingSessionModel
from .learner_session_model import LearnerSessionModel
from .chat_message_model import ChatMessageModel
from .slide_model import SlideModel
from .learner_training_plan_model import LearnerTrainingPlanModel
from .training_module_model import TrainingModuleModel
from .training_submodule_model import TrainingSubmoduleModel
from .training_slide_model import TrainingSlideModel

__all__ = [
    "TrainerModel",
    "TrainingModel", 
    "TrainingSessionModel",
    "LearnerSessionModel",
    "ChatMessageModel",
    "SlideModel",
    "LearnerTrainingPlanModel",
    "TrainingModuleModel",
    "TrainingSubmoduleModel", 
    "TrainingSlideModel"
]