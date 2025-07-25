from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities import Trainer
from app.domain.ports.repositories import TrainerRepositoryPort


class TrainerRepository(TrainerRepositoryPort):
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, trainer: Trainer) -> Trainer:
        self.session.add(trainer)
        await self.session.commit()
        await self.session.refresh(trainer)
        return trainer
    
    async def get_by_id(self, trainer_id: UUID) -> Optional[Trainer]:
        result = await self.session.execute(
            select(Trainer).where(Trainer.id == trainer_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[Trainer]:
        result = await self.session.execute(
            select(Trainer).where(Trainer.email == email)
        )
        return result.scalar_one_or_none()
    
    async def update(self, trainer: Trainer) -> Trainer:
        await self.session.commit()
        await self.session.refresh(trainer)
        return trainer
    
    async def delete(self, trainer_id: UUID) -> bool:
        result = await self.session.execute(
            select(Trainer).where(Trainer.id == trainer_id)
        )
        trainer = result.scalar_one_or_none()
        if trainer:
            await self.session.delete(trainer)
            await self.session.commit()
            return True
        return False