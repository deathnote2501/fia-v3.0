"""
FIA v3.0 - Conversation Service Schemas
Pydantic schemas for AI conversation service data validation
"""

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List, Dict, Any, Literal


class ConversationMessage(BaseModel):
    """Schema for a single conversation message"""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: Optional[str] = None  # Accept string timestamp from frontend
    metadata: Optional[Dict[str, Any]] = None


class ConversationContext(BaseModel):
    """Schema for conversation context"""
    training_id: UUID
    learner_session_id: UUID
    current_slide_id: Optional[UUID] = None
    training_content: str
    learner_profile: Dict[str, Any]
    conversation_history: List[ConversationMessage] = Field(default_factory=list)


class ChatRequest(BaseModel):
    """Schema for chat request"""
    message: str = Field(..., min_length=1, max_length=2000)
    context: ConversationContext
    conversation_type: Literal["general", "hint", "explanation", "clarification"] = "general"


class ChatResponse(BaseModel):
    """Schema for AI chat response"""
    response: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    conversation_type: str
    suggested_actions: List[str] = Field(default_factory=list)
    related_concepts: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class HintRequest(BaseModel):
    """Schema for contextual hint request"""
    current_slide: Dict[str, Any]
    learner_question: str = Field(..., min_length=1, max_length=1000)
    learner_profile: Dict[str, Any]
    difficulty_level: Optional[Literal["easy", "medium", "hard"]] = "medium"


class ConceptExplanationRequest(BaseModel):
    """Schema for concept explanation request"""
    concept: str = Field(..., min_length=1, max_length=200)
    training_context: str
    learner_profile: Dict[str, Any]
    explanation_style: Optional[Literal["simple", "detailed", "example-based"]] = "detailed"


class ConversationMetrics(BaseModel):
    """Schema for conversation metrics"""
    total_messages: int
    average_response_time: float
    user_satisfaction_score: Optional[float] = Field(None, ge=0.0, le=5.0)
    most_common_topics: List[str] = Field(default_factory=list)
    conversation_duration_minutes: float
    last_activity: datetime