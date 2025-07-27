"""
FIA v3.0 - User Schemas (Pure Domain)
Pydantic schemas for user data validation without FastAPI-Users dependency
"""

import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class UserRead(BaseModel):
    """Schema for reading user data"""
    id: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    """Schema for creating a new user"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating user data"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)