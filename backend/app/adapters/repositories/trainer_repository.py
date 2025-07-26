from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities.trainer import Trainer
from app.domain.ports.repositories import TrainerRepositoryPort
from app.infrastructure.models.trainer_model import TrainerModel


class TrainerRepository(TrainerRepositoryPort):
    """Repository implementation for Trainer entities using SQLAlchemy models"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, trainer: Trainer) -> Trainer:
        """Create a new trainer"""
        trainer_model = self._to_model(trainer)
        self.session.add(trainer_model)
        await self.session.commit()
        await self.session.refresh(trainer_model)
        return self._to_entity(trainer_model)
    
    async def get_by_id(self, trainer_id: UUID) -> Optional[Trainer]:
        """Get trainer by ID"""
        result = await self.session.execute(
            select(TrainerModel).where(TrainerModel.id == trainer_id)
        )
        trainer_model = result.scalar_one_or_none()
        return self._to_entity(trainer_model) if trainer_model else None
    
    async def get_by_email(self, email: str) -> Optional[Trainer]:
        """Get trainer by email"""
        result = await self.session.execute(
            select(TrainerModel).where(TrainerModel.email == email)
        )
        trainer_model = result.scalar_one_or_none()
        return self._to_entity(trainer_model) if trainer_model else None
    
    async def update(self, trainer: Trainer) -> Trainer:
        """Update existing trainer"""
        result = await self.session.execute(
            select(TrainerModel).where(TrainerModel.id == trainer.id)
        )
        trainer_model = result.scalar_one_or_none()
        
        if not trainer_model:
            raise ValueError(f"Trainer with ID {trainer.id} not found")
        
        # Update model fields from entity
        trainer_model.email = trainer.email
        trainer_model.first_name = trainer.first_name
        trainer_model.last_name = trainer.last_name
        trainer_model.is_active = trainer.is_active
        trainer_model.is_verified = trainer.is_verified
        trainer_model.updated_at = trainer.updated_at
        
        await self.session.commit()
        await self.session.refresh(trainer_model)
        return self._to_entity(trainer_model)
    
    async def delete(self, trainer_id: UUID) -> bool:
        """Delete trainer by ID"""
        result = await self.session.execute(
            select(TrainerModel).where(TrainerModel.id == trainer_id)
        )
        trainer_model = result.scalar_one_or_none()
        if trainer_model:
            await self.session.delete(trainer_model)
            await self.session.commit()
            return True
        return False
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Trainer]:
        """List all trainers with pagination"""
        result = await self.session.execute(
            select(TrainerModel)
            .limit(limit)
            .offset(offset)
            .order_by(TrainerModel.created_at.desc())
        )
        trainer_models = result.scalars().all()
        return [self._to_entity(model) for model in trainer_models]
    
    def _to_entity(self, model: TrainerModel) -> Trainer:
        """Convert SQLAlchemy model to domain entity"""
        return Trainer(
            email=model.email,
            first_name=model.first_name,
            last_name=model.last_name,
            trainer_id=model.id,
            is_active=model.is_active,
            is_verified=model.is_verified,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def _to_model(self, entity: Trainer) -> TrainerModel:
        """Convert domain entity to SQLAlchemy model"""
        return TrainerModel(
            id=entity.id,
            email=entity.email,
            first_name=entity.first_name,
            last_name=entity.last_name,
            is_active=entity.is_active,
            is_verified=entity.is_verified,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )