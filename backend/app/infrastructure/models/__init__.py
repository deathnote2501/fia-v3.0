"""
FIA v3.0 - Infrastructure Models Package
SQLAlchemy models for database tables
"""

# Import only the critical models to avoid table conflicts
from .trainer_model import TrainerModel
from .training_model import TrainingModel
from .training_session_model import TrainingSessionModel
from .learner_session_model import LearnerSessionModel
from .chat_message_model import ChatMessageModel
from .slide_model import SlideModel

__all__ = [
    "TrainerModel",
    "TrainingModel", 
    "TrainingSessionModel",
    "LearnerSessionModel",
    "ChatMessageModel",
    "SlideModel"
]