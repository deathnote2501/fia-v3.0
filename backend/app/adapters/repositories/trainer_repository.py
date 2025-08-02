from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.domain.entities.trainer import Trainer
from app.domain.ports.repositories import TrainerRepositoryPort
from app.infrastructure.models.trainer_model import TrainerModel

# Configure logging
logger = logging.getLogger(__name__)


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
        trainer_model.language = trainer.language
        trainer_model.is_active = trainer.is_active
        trainer_model.is_verified = trainer.is_verified
        trainer_model.is_superuser = trainer.is_superuser
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
    
    async def get_all_for_admin_overview(self) -> List[Trainer]:
        """Get all trainers for admin overview (no pagination)"""
        result = await self.session.execute(
            select(TrainerModel)
            .order_by(TrainerModel.created_at.desc())
        )
        trainer_models = result.scalars().all()
        return [self._to_entity(model) for model in trainer_models]
    
    async def get_superusers(self) -> List[Trainer]:
        """Get all superuser trainers"""
        result = await self.session.execute(
            select(TrainerModel)
            .where(TrainerModel.is_superuser == True)
            .order_by(TrainerModel.created_at.desc())
        )
        trainer_models = result.scalars().all()
        return [self._to_entity(model) for model in trainer_models]
    
    async def get_or_create_anonymous_trainer(self) -> Trainer:
        """Get or create anonymous trainer for public quick start workflow"""
        anonymous_email = "anonymous@fia-v3.system"
        
        # Try to get existing anonymous trainer
        existing_trainer = await self.get_by_email(anonymous_email)
        if existing_trainer:
            logger.info(f"🔍 TRAINER_REPO [FOUND] Anonymous trainer exists: {existing_trainer.id}")
            return existing_trainer
        
        # Create new anonymous trainer directly with SQLAlchemy (bypass domain entity for this special case)
        logger.info("🆕 TRAINER_REPO [CREATE] Creating new anonymous trainer with hashed password")
        
        from app.infrastructure.models.trainer_model import TrainerModel
        from fastapi_users.password import PasswordHelper
        import uuid
        
        # Generate a secure password hash for the anonymous user
        password_helper = PasswordHelper()
        hashed_password = password_helper.hash("anonymous_secure_password_2025")
        
        # Create model directly to avoid domain entity validation
        anonymous_model = TrainerModel(
            id=uuid.uuid4(),
            email=anonymous_email,
            first_name="Anonymous",
            last_name="User",
            hashed_password=hashed_password,
            is_active=True,
            is_verified=True,
            is_superuser=False,
            language="fr"
        )
        
        self.session.add(anonymous_model)
        await self.session.commit()
        await self.session.refresh(anonymous_model)
        
        # Convert to domain entity
        created_trainer = self._to_entity(anonymous_model)
        logger.info(f"✅ TRAINER_REPO [CREATED] Anonymous trainer: {created_trainer.id}")
        
        return created_trainer
    
    def _to_entity(self, model: TrainerModel) -> Trainer:
        """Convert SQLAlchemy model to domain entity"""
        return Trainer(
            email=model.email,
            first_name=model.first_name,
            last_name=model.last_name,
            trainer_id=model.id,
            is_active=model.is_active,
            is_verified=model.is_verified,
            is_superuser=model.is_superuser or False,
            language=model.language or 'fr',
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
            language=entity.language,
            is_active=entity.is_active,
            is_verified=entity.is_verified,
            is_superuser=entity.is_superuser,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )