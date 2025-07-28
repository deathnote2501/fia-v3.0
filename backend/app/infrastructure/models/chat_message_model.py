"""
FIA v3.0 - Chat Message SQLAlchemy Model
Infrastructure layer model for chat_messages table
"""

from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.infrastructure.database import Base


class ChatMessageModel(Base):
    """SQLAlchemy model for chat_messages table"""
    
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learner_session_id = Column(UUID(as_uuid=True), ForeignKey("learner_sessions.id"), nullable=False)
    message = Column(Text)  # Actual column name in DB
    response = Column(Text)  # Additional column in DB
    message_type = Column(String)  # 'question', 'answer'
    ai_context = Column(Text)  # Additional column in DB
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    learner_session = relationship("LearnerSessionModel", back_populates="chat_messages")