"""
FIA v3.0 - Conversation Controller
FastAPI routes for AI conversation service with learners
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Dict, Any
import logging

from app.infrastructure.database import get_database_session
from app.domain.schemas.conversation import (
    ChatRequest, 
    ChatResponse, 
    HintRequest, 
    ConceptExplanationRequest,
    ConversationMetrics
)
from app.domain.services.conversation_service import ConversationService
from app.adapters.outbound.conversation_adapter import ConversationAdapter
from app.adapters.repositories.learner_session_repository import LearnerSessionRepository
from app.adapters.repositories.training_slide_repository import TrainingSlideRepository

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["conversation"])


# ============================================================================
# LEARNER CONVERSATION ROUTES (public - no auth required)
# ============================================================================

@router.post("/api/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_with_ai_trainer(
    chat_request: ChatRequest,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Handle chat conversation between learner and AI trainer
    
    This endpoint allows learners to chat with the AI trainer during their training session.
    The AI trainer responds based on the current slide context and learner profile.
    """
    try:
        logger.info(f"🤖 CONVERSATION [CHAT] Processing chat for learner session {chat_request.context.learner_session_id}")
        
        # Validate learner session exists
        learner_repo = LearnerSessionRepository(db)
        learner_session = await learner_repo.get_by_id(chat_request.context.learner_session_id)
        
        if not learner_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Learner session not found"
            )
        
        # Initialize conversation service
        conversation_adapter = ConversationAdapter()
        conversation_service = ConversationService(conversation_adapter)
        
        # Process chat request
        chat_response = await conversation_service.handle_learner_chat(chat_request)
        
        logger.info(f"✅ CONVERSATION [CHAT] Successfully processed chat for learner session {chat_request.context.learner_session_id}")
        return chat_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ CONVERSATION [CHAT] Failed to process chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Conversation service temporarily unavailable"
        )


@router.post("/api/chat/hint", response_model=str, status_code=status.HTTP_200_OK)
async def get_contextual_hint(
    hint_request: HintRequest,
    learner_session_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Generate contextual hint for learner question
    
    This endpoint provides intelligent hints to help learners understand concepts
    without giving away complete answers.
    """
    try:
        logger.info(f"🤖 CONVERSATION [HINT] Generating hint for learner session {learner_session_id}")
        
        # Validate learner session exists
        learner_repo = LearnerSessionRepository(db)
        learner_session = await learner_repo.get_by_id(learner_session_id)
        
        if not learner_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Learner session not found"
            )
        
        # Initialize conversation service
        conversation_adapter = ConversationAdapter()
        conversation_service = ConversationService(conversation_adapter)
        
        # Generate hint
        hint = await conversation_service.generate_contextual_hint(hint_request)
        
        logger.info(f"✅ CONVERSATION [HINT] Successfully generated hint for learner session {learner_session_id}")
        return hint
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ CONVERSATION [HINT] Failed to generate hint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Hint generation service temporarily unavailable"
        )


@router.post("/api/chat/explain", response_model=str, status_code=status.HTTP_200_OK)
async def explain_concept(
    explanation_request: ConceptExplanationRequest,
    learner_session_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Explain a specific concept to the learner
    
    This endpoint provides detailed explanations of concepts adapted to the
    learner's profile and experience level.
    """
    try:
        logger.info(f"🤖 CONVERSATION [EXPLAIN] Explaining concept '{explanation_request.concept}' for learner session {learner_session_id}")
        
        # Validate learner session exists
        learner_repo = LearnerSessionRepository(db)
        learner_session = await learner_repo.get_by_id(learner_session_id)
        
        if not learner_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Learner session not found"
            )
        
        # Initialize conversation service
        conversation_adapter = ConversationAdapter()
        conversation_service = ConversationService(conversation_adapter)
        
        # Generate explanation  
        explanation = await conversation_service.explain_concept(explanation_request)
        
        logger.info(f"✅ CONVERSATION [EXPLAIN] Successfully explained concept '{explanation_request.concept}' for learner session {learner_session_id}")
        return explanation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ CONVERSATION [EXPLAIN] Failed to explain concept: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Concept explanation service temporarily unavailable"
        )


@router.get("/api/chat/metrics/{learner_session_id}", response_model=ConversationMetrics, status_code=status.HTTP_200_OK)
async def get_conversation_metrics(
    learner_session_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Get conversation metrics for a learner session
    
    This endpoint provides analytics about the learner's conversation patterns,
    engagement, and interaction history.
    """
    try:
        logger.info(f"🤖 CONVERSATION [METRICS] Getting metrics for learner session {learner_session_id}")
        
        # Validate learner session exists
        learner_repo = LearnerSessionRepository(db)
        learner_session = await learner_repo.get_by_id(learner_session_id)
        
        if not learner_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Learner session not found"
            )
        
        # Initialize conversation service
        conversation_adapter = ConversationAdapter()
        conversation_service = ConversationService(conversation_adapter)
        
        # Get conversation history (simplified - would need actual implementation)
        conversation_history = []  # TODO: Implement conversation history retrieval
        
        # Calculate metrics
        metrics = await conversation_service.get_conversation_metrics(
            learner_session_id, conversation_history
        )
        
        logger.info(f"✅ CONVERSATION [METRICS] Successfully retrieved metrics for learner session {learner_session_id}")
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ CONVERSATION [METRICS] Failed to get metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Metrics service temporarily unavailable"
        )


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/api/chat/health", status_code=status.HTTP_200_OK)
async def conversation_health_check():
    """Health check for conversation service"""
    try:
        # Test if VertexAI adapter is available
        conversation_adapter = ConversationAdapter()
        is_available = conversation_adapter.vertex_adapter.is_available()
        
        return {
            "status": "healthy" if is_available else "degraded",
            "vertex_ai_available": is_available,
            "service": "conversation",
            "version": "3.0"
        }
    except Exception as e:
        logger.error(f"❌ CONVERSATION [HEALTH] Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "vertex_ai_available": False,
            "service": "conversation",
            "version": "3.0",
            "error": str(e)
        }