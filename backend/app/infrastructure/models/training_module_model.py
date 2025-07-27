"""
FIA v3.0 - Training Module SQLAlchemy Model
Infrastructure layer model for training_modules table
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.infrastructure.database import Base


class TrainingModuleModel(Base):
    """SQLAlchemy model for training_modules table"""
    
    __tablename__ = "training_modules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("learner_training_plans.id", ondelete="CASCADE"), nullable=False)
    stage_number = Column(Integer, nullable=False)  # 1-5 (fixed stages)
    order_in_stage = Column(Integer, nullable=False)  # Order within stage
    title = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    learner_training_plan = relationship("LearnerTrainingPlanModel", back_populates="training_modules")
    training_submodules = relationship("TrainingSubmoduleModel", back_populates="training_module")