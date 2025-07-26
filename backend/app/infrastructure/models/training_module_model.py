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
    learner_training_plan_id = Column(UUID(as_uuid=True), ForeignKey("learner_training_plans.id"), nullable=False)
    module_number = Column(Integer, nullable=False)
    phase_name = Column(String, nullable=False)  # 'Discovery', 'Learning', etc.
    module_name = Column(String, nullable=False)
    description = Column(String)
    learning_objectives = Column(JSONB)  # Array of objectives
    duration_hours = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    learner_training_plan = relationship("LearnerTrainingPlanModel", back_populates="training_modules")
    training_submodules = relationship("TrainingSubmoduleModel", back_populates="training_module")