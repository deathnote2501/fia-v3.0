"""
FIA v3.0 - Slide Schemas
Pydantic schemas for slide data validation
"""

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any


class SlideCreate(BaseModel):
    """Schema for creating a slide"""
    learner_session_id: UUID
    slide_number: int = Field(..., ge=1)
    content: Dict[str, Any]


class SlideResponse(BaseModel):
    """Schema for slide response"""
    id: UUID
    learner_session_id: UUID
    slide_number: int
    content: Dict[str, Any]
    generated_at: datetime
    viewed_at: Optional[datetime]
    time_spent: int  # en secondes

    class Config:
        from_attributes = True


class SlideContentOnly(BaseModel):
    """Schema for slide content only"""
    slide_number: int
    content: Dict[str, Any]


class SlideTimeUpdate(BaseModel):
    """Schema for updating slide viewing time"""
    time_spent: int = Field(..., ge=0)  # temps en secondes