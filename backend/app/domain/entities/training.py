"""
FIA v3.0 - Training Entity
SQLAlchemy model for trainings table
"""

from sqlalchemy import Column, String, Text, DateTime, LargeBinary, ForeignKey
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
    raw_content = Column(LargeBinary)  # PDF/PPT en format brut
    file_name = Column(String)
    file_type = Column(String)  # 'pdf', 'ppt', 'pptx'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    trainer = relationship("Trainer", back_populates="trainings")
    sessions = relationship("TrainingSession", back_populates="training")