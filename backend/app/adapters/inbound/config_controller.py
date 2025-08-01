"""
FIA v3.0 - Configuration Controller
Exposes necessary configuration values for frontend components
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.infrastructure.settings import settings
from app.infrastructure.database import get_database_session
from app.adapters.repositories.learner_session_repository import LearnerSessionRepository
from app.adapters.repositories.training_slide_repository import TrainingSlideRepository
from app.services.conversation_prompt_builder import ConversationPromptBuilder

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/config", tags=["configuration"])


class GeminiKeyResponse(BaseModel):
    """Response model for Gemini API key"""
    api_key: str


class LiveContextResponse(BaseModel):
    """Response model for Live API context data"""
    learner_session_id: str
    slide_title: Optional[str] = None
    slide_content: Optional[str] = None
    learner_profile: Dict[str, Any]
    system_instruction: str
    training_context: Optional[str] = None


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


@router.get("/live-context/{learner_session_id}", response_model=LiveContextResponse)
async def get_live_context(
    learner_session_id: str,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Get contextual information for Gemini Live API
    
    Args:
        learner_session_id: ID of the learner session
        db: Database session
        
    Returns:
        LiveContextResponse: Context data including slide, profile, and system instruction
        
    Raises:
        HTTPException: If session not found or error retrieving context
    """
    try:
        logger.info(f"🎯 CONFIG [LIVE_CONTEXT] Getting context for session {learner_session_id}")
        
        # Initialize repositories
        learner_session_repo = LearnerSessionRepository(db)
        slide_repo = TrainingSlideRepository(db)
        prompt_builder = ConversationPromptBuilder()
        
        # Get learner session
        try:
            session_uuid = UUID(learner_session_id)
        except ValueError:
            logger.error(f"❌ CONFIG [LIVE_CONTEXT] Invalid UUID format: {learner_session_id}")
            raise HTTPException(
                status_code=400,
                detail="Invalid learner session ID format"
            )
        
        learner_session = await learner_session_repo.get_by_id(session_uuid)
        if not learner_session:
            logger.error(f"❌ CONFIG [LIVE_CONTEXT] Session not found: {learner_session_id}")
            raise HTTPException(
                status_code=404,
                detail="Learner session not found"
            )
        
        # Get current slide information from learner_training_plans
        slide_title = None
        slide_content = None
        training_context = None
        
        try:
            # Récupérer le current_slide_id depuis learner_training_plans
            from sqlalchemy import text
            result = await db.execute(text("""
                SELECT ts.title, ts.content 
                FROM learner_training_plans ltp 
                JOIN training_slides ts ON ltp.current_slide_id = ts.id 
                WHERE ltp.learner_session_id = :session_id
            """), {"session_id": session_uuid})
            
            current_slide = result.fetchone()
            if current_slide:
                slide_title = current_slide[0]
                slide_content = current_slide[1]
                logger.info(f"✅ CONFIG [LIVE_CONTEXT] Current slide found: {slide_title}")
            else:
                logger.warning(f"⚠️ CONFIG [LIVE_CONTEXT] No current slide found in learner_training_plans for session {session_uuid}")
                
        except Exception as e:
            logger.warning(f"⚠️ CONFIG [LIVE_CONTEXT] Could not retrieve current slide: {e}")
        
        # Prepare learner profile data
        learner_profile = {
            "niveau": getattr(learner_session, 'experience_level', 'beginner'),
            "poste_et_secteur": getattr(learner_session, 'job_and_sector', None) or 
                              getattr(learner_session, 'job_position', 'professionnel'),
            "objectifs": getattr(learner_session, 'objectives', 'développer mes compétences'),
            "langue": getattr(learner_session, 'language', 'fr'),
            "enriched_profile": getattr(learner_session, 'enriched_profile', None)
        }
        
        # Build system instruction using ConversationPromptBuilder logic
        system_instruction = prompt_builder._build_live_system_instruction(
            slide_title=slide_title,
            slide_content=slide_content,
            learner_profile=learner_session,
            training_context=training_context
        )
        
        logger.info(f"✅ CONFIG [LIVE_CONTEXT] Context built for session {learner_session_id}")
        
        return LiveContextResponse(
            learner_session_id=learner_session_id,
            slide_title=slide_title,
            slide_content=slide_content,
            learner_profile=learner_profile,
            system_instruction=system_instruction,
            training_context=training_context
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ CONFIG [LIVE_CONTEXT] Error retrieving context: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve Live API context"
        )