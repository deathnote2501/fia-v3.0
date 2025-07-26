"""
FIA v3.0 - Learner Training Plan Entity
SQLAlchemy model for learner_training_plans table
"""

from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.infrastructure.database import Base


class LearnerTrainingPlan(Base):
    __tablename__ = "learner_training_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learner_session_id = Column(UUID(as_uuid=True), ForeignKey("learner_sessions.id"), nullable=False, unique=True)
    current_slide_id = Column(UUID(as_uuid=True), ForeignKey("training_slides.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    learner_session = relationship("LearnerSession", back_populates="training_plan")
    current_slide = relationship("TrainingSlide", foreign_keys=[current_slide_id])
    modules = relationship("TrainingModule", back_populates="plan", cascade="all, delete-orphan", order_by="TrainingModule.stage_number, TrainingModule.order_in_stage")