"""
FIA v3.0 - Chat Message Schemas
Pydantic schemas for chat message data validation
"""

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, Literal


class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message"""
    learner_session_id: UUID
    slide_number: Optional[int] = Field(None, ge=1)
    message_type: Literal["question", "answer"]
    content: str = Field(..., min_length=1, max_length=2000)


class ChatMessageResponse(BaseModel):
    """Schema for chat message response"""
    id: UUID
    learner_session_id: UUID
    slide_number: Optional[int]
    message_type: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatQuestionCreate(BaseModel):
    """Schema for learner question"""
    content: str = Field(..., min_length=1, max_length=2000)
    slide_number: Optional[int] = Field(None, ge=1)


class ChatConversation(BaseModel):
    """Schema for chat conversation"""
    messages: list[ChatMessageResponse]
    total_messages: int