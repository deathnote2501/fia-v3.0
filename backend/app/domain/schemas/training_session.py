"""
FIA v3.0 - Training Session Schemas
Pydantic schemas for training session data validation
"""

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class TrainingSessionBase(BaseModel):
    """Base training session schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)


class TrainingSessionCreate(TrainingSessionBase):
    """Schema for creating a training session"""
    training_id: UUID


class TrainingSessionUpdate(BaseModel):
    """Schema for updating a training session"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None


class TrainingSessionResponse(TrainingSessionBase):
    """Schema for training session response"""
    id: UUID
    training_id: UUID
    session_token: str
    created_at: datetime
    is_active: bool
    training_is_ai_generated: Optional[bool] = None

    class Config:
        from_attributes = True


class TrainingSessionWithLink(TrainingSessionResponse):
    """Schema for training session with generated link"""
    session_link: str