"""
FIA v3.0 - Training Module Entity
SQLAlchemy model for training_modules table
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.infrastructure.database import Base


class TrainingModule(Base):
    __tablename__ = "training_modules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("learner_training_plans.id", ondelete="CASCADE"), nullable=False)
    stage_number = Column(Integer, nullable=False)  # 1-5 (fixed stages)
    order_in_stage = Column(Integer, nullable=False)  # Order within stage
    title = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint('stage_number >= 1 AND stage_number <= 5', name='_valid_stage_number'),
    )

    # Relationships
    plan = relationship("LearnerTrainingPlan", back_populates="modules")
    submodules = relationship("TrainingSubmodule", back_populates="module", cascade="all, delete-orphan", order_by="TrainingSubmodule.order_in_module")