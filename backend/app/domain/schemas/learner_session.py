"""
FIA v3.0 - Learner Session Schemas
Pydantic schemas for learner session data validation
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any, Literal


class LearnerProfileCreate(BaseModel):
    """Schema for creating learner profile"""
    email: EmailStr
    experience_level: Literal["beginner", "intermediate", "advanced"]
    learning_style: Literal["visual", "auditory", "kinesthetic", "reading"]
    job_position: str = Field(..., min_length=1, max_length=100)
    activity_sector: str = Field(..., min_length=1, max_length=100)
    country: str = Field(..., min_length=1, max_length=100)
    language: Optional[str] = Field(default="fr", max_length=10)


class LearnerSessionResponse(BaseModel):
    """Schema for learner session response"""
    id: UUID
    training_session_id: UUID
    email: EmailStr
    experience_level: str
    learning_style: str
    job_position: str
    activity_sector: str
    country: str
    language: str
    current_slide_number: int
    total_time_spent: int  # en secondes
    started_at: datetime
    last_activity_at: datetime

    class Config:
        from_attributes = True


class LearnerSessionWithPlan(LearnerSessionResponse):
    """Schema for learner session with personalized plan"""
    personalized_plan: Optional[Dict[str, Any]]


class LearnerProgressUpdate(BaseModel):
    """Schema for updating learner progress"""
    current_slide_number: Optional[int] = Field(None, ge=1)
    time_spent_increment: Optional[int] = Field(None, ge=0)  # temps à ajouter en secondes