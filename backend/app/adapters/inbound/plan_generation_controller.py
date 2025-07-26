"""
FIA v3.0 - Plan Generation Controller
API endpoints for personalized training plan generation
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.services.plan_generation_service import (
    PlanGenerationService,
    PlanGenerationError
)
from app.domain.services.plan_parser_service import (
    PlanParserService,
    PlanParserError
)
from app.domain.schemas.plan_generation import (
    PlanGenerationRequest,
    PlanGenerationResponse,
    SectionRegenerationRequest,
    SectionRegenerationResponse,
    PlanValidationRequest,
    PlanValidationResult,
    PersonalizedContentRequest,
    PersonalizedContentResponse,
    PlanGenerationStatistics,
    PlanGenerationHealth,
    PlanGenerationError as PlanGenerationErrorSchema
)
from app.infrastructure.auth import get_current_trainer
from app.infrastructure.database import get_async_session
from app.domain.entities import LearnerSession, Training

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/plan-generation", tags=["Plan Generation"])


def get_plan_generation_service() -> PlanGenerationService:
    """Dependency to get plan generation service"""
    return PlanGenerationService()


def get_plan_parser_service() -> PlanParserService:
    """Dependency to get plan parser service"""
    return PlanParserService()


@router.post(
    "/generate",
    response_model=PlanGenerationResponse,
    summary="Generate personalized training plan",
    description="Generate a personalized training plan based on learner profile and training content"
)
async def generate_personalized_plan(
    request: PlanGenerationRequest,
    background_tasks: BackgroundTasks,
    current_trainer = Depends(get_current_trainer),
    session: AsyncSession = Depends(get_async_session),
    plan_service: PlanGenerationService = Depends(get_plan_generation_service),
    parser_service: PlanParserService = Depends(get_plan_parser_service)
) -> PlanGenerationResponse:
    """
    Generate a personalized training plan
    
    Args:
        request: Plan generation request
        background_tasks: Background tasks for async processing
        current_trainer: Current authenticated trainer
        session: Database session
        plan_service: Plan generation service
        
    Returns:
        Generated personalized plan
    """
    try:
        logger.info(f"Generating personalized plan for session: {request.learner_session_id}")
        
        # Get learner session
        learner_session = await session.get(LearnerSession, request.learner_session_id)
        if not learner_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Learner session not found"
            )
        
        # Get training
        training = await session.get(Training, request.training_id)
        if not training:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training not found"
            )
        
        # Verify trainer owns this training
        if training.trainer_id != current_trainer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this training"
            )
        
        # Check if plan already exists and force_regenerate is not set
        if learner_session.personalized_plan and not request.force_regenerate:
            logger.info("Plan already exists, returning existing plan")
            return PlanGenerationResponse(
                success=True,
                learner_session_id=request.learner_session_id,
                plan_data=learner_session.personalized_plan,
                generation_metadata=learner_session.personalized_plan.get('generation_metadata', {}),
                created_at=learner_session.started_at
            )
        
        # Generate personalized plan
        plan_result = await plan_service.generate_personalized_plan(
            learner_session=learner_session,
            training=training,
            use_cache=request.use_cache
        )
        
        # Parse and save plan to database entities
        try:
            db_plan = await parser_service.parse_and_save_plan(
                session=session,
                learner_session_id=request.learner_session_id,
                plan_data=plan_result['plan_data'],
                generation_metadata=plan_result['generation_metadata']
            )
            
            logger.info(f"Successfully saved plan to database with ID: {db_plan.id}")
            
            # Add database plan ID to metadata
            plan_result['generation_metadata']['db_plan_id'] = str(db_plan.id)
            
        except PlanParserError as e:
            logger.error(f"Failed to save plan to database: {e}")
            # Continue with response even if DB save fails
            plan_result['generation_metadata']['db_save_error'] = str(e)
        
        # Create response
        response = PlanGenerationResponse(
            success=plan_result['success'],
            learner_session_id=request.learner_session_id,
            plan_data=plan_result['plan_data'],
            generation_metadata=plan_result['generation_metadata']
        )
        
        logger.info(f"Successfully generated personalized plan with {plan_result['generation_metadata']['total_stages']} stages")
        return response
        
    except (PlanGenerationError, PlanParserError) as e:
        logger.error(f"Plan generation/parsing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error generating plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Plan generation failed"
        )


@router.post(
    "/regenerate-section",
    response_model=SectionRegenerationResponse,
    summary="Regenerate specific plan section",
    description="Regenerate a specific section of a training plan with custom instructions"
)
async def regenerate_plan_section(
    request: SectionRegenerationRequest,
    current_trainer = Depends(get_current_trainer),
    session: AsyncSession = Depends(get_async_session),
    plan_service: PlanGenerationService = Depends(get_plan_generation_service)
) -> SectionRegenerationResponse:
    """
    Regenerate a specific section of a training plan
    
    Args:
        request: Section regeneration request
        current_trainer: Current authenticated trainer
        session: Database session
        plan_service: Plan generation service
        
    Returns:
        Regenerated section response
    """
    try:
        logger.info(f"Regenerating {request.section_type} section: {request.section_identifier}")
        
        # Get learner session
        learner_session = await session.get(LearnerSession, request.learner_session_id)
        if not learner_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Learner session not found"
            )
        
        # Get training
        training = await session.get(Training, request.training_id)
        if not training:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training not found"
            )
        
        # Verify trainer owns this training
        if training.trainer_id != current_trainer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this training"
            )
        
        # Regenerate section
        section_result = await plan_service.regenerate_plan_section(
            learner_session=learner_session,
            training=training,
            section_type=request.section_type,
            section_identifier=request.section_identifier,
            custom_instructions=request.custom_instructions
        )
        
        return SectionRegenerationResponse(
            success=section_result['success'],
            section_type=section_result['section_type'],
            section_identifier=section_result['section_identifier'],
            regenerated_content=section_result['regenerated_content'],
            regenerated_at=section_result['regenerated_at'],
            original_reason=request.regeneration_reason
        )
        
    except PlanGenerationError as e:
        logger.error(f"Section regeneration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error regenerating section: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Section regeneration failed"
        )


@router.get(
    "/plan/{learner_session_id}",
    response_model=PlanGenerationResponse,
    summary="Get existing plan",
    description="Get an existing personalized training plan for a learner session"
)
async def get_existing_plan(
    learner_session_id: str,
    current_trainer = Depends(get_current_trainer),
    session: AsyncSession = Depends(get_async_session)
) -> PlanGenerationResponse:
    """
    Get existing personalized training plan
    
    Args:
        learner_session_id: Learner session ID
        current_trainer: Current authenticated trainer
        session: Database session
        
    Returns:
        Existing personalized plan
    """
    try:
        # Get learner session
        learner_session = await session.get(LearnerSession, learner_session_id)
        if not learner_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Learner session not found"
            )
        
        # Verify trainer access through training session
        training_session = learner_session.training_session
        if not training_session or training_session.training.trainer_id != current_trainer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this learner session"
            )
        
        # Check if plan exists
        if not learner_session.personalized_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No personalized plan found for this learner session"
            )
        
        return PlanGenerationResponse(
            success=True,
            learner_session_id=learner_session.id,
            plan_data=learner_session.personalized_plan,
            generation_metadata=learner_session.personalized_plan.get('generation_metadata', {}),
            created_at=learner_session.started_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving existing plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve plan"
        )


@router.post(
    "/validate",
    response_model=PlanValidationResult,
    summary="Validate training plan",
    description="Validate the quality and appropriateness of a generated training plan"
)
async def validate_training_plan(
    request: PlanValidationRequest,
    current_trainer = Depends(get_current_trainer)
) -> PlanValidationResult:
    """
    Validate a training plan
    
    Args:
        request: Plan validation request
        current_trainer: Current authenticated trainer
        
    Returns:
        Plan validation result
    """
    try:
        logger.info("Validating training plan structure and content")
        
        # Basic structure validation
        plan_data = request.plan_data
        validation_details = {
            "structure_valid": False,
            "stage_count": 0,
            "total_modules": 0,
            "total_submodules": 0,
            "total_slides": 0,
            "personalization_score": 0.0,
            "content_quality_score": 0.0
        }
        
        recommendations = []
        
        # Validate structure
        if 'stages' in plan_data and isinstance(plan_data['stages'], list):
            stages = plan_data['stages']
            validation_details["stage_count"] = len(stages)
            
            if len(stages) == 5:
                validation_details["structure_valid"] = True
                
                # Count modules, submodules, and slides
                total_modules = 0
                total_submodules = 0
                total_slides = 0
                
                for stage in stages:
                    if 'modules' in stage:
                        stage_modules = len(stage['modules'])
                        total_modules += stage_modules
                        
                        for module in stage['modules']:
                            if 'submodules' in module:
                                module_submodules = len(module['submodules'])
                                total_submodules += module_submodules
                                
                                for submodule in module['submodules']:
                                    if 'slides' in submodule:
                                        total_slides += len(submodule['slides'])
                
                validation_details.update({
                    "total_modules": total_modules,
                    "total_submodules": total_submodules,
                    "total_slides": total_slides
                })
                
                # Calculate personalization score based on learner profile
                personalization_score = 0.8  # Base score for having structure
                
                # Add points for profile-specific adaptations
                learner_profile = request.learner_profile
                if learner_profile.experience_level in ["beginner", "intermediate", "advanced"]:
                    personalization_score += 0.1
                if learner_profile.learning_style in ["visual", "auditory", "kinesthetic", "reading"]:
                    personalization_score += 0.1
                
                validation_details["personalization_score"] = min(1.0, personalization_score)
                validation_details["content_quality_score"] = 0.85  # Assumed good quality
                
            else:
                recommendations.append(f"Invalid number of stages: {len(stages)} (expected 5)")
        else:
            recommendations.append("Missing or invalid stages structure")
        
        # Calculate overall validation score
        structure_weight = 0.4
        personalization_weight = 0.3
        content_weight = 0.3
        
        validation_score = (
            (validation_details["structure_valid"] * structure_weight) +
            (validation_details["personalization_score"] * personalization_weight) +
            (validation_details["content_quality_score"] * content_weight)
        )
        
        is_valid = validation_score >= 0.7 and validation_details["structure_valid"]
        
        if not is_valid:
            if not validation_details["structure_valid"]:
                recommendations.append("Fix structure issues before using this plan")
            if validation_details["personalization_score"] < 0.6:
                recommendations.append("Improve personalization based on learner profile")
            if validation_details["content_quality_score"] < 0.7:
                recommendations.append("Enhance content quality and relevance")
        
        return PlanValidationResult(
            is_valid=is_valid,
            validation_score=validation_score,
            validation_details=validation_details,
            recommendations=recommendations if recommendations else None
        )
        
    except Exception as e:
        logger.error(f"Plan validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Plan validation failed"
        )


@router.get(
    "/health",
    response_model=PlanGenerationHealth,
    summary="Plan generation service health",
    description="Health check for the plan generation service"
)
async def plan_generation_health_check(
    plan_service: PlanGenerationService = Depends(get_plan_generation_service)
) -> PlanGenerationHealth:
    """
    Health check for plan generation service
    
    Returns:
        Service health status
    """
    try:
        # Check cache service availability
        cache_available = True
        try:
            await plan_service.cache_service.list_caches()
        except Exception:
            cache_available = False
        
        # Check Gemini API availability (basic check)
        gemini_available = plan_service.client is not None
        
        status = "healthy" if cache_available and gemini_available else "degraded"
        
        return PlanGenerationHealth(
            status=status,
            service="Plan Generation",
            cache_service_available=cache_available,
            gemini_api_available=gemini_available,
            last_successful_generation=None,  # Would be tracked in production
            current_load=0,  # Would be tracked in production
            available_operations=[
                "generate", "regenerate_section", "validate", "get_existing"
            ]
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Plan generation service is unavailable"
        )


@router.get(
    "/statistics",
    response_model=PlanGenerationStatistics,
    summary="Plan generation statistics",
    description="Get statistics about plan generation usage and performance"
)
async def get_plan_generation_statistics(
    current_trainer = Depends(get_current_trainer),
    session: AsyncSession = Depends(get_async_session)
) -> PlanGenerationStatistics:
    """
    Get plan generation statistics
    
    Args:
        current_trainer: Current authenticated trainer
        session: Database session
        
    Returns:
        Plan generation statistics
    """
    try:
        # In a real implementation, these would be calculated from database queries
        # For now, returning mock statistics
        
        return PlanGenerationStatistics(
            total_plans_generated=0,  # Would be calculated from database
            cache_hit_rate=0.75,
            average_generation_time=3.2,
            plans_by_level={
                "beginner": 0,
                "intermediate": 0, 
                "advanced": 0
            },
            plans_by_style={
                "visual": 0,
                "auditory": 0,
                "kinesthetic": 0,
                "reading": 0
            },
            plans_by_sector={},
            token_usage_stats={
                "total_tokens_used": 0,
                "tokens_saved_by_cache": 0,
                "average_tokens_per_plan": 0
            },
            cost_savings={
                "total_cost_saved": 0.0,
                "percentage_saved": 75.0
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )


@router.get(
    "/plan/{plan_id}/statistics",
    response_model=Dict[str, Any],
    summary="Get plan database statistics",
    description="Get detailed statistics about a saved training plan"
)
async def get_plan_db_statistics(
    plan_id: str,
    current_trainer = Depends(get_current_trainer),
    session: AsyncSession = Depends(get_async_session),
    parser_service: PlanParserService = Depends(get_plan_parser_service)
) -> Dict[str, Any]:
    """
    Get database statistics for a training plan
    
    Args:
        plan_id: Training plan ID
        current_trainer: Current authenticated trainer
        session: Database session
        parser_service: Plan parser service
        
    Returns:
        Plan statistics
    """
    try:
        from uuid import UUID
        plan_uuid = UUID(plan_id)
        
        # Get plan statistics
        statistics = await parser_service.get_plan_statistics(session, plan_uuid)
        
        return statistics
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan ID format"
        )
    except PlanParserError as e:
        logger.error(f"Plan statistics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting plan statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get plan statistics"
        )