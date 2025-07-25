# Pydantic Schemas
# Data validation and serialization schemas

from .trainer import TrainerCreate, TrainerUpdate, TrainerResponse, TrainerLogin
from .training import TrainingCreate, TrainingUpdate, TrainingResponse, TrainingListResponse
from .training_session import (
    TrainingSessionCreate, TrainingSessionUpdate, TrainingSessionResponse, TrainingSessionWithLink
)
from .learner_session import (
    LearnerProfileCreate, LearnerSessionResponse, LearnerSessionWithPlan, LearnerProgressUpdate
)
from .slide import SlideCreate, SlideResponse, SlideContentOnly, SlideTimeUpdate
from .chat_message import (
    ChatMessageCreate, ChatMessageResponse, ChatQuestionCreate, ChatConversation
)
from .api_log import ApiLogCreate, ApiLogResponse, ApiLogSummary
from .auth import Token, TokenData, LoginResponse
from .common import ErrorResponse, SuccessResponse, PaginatedResponse, HealthResponse

__all__ = [
    # Trainer schemas
    "TrainerCreate", "TrainerUpdate", "TrainerResponse", "TrainerLogin",
    
    # Training schemas
    "TrainingCreate", "TrainingUpdate", "TrainingResponse", "TrainingListResponse",
    
    # Training session schemas
    "TrainingSessionCreate", "TrainingSessionUpdate", "TrainingSessionResponse", "TrainingSessionWithLink",
    
    # Learner session schemas
    "LearnerProfileCreate", "LearnerSessionResponse", "LearnerSessionWithPlan", "LearnerProgressUpdate",
    
    # Slide schemas
    "SlideCreate", "SlideResponse", "SlideContentOnly", "SlideTimeUpdate",
    
    # Chat message schemas
    "ChatMessageCreate", "ChatMessageResponse", "ChatQuestionCreate", "ChatConversation",
    
    # API log schemas
    "ApiLogCreate", "ApiLogResponse", "ApiLogSummary",
    
    # Auth schemas
    "Token", "TokenData", "LoginResponse",
    
    # Common schemas
    "ErrorResponse", "SuccessResponse", "PaginatedResponse", "HealthResponse"
]