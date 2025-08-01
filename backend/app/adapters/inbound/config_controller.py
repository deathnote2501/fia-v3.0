"""
FIA v3.0 - Configuration Controller
Exposes necessary configuration values for frontend components
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.infrastructure.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/config", tags=["configuration"])


class GeminiKeyResponse(BaseModel):
    """Response model for Gemini API key"""
    api_key: str


@router.get("/gemini-key", response_model=GeminiKeyResponse)
async def get_gemini_api_key():
    """
    Get Gemini API key for Live API functionality
    
    Returns:
        GeminiKeyResponse: The API key from environment variables
        
    Raises:
        HTTPException: If API key is not configured
    """
    try:
        if not settings.gemini_api_key:
            logger.error("Gemini API key not configured in environment variables")
            raise HTTPException(
                status_code=500,
                detail="Gemini API key not configured. Please check environment variables."
            )
        
        logger.info("✅ Gemini API key requested for Live API functionality")
        
        return GeminiKeyResponse(api_key=settings.gemini_api_key)
        
    except Exception as e:
        logger.error(f"❌ Error retrieving Gemini API key: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve API configuration"
        )