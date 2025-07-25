"""
FIA v3.0 - Chat Message Entity
SQLAlchemy model for chat_messages table
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.infrastructure.database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learner_session_id = Column(UUID(as_uuid=True), ForeignKey("learner_sessions.id"), nullable=False)
    slide_number = Column(Integer)  # Plus simple qu'une FK vers slides
    message_type = Column(String, nullable=False)  # 'question', 'answer'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    learner_session = relationship("LearnerSession", back_populates="chat_messages")