"""
FIA v3.0 - Slide Controller
API endpoints for slide generation and management
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from pydantic import BaseModel

from app.services.slide_generation_service import SlideGenerationService
from app.infrastructure.rate_limiter import SlidingWindowRateLimiter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/slides", tags=["slides"])

# Rate limiter for slide generation (costly AI operations)
rate_limiter = SlidingWindowRateLimiter(requests_per_minute=30, window_size_seconds=60)


class SimplifySlideRequest(BaseModel):
    """Request model for slide content simplification"""
    current_content: str


class MoreDetailsSlideRequest(BaseModel):
    """Request model for slide content enhancement with more details"""
    current_content: str


@router.post("/generate-first/{learner_session_id}", response_model=Dict[str, Any])
async def generate_first_slide(
    learner_session_id: str
) -> Dict[str, Any]:
    """
    Generate the first slide content for a learner session
    
    Args:
        learner_session_id: ID of the learner session
        
    Returns:
        Dict containing slide information and generated content
    """
    try:
        logger.info(f"🎯 SLIDE API [REQUEST] Generating first slide for session {learner_session_id}")
        
        # Apply rate limiting
        if not await rate_limiter.is_allowed(f"slide_gen_{learner_session_id}"):
            raise HTTPException(
                status_code=429, 
                detail="Rate limit exceeded for slide generation"
            )
        
        # Initialize slide generation service
        slide_service = SlideGenerationService()
        
        # Generate first slide content
        result = await slide_service.generate_first_slide_content(learner_session_id)
        
        logger.info(f"✅ SLIDE API [SUCCESS] First slide generated for session {learner_session_id}")
        return {
            "success": True,
            "data": result,
            "message": "First slide generated successfully"
        }
        
    except ValueError as e:
        logger.error(f"❌ SLIDE API [NOT_FOUND] {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
        
    except Exception as e:
        logger.error(f"❌ SLIDE API [ERROR] Failed to generate first slide: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate slide content"
        )


@router.post("/simplify/{learner_session_id}", response_model=Dict[str, Any])
async def simplify_slide_content(
    learner_session_id: str,
    request: SimplifySlideRequest
) -> Dict[str, Any]:
    """
    Simplify the content of a slide for better accessibility
    
    Args:
        learner_session_id: ID of the learner session
        request: Request containing current slide content
        
    Returns:
        Dict containing simplified slide content
    """
    try:
        logger.info(f"🎯 SLIDE API [SIMPLIFY] Simplifying content for session {learner_session_id}")
        
        # Apply rate limiting
        if not await rate_limiter.is_allowed(f"slide_simplify_{learner_session_id}"):
            raise HTTPException(
                status_code=429, 
                detail="Rate limit exceeded for slide simplification"
            )
        
        # Validate request
        if not request.current_content or len(request.current_content.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Current content is required and must be at least 10 characters"
            )
        
        # Initialize slide generation service
        slide_service = SlideGenerationService()
        
        # Simplify slide content
        result = await slide_service.simplify_slide_content(
            learner_session_id=learner_session_id,
            current_slide_content=request.current_content
        )
        
        logger.info(f"✅ SLIDE API [SIMPLIFY] Content simplified for session {learner_session_id}")
        return {
            "success": True,
            "data": result,
            "message": "Slide content simplified successfully"
        }
        
    except ValueError as e:
        logger.error(f"❌ SLIDE API [SIMPLIFY_NOT_FOUND] {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
        
    except Exception as e:
        logger.error(f"❌ SLIDE API [SIMPLIFY_ERROR] Failed to simplify slide content: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to simplify slide content"
        )


@router.post("/more-details/{learner_session_id}", response_model=Dict[str, Any])
async def more_details_slide_content(
    learner_session_id: str,
    request: MoreDetailsSlideRequest
) -> Dict[str, Any]:
    """
    Add more technical details to the content of a slide for deeper understanding
    
    Args:
        learner_session_id: ID of the learner session
        request: Request containing current slide content
        
    Returns:
        Dict containing enhanced slide content with more details
    """
    try:
        logger.info(f"🎯 SLIDE API [MORE_DETAILS] Enhancing content for session {learner_session_id}")
        
        # Apply rate limiting
        if not await rate_limiter.is_allowed(f"slide_more_details_{learner_session_id}"):
            raise HTTPException(
                status_code=429, 
                detail="Rate limit exceeded for slide enhancement"
            )
        
        # Validate request
        if not request.current_content or len(request.current_content.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Current content is required and must be at least 10 characters"
            )
        
        # Initialize slide generation service
        slide_service = SlideGenerationService()
        
        # Enhance slide content with more details
        result = await slide_service.more_details_slide_content(
            learner_session_id=learner_session_id,
            current_slide_content=request.current_content
        )
        
        logger.info(f"✅ SLIDE API [MORE_DETAILS] Content enhanced for session {learner_session_id}")
        return {
            "success": True,
            "data": result,
            "message": "Slide content enhanced with more details successfully"
        }
        
    except ValueError as e:
        logger.error(f"❌ SLIDE API [MORE_DETAILS_NOT_FOUND] {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
        
    except Exception as e:
        logger.error(f"❌ SLIDE API [MORE_DETAILS_ERROR] Failed to enhance slide content: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to enhance slide content with more details"
        )


@router.get("/session/{learner_session_id}/current")
async def get_current_slide(learner_session_id: str) -> Dict[str, Any]:
    """
    Get the current slide for a learner session
    
    Args:
        learner_session_id: ID of the learner session
        
    Returns:
        Dict containing current slide information
    """
    try:
        logger.info(f"🎯 SLIDE API [REQUEST] Getting current slide for session {learner_session_id}")
        
        # TODO: Implement getting current slide based on learner_session.current_slide_number
        # For now, return first slide if available
        slide_service = SlideGenerationService()
        result = await slide_service.generate_first_slide_content(learner_session_id)
        
        logger.info(f"✅ SLIDE API [SUCCESS] Current slide retrieved for session {learner_session_id}")
        return {
            "success": True,
            "data": result,
            "message": "Current slide retrieved successfully"
        }
        
    except ValueError as e:
        logger.error(f"❌ SLIDE API [NOT_FOUND] {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
        
    except Exception as e:
        logger.error(f"❌ SLIDE API [ERROR] Failed to get current slide: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve current slide"
        )


@router.get("/health")
async def slide_service_health() -> Dict[str, Any]:
    """Health check for slide generation service"""
    try:
        slide_service = SlideGenerationService()
        stats = slide_service.get_stats()
        
        return {
            "service": "slide_generation",
            "status": "healthy" if stats["vertex_ai_available"] else "degraded",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"❌ SLIDE API [HEALTH] Health check failed: {str(e)}")
        return {
            "service": "slide_generation",
            "status": "unhealthy",
            "error": str(e)
        }