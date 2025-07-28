from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities.slide import Slide
from app.domain.ports.repositories import SlideRepositoryPort
from app.infrastructure.models.slide_model import SlideModel


class SlideRepository(SlideRepositoryPort):
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, slide: Slide) -> Slide:
        slide_model = self._entity_to_model(slide)
        self.session.add(slide_model)
        await self.session.commit()
        await self.session.refresh(slide_model)
        return self._model_to_entity(slide_model)
    
    async def get_by_id(self, slide_id: UUID) -> Optional[Slide]:
        result = await self.session.execute(
            select(SlideModel).where(SlideModel.id == slide_id)
        )
        slide_model = result.scalar_one_or_none()
        if slide_model:
            return self._model_to_entity(slide_model)
        return None
    
    async def get_by_learner_session_id(self, learner_session_id: UUID) -> List[Slide]:
        result = await self.session.execute(
            select(SlideModel).where(SlideModel.learner_session_id == learner_session_id)
            .order_by(SlideModel.slide_index)
        )
        slide_models = result.scalars().all()
        return [self._model_to_entity(model) for model in slide_models]
    
    async def get_by_learner_session_and_slide_number(
        self, learner_session_id: UUID, slide_number: int
    ) -> Optional[Slide]:
        result = await self.session.execute(
            select(SlideModel).where(
                SlideModel.learner_session_id == learner_session_id,
                SlideModel.slide_index == slide_number
            )
        )
        slide_model = result.scalar_one_or_none()
        if slide_model:
            return self._model_to_entity(slide_model)
        return None
    
    async def update(self, slide: Slide) -> Slide:
        # Find existing slide model
        result = await self.session.execute(
            select(SlideModel).where(SlideModel.id == slide.id)
        )
        slide_model = result.scalar_one_or_none()
        if not slide_model:
            raise ValueError(f"Slide not found: {slide.id}")
        
        # Update fields
        slide_model.title = slide.title
        slide_model.content = slide.content
        slide_model.slide_index = slide.slide_number
        slide_model.time_spent = slide.time_spent
        # Note: completed field doesn't exist in DB, skip it
        
        await self.session.commit()
        await self.session.refresh(slide_model)
        return self._model_to_entity(slide_model)
    
    def _entity_to_model(self, slide: Slide) -> SlideModel:
        """Convert domain entity to SQLAlchemy model"""
        return SlideModel(
            id=slide.id,
            learner_session_id=slide.learner_session_id,
            slide_index=slide.slide_number,  # Map slide_number to slide_index
            title=slide.title,
            content=slide.content,
            time_spent=slide.time_spent,
            created_at=slide.created_at,
            viewed_at=slide.updated_at  # Map updated_at to viewed_at
        )
    
    def _model_to_entity(self, model: SlideModel) -> Slide:
        """Convert SQLAlchemy model to domain entity"""
        return Slide(
            id=model.id,
            learner_session_id=model.learner_session_id,
            slide_number=model.slide_index,  # Map slide_index to slide_number
            title=model.title,
            content=model.content,
            time_spent=model.time_spent,
            completed=False,  # Default value since not in DB
            created_at=model.created_at,
            updated_at=model.viewed_at  # Map viewed_at to updated_at
        )
    
    async def delete(self, slide_id: UUID) -> bool:
        result = await self.session.execute(
            select(SlideModel).where(SlideModel.id == slide_id)
        )
        slide_model = result.scalar_one_or_none()
        if slide_model:
            await self.session.delete(slide_model)
            await self.session.commit()
            return True
        return False