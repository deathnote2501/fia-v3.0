"""
FIA v3.0 - Token Usage Controller
FastAPI routes for token usage tracking and analytics
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from app.infrastructure.database import get_database_session
from app.domain.schemas.token_usage import (
    TokenUsageResponse,
    ServiceTypeAnalyticsResponse,
    TokenUsageHealthResponse
)
from app.domain.services.token_usage_service import TokenUsageService
from app.adapters.outbound.logger_adapter import LoggerAdapter

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["token-usage"])


# ============================================================================
# DEPENDENCY INJECTION FUNCTIONS
# ============================================================================

async def get_token_usage_service(
    db: AsyncSession = Depends(get_database_session)
) -> TokenUsageService:
    """
    Dependency injection for TokenUsageService
    
    Creates TokenUsageService with proper dependency injection following
    hexagonal architecture principles.
    """
    logger_adapter = LoggerAdapter()
    return TokenUsageService(logger_adapter)


# ============================================================================
# TOKEN USAGE ENDPOINTS
# ============================================================================

@router.get(
    "/api/sessions/{learner_session_id}/token-usage",
    response_model=TokenUsageResponse,
    status_code=status.HTTP_200_OK
)
async def get_session_token_usage(
    learner_session_id: str,
    start_time: Optional[str] = Query(None, description="Start time filter (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time filter (ISO format)"),
    service: TokenUsageService = Depends(get_token_usage_service)
):
    """
    Get comprehensive token usage statistics for a learner session
    
    Returns detailed token consumption breakdown including:
    - Total tokens (input/output) across all AI services
    - Service type breakdown (plan generation, conversation, TTS, etc.)
    - Recent AI calls timeline
    - Cost estimation based on current Gemini pricing
    - Usage insights and optimization recommendations
    
    Args:
        learner_session_id: ID of the learner session to analyze
        start_time: Optional start time filter (ISO format: YYYY-MM-DDTHH:MM:SSZ)
        end_time: Optional end time filter (ISO format: YYYY-MM-DDTHH:MM:SSZ)
        
    Returns:
        TokenUsageResponse with comprehensive usage statistics
    """
    try:
        logger.info(f"🪙 TOKEN_USAGE_CONTROLLER [GET_USAGE] Processing request for session: {learner_session_id}")
        
        # Validate session ID format (basic validation)
        if not learner_session_id or len(learner_session_id.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Learner session ID is required and cannot be empty"
            )
        
        # Get comprehensive token usage statistics
        usage_stats = await service.get_session_token_stats(
            learner_session_id=learner_session_id,
            start_time=start_time,
            end_time=end_time
        )
        
        # Check if service returned error data
        if "error" in usage_stats:
            logger.warning(f"⚠️ TOKEN_USAGE_CONTROLLER [GET_USAGE] Service returned error for session {learner_session_id}: {usage_stats['error']}")
            # Return error response but with 200 status (partial data available)
            return TokenUsageResponse(**usage_stats)
        
        logger.info(f"✅ TOKEN_USAGE_CONTROLLER [GET_USAGE] Successfully retrieved token usage for session {learner_session_id}")
        return TokenUsageResponse(**usage_stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ TOKEN_USAGE_CONTROLLER [GET_USAGE] Failed to retrieve token usage for session {learner_session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token usage service temporarily unavailable"
        )


@router.get(
    "/api/sessions/{learner_session_id}/token-usage/analytics",
    response_model=ServiceTypeAnalyticsResponse,
    status_code=status.HTTP_200_OK
)
async def get_service_type_analytics(
    learner_session_id: str,
    service: TokenUsageService = Depends(get_token_usage_service)
):
    """
    Get detailed analytics broken down by AI service type
    
    Provides in-depth analysis of token usage patterns across different
    AI services (plan generation, conversation, TTS, image generation, etc.)
    with insights and optimization recommendations.
    
    Args:
        learner_session_id: ID of the learner session to analyze
        
    Returns:
        ServiceTypeAnalyticsResponse with service-specific analytics
    """
    try:
        logger.info(f"🪙 TOKEN_USAGE_CONTROLLER [ANALYTICS] Processing analytics request for session: {learner_session_id}")
        
        # Validate session ID format
        if not learner_session_id or len(learner_session_id.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Learner session ID is required and cannot be empty"
            )
        
        # Get service type analytics
        analytics = await service.get_service_type_analytics(learner_session_id)
        
        # Check if service returned error data
        if "error" in analytics:
            logger.warning(f"⚠️ TOKEN_USAGE_CONTROLLER [ANALYTICS] Service returned error for session {learner_session_id}: {analytics['error']}")
            # Return error response but with 200 status (partial data available)
            return ServiceTypeAnalyticsResponse(**analytics)
        
        logger.info(f"✅ TOKEN_USAGE_CONTROLLER [ANALYTICS] Successfully generated analytics for session {learner_session_id}")
        return ServiceTypeAnalyticsResponse(**analytics)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ TOKEN_USAGE_CONTROLLER [ANALYTICS] Failed to generate analytics for session {learner_session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analytics service temporarily unavailable"
        )


@router.get(
    "/api/token-usage/health",
    response_model=TokenUsageHealthResponse,
    status_code=status.HTTP_200_OK
)
async def token_usage_health_check(
    service: TokenUsageService = Depends(get_token_usage_service)
):
    """
    Health check for token usage tracking service
    
    Verifies that the token usage service and its dependencies
    (logger adapter, log parsing) are functioning correctly.
    
    Returns:
        TokenUsageHealthResponse with service health status
    """
    try:
        logger.info("🪙 TOKEN_USAGE_CONTROLLER [HEALTH] Performing health check")
        
        # Test logger adapter availability
        logger_adapter_available = True
        try:
            # Simple test to verify logger adapter is functional
            test_result = await service.logger_adapter.get_token_usage_by_session(
                learner_session_id="health-check-test"
            )
            logger_adapter_available = test_result is not None
        except Exception as e:
            logger.warning(f"⚠️ TOKEN_USAGE_CONTROLLER [HEALTH] Logger adapter test failed: {str(e)}")
            logger_adapter_available = False
        
        # Determine overall health status
        if logger_adapter_available:
            status_value = "healthy"
            error_message = None
        else:
            status_value = "degraded"
            error_message = "Logger adapter is not fully functional"
        
        health_response = TokenUsageHealthResponse(
            status=status_value,
            logger_adapter_available=logger_adapter_available,
            error=error_message
        )
        
        logger.info(f"✅ TOKEN_USAGE_CONTROLLER [HEALTH] Health check completed - Status: {status_value}")
        return health_response
        
    except Exception as e:
        logger.error(f"❌ TOKEN_USAGE_CONTROLLER [HEALTH] Health check failed: {str(e)}")
        return TokenUsageHealthResponse(
            status="unhealthy",
            logger_adapter_available=False,
            error=str(e)
        )


# ============================================================================
# UTILITY ENDPOINTS (for testing and debugging)
# ============================================================================

@router.get(
    "/api/token-usage/test/{learner_session_id}",
    status_code=status.HTTP_200_OK
)
async def test_token_usage_parsing(
    learner_session_id: str,
    service: TokenUsageService = Depends(get_token_usage_service)
):
    """
    Test endpoint for validating token usage parsing logic
    
    This endpoint is useful for testing and debugging the token usage
    tracking system without affecting production data.
    
    Args:
        learner_session_id: Test session ID
        
    Returns:
        Basic test results
    """
    try:
        logger.info(f"🪙 TOKEN_USAGE_CONTROLLER [TEST] Running test for session: {learner_session_id}")
        
        # Test basic functionality
        usage_stats = await service.get_session_token_stats(learner_session_id)
        analytics = await service.get_service_type_analytics(learner_session_id)
        
        test_results = {
            "session_id": learner_session_id,
            "test_status": "passed",
            "usage_stats_available": "error" not in usage_stats,
            "analytics_available": "error" not in analytics,
            "total_tokens_found": usage_stats.get("summary", {}).get("total_tokens", 0),
            "service_types_detected": len(analytics.get("service_types", {})),
            "timestamp": usage_stats.get("query_time")
        }
        
        logger.info(f"✅ TOKEN_USAGE_CONTROLLER [TEST] Test completed successfully for session {learner_session_id}")
        return test_results
        
    except Exception as e:
        logger.error(f"❌ TOKEN_USAGE_CONTROLLER [TEST] Test failed for session {learner_session_id}: {str(e)}")
        return {
            "session_id": learner_session_id,
            "test_status": "failed",
            "error": str(e),
            "usage_stats_available": False,
            "analytics_available": False
        }