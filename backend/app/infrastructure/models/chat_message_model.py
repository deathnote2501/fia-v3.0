"""
FIA v3.0 - Chat Message SQLAlchemy Model
Infrastructure layer model for chat_messages table
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
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
    slide_number = Column(Integer)
    message_type = Column(String)  # 'question', 'answer'
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    learner_session = relationship("LearnerSessionModel", back_populates="chat_messages")