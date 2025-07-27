"""
FIA v3.0 - User Schemas for FastAPI-Users
Pydantic schemas for user authentication and management
"""

import uuid
from typing import Optional
from datetime import datetime
from pydantic import Field
from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    """Schema for reading user data"""
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: datetime


class UserCreate(schemas.BaseUserCreate):
    """Schema for creating a new user"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(schemas.BaseUserUpdate):
    """Schema for updating user data"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)