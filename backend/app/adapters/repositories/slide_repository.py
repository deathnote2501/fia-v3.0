from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities import Slide
from app.domain.ports.repositories import SlideRepositoryPort


class SlideRepository(SlideRepositoryPort):
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, slide: Slide) -> Slide:
        self.session.add(slide)
        await self.session.commit()
        await self.session.refresh(slide)
        return slide
    
    async def get_by_id(self, slide_id: UUID) -> Optional[Slide]:
        result = await self.session.execute(
            select(Slide).where(Slide.id == slide_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_learner_session_id(self, learner_session_id: UUID) -> List[Slide]:
        result = await self.session.execute(
            select(Slide).where(Slide.learner_session_id == learner_session_id)
            .order_by(Slide.slide_number)
        )
        return list(result.scalars().all())
    
    async def get_by_learner_session_and_slide_number(
        self, learner_session_id: UUID, slide_number: int
    ) -> Optional[Slide]:
        result = await self.session.execute(
            select(Slide).where(
                Slide.learner_session_id == learner_session_id,
                Slide.slide_number == slide_number
            )
        )
        return result.scalar_one_or_none()
    
    async def update(self, slide: Slide) -> Slide:
        await self.session.commit()
        await self.session.refresh(slide)
        return slide
    
    async def delete(self, slide_id: UUID) -> bool:
        result = await self.session.execute(
            select(Slide).where(Slide.id == slide_id)
        )
        slide = result.scalar_one_or_none()
        if slide:
            await self.session.delete(slide)
            await self.session.commit()
            return True
        return False