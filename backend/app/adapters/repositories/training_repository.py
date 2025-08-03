from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities.training import Training, FileType
from app.domain.ports.repositories import TrainingRepositoryPort
from app.infrastructure.models.training_model import TrainingModel


class TrainingRepository(TrainingRepositoryPort):
    """Repository implementation for Training entities using SQLAlchemy models"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, training: Training) -> Training:
        """Create a new training"""
        training_model = self._to_model(training)
        self.session.add(training_model)
        await self.session.commit()
        await self.session.refresh(training_model)
        return self._to_entity(training_model)
    
    async def get_by_id(self, training_id: UUID) -> Optional[Training]:
        """Get training by ID"""
        result = await self.session.execute(
            select(TrainingModel).where(TrainingModel.id == training_id)
        )
        training_model = result.scalar_one_or_none()
        return self._to_entity(training_model) if training_model else None
    
    async def get_by_trainer_id(self, trainer_id: UUID) -> List[Training]:
        """Get all trainings for a specific trainer"""
        result = await self.session.execute(
            select(TrainingModel)
            .where(TrainingModel.trainer_id == trainer_id)
            .order_by(TrainingModel.created_at.desc())
        )
        training_models = result.scalars().all()
        return [self._to_entity(model) for model in training_models]
    
    async def update(self, training: Training) -> Training:
        """Update existing training"""
        result = await self.session.execute(
            select(TrainingModel).where(TrainingModel.id == training.id)
        )
        training_model = result.scalar_one_or_none()
        
        if not training_model:
            raise ValueError(f"Training with ID {training.id} not found")
        
        # Update model fields from entity
        training_model.name = training.name
        training_model.description = training.description
        training_model.file_path = training.file_path
        training_model.file_name = training.file_name
        training_model.file_type = training.file_type.value if training.file_type else None
        training_model.file_size = training.file_size
        training_model.mime_type = training.mime_type
        training_model.is_ai_generated = training.is_ai_generated
        
        await self.session.commit()
        await self.session.refresh(training_model)
        return self._to_entity(training_model)
    
    async def delete(self, training_id: UUID) -> bool:
        """Delete training by ID"""
        result = await self.session.execute(
            select(TrainingModel).where(TrainingModel.id == training_id)
        )
        training_model = result.scalar_one_or_none()
        if training_model:
            self.session.delete(training_model)
            # Note: commit will be handled by the controller
            return True
        return False
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Training]:
        """List all trainings with pagination"""
        result = await self.session.execute(
            select(TrainingModel)
            .limit(limit)
            .offset(offset)
            .order_by(TrainingModel.created_at.desc())
        )
        training_models = result.scalars().all()
        return [self._to_entity(model) for model in training_models]
    
    def _to_entity(self, model: TrainingModel) -> Training:
        """Convert SQLAlchemy model to domain entity"""
        file_type = None
        if model.file_type:
            try:
                file_type = FileType(model.file_type)
            except ValueError:
                file_type = None
        
        return Training(
            trainer_id=model.trainer_id,
            name=model.name,
            description=model.description,
            file_path=model.file_path,
            file_name=model.file_name,
            file_type=file_type,
            file_size=model.file_size,
            mime_type=model.mime_type,
            is_ai_generated=model.is_ai_generated or False,
            training_id=model.id,
            created_at=model.created_at
        )
    
    def _to_model(self, entity: Training) -> TrainingModel:
        """Convert domain entity to SQLAlchemy model"""
        return TrainingModel(
            id=entity.id,
            trainer_id=entity.trainer_id,
            name=entity.name,
            description=entity.description,
            file_path=entity.file_path,
            file_name=entity.file_name,
            file_type=entity.file_type.value if entity.file_type else None,
            file_size=entity.file_size,
            mime_type=entity.mime_type,
            is_ai_generated=entity.is_ai_generated,
            created_at=entity.created_at
        )