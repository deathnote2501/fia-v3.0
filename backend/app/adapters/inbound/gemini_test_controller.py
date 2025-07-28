"""
FIA v3.0 - Gemini Test Controller
API endpoints for testing Gemini 2.0 Flash integration
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from app.adapters.outbound.gemini_adapter import GeminiAdapter
from app.infrastructure.rate_limiter import RateLimitExceeded

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/gemini-test", tags=["Gemini Testing"])


def get_gemini_adapter() -> GeminiAdapter:
    """Dependency to get Gemini adapter instance"""
    return GeminiAdapter()


@router.post("/health-check")
async def gemini_health_check(
    gemini_adapter: GeminiAdapter = Depends(get_gemini_adapter)
) -> Dict[str, Any]:
    """
    Test basic Gemini 2.0 Flash connectivity
    
    Performs a simple test to verify:
    - Gemini 2.0 Flash model is accessible
    - Vertex AI authentication is working
    - Rate limiting is functional
    """
    try:
        test_profile = {
            "email": "test@example.com",
            "experience_level": "beginner",
            "learning_style": "visual",
            "job_position": "developer",
            "activity_sector": "technology",
            "country": "France",
            "language": "en"
        }
        
        test_content = "Test training content for health check"
        
        # This will test rate limiting + Gemini 2.0 Flash
        result = await gemini_adapter.generate_training_plan(
            learner_profile=test_profile,
            training_content=test_content
        )
        
        return {
            "success": True,
            "message": "Gemini 2.0 Flash is working correctly",
            "model_used": gemini_adapter.model_name,
            "plan_generated": bool(result and "stages" in result),
            "stages_count": len(result.get("stages", [])) if result else 0
        }
        
    except RateLimitExceeded as e:
        return {
            "success": False,
            "message": f"Rate limit exceeded: {str(e)}",
            "model_used": gemini_adapter.model_name,
            "rate_limit_active": True
        }
        
    except Exception as e:
        logger.error(f"Gemini health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": f"Gemini health check failed: {str(e)}",
                "model_used": gemini_adapter.model_name
            }
        )


@router.post("/slide-generation-test")
async def test_slide_generation(
    gemini_adapter: GeminiAdapter = Depends(get_gemini_adapter)
) -> Dict[str, Any]:
    """
    Test slide content generation with Gemini 2.0 Flash
    """
    try:
        test_profile = {
            "email": "test@example.com",
            "experience_level": "intermediate",
            "learning_style": "reading",
            "job_position": "manager",
            "activity_sector": "education",
            "country": "France",
            "language": "en"
        }
        
        result = await gemini_adapter.generate_slide_content(
            slide_title="Introduction to AI",
            module_context="Fundamentals of Artificial Intelligence",
            learner_profile=test_profile
        )
        
        return {
            "success": True,
            "message": "Slide generation test successful",
            "model_used": gemini_adapter.model_name,
            "slide_generated": bool(result and "title" in result),
            "content_length": len(result.get("content", "")) if result else 0
        }
        
    except RateLimitExceeded as e:
        return {
            "success": False,
            "message": f"Rate limit exceeded during slide test: {str(e)}",
            "model_used": gemini_adapter.model_name
        }
        
    except Exception as e:
        logger.error(f"Slide generation test failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": f"Slide generation test failed: {str(e)}",
                "model_used": gemini_adapter.model_name
            }
        )


@router.post("/chat-test")
async def test_chat_functionality(
    gemini_adapter: GeminiAdapter = Depends(get_gemini_adapter)
) -> Dict[str, Any]:
    """
    Test chat functionality with Gemini 2.0 Flash
    """
    try:
        conversation_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hello! How can I help you with your training?"}
        ]
        
        from uuid import uuid4
        result = await gemini_adapter.chat_with_learner(
            message="Can you explain what AI is?",
            conversation_history=conversation_history,
            training_context="Introduction to Artificial Intelligence course",
            learner_profile={"experience_level": "beginner", "learning_style": "visual"},
            learner_session_id=uuid4()
        )
        
        return {
            "success": True,
            "message": "Chat test successful",
            "model_used": gemini_adapter.model_name,
            "response_generated": bool(result),
            "response_length": len(result) if result else 0
        }
        
    except RateLimitExceeded as e:
        return {
            "success": False,
            "message": f"Rate limit exceeded during chat test: {str(e)}",
            "model_used": gemini_adapter.model_name
        }
        
    except Exception as e:
        logger.error(f"Chat test failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": f"Chat test failed: {str(e)}",
                "model_used": gemini_adapter.model_name
            }
        )