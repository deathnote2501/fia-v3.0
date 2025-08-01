"""
FIA v3.0 - Conversation Controller
FastAPI routes for AI conversation service with learners
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Dict, Any
import logging
import traceback

from app.infrastructure.database import get_database_session
from app.domain.schemas.conversation import (
    ChatRequest, 
    ChatResponse, 
    HintRequest, 
    ConceptExplanationRequest,
    ConversationMetrics
)
from pydantic import BaseModel
from app.domain.services.conversation_service import ConversationService
from app.domain.services.chat_history_service import ChatHistoryService
from app.adapters.outbound.conversation_adapter import ConversationAdapter
from app.adapters.repositories.learner_session_repository import LearnerSessionRepository
from app.adapters.repositories.training_slide_repository import TrainingSlideRepository
from app.adapters.repositories.chat_message_repository import ChatMessageRepository

# Configure logging
logger = logging.getLogger(__name__)

# Initialize GeminiCallLogger for conversation endpoints
try:
    from app.infrastructure.gemini_call_logger import gemini_call_logger
except ImportError as e:
    logger.error(f"❌ CONVERSATION_CONTROLLER [INIT] GeminiCallLogger import failed: {e}")

router = APIRouter(tags=["conversation"])


# ============================================================================
# PYDANTIC MODELS FOR CONTEXTUAL CHAT ACTIONS
# ============================================================================

class SlideContextRequest(BaseModel):
    """Request model for slide-contextual chat actions"""
    learner_session_id: UUID
    slide_content: str
    slide_title: str


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
        
        # Initialize conversation services with chat history
        conversation_adapter = ConversationAdapter()
        conversation_service = ConversationService(conversation_adapter)
        chat_message_repo = ChatMessageRepository(db)
        chat_history_service = ChatHistoryService(conversation_service, chat_message_repo)
        
        # Process chat request with automatic history storage
        chat_response = await chat_history_service.handle_learner_chat_with_history(
            chat_request=chat_request,
            conversation_type="general"
        )
        
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
# CONTEXTUAL CHAT ACTION ROUTES (public - no auth required)
# ============================================================================

async def _handle_contextual_action_with_history(
    request: SlideContextRequest,
    action_type: str,
    adapter_method_name: str,
    db: AsyncSession
) -> ChatResponse:
    """
    Helper function to handle contextual chat actions with automatic history storage
    
    Args:
        request: Slide context request
        action_type: Type of action (comment, quiz, examples, key-points)
        adapter_method_name: Name of the method to call on conversation adapter
        db: Database session
        
    Returns:
        ChatResponse with AI-generated response
    """
    # Validate learner session exists
    learner_repo = LearnerSessionRepository(db)
    learner_session = await learner_repo.get_by_id(request.learner_session_id)
    
    if not learner_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner session not found"
        )
    
    # Prepare learner profile
    learner_profile = {
        "experience_level": learner_session.experience_level,
        "learning_style": learner_session.learning_style,
        "job_position": learner_session.job_position,
        "activity_sector": learner_session.activity_sector,
        "country": learner_session.country,
        "language": learner_session.language
    }
    
    # Initialize services with chat history
    conversation_adapter = ConversationAdapter()
    conversation_service = ConversationService(conversation_adapter)
    chat_message_repo = ChatMessageRepository(db)
    chat_history_service = ChatHistoryService(conversation_service, chat_message_repo)
    
    # Get the specific adapter method
    adapter_method = getattr(conversation_adapter, adapter_method_name)
    
    # Handle contextual action with automatic history storage
    chat_response = await chat_history_service.handle_contextual_action_with_history(
        action_type=action_type,
        slide_content=request.slide_content,
        slide_title=request.slide_title,
        learner_session_id=request.learner_session_id,
        learner_profile=learner_profile,
        conversation_adapter_method=adapter_method,
        current_slide_id=None  # Could be extracted from request if available
    )
    
    return chat_response

@router.post("/api/chat/comment", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def comment_slide(
    request: SlideContextRequest,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Generate AI trainer's comment about the current slide
    
    This endpoint provides insightful commentary about the slide content,
    explaining its importance and relevance to the learner's profile.
    """
    try:
        logger.info(f"🤖 CONVERSATION [COMMENT] Generating comment for learner session {request.learner_session_id}")
        
        chat_response = await _handle_contextual_action_with_history(
            request=request,
            action_type="comment",
            adapter_method_name="comment_slide",
            db=db
        )
        
        logger.info(f"✅ CONVERSATION [COMMENT] Successfully generated comment for learner session {request.learner_session_id}")
        return chat_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ CONVERSATION [COMMENT] Failed to generate comment: {str(e)}")
        logger.error(f"❌ CONVERSATION [COMMENT] Exception type: {type(e).__name__}")
        logger.error(f"❌ CONVERSATION [COMMENT] Request data: slide_title='{request.slide_title}', learner_session_id={request.learner_session_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Comment generation service temporarily unavailable"
        )


@router.post("/api/chat/quiz", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def generate_quiz(
    request: SlideContextRequest,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Generate a quiz based on the current slide to evaluate comprehension
    
    This endpoint creates 2-3 quiz questions adapted to the learner's
    experience level to test their understanding of the slide content.
    """
    try:
        logger.info(f"🤖 CONVERSATION [QUIZ] Generating quiz for learner session {request.learner_session_id}")
        
        chat_response = await _handle_contextual_action_with_history(
            request=request,
            action_type="quiz",
            adapter_method_name="generate_quiz",
            db=db
        )
        
        logger.info(f"✅ CONVERSATION [QUIZ] Successfully generated quiz for learner session {request.learner_session_id}")
        return chat_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ CONVERSATION [QUIZ] Failed to generate quiz: {str(e)}")
        logger.error(f"❌ CONVERSATION [QUIZ] Exception type: {type(e).__name__}")
        logger.error(f"❌ CONVERSATION [QUIZ] Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Quiz generation service temporarily unavailable"
        )


@router.post("/api/chat/examples", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def provide_examples(
    request: SlideContextRequest,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Provide practical examples to illustrate the slide content
    
    This endpoint generates concrete, practical examples that are relevant
    to the learner's job position and activity sector.
    """
    try:
        logger.info(f"🤖 CONVERSATION [EXAMPLES] Generating examples for learner session {request.learner_session_id}")
        
        chat_response = await _handle_contextual_action_with_history(
            request=request,
            action_type="examples",
            adapter_method_name="provide_examples",
            db=db
        )
        
        logger.info(f"✅ CONVERSATION [EXAMPLES] Successfully generated examples for learner session {request.learner_session_id}")
        return chat_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ CONVERSATION [EXAMPLES] Failed to generate examples: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Examples generation service temporarily unavailable"
        )


@router.post("/api/chat/key-points", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def extract_key_points(
    request: SlideContextRequest,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Extract the 1-3 most important points to remember from the slide
    
    This endpoint identifies the crucial takeaways from the slide content,
    prioritized based on the learner's profile and learning objectives.
    """
    try:
        logger.info(f"🤖 CONVERSATION [KEY_POINTS] Extracting key points for learner session {request.learner_session_id}")
        
        chat_response = await _handle_contextual_action_with_history(
            request=request,
            action_type="key-points",
            adapter_method_name="extract_key_points",
            db=db
        )
        
        logger.info(f"✅ CONVERSATION [KEY_POINTS] Successfully extracted key points for learner session {request.learner_session_id}")
        return chat_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ CONVERSATION [KEY_POINTS] Failed to extract key points: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Key points extraction service temporarily unavailable"
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