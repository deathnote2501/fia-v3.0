"""
FIA v3.0 - Authentication Schemas
Pydantic schemas for authentication data validation
"""

from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # en secondes


class TokenData(BaseModel):
    """Schema for token data (used internally)"""
    trainer_id: Optional[str] = None
    email: Optional[str] = None


class LoginResponse(BaseModel):
    """Schema for login response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict  # TrainerResponse will be used here