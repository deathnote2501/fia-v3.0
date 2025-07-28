"""
FIA v3.0 - Conversation Service
Domain service for managing AI conversations with learners
"""

import logging
from typing import Dict, Any, List
from uuid import UUID

from app.domain.ports.outbound_ports import ConversationServicePort
from app.domain.schemas.conversation import (
    ChatRequest, 
    ChatResponse, 
    HintRequest, 
    ConceptExplanationRequest,
    ConversationMetrics
)

logger = logging.getLogger(__name__)


class ConversationService:
    """Domain service for managing learner conversations"""
    
    def __init__(self, conversation_port: ConversationServicePort):
        """Initialize conversation service with port dependency"""
        self.conversation_port = conversation_port
        
    async def handle_learner_chat(
        self, 
        chat_request: ChatRequest
    ) -> ChatResponse:
        """
        Handle a chat message from a learner
        
        Args:
            chat_request: Chat request with message and context
            
        Returns:
            ChatResponse with AI-generated response
        """
        try:
            logger.info(f"Processing chat for learner session {chat_request.context.learner_session_id}")
            
            # Convert context to dict format for the port
            conversation_history = [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp if isinstance(msg.timestamp, str) else msg.timestamp.isoformat() if msg.timestamp else "",
                    "metadata": msg.metadata or {}
                }
                for msg in chat_request.context.conversation_history
            ]
            
            # Call the outbound port
            response_data = await self.conversation_port.chat_with_learner(
                message=chat_request.message,
                conversation_history=conversation_history,
                training_context=chat_request.context.training_content,
                learner_profile=chat_request.context.learner_profile,
                learner_session_id=chat_request.context.learner_session_id
            )
            
            # Convert port response to domain schema
            chat_response = ChatResponse(
                response=response_data.get("response", ""),
                confidence_score=response_data.get("confidence_score", 0.8),
                conversation_type=chat_request.conversation_type,
                suggested_actions=response_data.get("suggested_actions", []),
                related_concepts=response_data.get("related_concepts", []),
                metadata=response_data.get("metadata", {})
            )
            
            logger.info(f"Generated chat response with confidence {chat_response.confidence_score}")
            return chat_response
            
        except Exception as e:
            logger.error(f"Failed to process chat request: {str(e)}")
            raise Exception("Conversation service temporarily unavailable")
    
    async def generate_contextual_hint(
        self, 
        hint_request: HintRequest
    ) -> str:
        """
        Generate a contextual hint for learner
        
        Args:
            hint_request: Request for hint with context
            
        Returns:
            Generated hint text
        """
        try:
            logger.info(f"Generating hint for slide content")
            
            hint_response = await self.conversation_port.generate_contextual_hint(
                current_slide=hint_request.current_slide,
                learner_question=hint_request.learner_question,
                learner_profile=hint_request.learner_profile
            )
            
            logger.info("Successfully generated contextual hint")
            return hint_response
            
        except Exception as e:
            logger.error(f"Failed to generate hint: {str(e)}")
            raise Exception("Hint generation service temporarily unavailable")
    
    async def explain_concept(
        self, 
        explanation_request: ConceptExplanationRequest
    ) -> str:
        """
        Explain a specific concept to the learner
        
        Args:
            explanation_request: Request for concept explanation
            
        Returns:
            Generated explanation text
        """
        try:
            logger.info(f"Explaining concept: {explanation_request.concept}")
            
            explanation = await self.conversation_port.explain_concept(
                concept=explanation_request.concept,
                training_context=explanation_request.training_context,
                learner_profile=explanation_request.learner_profile
            )
            
            logger.info(f"Successfully explained concept: {explanation_request.concept}")
            return explanation
            
        except Exception as e:
            logger.error(f"Failed to explain concept: {str(e)}")
            raise Exception("Concept explanation service temporarily unavailable")
    
    async def get_conversation_metrics(
        self, 
        learner_session_id: UUID,
        conversation_history: List[Dict[str, Any]]
    ) -> ConversationMetrics:
        """
        Calculate conversation metrics for a learner session
        
        Args:
            learner_session_id: ID of the learner session
            conversation_history: List of conversation messages
            
        Returns:
            ConversationMetrics with calculated metrics
        """
        try:
            logger.info(f"Calculating conversation metrics for session {learner_session_id}")
            
            # Calculate basic metrics
            total_messages = len(conversation_history)
            user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]
            
            # Calculate average response time (mock implementation)
            avg_response_time = 2.5  # seconds
            
            # Extract common topics (mock implementation)
            most_common_topics = ["AI basics", "Machine Learning", "Data Science"]
            
            # Calculate conversation duration
            if conversation_history:
                start_time = conversation_history[0].get("timestamp", "")
                end_time = conversation_history[-1].get("timestamp", "")
                # Simplified duration calculation
                conversation_duration = len(conversation_history) * 2.0  # minutes
            else:
                conversation_duration = 0.0
            
            metrics = ConversationMetrics(
                total_messages=total_messages,
                average_response_time=avg_response_time,
                most_common_topics=most_common_topics,
                conversation_duration_minutes=conversation_duration,
                last_activity=conversation_history[-1].get("timestamp") if conversation_history else None
            )
            
            logger.info(f"Calculated metrics: {total_messages} messages, {conversation_duration} minutes")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate conversation metrics: {str(e)}")
            raise Exception("Metrics calculation service temporarily unavailable")