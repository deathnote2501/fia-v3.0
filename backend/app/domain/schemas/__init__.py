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
from .learner_training_plan import (
    LearnerTrainingPlanCreate, LearnerTrainingPlanResponse, TrainingModuleResponse,
    TrainingSubmoduleResponse, TrainingSlideResponse, CurrentSlideUpdate,
    GeminiTrainingPlanStructure, GeminiStageStructure, GeminiModuleStructure,
    GeminiSubmoduleStructure, GeminiSlideStructure
)
from .document_processing import (
    DocumentProcessingRequest, DocumentProcessingResponse, DocumentSummaryResponse,
    DocumentStructureResponse, DocumentValidationResponse, DocumentProcessingError,
    DocumentFileInfo, ProcessingMetadata
)
from .context_cache import (
    ContextCacheCreateRequest, ContextCacheResponse, ContextCacheInfo, ContextCacheListResponse,
    CacheExpirationUpdateRequest, CacheExpirationUpdateResponse, CacheContentGenerationRequest,
    CacheContentGenerationResponse, CacheDeleteResponse, CacheHealthResponse, CacheError,
    CacheStatistics, TrainingDocumentCacheRequest, TrainingDocumentCacheResponse,
    CacheFindRequest, CacheFindResponse, CacheFileInfo, CacheUsageMetadata
)
from .plan_generation import (
    LearnerProfileSummary, TrainingSummary, PlanGenerationRequest, PlanGenerationMetadata,
    PlanGenerationResponse, SectionRegenerationRequest, SectionRegenerationResponse,
    PlanValidationRequest, PlanValidationResult, PlanOptimizationRequest, PlanOptimizationResponse,
    PersonalizedContentRequest, PersonalizedContentResponse, PlanGenerationStatistics,
    PlanGenerationHealth, PlanTemplateRequest, PlanTemplateResponse, PlanGenerationError
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
    
    # Learner training plan schemas
    "LearnerTrainingPlanCreate", "LearnerTrainingPlanResponse", "TrainingModuleResponse",
    "TrainingSubmoduleResponse", "TrainingSlideResponse", "CurrentSlideUpdate",
    "GeminiTrainingPlanStructure", "GeminiStageStructure", "GeminiModuleStructure",
    "GeminiSubmoduleStructure", "GeminiSlideStructure",
    
    # Document processing schemas
    "DocumentProcessingRequest", "DocumentProcessingResponse", "DocumentSummaryResponse",
    "DocumentStructureResponse", "DocumentValidationResponse", "DocumentProcessingError",
    "DocumentFileInfo", "ProcessingMetadata",
    
    # Context cache schemas
    "ContextCacheCreateRequest", "ContextCacheResponse", "ContextCacheInfo", "ContextCacheListResponse",
    "CacheExpirationUpdateRequest", "CacheExpirationUpdateResponse", "CacheContentGenerationRequest",
    "CacheContentGenerationResponse", "CacheDeleteResponse", "CacheHealthResponse", "CacheError",
    "CacheStatistics", "TrainingDocumentCacheRequest", "TrainingDocumentCacheResponse",
    "CacheFindRequest", "CacheFindResponse", "CacheFileInfo", "CacheUsageMetadata",
    
    # Plan generation schemas
    "LearnerProfileSummary", "TrainingSummary", "PlanGenerationRequest", "PlanGenerationMetadata",
    "PlanGenerationResponse", "SectionRegenerationRequest", "SectionRegenerationResponse",
    "PlanValidationRequest", "PlanValidationResult", "PlanOptimizationRequest", "PlanOptimizationResponse",
    "PersonalizedContentRequest", "PersonalizedContentResponse", "PlanGenerationStatistics",
    "PlanGenerationHealth", "PlanTemplateRequest", "PlanTemplateResponse", "PlanGenerationError",
    
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