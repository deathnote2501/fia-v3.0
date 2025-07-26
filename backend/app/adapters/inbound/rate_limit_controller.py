"""
FIA v3.0 - Rate Limit Controller
API endpoints for monitoring rate limiting status
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from app.infrastructure.rate_limiter import gemini_rate_limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rate-limit", tags=["Rate Limiting"])


@router.get("/gemini/status")
async def get_gemini_rate_limit_status() -> Dict[str, Any]:
    """
    Get current Gemini API rate limit status
    
    Returns rate limit information including:
    - Requests per minute limit
    - Remaining requests in current window
    - Reset time for rate limit window
    """
    try:
        status = gemini_rate_limiter.get_status()
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        logger.error(f"Error getting rate limit status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error getting rate limit status"
        )


@router.post("/gemini/test")
async def test_gemini_rate_limit() -> Dict[str, Any]:
    """
    Test Gemini API rate limiting by attempting to acquire a slot
    
    This endpoint can be used to verify that rate limiting is working
    without making an actual API call to Gemini
    """
    try:
        # Try to acquire rate limit slot without waiting
        await gemini_rate_limiter.acquire(wait=False)
        
        status = gemini_rate_limiter.get_status()
        return {
            "success": True,
            "message": "Rate limit slot acquired successfully",
            "rate_limit_status": status
        }
        
    except Exception as e:
        status = gemini_rate_limiter.get_status()
        return {
            "success": False,
            "message": f"Rate limit test failed: {str(e)}",
            "rate_limit_status": status
        }