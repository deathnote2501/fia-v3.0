from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities import ApiLog
from app.domain.ports.repositories import ApiLogRepositoryPort


class ApiLogRepository(ApiLogRepositoryPort):
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, api_log: ApiLog) -> ApiLog:
        self.session.add(api_log)
        await self.session.commit()
        await self.session.refresh(api_log)
        return api_log
    
    async def get_by_id(self, log_id: UUID) -> Optional[ApiLog]:
        result = await self.session.execute(
            select(ApiLog).where(ApiLog.id == log_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_learner_session_id(self, learner_session_id: UUID) -> List[ApiLog]:
        result = await self.session.execute(
            select(ApiLog).where(ApiLog.learner_session_id == learner_session_id)
            .order_by(ApiLog.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_by_operation_type(self, operation_type: str) -> List[ApiLog]:
        result = await self.session.execute(
            select(ApiLog).where(ApiLog.operation_type == operation_type)
            .order_by(ApiLog.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def delete(self, log_id: UUID) -> bool:
        result = await self.session.execute(
            select(ApiLog).where(ApiLog.id == log_id)
        )
        api_log = result.scalar_one_or_none()
        if api_log:
            await self.session.delete(api_log)
            await self.session.commit()
            return True
        return False