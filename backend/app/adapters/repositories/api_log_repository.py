from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities import ApiLog
from app.infrastructure.models.api_log_model import ApiLogModel
from app.domain.ports.repositories import ApiLogRepositoryPort


class ApiLogRepository(ApiLogRepositoryPort):
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, api_log: ApiLog) -> ApiLog:
        # Convertir l'entité domain en modèle SQLAlchemy
        api_log_model = ApiLogModel(
            id=api_log.id,
            service_name=api_log.service_name,
            endpoint=api_log.endpoint,
            method=api_log.method,
            request_data=api_log.request_data,
            response_data=api_log.response_data,
            status_code=api_log.status_code,
            response_time_ms=api_log.response_time_ms,
            tokens_used=api_log.tokens_used,
            cost_estimate=api_log.cost_estimate,
            learner_session_id=api_log.learner_session_id
        )
        
        self.session.add(api_log_model)
        await self.session.commit()
        await self.session.refresh(api_log_model)
        return api_log
    
    async def get_by_id(self, log_id: UUID) -> Optional[ApiLog]:
        result = await self.session.execute(
            select(ApiLogModel).where(ApiLogModel.id == log_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_learner_session_id(self, learner_session_id: UUID) -> List[ApiLog]:
        result = await self.session.execute(
            select(ApiLogModel).where(ApiLogModel.learner_session_id == learner_session_id)
            .order_by(ApiLogModel.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_by_operation_type(self, operation_type: str) -> List[ApiLog]:
        result = await self.session.execute(
            select(ApiLogModel).where(ApiLogModel.service_name == operation_type)
            .order_by(ApiLogModel.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def delete(self, log_id: UUID) -> bool:
        result = await self.session.execute(
            select(ApiLogModel).where(ApiLogModel.id == log_id)
        )
        api_log = result.scalar_one_or_none()
        if api_log:
            await self.session.delete(api_log)
            await self.session.commit()
            return True
        return False