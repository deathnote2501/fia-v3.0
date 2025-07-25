from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities import Training
from app.domain.ports.repositories import TrainingRepositoryPort


class TrainingRepository(TrainingRepositoryPort):
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, training: Training) -> Training:
        self.session.add(training)
        await self.session.commit()
        await self.session.refresh(training)
        return training
    
    async def get_by_id(self, training_id: UUID) -> Optional[Training]:
        result = await self.session.execute(
            select(Training).where(Training.id == training_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_trainer_id(self, trainer_id: UUID) -> List[Training]:
        result = await self.session.execute(
            select(Training).where(Training.trainer_id == trainer_id)
        )
        return list(result.scalars().all())
    
    async def update(self, training: Training) -> Training:
        await self.session.commit()
        await self.session.refresh(training)
        return training
    
    async def delete(self, training_id: UUID) -> bool:
        result = await self.session.execute(
            select(Training).where(Training.id == training_id)
        )
        training = result.scalar_one_or_none()
        if training:
            await self.session.delete(training)
            await self.session.commit()
            return True
        return False