"""
FIA v3.0 - Learner Session Repository
Repository implementation for learner sessions with model-entity mapping
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities.learner_session import LearnerSession
from app.domain.ports.repositories import LearnerSessionRepositoryPort
from app.infrastructure.models.learner_session_model import LearnerSessionModel


class LearnerSessionRepository(LearnerSessionRepositoryPort):
    """Repository for learner sessions with hexagonal architecture compliance"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def _model_to_entity(self, model: LearnerSessionModel) -> LearnerSession:
        """Convert SQLAlchemy model to domain entity"""
        return LearnerSession(
            training_session_id=model.training_session_id,
            email=model.email,
            experience_level=model.experience_level,
            learning_style=model.learning_style,
            job_position=model.job_position,
            activity_sector=model.activity_sector,
            country=model.country,
            language=model.language,
            learner_session_id=model.id,
            enriched_profile=model.enriched_profile,
            current_slide_number=model.current_slide_number,
            total_time_spent=model.total_time_spent,
            started_at=model.started_at,
            last_activity_at=model.last_activity_at,
            # New fields for profile refactoring
            objectives=model.objectives,
            training_duration=model.training_duration
        )
    
    def _entity_to_model(self, entity: LearnerSession) -> LearnerSessionModel:
        """Convert domain entity to SQLAlchemy model"""
        return LearnerSessionModel(
            id=entity.id,
            training_session_id=entity.training_session_id,
            email=entity.email,
            experience_level=entity.experience_level,
            learning_style=entity.learning_style,
            job_position=entity.job_position,
            activity_sector=entity.activity_sector,
            country=entity.country,
            language=entity.language,
            enriched_profile=entity.enriched_profile,
            current_slide_number=entity.current_slide_number,
            total_time_spent=entity.total_time_spent,
            started_at=entity.started_at,
            last_activity_at=entity.last_activity_at,
            # New fields for profile refactoring
            objectives=entity.objectives,
            training_duration=entity.training_duration
        )
    
    async def create(self, learner_session: LearnerSession) -> LearnerSession:
        """Create a new learner session"""
        model = self._entity_to_model(learner_session)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def get_by_id(self, learner_session_id: UUID) -> Optional[LearnerSession]:
        """Get learner session by ID"""
        result = await self.session.execute(
            select(LearnerSessionModel).where(LearnerSessionModel.id == learner_session_id)
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None
    
    async def get_by_training_session_and_email(
        self, training_session_id: UUID, email: str
    ) -> Optional[LearnerSession]:
        """Get learner session by training session and email"""
        result = await self.session.execute(
            select(LearnerSessionModel).where(
                LearnerSessionModel.training_session_id == training_session_id,
                LearnerSessionModel.email == email
            )
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None
    
    async def update(self, learner_session: LearnerSession) -> LearnerSession:
        """Update an existing learner session"""
        result = await self.session.execute(
            select(LearnerSessionModel).where(LearnerSessionModel.id == learner_session.id)
        )
        model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError(f"LearnerSession with id {learner_session.id} not found")
        
        # Update model fields
        model.email = learner_session.email
        model.experience_level = learner_session.experience_level
        model.learning_style = learner_session.learning_style
        model.job_position = learner_session.job_position
        model.activity_sector = learner_session.activity_sector
        model.country = learner_session.country
        model.language = learner_session.language
        model.enriched_profile = learner_session.enriched_profile
        model.current_slide_number = learner_session.current_slide_number
        model.total_time_spent = learner_session.total_time_spent
        model.last_activity_at = learner_session.last_activity_at
        # New fields for profile refactoring
        model.objectives = learner_session.objectives
        model.training_duration = learner_session.training_duration
        
        await self.session.commit()
        await self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def delete(self, learner_session_id: UUID) -> bool:
        """Delete a learner session"""
        result = await self.session.execute(
            select(LearnerSessionModel).where(LearnerSessionModel.id == learner_session_id)
        )
        model = result.scalar_one_or_none()
        
        if not model:
            return False
        
        await self.session.delete(model)
        await self.session.commit()
        return True
    
    async def get_by_training_session_id(self, training_session_id: UUID) -> List[LearnerSession]:
        """Get all learner sessions for a training session"""
        result = await self.session.execute(
            select(LearnerSessionModel).where(
                LearnerSessionModel.training_session_id == training_session_id
            )
        )
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
    
    async def update_current_slide_number(self, learner_session_id: UUID, slide_number: int) -> bool:
        """
        Mettre à jour le numéro de slide courante de l'apprenant
        
        Args:
            learner_session_id: ID de la session apprenant
            slide_number: Nouveau numéro de slide (1-based)
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        try:
            from sqlalchemy import update
            from datetime import datetime, timezone
            
            # Mettre à jour le current_slide_number et last_activity_at
            result = await self.session.execute(
                update(LearnerSessionModel)
                .where(LearnerSessionModel.id == learner_session_id)
                .values(
                    current_slide_number=slide_number,
                    last_activity_at=datetime.now(timezone.utc)
                )
            )
            
            await self.session.commit()
            
            # Vérifier qu'une ligne a été mise à jour
            return result.rowcount > 0
            
        except Exception as e:
            await self.session.rollback()
            # Log l'erreur sans importer logging pour éviter les dépendances circulaires
            print(f"❌ Error updating current slide number: {e}")
            return False