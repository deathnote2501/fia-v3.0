"""
FIA v3.0 - Training SQLAlchemy Model
Infrastructure layer model for trainings table
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.infrastructure.database import Base


class TrainingModel(Base):
    """SQLAlchemy model for trainings table"""
    
    __tablename__ = "trainings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trainer_id = Column(UUID(as_uuid=True), ForeignKey("trainers.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    file_path = Column(String)  # Path to stored file
    file_name = Column(String)  # Original file name
    file_type = Column(String)  # Extension: 'pdf', 'ppt', 'pptx'
    file_size = Column(Integer)  # Size in bytes
    mime_type = Column(String)  # MIME type: 'application/pdf', etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    trainer = relationship("TrainerModel", back_populates="trainings")
    sessions = relationship("TrainingSessionModel", back_populates="training")