"""
FIA v3.0 - Slide SQLAlchemy Model
Infrastructure layer model for slides table
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.infrastructure.database import Base


class SlideModel(Base):
    """SQLAlchemy model for slides table"""
    
    __tablename__ = "slides"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learner_session_id = Column(UUID(as_uuid=True), ForeignKey("learner_sessions.id"), nullable=False)
    slide_number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    content = Column(JSONB)  # Slide content structure
    time_spent = Column(Integer, default=0)  # time spent on this slide in seconds
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    learner_session = relationship("LearnerSessionModel", back_populates="slides")