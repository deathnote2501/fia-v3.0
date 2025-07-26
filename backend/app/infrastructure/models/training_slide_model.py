"""
FIA v3.0 - Training Slide SQLAlchemy Model
Infrastructure layer model for training_slides table
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.infrastructure.database import Base


class TrainingSlideModel(Base):
    """SQLAlchemy model for training_slides table"""
    
    __tablename__ = "training_slides"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    training_submodule_id = Column(UUID(as_uuid=True), ForeignKey("training_submodules.id"), nullable=False)
    slide_number = Column(Integer, nullable=False)
    slide_title = Column(String, nullable=False)
    content_type = Column(String)  # 'visual', 'auditory', 'kinesthetic', 'reading'
    slide_content = Column(JSONB)  # Detailed slide content
    learning_points = Column(JSONB)  # Key learning points
    estimated_duration_minutes = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    training_submodule = relationship("TrainingSubmoduleModel", back_populates="training_slides")