"""
FIA v3.0 - Training Session Entity
SQLAlchemy model for training_sessions table
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.infrastructure.database import Base


class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    training_id = Column(UUID(as_uuid=True), ForeignKey("trainings.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    session_token = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    training = relationship("Training", back_populates="sessions")
    learner_sessions = relationship("LearnerSession", back_populates="training_session")