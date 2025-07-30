"""
FIA v3.0 - Image Generation Controller
FastAPI routes for OpenAI image generation service
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import traceback
import time
from typing import Dict, Any

from app.infrastructure.database import get_database_session
from app.domain.schemas.image_generation import (
    ImageGenerationRequest,
    ImageGenerationResponse,
    ImageGenerationStatus,
    ImageGenerationMetrics
)
from app.adapters.outbound.openai_adapter import OpenAIAdapter
from app.adapters.repositories.learner_session_repository import LearnerSessionRepository
from app.adapters.repositories.training_slide_repository import TrainingSlideRepository
from app.infrastructure.rate_limiter import openai_rate_limiter, RateLimitExceeded

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["image-generation"])


# ============================================================================
# IMAGE GENERATION ROUTES (public - no auth required for learners)
# ============================================================================

@router.post("/api/image-generation/generate", response_model=ImageGenerationResponse, status_code=status.HTTP_200_OK)
async def generate_infographic(
    request: ImageGenerationRequest,
    db: AsyncSession = Depends(get_database_session)
) -> ImageGenerationResponse:
    """
    Generate educational infographic from slide content using OpenAI
    
    This endpoint generates a visual infographic based on slide content,
    personalized with the learner's profile for enhanced learning experience.
    """
    start_time = time.time()
    
    try:
        logger.info(f"Starting infographic generation for learner session {request.learner_session_id}")
        
        # Initialize repositories and adapters
        learner_session_repo = LearnerSessionRepository(db)
        training_slide_repo = TrainingSlideRepository(db)
        openai_adapter = OpenAIAdapter()
        
        # Fetch learner session for personalization
        learner_session = await learner_session_repo.get_by_id(request.learner_session_id)
        if not learner_session:
            logger.warning(f"Learner session not found: {request.learner_session_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Learner session not found"
            )
        
        # Extract learner profile for personalization
        learner_profile = None
        if learner_session.enriched_profile:
            learner_profile = learner_session.enriched_profile
        elif hasattr(learner_session, 'level') and hasattr(learner_session, 'learning_style'):
            # Fallback to basic profile data
            learner_profile = {
                "level": learner_session.level,
                "learning_style": learner_session.learning_style
            }
        
        logger.debug(f"Using learner profile for personalization: {bool(learner_profile)}")
        
        # Generate infographic using OpenAI
        result = await openai_adapter.generate_infographic(
            slide_content=request.slide_content,
            learner_profile=learner_profile,
            learner_session_id=request.learner_session_id,
            slide_id=request.slide_id
        )
        
        # Save image information to database if slide_id is provided
        if request.slide_id and result.get("image_path"):
            try:
                slide = await training_slide_repo.get_by_id(request.slide_id)
                if slide:
                    # Update slide with image information
                    slide.generated_image_path = result["image_path"]
                    slide.generated_image_metadata = {
                        "revised_prompt": result["revised_prompt"],
                        "generation_time": time.time() - start_time,
                        "model": result["metadata"]["model"],
                        "size": result["metadata"]["size"],
                        "quality": result["metadata"]["quality"]
                    }
                    await training_slide_repo.update(slide)
                    logger.info(f"Updated slide {request.slide_id} with image path: {result['image_path']}")
                else:
                    logger.warning(f"Slide {request.slide_id} not found for updating image path")
            except Exception as e:
                logger.error(f"Failed to save image path to database: {str(e)}")
                # Don't fail the request if DB update fails
        
        generation_time = time.time() - start_time
        
        logger.info(f"Successfully generated infographic in {generation_time:.2f}s for session {request.learner_session_id}")
        
        return ImageGenerationResponse(
            success=True,
            image_data=result["image_data"],
            revised_prompt=result["revised_prompt"],
            metadata=result["metadata"],
            generation_time_seconds=generation_time
        )
        
    except RateLimitExceeded as e:
        generation_time = time.time() - start_time
        logger.warning(f"Rate limit exceeded for image generation: {str(e)}")
        
        return ImageGenerationResponse(
            success=False,
            error_message="Image generation rate limit exceeded. Please try again later.",
            generation_time_seconds=generation_time
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404 for learner session not found)
        raise
        
    except Exception as e:
        generation_time = time.time() - start_time
        error_trace = traceback.format_exc()
        logger.error(f"Unexpected error in image generation: {str(e)}")
        logger.debug(f"Error traceback: {error_trace}")
        
        return ImageGenerationResponse(
            success=False,
            error_message="Failed to generate infographic. Please try again.",
            generation_time_seconds=generation_time
        )


@router.get("/api/image-generation/status", response_model=ImageGenerationStatus, status_code=status.HTTP_200_OK)
async def get_image_generation_status() -> ImageGenerationStatus:
    """
    Get current status of the image generation service
    
    Returns service availability and rate limiting information
    """
    try:
        # Get rate limit status
        rate_limit_status = openai_rate_limiter.get_status()
        
        return ImageGenerationStatus(
            service_available=True,
            rate_limit_status=rate_limit_status,
            total_images_generated=0,  # Could be tracked in the future
            last_generation_at=None   # Could be tracked in the future
        )
        
    except Exception as e:
        logger.error(f"Error getting image generation status: {str(e)}")
        
        return ImageGenerationStatus(
            service_available=False,
            rate_limit_status={
                "error": "Unable to get rate limit status"
            }
        )


# ============================================================================
# ADMIN/DEBUG ROUTES (for development and monitoring)
# ============================================================================

@router.get("/api/image-generation/rate-limit-status", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def get_rate_limit_status() -> Dict[str, Any]:
    """
    Get detailed rate limiting status for OpenAI API
    
    Useful for debugging and monitoring rate limit usage
    """
    try:
        status_info = openai_rate_limiter.get_status()
        
        return {
            "service": "OpenAI Image Generation",
            "rate_limit": status_info,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Error getting rate limit status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve rate limit status"
        )