"""
FIA v3.0 - Slide Entity
SQLAlchemy model for slides table
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.infrastructure.database import Base


class Slide(Base):
    __tablename__ = "slides"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learner_session_id = Column(UUID(as_uuid=True), ForeignKey("learner_sessions.id"), nullable=False)
    slide_number = Column(Integer, nullable=False)
    content = Column(JSONB)  # Contenu HTML/JSON du slide
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    viewed_at = Column(DateTime(timezone=True), nullable=True)
    time_spent = Column(Integer, default=0)  # temps passé sur ce slide en secondes

    # Relationships
    learner_session = relationship("LearnerSession", back_populates="slides")