"""
FIA v3.0 - Training Slide Repository
Repository for slides table operations (using existing slides table)
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone

from app.infrastructure.models.training_slide_model import TrainingSlideModel


class TrainingSlideRepository:
    """Repository for training slide operations"""
    
    def __init__(self, session: AsyncSession = None):
        self.session = session
    
    def set_session(self, session: AsyncSession):
        """Set database session"""
        self.session = session
    
    async def get_by_id(self, slide_id: UUID) -> Optional[TrainingSlideModel]:
        """Get training slide by ID"""
        if not self.session:
            raise ValueError("Database session not set")
        
        result = await self.session.execute(
            select(TrainingSlideModel)
            .where(TrainingSlideModel.id == slide_id)
            .options(selectinload(TrainingSlideModel.training_submodule))
        )
        return result.scalar_one_or_none()
    
    async def get_first_slide(self, training_plan_id: UUID) -> Optional[TrainingSlideModel]:
        """Get the first slide of a training plan"""
        if not self.session:
            raise ValueError("Database session not set")
        
        # Import needed models for joins
        from app.infrastructure.models.training_submodule_model import TrainingSubmoduleModel
        from app.infrastructure.models.training_module_model import TrainingModuleModel
        
        # Query to get the first slide of the first submodule of the first module
        result = await self.session.execute(
            select(TrainingSlideModel)
            .join(TrainingSubmoduleModel, TrainingSlideModel.submodule_id == TrainingSubmoduleModel.id)
            .join(TrainingModuleModel, TrainingSubmoduleModel.module_id == TrainingModuleModel.id)
            .where(TrainingModuleModel.plan_id == training_plan_id)
            .order_by(
                TrainingModuleModel.stage_number,
                TrainingModuleModel.order_in_stage,
                TrainingSubmoduleModel.order_in_module,
                TrainingSlideModel.order_in_submodule
            )
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_slides_by_submodule(self, submodule_id: UUID) -> List[TrainingSlideModel]:
        """Get all slides for a submodule, ordered by order_in_submodule"""
        if not self.session:
            raise ValueError("Database session not set")
        
        result = await self.session.execute(
            select(TrainingSlideModel)
            .where(TrainingSlideModel.submodule_id == submodule_id)
            .order_by(TrainingSlideModel.order_in_submodule)
        )
        return list(result.scalars().all())
    
    async def update_content(self, slide_id: UUID, content: str) -> bool:
        """Update slide content and mark as generated"""
        if not self.session:
            raise ValueError("Database session not set")
        
        try:
            await self.session.execute(
                update(TrainingSlideModel)
                .where(TrainingSlideModel.id == slide_id)
                .values(
                    content=content,
                    generated_at=datetime.now(timezone.utc)
                )
            )
            await self.session.commit()
            return True
        except Exception:
            await self.session.rollback()
            return False
    
    async def get_slides_by_training_plan(self, training_plan_id: UUID) -> List[TrainingSlideModel]:
        """Get all slides for a training plan, ordered by module/submodule/slide order"""
        if not self.session:
            raise ValueError("Database session not set")
        
        # Import needed models for joins
        from app.infrastructure.models.training_submodule_model import TrainingSubmoduleModel
        from app.infrastructure.models.training_module_model import TrainingModuleModel
        
        result = await self.session.execute(
            select(TrainingSlideModel)
            .join(TrainingSubmoduleModel, TrainingSlideModel.submodule_id == TrainingSubmoduleModel.id)
            .join(TrainingModuleModel, TrainingSubmoduleModel.module_id == TrainingModuleModel.id)
            .where(TrainingModuleModel.plan_id == training_plan_id)
            .order_by(
                TrainingModuleModel.stage_number,
                TrainingModuleModel.order_in_stage,
                TrainingSubmoduleModel.order_in_module,
                TrainingSlideModel.order_in_submodule
            )
            .options(
                selectinload(TrainingSlideModel.training_submodule)
            )
        )
        return list(result.scalars().all())
    
    async def get_next_slide(self, current_slide_id: UUID, training_plan_id: UUID) -> Optional[TrainingSlideModel]:
        """Get the next slide after the current one in the training plan"""
        if not self.session:
            raise ValueError("Database session not set")
        
        # Get all slides ordered
        all_slides = await self.get_slides_by_training_plan(training_plan_id)
        
        # Find current slide index
        current_index = None
        for i, slide in enumerate(all_slides):
            if slide.id == current_slide_id:
                current_index = i
                break
        
        # Return next slide if exists
        if current_index is not None and current_index + 1 < len(all_slides):
            return all_slides[current_index + 1]
        
        return None
    
    async def get_previous_slide(self, current_slide_id: UUID, training_plan_id: UUID) -> Optional[TrainingSlideModel]:
        """Get the previous slide before the current one in the training plan"""
        if not self.session:
            raise ValueError("Database session not set")
        
        # Get all slides ordered
        all_slides = await self.get_slides_by_training_plan(training_plan_id)
        
        # Find current slide index
        current_index = None
        for i, slide in enumerate(all_slides):
            if slide.id == current_slide_id:
                current_index = i
                break
        
        # Return previous slide if exists
        if current_index is not None and current_index > 0:
            return all_slides[current_index - 1]
        
        return None
    
    async def get_slide_position(self, slide_id: UUID, training_plan_id: UUID) -> dict:
        """Get position information for a slide within the training plan"""
        if not self.session:
            raise ValueError("Database session not set")
        
        # Get all slides ordered
        all_slides = await self.get_slides_by_training_plan(training_plan_id)
        
        # Find current slide index
        current_index = None
        for i, slide in enumerate(all_slides):
            if slide.id == slide_id:
                current_index = i
                break
        
        if current_index is not None:
            return {
                "current_position": current_index + 1,
                "total_slides": len(all_slides),
                "has_previous": current_index > 0,
                "has_next": current_index + 1 < len(all_slides)
            }
        
        return {
            "current_position": 0,
            "total_slides": len(all_slides),
            "has_previous": False,
            "has_next": False
        }