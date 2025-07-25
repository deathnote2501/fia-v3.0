"""
FIA v3.0 - Learner Session Entity
SQLAlchemy model for learner_sessions table
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.infrastructure.database import Base


class LearnerSession(Base):
    __tablename__ = "learner_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    training_session_id = Column(UUID(as_uuid=True), ForeignKey("training_sessions.id"), nullable=False)
    email = Column(String, nullable=False)
    experience_level = Column(String)  # 'beginner', 'intermediate', 'advanced'
    learning_style = Column(String)    # 'visual', 'auditory', 'kinesthetic', 'reading'
    job_position = Column(String)
    activity_sector = Column(String)
    country = Column(String)
    language = Column(String, default='fr')
    personalized_plan = Column(JSONB)  # Plan généré par Gemini
    current_slide_number = Column(Integer, default=1)
    total_time_spent = Column(Integer, default=0)  # en secondes
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())

    # Contrainte unique : un apprenant par session
    __table_args__ = (UniqueConstraint('training_session_id', 'email', name='_training_session_email_uc'),)

    # Relationships
    training_session = relationship("TrainingSession", back_populates="learner_sessions")
    slides = relationship("Slide", back_populates="learner_session")
    chat_messages = relationship("ChatMessage", back_populates="learner_session")