"""
FIA v3.0 - Learner Session Schemas
Pydantic schemas for learner session data validation
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any, Literal


class LearnerProfileCreate(BaseModel):
    """Schema for creating learner profile - Updated for new profile fields"""
    email: EmailStr
    experience_level: Literal["beginner", "intermediate", "advanced"]
    job_and_sector: str = Field(..., min_length=1, max_length=200, description="Combined job position and activity sector")
    language: Optional[str] = Field(default="fr", max_length=10)
    # New required fields for profile refactoring
    objectives: str = Field(..., min_length=5, max_length=1000, description="Learner's expectations and objectives")
    training_duration: Literal["2h", "4h", "6h", "1 jour", "1.5 jour", "2 jours", "3 jours"] = Field(..., description="Desired training duration")


class LearnerSessionResponse(BaseModel):
    """Schema for learner session response - Updated for new profile fields"""
    id: UUID
    training_session_id: UUID
    email: EmailStr
    experience_level: str
    # Keep legacy fields for compatibility (optional)
    learning_style: Optional[str] = None
    job_position: Optional[str] = None
    activity_sector: Optional[str] = None
    country: Optional[str] = None
    language: str
    current_slide_number: int
    total_time_spent: int  # en secondes
    started_at: datetime
    last_activity_at: Optional[datetime]
    # New fields for profile refactoring
    objectives: Optional[str] = None
    training_duration: Optional[str] = None

    class Config:
        from_attributes = True


class LearnerSessionWithEnrichedProfile(LearnerSessionResponse):
    """Schema for learner session with enriched profile"""
    enriched_profile: Optional[Dict[str, Any]]


class LearnerProgressUpdate(BaseModel):
    """Schema for updating learner progress"""
    current_slide_number: Optional[int] = Field(None, ge=1)
    time_spent_increment: Optional[int] = Field(None, ge=0)  # time to add in seconds