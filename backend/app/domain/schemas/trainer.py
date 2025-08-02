"""
FIA v3.0 - Trainer Schemas
Pydantic schemas for trainer data validation
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, Literal


class TrainerBase(BaseModel):
    """Base trainer schema"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    language: Literal["fr", "en", "es", "de"] = Field(default="fr", description="Trainer's preferred interface language")


class TrainerCreate(TrainerBase):
    """Schema for creating a trainer"""
    password: str = Field(..., min_length=8, max_length=100)


class TrainerUpdate(BaseModel):
    """Schema for updating trainer profile"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    language: Optional[Literal["fr", "en", "es", "de"]] = Field(None, description="Trainer's preferred interface language")


class TrainerResponse(TrainerBase):
    """Schema for trainer response (without password)"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class TrainerLanguageUpdate(BaseModel):
    """Schema for updating trainer's language preference only"""
    language: Literal["fr", "en", "es", "de"] = Field(..., description="Trainer's preferred interface language")


class TrainerLogin(BaseModel):
    """Schema for trainer login"""
    email: EmailStr
    password: str = Field(..., min_length=1)