"""
FIA v3.0 - Common Schemas
Shared Pydantic schemas for common responses
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, List


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str
    error_code: Optional[str] = None


class SuccessResponse(BaseModel):
    """Schema for success responses"""
    message: str
    data: Optional[Any] = None


class PaginatedResponse(BaseModel):
    """Schema for paginated responses"""
    items: List[Any]
    total: int
    page: int = Field(..., ge=1)
    per_page: int = Field(..., ge=1, le=100)
    total_pages: int


class HealthResponse(BaseModel):
    """Schema for health check response"""
    status: str
    service: str
    version: str
    database: Optional[str] = None
    error: Optional[str] = None