"""
FIA v3.0 - Chart Generation Controller
API endpoints for chart generation functionality
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from uuid import UUID

from app.domain.services.chart_generation_service import ChartGenerationService
from app.domain.schemas.chart_generation import ChartGenerationRequest, ChartGenerationResponse
from app.infrastructure.rate_limiter import SlidingWindowRateLimiter
from app.adapters.repositories.learner_session_repository import LearnerSessionRepository
from app.infrastructure.database import AsyncSessionLocal

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/slides", tags=["chart-generation"])

# Rate limiter for chart generation (costly AI operations)
rate_limiter = SlidingWindowRateLimiter(requests_per_minute=20, window_size_seconds=60)


class ChartGenerationRequestWithContent(ChartGenerationRequest):
    """Extended request model that gets slide content from current slide"""
    pass


@router.post("/{learner_session_id}/generate-chart", response_model=ChartGenerationResponse)
async def generate_chart_for_slide(
    learner_session_id: str,
    request: ChartGenerationRequestWithContent
) -> ChartGenerationResponse:
    """
    Generate chart configurations for slide content
    
    Args:
        learner_session_id: ID of the learner session
        request: Chart generation request with slide content
        
    Returns:
        Chart generation response with configurations
    """
    try:
        logger.info(f"🎯 CHART API [REQUEST] Generating charts for session {learner_session_id}")
        
        # Validate learner session ID format
        try:
            session_uuid = UUID(learner_session_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid learner session ID format"
            )
        
        # Apply rate limiting
        if not await rate_limiter.is_allowed(f"chart_gen_{learner_session_id}"):
            raise HTTPException(
                status_code=429, 
                detail="Rate limit exceeded for chart generation. Please wait before trying again."
            )
        
        # Validate that learner session exists
        async with AsyncSessionLocal() as db_session:
            learner_repo = LearnerSessionRepository(db_session)
            learner_session = await learner_repo.get_by_id(learner_session_id)
            
            if not learner_session:
                raise HTTPException(
                    status_code=404,
                    detail="Learner session not found"
                )
        
        # Validate request content
        if not request.slide_content or len(request.slide_content.strip()) < 20:
            raise HTTPException(
                status_code=400,
                detail="Slide content is required and must be at least 20 characters long"
            )
        
        if len(request.slide_content) > 10000:
            raise HTTPException(
                status_code=400,
                detail="Slide content is too long (maximum 10,000 characters)"
            )
        
        # Initialize chart generation service
        chart_service = ChartGenerationService()
        
        # Check if service is available
        if not chart_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Chart generation service is currently unavailable"
            )
        
        # Generate charts
        result = await chart_service.generate_charts(request)
        
        # Log result
        if result.success:
            logger.info(f"✅ CHART API [SUCCESS] Generated {len(result.charts)} charts for session {learner_session_id}")
        else:
            logger.info(f"⚠️ CHART API [NO_CHARTS] No charts generated for session {learner_session_id}: {result.message}")
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions (already have proper status codes)
        raise
        
    except Exception as e:
        logger.error(f"❌ CHART API [ERROR] Failed to generate charts for session {learner_session_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during chart generation"
        )


@router.post("/{learner_session_id}/generate-chart-from-current", response_model=ChartGenerationResponse)
async def generate_chart_from_current_slide(
    learner_session_id: str,
    max_charts: int = 3
) -> ChartGenerationResponse:
    """
    Generate chart configurations from current slide content of learner session
    
    Args:
        learner_session_id: ID of the learner session
        max_charts: Maximum number of charts to generate (1-5)
        
    Returns:
        Chart generation response with configurations
    """
    try:
        logger.info(f"🎯 CHART API [CURRENT] Generating charts from current slide for session {learner_session_id}")
        
        # Validate learner session ID format
        try:
            session_uuid = UUID(learner_session_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid learner session ID format"
            )
        
        # Validate max_charts parameter
        if max_charts < 1 or max_charts > 5:
            raise HTTPException(
                status_code=400,
                detail="max_charts must be between 1 and 5"
            )
        
        # Apply rate limiting
        if not await rate_limiter.is_allowed(f"chart_gen_{learner_session_id}"):
            raise HTTPException(
                status_code=429, 
                detail="Rate limit exceeded for chart generation. Please wait before trying again."
            )
        
        # Get current slide content from learner session
        async with AsyncSessionLocal() as db_session:
            learner_repo = LearnerSessionRepository(db_session)
            learner_session = await learner_repo.get_by_id(learner_session_id)
            
            if not learner_session:
                raise HTTPException(
                    status_code=404,
                    detail="Learner session not found"
                )
            
            # For this endpoint, we'll need to get the current slide content
            # This would require integration with slide service to get current slide
            # For now, return an informative error
            raise HTTPException(
                status_code=501,
                detail="This endpoint requires integration with slide service. Use /generate-chart with explicit content instead."
            )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"❌ CHART API [CURRENT_ERROR] Failed to generate charts from current slide for session {learner_session_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during chart generation"
        )


@router.get("/chart-generation/health")
async def chart_generation_health() -> Dict[str, Any]:
    """Health check for chart generation service"""
    try:
        chart_service = ChartGenerationService()
        stats = chart_service.get_stats()
        
        return {
            "service": "chart_generation",
            "status": "healthy" if stats["vertex_ai_available"] else "degraded",
            "stats": stats,
            "rate_limit": {
                "requests_per_minute": 20,
                "window_size_seconds": 60
            }
        }
        
    except Exception as e:
        logger.error(f"❌ CHART API [HEALTH] Health check failed: {str(e)}")
        return {
            "service": "chart_generation", 
            "status": "unhealthy",
            "error": str(e)
        }


@router.get("/chart-generation/supported-types")
async def get_supported_chart_types() -> Dict[str, Any]:
    """Get list of supported chart types and color palettes"""
    return {
        "supported_chart_types": [
            {
                "type": "line",
                "name": "Line Chart",
                "description": "Best for showing trends and evolution over time",
                "use_cases": ["time series", "progress tracking", "trend analysis"]
            },
            {
                "type": "pie", 
                "name": "Pie Chart",
                "description": "Best for showing proportions and distributions",
                "use_cases": ["market share", "budget allocation", "demographic breakdown"]
            },
            {
                "type": "radar",
                "name": "Radar Chart", 
                "description": "Best for comparing multiple dimensions/criteria",
                "use_cases": ["skill assessment", "performance comparison", "multi-criteria analysis"]
            }
        ],
        "color_palettes": [
            {
                "name": "default",
                "description": "Bootstrap theme colors",
                "colors": ["#0d6efd", "#198754", "#ffc107", "#dc3545", "#0dcaf0", "#6c757d"]
            },
            {
                "name": "blues",
                "description": "Blue color variations",
                "colors": ["#0d6efd", "#0dcaf0", "#4dabf7", "#1c7ed6", "#339af0", "#6c757d"]
            },
            {
                "name": "success",
                "description": "Green and success colors",
                "colors": ["#198754", "#51cf66", "#37b24d", "#2f9e44", "#0dcaf0", "#0d6efd"]
            }
        ]
    }