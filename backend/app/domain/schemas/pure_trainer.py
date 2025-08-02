"""
FIA v3.0 - Pure Domain Trainer Schemas
Pure domain schemas without infrastructure dependencies
"""

import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TrainerBase(BaseModel):
    """Base trainer schema with common fields"""
    email: str = Field(..., description="Trainer email address")
    first_name: str = Field(..., min_length=1, max_length=100, description="Trainer first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Trainer last name")


class TrainerCreate(TrainerBase):
    """Schema for creating a new trainer"""
    password: str = Field(..., min_length=8, max_length=100, description="Trainer password")


class TrainerUpdate(BaseModel):
    """Schema for updating trainer data"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = None


class TrainerRead(TrainerBase):
    """Schema for reading trainer data"""
    id: uuid.UUID
    is_active: bool
    is_superuser: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TrainerInDB(TrainerRead):
    """Schema for trainer as stored in database"""
    password_hash: str = Field(..., description="Hashed password")