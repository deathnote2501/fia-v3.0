"""
FIA v3.0 - Engagement Analysis Service Schemas
Pydantic schemas for learner engagement analysis data validation
"""

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List, Dict, Any, Literal


class SlideInteraction(BaseModel):
    """Schema for slide interaction data"""
    interaction_type: Literal["click", "scroll", "hover", "focus", "blur", "view"]
    timestamp: datetime
    element_id: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None
    duration: Optional[float] = None  # in seconds


class SlideEngagementData(BaseModel):
    """Schema for slide engagement data"""
    slide_id: UUID
    slide_number: int
    time_spent: float = Field(..., ge=0.0)  # in seconds
    interactions: List[SlideInteraction] = Field(default_factory=list)
    completion_percentage: float = Field(..., ge=0.0, le=100.0)
    revisit_count: int = Field(0, ge=0)
    exit_reason: Optional[Literal["completed", "abandoned", "navigated_away"]] = None


class SessionActivityData(BaseModel):
    """Schema for session activity data"""
    learner_session_id: UUID
    session_start: datetime
    session_end: Optional[datetime] = None
    total_time_spent: float = Field(0.0, ge=0.0)  # in seconds
    slides_viewed: List[SlideEngagementData] = Field(default_factory=list)
    chat_messages_sent: int = Field(0, ge=0)
    questions_asked: int = Field(0, ge=0)
    hints_requested: int = Field(0, ge=0)
    pause_count: int = Field(0, ge=0)
    devices_used: List[str] = Field(default_factory=list)


class EngagementMetrics(BaseModel):
    """Schema for calculated engagement metrics"""
    engagement_score: float = Field(..., ge=0.0, le=100.0)
    attention_score: float = Field(..., ge=0.0, le=100.0)
    interaction_frequency: float = Field(..., ge=0.0)  # interactions per minute
    progress_velocity: float = Field(..., ge=0.0)  # slides per hour
    comprehension_indicators: Dict[str, float] = Field(default_factory=dict)
    risk_factors: List[str] = Field(default_factory=list)


class LearningDifficulty(BaseModel):
    """Schema for detected learning difficulties"""
    difficulty_type: Literal["comprehension", "attention", "pace", "motivation", "technical"]
    severity: Literal["low", "medium", "high", "critical"]
    evidence: List[str]
    affected_concepts: List[str] = Field(default_factory=list)
    suggested_interventions: List[str] = Field(default_factory=list)
    confidence_score: float = Field(..., ge=0.0, le=1.0)


class ProgressInsight(BaseModel):
    """Schema for progress insights"""
    insight_type: Literal["strength", "weakness", "recommendation", "achievement"]
    category: Literal["knowledge", "skills", "engagement", "pace", "style"]
    description: str
    evidence: List[str]
    actionable_recommendation: Optional[str] = None
    priority: Literal["low", "medium", "high"] = "medium"


class EngagementAnalysisRequest(BaseModel):
    """Schema for engagement analysis request"""
    learner_session_id: UUID
    activity_data: SessionActivityData
    analysis_type: Literal["session", "slide", "difficulty", "progress"] = "session"
    include_predictions: bool = False


class EngagementAnalysisResponse(BaseModel):
    """Schema for engagement analysis response"""
    learner_session_id: UUID
    analysis_type: str
    metrics: EngagementMetrics
    difficulties: List[LearningDifficulty] = Field(default_factory=list)
    insights: List[ProgressInsight] = Field(default_factory=list)
    predictions: Optional[Dict[str, Any]] = None
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    analysis_metadata: Dict[str, Any] = Field(default_factory=dict)


class SlideEngagementAnalysisRequest(BaseModel):
    """Schema for slide-specific engagement analysis"""
    slide_id: UUID
    engagement_data: SlideEngagementData
    learner_profile: Dict[str, Any]
    expected_duration: Optional[float] = None  # in seconds


class ComprehensionIndicator(BaseModel):
    """Schema for comprehension indicators"""
    indicator_type: Literal["time_spent", "interaction_pattern", "question_quality", "hint_usage"]
    value: float
    interpretation: Literal["positive", "neutral", "negative"]
    weight: float = Field(..., ge=0.0, le=1.0)
    description: str