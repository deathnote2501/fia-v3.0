"""
FIA v3.0 - API Log Entity
SQLAlchemy model for api_logs table
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from app.infrastructure.database import Base


class ApiLog(Base):
    __tablename__ = "api_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    operation_type = Column(String, nullable=False)  # 'generate_plan', 'generate_slide', 'chat'
    request_data = Column(JSONB)
    response_data = Column(JSONB)
    response_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    learner_session_id = Column(UUID(as_uuid=True), ForeignKey("learner_sessions.id"), nullable=True)  # optionnel pour traçabilité