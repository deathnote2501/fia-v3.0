from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities import LearnerSession
from app.domain.ports.repositories import LearnerSessionRepositoryPort


class LearnerSessionRepository(LearnerSessionRepositoryPort):
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, learner_session: LearnerSession) -> LearnerSession:
        self.session.add(learner_session)
        await self.session.commit()
        await self.session.refresh(learner_session)
        return learner_session
    
    async def get_by_id(self, learner_session_id: UUID) -> Optional[LearnerSession]:
        result = await self.session.execute(
            select(LearnerSession).where(LearnerSession.id == learner_session_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_training_session_and_email(
        self, training_session_id: UUID, email: str
    ) -> Optional[LearnerSession]:
        result = await self.session.execute(
            select(LearnerSession).where(
                LearnerSession.training_session_id == training_session_id,
                LearnerSession.email == email
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_training_session_id(self, training_session_id: UUID) -> List[LearnerSession]:
        result = await self.session.execute(
            select(LearnerSession).where(
                LearnerSession.training_session_id == training_session_id
            )
        )
        return list(result.scalars().all())
    
    async def update(self, learner_session: LearnerSession) -> LearnerSession:
        await self.session.commit()
        await self.session.refresh(learner_session)
        return learner_session
    
    async def delete(self, learner_session_id: UUID) -> bool:
        result = await self.session.execute(
            select(LearnerSession).where(LearnerSession.id == learner_session_id)
        )
        learner_session = result.scalar_one_or_none()
        if learner_session:
            await self.session.delete(learner_session)
            await self.session.commit()
            return True
        return False