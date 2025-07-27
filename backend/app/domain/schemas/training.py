"""
FIA v3.0 - Training Schemas
Pydantic schemas for training data validation
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID
from typing import Optional
from fastapi import UploadFile


class TrainingBase(BaseModel):
    """Base training schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)


class TrainingCreate(TrainingBase):
    """Schema for creating a training"""
    pass


class TrainingUpdate(BaseModel):
    """Schema for updating a training"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)


class TrainingUpload(BaseModel):
    """Schema for training upload with file validation"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Training name cannot be empty')
        return v.strip()


class TrainingResponse(TrainingBase):
    """Schema for training response"""
    id: UUID
    trainer_id: UUID
    file_name: Optional[str]
    file_type: Optional[str]
    file_size: Optional[int]
    mime_type: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TrainingListResponse(BaseModel):
    """Schema for training list with basic info"""
    id: UUID
    name: str
    description: Optional[str]
    file_path: Optional[str]
    file_name: Optional[str]
    file_type: Optional[str]
    file_size: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True