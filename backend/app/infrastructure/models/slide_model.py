"""
FIA v3.0 - Slide SQLAlchemy Model
Infrastructure layer model for slides table
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.infrastructure.database import Base


class SlideModel(Base):
    """SQLAlchemy model for slides table"""
    
    __tablename__ = "slides"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learner_session_id = Column(UUID(as_uuid=True), ForeignKey("learner_sessions.id"), nullable=False)
    slide_index = Column(Integer, nullable=False)  # Actual column name in DB
    title = Column(String, nullable=False)
    content = Column(Text)  # Actual column type in DB
    ai_context = Column(Text)  # Additional column in DB
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    viewed_at = Column(DateTime(timezone=True))  # Actual column in DB
    time_spent = Column(Integer, default=0)

    # Relationships
    learner_session = relationship("LearnerSessionModel", back_populates="slides")