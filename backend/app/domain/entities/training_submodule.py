"""
FIA v3.0 - Training Submodule Entity
SQLAlchemy model for training_submodules table
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.infrastructure.database import Base


class TrainingSubmodule(Base):
    __tablename__ = "training_submodules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_id = Column(UUID(as_uuid=True), ForeignKey("training_modules.id", ondelete="CASCADE"), nullable=False)
    order_in_module = Column(Integer, nullable=False)  # Order within module
    title = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    module = relationship("TrainingModule", back_populates="submodules")
    slides = relationship("TrainingSlide", back_populates="submodule", cascade="all, delete-orphan", order_by="TrainingSlide.order_in_submodule")