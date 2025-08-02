"""
FIA v3.0 - Trainer SQLAlchemy Model
Infrastructure layer model for trainers table with FastAPI-Users integration
"""

from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID

from app.infrastructure.database import Base


class TrainerModel(SQLAlchemyBaseUserTableUUID, Base):
    """SQLAlchemy model for trainers table"""
    
    __tablename__ = "trainers"

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    language = Column(String(10), nullable=False, server_default='fr')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    trainings = relationship("TrainingModel", back_populates="trainer")