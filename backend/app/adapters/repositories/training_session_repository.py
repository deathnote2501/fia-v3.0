"""
FIA v3.0 - Training Session Repository
Repository implementation for training sessions with model-entity mapping
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities.training_session import TrainingSession
from app.domain.ports.repositories import TrainingSessionRepositoryPort
from app.infrastructure.models.training_session_model import TrainingSessionModel


class TrainingSessionRepository(TrainingSessionRepositoryPort):
    """Repository for training sessions with hexagonal architecture compliance"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def _model_to_entity(self, model: TrainingSessionModel) -> TrainingSession:
        """Convert SQLAlchemy model to domain entity"""
        return TrainingSession(
            training_id=model.training_id,
            name=model.name,
            session_token=model.session_token,
            description=model.description,
            training_session_id=model.id,
            is_active=model.is_active,
            created_at=model.created_at,
            expires_at=model.expires_at
        )
    
    def _entity_to_model(self, entity: TrainingSession) -> TrainingSessionModel:
        """Convert domain entity to SQLAlchemy model"""
        return TrainingSessionModel(
            id=entity.id,
            training_id=entity.training_id,
            name=entity.name,
            description=entity.description,
            session_token=entity.session_token,
            is_active=entity.is_active,
            created_at=entity.created_at,
            expires_at=entity.expires_at
        )
    
    async def create(self, training_session: TrainingSession) -> TrainingSession:
        """Create a new training session"""
        model = self._entity_to_model(training_session)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def get_by_id(self, training_session_id: UUID) -> Optional[TrainingSession]:
        """Get training session by ID"""
        result = await self.session.execute(
            select(TrainingSessionModel).where(TrainingSessionModel.id == training_session_id)
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None
    
    async def get_by_token(self, token: str) -> Optional[TrainingSession]:
        """Get training session by token"""
        result = await self.session.execute(
            select(TrainingSessionModel).where(TrainingSessionModel.session_token == token)
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None
    
    async def get_by_training_id(self, training_id: UUID) -> List[TrainingSession]:
        """Get all training sessions for a training"""
        result = await self.session.execute(
            select(TrainingSessionModel).where(TrainingSessionModel.training_id == training_id)
        )
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
    
    async def update(self, training_session: TrainingSession) -> TrainingSession:
        """Update an existing training session"""
        result = await self.session.execute(
            select(TrainingSessionModel).where(TrainingSessionModel.id == training_session.id)
        )
        model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError(f"TrainingSession with id {training_session.id} not found")
        
        # Update model fields
        model.name = training_session.name
        model.description = training_session.description
        model.session_token = training_session.session_token
        model.is_active = training_session.is_active
        model.updated_at = training_session.updated_at
        
        await self.session.commit()
        await self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def delete(self, training_session_id: UUID) -> bool:
        """Delete a training session"""
        result = await self.session.execute(
            select(TrainingSessionModel).where(TrainingSessionModel.id == training_session_id)
        )
        model = result.scalar_one_or_none()
        
        if not model:
            return False
        
        await self.session.delete(model)
        await self.session.commit()
        return True