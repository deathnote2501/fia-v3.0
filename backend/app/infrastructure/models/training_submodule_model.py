"""
FIA v3.0 - Training Submodule SQLAlchemy Model
Infrastructure layer model for training_submodules table
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.infrastructure.database import Base


class TrainingSubmoduleModel(Base):
    """SQLAlchemy model for training_submodules table"""
    
    __tablename__ = "training_submodules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_id = Column(UUID(as_uuid=True), ForeignKey("training_modules.id", ondelete="CASCADE"), nullable=False)
    order_in_module = Column(Integer, nullable=False)  # Order within module
    title = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    training_module = relationship("TrainingModuleModel", back_populates="training_submodules")
    training_slides = relationship("TrainingSlideModel", back_populates="training_submodule")