"""
FIA v3.0 - Learner Training Plan SQLAlchemy Model
Infrastructure layer model for learner_training_plans table
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.infrastructure.database import Base


class LearnerTrainingPlanModel(Base):
    """SQLAlchemy model for learner_training_plans table"""
    
    __tablename__ = "learner_training_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learner_session_id = Column(UUID(as_uuid=True), ForeignKey("learner_sessions.id"), nullable=False)
    plan_data = Column(JSONB, nullable=False)  # Generated plan structure
    generation_method = Column(String)  # 'gemini', 'vertex', 'manual'
    tokens_used = Column(Integer)
    generation_time_seconds = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    learner_session = relationship("LearnerSessionModel", back_populates="learner_training_plans")
    training_modules = relationship("TrainingModuleModel", back_populates="learner_training_plan")