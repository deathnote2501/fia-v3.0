"""
FIA v3.0 - API Log SQLAlchemy Model
Infrastructure layer model for api_logs table
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.infrastructure.database import Base


class ApiLogModel(Base):
    """SQLAlchemy model for api_logs table"""
    
    __tablename__ = "api_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_name = Column(String, nullable=False)  # 'gemini', 'vertex', etc.
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    request_data = Column(JSONB)
    response_data = Column(JSONB)
    status_code = Column(Integer)
    response_time_ms = Column(Integer)
    tokens_used = Column(Integer)
    cost_estimate = Column(String)  # monetary cost if available
    learner_session_id = Column(UUID(as_uuid=True), ForeignKey("learner_sessions.id"), nullable=True)  # optional for traceability
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    learner_session = relationship("LearnerSessionModel", foreign_keys=[learner_session_id])