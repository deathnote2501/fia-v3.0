from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities import TrainingSession
from app.domain.ports.repositories import TrainingSessionRepositoryPort


class TrainingSessionRepository(TrainingSessionRepositoryPort):
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, training_session: TrainingSession) -> TrainingSession:
        self.session.add(training_session)
        await self.session.commit()
        await self.session.refresh(training_session)
        return training_session
    
    async def get_by_id(self, session_id: UUID) -> Optional[TrainingSession]:
        result = await self.session.execute(
            select(TrainingSession).where(TrainingSession.id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_token(self, session_token: str) -> Optional[TrainingSession]:
        result = await self.session.execute(
            select(TrainingSession).where(TrainingSession.session_token == session_token)
        )
        return result.scalar_one_or_none()
    
    async def get_by_training_id(self, training_id: UUID) -> List[TrainingSession]:
        result = await self.session.execute(
            select(TrainingSession).where(TrainingSession.training_id == training_id)
        )
        return list(result.scalars().all())
    
    async def update(self, training_session: TrainingSession) -> TrainingSession:
        await self.session.commit()
        await self.session.refresh(training_session)
        return training_session
    
    async def delete(self, session_id: UUID) -> bool:
        result = await self.session.execute(
            select(TrainingSession).where(TrainingSession.id == session_id)
        )
        training_session = result.scalar_one_or_none()
        if training_session:
            await self.session.delete(training_session)
            await self.session.commit()
            return True
        return False