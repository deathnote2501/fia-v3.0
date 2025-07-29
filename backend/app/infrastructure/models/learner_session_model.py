"""
FIA v3.0 - Learner Session SQLAlchemy Model
Infrastructure layer model for learner_sessions table
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.infrastructure.database import Base


class LearnerSessionModel(Base):
    """SQLAlchemy model for learner_sessions table"""
    
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
    enriched_profile = Column(JSONB)  # Enriched learner profile data
    current_slide_number = Column(Integer, default=1)
    total_time_spent = Column(Integer, default=0)  # in seconds
    # New fields for profile refactoring
    objectives = Column(Text)  # Learner's expectations/objectives
    training_duration = Column(String(20))  # Duration: 2h, 4h, 6h, 1 jour, 1.5 jour, 2 jours, 3 jours
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())

    # Unique constraint: one learner per session
    __table_args__ = (UniqueConstraint('training_session_id', 'email', name='_training_session_email_uc'),)

    # Relationships
    training_session = relationship("TrainingSessionModel", back_populates="learner_sessions")
    slides = relationship("SlideModel", back_populates="learner_session")
    chat_messages = relationship("ChatMessageModel", back_populates="learner_session")
    learner_training_plans = relationship("LearnerTrainingPlanModel", back_populates="learner_session")