"""
FIA v3.0 - Training Entity
SQLAlchemy model for trainings table
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.infrastructure.database import Base


class Training(Base):
    __tablename__ = "trainings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trainer_id = Column(UUID(as_uuid=True), ForeignKey("trainers.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    file_path = Column(String)  # Chemin vers le fichier stocké
    file_name = Column(String)  # Nom original du fichier
    file_type = Column(String)  # Extension: 'pdf', 'ppt', 'pptx'
    file_size = Column(Integer)  # Taille en bytes
    mime_type = Column(String)  # Type MIME: 'application/pdf', etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    trainer = relationship("Trainer", back_populates="trainings")
    sessions = relationship("TrainingSession", back_populates="training")