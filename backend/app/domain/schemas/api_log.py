"""
FIA v3.0 - API Log Schemas
Pydantic schemas for API log data validation
"""

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any, Literal


class ApiLogCreate(BaseModel):
    """Schema for creating an API log"""
    operation_type: Literal["generate_plan", "generate_slide", "chat"]
    request_data: Dict[str, Any]
    response_data: Dict[str, Any]
    response_time_ms: int = Field(..., ge=0)
    learner_session_id: Optional[UUID] = None


class ApiLogResponse(BaseModel):
    """Schema for API log response"""
    id: UUID
    operation_type: str
    request_data: Dict[str, Any]
    response_data: Dict[str, Any]
    response_time_ms: int
    created_at: datetime
    learner_session_id: Optional[UUID]

    class Config:
        from_attributes = True


class ApiLogSummary(BaseModel):
    """Schema for API log summary (for admin dashboard)"""
    operation_type: str
    total_calls: int
    avg_response_time_ms: float
    last_call_at: datetime