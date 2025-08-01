"""
FIA v3.0 - Learner Training Plan Repository
Repository implementation for learner training plans database operations
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.domain.entities.learner_training_plan import LearnerTrainingPlan
from app.domain.ports.repositories import LearnerTrainingPlanRepositoryPort
from app.infrastructure.models.learner_training_plan_model import LearnerTrainingPlanModel
from app.infrastructure.models.training_module_model import TrainingModuleModel
from app.infrastructure.models.training_submodule_model import TrainingSubmoduleModel


class LearnerTrainingPlanRepository(LearnerTrainingPlanRepositoryPort):
    """Repository implementation for learner training plans"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, plan: LearnerTrainingPlan) -> LearnerTrainingPlan:
        """Create a new learner training plan"""
        # Convert domain entity to SQLAlchemy model
        plan_model = LearnerTrainingPlanModel(
            id=plan.id,
            learner_session_id=plan.learner_session_id,
            plan_data=plan.plan_data,
            generation_method=plan.generation_method,
            tokens_used=plan.tokens_used,
            generation_time_seconds=plan.generation_time_seconds
        )
        
        self.session.add(plan_model)
        await self.session.commit()
        await self.session.refresh(plan_model)
        
        # Convert back to domain entity
        return self._model_to_entity(plan_model)
    
    async def get_by_id(self, plan_id: UUID) -> Optional[LearnerTrainingPlan]:
        """Get learner training plan by ID"""
        result = await self.session.execute(
            select(LearnerTrainingPlanModel)
            .options(selectinload(LearnerTrainingPlanModel.training_modules))
            .where(LearnerTrainingPlanModel.id == plan_id)
        )
        plan_model = result.scalar_one_or_none()
        
        if plan_model:
            return self._model_to_entity(plan_model)
        return None
    
    async def get_by_learner_session_id(self, learner_session_id: UUID) -> List[LearnerTrainingPlan]:
        """Get all training plans for a learner session"""
        result = await self.session.execute(
            select(LearnerTrainingPlanModel)
            .options(selectinload(LearnerTrainingPlanModel.training_modules))
            .where(LearnerTrainingPlanModel.learner_session_id == learner_session_id)
            .order_by(LearnerTrainingPlanModel.created_at.desc())
        )
        plan_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in plan_models]
    
    async def get_latest_by_learner_session_id(self, learner_session_id: UUID) -> Optional[LearnerTrainingPlan]:
        """Get the most recent training plan for a learner session"""
        result = await self.session.execute(
            select(LearnerTrainingPlanModel)
            .options(selectinload(LearnerTrainingPlanModel.training_modules))
            .where(LearnerTrainingPlanModel.learner_session_id == learner_session_id)
            .order_by(LearnerTrainingPlanModel.created_at.desc())
            .limit(1)
        )
        plan_model = result.scalar_one_or_none()
        
        if plan_model:
            return self._model_to_entity(plan_model)
        return None
    
    async def update(self, plan: LearnerTrainingPlan) -> LearnerTrainingPlan:
        """Update an existing learner training plan"""
        result = await self.session.execute(
            select(LearnerTrainingPlanModel)
            .where(LearnerTrainingPlanModel.id == plan.id)
        )
        plan_model = result.scalar_one_or_none()
        
        if not plan_model:
            raise ValueError(f"LearnerTrainingPlan with id {plan.id} not found")
        
        # Update fields
        plan_model.plan_data = plan.plan_data
        plan_model.generation_method = plan.generation_method
        plan_model.tokens_used = plan.tokens_used
        plan_model.generation_time_seconds = plan.generation_time_seconds
        
        await self.session.commit()
        await self.session.refresh(plan_model)
        
        return self._model_to_entity(plan_model)
    
    async def update_current_slide_id(self, learner_session_id: UUID, slide_id: UUID) -> bool:
        """Update the current slide ID for a learner training plan"""
        result = await self.session.execute(
            select(LearnerTrainingPlanModel)
            .where(LearnerTrainingPlanModel.learner_session_id == learner_session_id)
        )
        plan_model = result.scalar_one_or_none()
        
        if not plan_model:
            return False
        
        plan_model.current_slide_id = slide_id
        await self.session.commit()
        return True
    
    async def delete(self, plan_id: UUID) -> bool:
        """Delete a learner training plan"""
        result = await self.session.execute(
            select(LearnerTrainingPlanModel)
            .where(LearnerTrainingPlanModel.id == plan_id)
        )
        plan_model = result.scalar_one_or_none()
        
        if plan_model:
            await self.session.delete(plan_model)
            await self.session.commit()
            return True
        return False
    
    async def get_plans_by_generation_method(self, method: str, limit: int = 100) -> List[LearnerTrainingPlan]:
        """Get training plans by generation method (vertex_ai, gemini, manual)"""
        result = await self.session.execute(
            select(LearnerTrainingPlanModel)
            .options(selectinload(LearnerTrainingPlanModel.training_modules))
            .where(LearnerTrainingPlanModel.generation_method == method)
            .order_by(LearnerTrainingPlanModel.created_at.desc())
            .limit(limit)
        )
        plan_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in plan_models]
    
    async def get_plans_with_performance_metrics(self, min_tokens: int = None, max_generation_time: int = None) -> List[LearnerTrainingPlan]:
        """Get plans with specific performance criteria"""
        query = select(LearnerTrainingPlanModel).options(
            selectinload(LearnerTrainingPlanModel.training_modules)
        )
        
        conditions = []
        if min_tokens is not None:
            conditions.append(LearnerTrainingPlanModel.tokens_used >= min_tokens)
        if max_generation_time is not None:
            conditions.append(LearnerTrainingPlanModel.generation_time_seconds <= max_generation_time)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(LearnerTrainingPlanModel.created_at.desc())
        
        result = await self.session.execute(query)
        plan_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in plan_models]
    
    def _model_to_entity(self, model: LearnerTrainingPlanModel) -> LearnerTrainingPlan:
        """Convert SQLAlchemy model to domain entity"""
        return LearnerTrainingPlan(
            id=model.id,
            learner_session_id=model.learner_session_id,
            plan_data=model.plan_data,
            generation_method=model.generation_method,
            tokens_used=model.tokens_used,
            generation_time_seconds=model.generation_time_seconds,
            created_at=model.created_at,
            updated_at=model.updated_at
        )