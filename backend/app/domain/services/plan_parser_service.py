"""
FIA v3.0 - Plan Parser Service
Service for parsing generated JSON plans and saving them to database entities
"""

import logging
from typing import Dict, Any, List, Protocol
from uuid import UUID

from app.domain.entities.learner_training_plan import LearnerTrainingPlan
from app.domain.entities.training_module import TrainingModule
from app.domain.entities.training_submodule import TrainingSubmodule
from app.domain.entities.training_slide import TrainingSlide
from app.domain.entities.learner_session import LearnerSession

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseSession(Protocol):
    """Interface for database session (pure domain)"""
    async def add(self, instance: Any) -> None: ...
    async def commit(self) -> None: ...


class PlanParserError(Exception):
    """Custom exception for plan parsing errors"""
    pass


class PlanParserService:
    """Service for parsing JSON plans and converting them to database entities"""
    
    def __init__(self):
        """Initialize the plan parser service"""
        self.logger = logging.getLogger(__name__)
    
    async def parse_and_save_plan(
        self,
        session: DatabaseSession,
        learner_session_id: UUID,
        plan_data: Dict[str, Any],
        generation_metadata: Dict[str, Any]
    ) -> LearnerTrainingPlan:
        """
        Parse JSON plan data and save it as database entities
        
        Args:
            session: Database session
            learner_session_id: Learner session ID
            plan_data: Generated plan data from Gemini
            generation_metadata: Plan generation metadata
            
        Returns:
            Created LearnerTrainingPlan entity
            
        Raises:
            PlanParserError: If parsing or saving fails
        """
        try:
            logger.info(f"Parsing and saving plan for learner session: {learner_session_id}")
            
            # Validate plan structure
            if 'stages' not in plan_data:
                raise PlanParserError("Plan data missing 'stages' field")
            
            stages = plan_data['stages']
            if len(stages) != 5:
                raise PlanParserError(f"Expected 5 stages, got {len(stages)}")
            
            # Check if plan already exists and delete it
            existing_plan = await session.get(LearnerTrainingPlan, learner_session_id)
            if existing_plan:
                logger.info("Deleting existing plan before creating new one")
                await session.delete(existing_plan)
                await session.flush()
            
            # Create new training plan
            training_plan = LearnerTrainingPlan(
                learner_session_id=learner_session_id
            )
            session.add(training_plan)
            await session.flush()  # Get the ID
            
            # Parse and create modules for each stage
            total_slides_created = 0
            for stage in stages:
                modules_in_stage = await self._parse_stage_modules(
                    session, training_plan.id, stage
                )
                
                # Count slides for logging
                for module in modules_in_stage:
                    for submodule in module.submodules:
                        total_slides_created += len(submodule.slides)
            
            # Set current slide to first slide if any exists
            if total_slides_created > 0:
                first_module = training_plan.modules[0] if training_plan.modules else None
                if first_module and first_module.submodules:
                    first_submodule = first_module.submodules[0]
                    if first_submodule.slides:
                        training_plan.current_slide_id = first_submodule.slides[0].id
            
            await session.commit()
            
            # Update learner session with plan data
            learner_session = await session.get(LearnerSession, learner_session_id)
            if learner_session:
                learner_session.personalized_plan = {
                    'plan_data': plan_data,
                    'generation_metadata': generation_metadata,
                    'db_plan_id': str(training_plan.id)
                }
                await session.commit()
            
            logger.info(f"Successfully saved plan with {len(training_plan.modules)} modules and {total_slides_created} slides")
            return training_plan
            
        except Exception as e:
            logger.error(f"Failed to parse and save plan: {e}")
            await session.rollback()
            raise PlanParserError(f"Plan parsing failed: {e}")
    
    async def _parse_stage_modules(
        self,
        session: AsyncSession,
        plan_id: UUID,
        stage_data: Dict[str, Any]
    ) -> List[TrainingModule]:
        """
        Parse modules for a specific stage
        
        Args:
            session: Database session
            plan_id: Training plan ID
            stage_data: Stage data from JSON
            
        Returns:
            List of created TrainingModule entities
        """
        modules = []
        stage_number = stage_data.get('stage_number', 1)
        stage_modules = stage_data.get('modules', [])
        
        for order_index, module_data in enumerate(stage_modules, 1):
            # Create training module
            module = TrainingModule(
                plan_id=plan_id,
                title=module_data.get('title', f'Module {stage_number}.{order_index}'),
                description=module_data.get('description', ''),
                stage_number=stage_number,
                order_in_stage=order_index
            )
            session.add(module)
            await session.flush()  # Get the ID
            
            # Parse submodules
            await self._parse_module_submodules(
                session, module.id, module_data.get('submodules', [])
            )
            
            modules.append(module)
        
        return modules
    
    async def _parse_module_submodules(
        self,
        session: AsyncSession,
        module_id: UUID,
        submodules_data: List[Dict[str, Any]]
    ) -> List[TrainingSubmodule]:
        """
        Parse submodules for a specific module
        
        Args:
            session: Database session
            module_id: Module ID
            submodules_data: Submodules data from JSON
            
        Returns:
            List of created TrainingSubmodule entities
        """
        submodules = []
        
        for order_index, submodule_data in enumerate(submodules_data, 1):
            # Create training submodule
            submodule = TrainingSubmodule(
                module_id=module_id,
                title=submodule_data.get('title', f'Submodule {order_index}'),
                description=submodule_data.get('description', ''),
                order_in_module=order_index
            )
            session.add(submodule)
            await session.flush()  # Get the ID
            
            # Parse slides
            await self._parse_submodule_slides(
                session, submodule.id, submodule_data.get('slides', [])
            )
            
            submodules.append(submodule)
        
        return submodules
    
    async def _parse_submodule_slides(
        self,
        session: AsyncSession,
        submodule_id: UUID,
        slides_data: List[Dict[str, Any]]
    ) -> List[TrainingSlide]:
        """
        Parse slides for a specific submodule
        
        Args:
            session: Database session
            submodule_id: Submodule ID
            slides_data: Slides data from JSON
            
        Returns:
            List of created TrainingSlide entities
        """
        slides = []
        
        for order_index, slide_data in enumerate(slides_data, 1):
            # Create training slide with title only (content generated on-demand)
            slide = TrainingSlide(
                submodule_id=submodule_id,
                title=slide_data.get('title', f'Slide {order_index}'),
                content=None,  # Content will be generated on-demand
                order_in_submodule=order_index
            )
            session.add(slide)
            slides.append(slide)
        
        return slides
    
    async def get_plan_statistics(
        self,
        session: AsyncSession,
        plan_id: UUID
    ) -> Dict[str, Any]:
        """
        Get statistics for a saved plan
        
        Args:
            session: Database session
            plan_id: Training plan ID
            
        Returns:
            Plan statistics dictionary
        """
        try:
            # Get plan with all relationships
            plan = await session.get(LearnerTrainingPlan, plan_id)
            if not plan:
                raise PlanParserError(f"Plan not found: {plan_id}")
            
            # Calculate statistics
            total_modules = len(plan.modules)
            total_submodules = sum(len(module.submodules) for module in plan.modules)
            total_slides = sum(
                len(submodule.slides)
                for module in plan.modules
                for submodule in module.submodules
            )
            
            # Group by stages
            stages_stats = {}
            for module in plan.modules:
                stage_num = module.stage_number
                if stage_num not in stages_stats:
                    stages_stats[stage_num] = {
                        'modules': 0,
                        'submodules': 0,
                        'slides': 0
                    }
                
                stages_stats[stage_num]['modules'] += 1
                stages_stats[stage_num]['submodules'] += len(module.submodules)
                stages_stats[stage_num]['slides'] += sum(
                    len(submodule.slides) for submodule in module.submodules
                )
            
            return {
                'plan_id': str(plan_id),
                'total_modules': total_modules,
                'total_submodules': total_submodules,
                'total_slides': total_slides,
                'stages': stages_stats,
                'current_slide_id': str(plan.current_slide_id) if plan.current_slide_id else None,
                'created_at': plan.created_at.isoformat(),
                'updated_at': plan.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get plan statistics: {e}")
            raise PlanParserError(f"Statistics retrieval failed: {e}")
    
    async def update_current_slide(
        self,
        session: AsyncSession,
        plan_id: UUID,
        slide_id: UUID
    ) -> bool:
        """
        Update the current slide for a training plan
        
        Args:
            session: Database session
            plan_id: Training plan ID
            slide_id: New current slide ID
            
        Returns:
            True if update was successful
        """
        try:
            plan = await session.get(LearnerTrainingPlan, plan_id)
            if not plan:
                raise PlanParserError(f"Plan not found: {plan_id}")
            
            # Verify slide belongs to this plan
            slide = await session.get(TrainingSlide, slide_id)
            if not slide:
                raise PlanParserError(f"Slide not found: {slide_id}")
            
            # Update current slide
            plan.current_slide_id = slide_id
            await session.commit()
            
            logger.info(f"Updated current slide to {slide_id} for plan {plan_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update current slide: {e}")
            await session.rollback()
            raise PlanParserError(f"Current slide update failed: {e}")
    
    async def delete_plan(
        self,
        session: AsyncSession,
        plan_id: UUID
    ) -> bool:
        """
        Delete a training plan and all its related entities
        
        Args:
            session: Database session
            plan_id: Training plan ID to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            plan = await session.get(LearnerTrainingPlan, plan_id)
            if not plan:
                logger.warning(f"Plan not found for deletion: {plan_id}")
                return False
            
            # Delete plan (cascade will handle modules, submodules, slides)
            await session.delete(plan)
            await session.commit()
            
            logger.info(f"Successfully deleted plan: {plan_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete plan: {e}")
            await session.rollback()
            raise PlanParserError(f"Plan deletion failed: {e}")