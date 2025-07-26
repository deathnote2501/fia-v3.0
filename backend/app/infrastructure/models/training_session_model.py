"""
FIA v3.0 - Training Session SQLAlchemy Model
Infrastructure layer model for training_sessions table
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.infrastructure.database import Base


class TrainingSessionModel(Base):
    """SQLAlchemy model for training_sessions table"""
    
    __tablename__ = "training_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    training_id = Column(UUID(as_uuid=True), ForeignKey("trainings.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    session_token = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))

    # Relationships
    training = relationship("TrainingModel", back_populates="training_sessions")
    learner_sessions = relationship("LearnerSessionModel", back_populates="training_session")