"""
FIA v3.0 - Chat History Service
Service for managing chat message history storage using decorator pattern
"""

import logging
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime

from app.domain.entities.chat_message import ChatMessage
from app.domain.ports.repositories import ChatMessageRepositoryPort
from app.domain.services.conversation_service import ConversationService
from app.domain.schemas.conversation import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)


class ChatHistoryService:
    """
    Chat History Service using decorator pattern
    
    This service wraps the ConversationService to automatically store
    chat messages and responses in the database for history purposes.
    Only stores text-based chat messages, excluding Live API and slide button actions.
    """
    
    def __init__(
        self, 
        conversation_service: ConversationService,
        chat_message_repository: ChatMessageRepositoryPort
    ):
        """
        Initialize chat history service
        
        Args:
            conversation_service: Core conversation service to wrap
            chat_message_repository: Repository for storing chat messages
        """
        self.conversation_service = conversation_service
        self.chat_message_repository = chat_message_repository
        logger.info("💬 CHAT_HISTORY [SERVICE] Initialized with decorator pattern")
    
    async def handle_learner_chat_with_history(
        self, 
        chat_request: ChatRequest,
        conversation_type: str = "general"
    ) -> ChatResponse:
        """
        Handle learner chat with automatic message history storage
        
        Args:
            chat_request: Chat request with message and context
            conversation_type: Type of conversation (general, comment, quiz, examples, key-points)
            
        Returns:
            ChatResponse with AI-generated response
        """
        try:
            learner_session_id = chat_request.context.learner_session_id
            current_slide_id = getattr(chat_request.context, 'current_slide_id', None)
            
            logger.info(f"💬 CHAT_HISTORY [START] Processing {conversation_type} chat for learner session {learner_session_id}")
            
            # Store user message/question
            await self._store_user_message(
                learner_session_id=learner_session_id,
                message_content=chat_request.message,
                conversation_type=conversation_type,
                slide_id=current_slide_id
            )
            
            # Process with wrapped conversation service
            chat_response = await self.conversation_service.handle_learner_chat(chat_request)
            
            # Store AI response
            await self._store_ai_response(
                learner_session_id=learner_session_id,
                response_content=chat_response.response,
                conversation_type=conversation_type,
                slide_id=current_slide_id,
                confidence_score=chat_response.confidence_score
            )
            
            logger.info(f"✅ CHAT_HISTORY [SUCCESS] Stored {conversation_type} conversation for learner session {learner_session_id}")
            return chat_response
            
        except Exception as e:
            logger.error(f"❌ CHAT_HISTORY [ERROR] Failed to process chat with history: {str(e)}")
            # Still return the response even if history storage fails
            try:
                return await self.conversation_service.handle_learner_chat(chat_request)
            except Exception as inner_e:
                logger.error(f"❌ CHAT_HISTORY [CRITICAL] Core conversation service also failed: {str(inner_e)}")
                raise inner_e
    
    async def handle_contextual_action_with_history(
        self,
        action_type: str,
        slide_content: str,
        slide_title: str,
        learner_session_id: UUID,
        learner_profile: Dict[str, Any],
        conversation_adapter_method,
        current_slide_id: Optional[int] = None
    ) -> ChatResponse:
        """
        Handle contextual chat actions with automatic history storage
        
        Args:
            action_type: Type of action (comment, quiz, examples, key-points)
            slide_content: Content of the current slide
            slide_title: Title of the current slide
            learner_session_id: ID of the learner session
            learner_profile: Learner profile data
            conversation_adapter_method: Method to call on conversation adapter
            current_slide_id: Current slide number/ID
            
        Returns:
            ChatResponse with AI-generated response
        """
        try:
            logger.info(f"💬 CHAT_HISTORY [CONTEXTUAL] Processing {action_type} action for learner session {learner_session_id}")
            
            # Create a contextual question for history
            contextual_question = f"[{action_type.upper()}] {slide_title}"
            
            # Store the contextual action as a user "question"
            await self._store_user_message(
                learner_session_id=learner_session_id,
                message_content=contextual_question,
                conversation_type=action_type,
                slide_id=current_slide_id
            )
            
            # Call the specific adapter method
            response_data = await conversation_adapter_method(
                slide_content=slide_content,
                slide_title=slide_title,
                learner_profile=learner_profile
            )
            
            # Create ChatResponse from adapter response
            chat_response = ChatResponse(
                response=response_data["response"],
                confidence_score=response_data["confidence_score"],
                conversation_type=action_type,
                suggested_actions=response_data["suggested_actions"],
                related_concepts=response_data["related_concepts"],
                metadata=response_data["metadata"]
            )
            
            # Store AI response
            await self._store_ai_response(
                learner_session_id=learner_session_id,
                response_content=chat_response.response,
                conversation_type=action_type,
                slide_id=current_slide_id,
                confidence_score=chat_response.confidence_score
            )
            
            logger.info(f"✅ CHAT_HISTORY [CONTEXTUAL] Stored {action_type} action for learner session {learner_session_id}")
            return chat_response
            
        except Exception as e:
            logger.error(f"❌ CHAT_HISTORY [CONTEXTUAL_ERROR] Failed to process {action_type} with history: {str(e)}")
            raise e
    
    async def _store_user_message(
        self,
        learner_session_id: UUID,
        message_content: str,
        conversation_type: str,
        slide_id: Optional[int] = None
    ) -> None:
        """Store user message in chat history"""
        try:
            user_message = ChatMessage(
                learner_session_id=learner_session_id,
                message_type="question",
                content=message_content,
                slide_number=slide_id
            )
            
            await self.chat_message_repository.create(user_message)
            logger.debug(f"📝 CHAT_HISTORY [USER_MSG] Stored user message: {message_content[:50]}...")
            
        except Exception as e:
            logger.error(f"❌ CHAT_HISTORY [USER_MSG_ERROR] Failed to store user message: {str(e)}")
            # Don't raise - history storage failure shouldn't block conversation
    
    async def _store_ai_response(
        self,
        learner_session_id: UUID,
        response_content: str,
        conversation_type: str,
        slide_id: Optional[int] = None,
        confidence_score: float = 0.8
    ) -> None:
        """Store AI response in chat history"""
        try:
            ai_message = ChatMessage(
                learner_session_id=learner_session_id,
                message_type="answer",
                content=response_content,
                slide_number=slide_id
            )
            
            await self.chat_message_repository.create(ai_message)
            logger.debug(f"🤖 CHAT_HISTORY [AI_MSG] Stored AI response: {response_content[:50]}...")
            
        except Exception as e:
            logger.error(f"❌ CHAT_HISTORY [AI_MSG_ERROR] Failed to store AI response: {str(e)}")
            # Don't raise - history storage failure shouldn't block conversation
    
    async def get_chat_history(
        self, 
        learner_session_id: UUID, 
        slide_number: Optional[int] = None
    ) -> list[ChatMessage]:
        """
        Get chat history for a learner session
        
        Args:
            learner_session_id: ID of the learner session
            slide_number: Optional slide number filter
            
        Returns:
            List of chat messages ordered by creation time
        """
        try:
            if slide_number is not None:
                messages = await self.chat_message_repository.get_by_learner_session_and_slide(
                    learner_session_id, slide_number
                )
            else:
                messages = await self.chat_message_repository.get_by_learner_session_id(
                    learner_session_id
                )
            
            logger.info(f"📚 CHAT_HISTORY [RETRIEVE] Retrieved {len(messages)} messages for learner session {learner_session_id}")
            return messages
            
        except Exception as e:
            logger.error(f"❌ CHAT_HISTORY [RETRIEVE_ERROR] Failed to get chat history: {str(e)}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            "service": "chat_history",
            "decorator_pattern": True,
            "wrapped_service": "conversation_service",
            "storage_types": ["text_chat", "contextual_actions"],
            "excluded_types": ["live_api", "slide_buttons"]
        }