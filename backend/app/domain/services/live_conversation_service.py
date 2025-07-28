"""
FIA v3.0 - Live Conversation Domain Service
Business logic for managing Live API conversations with learners
"""

import logging
from typing import Dict, Any, Optional
from uuid import UUID

from app.domain.entities.learner_session import LearnerSession
from app.domain.ports.repositories import (
    LearnerSessionRepositoryPort,
    SlideRepositoryPort,
    TrainingSessionRepositoryPort,
    ChatMessageRepositoryPort
)
from app.domain.ports.outbound_ports import LiveConversationServicePort

logger = logging.getLogger(__name__)


class LiveConversationError(Exception):
    """Exception for Live Conversation service operations"""
    pass


class LiveConversationService:
    """Domain service for managing Live API conversations with learners"""
    
    def __init__(
        self,
        live_api_adapter: LiveConversationServicePort,
        learner_session_repository: LearnerSessionRepositoryPort,
        slide_repository: SlideRepositoryPort,
        training_session_repository: TrainingSessionRepositoryPort,
        chat_message_repository: ChatMessageRepositoryPort
    ):
        """Initialize Live Conversation service"""
        self.live_api_adapter = live_api_adapter
        self.learner_session_repo = learner_session_repository
        self.slide_repo = slide_repository
        self.training_session_repo = training_session_repository
        self.chat_message_repo = chat_message_repository
        
        # Track active Live sessions for this service instance
        self.active_live_sessions: Dict[UUID, str] = {}  # learner_session_id -> live_session_id
        
        logger.info("🎙️ LIVE_CONVERSATION [SERVICE] Initialized")
    
    async def start_live_session(self, learner_session_id: UUID) -> Dict[str, Any]:
        """
        Start a Live API session for a learner with full context
        
        Args:
            learner_session_id: UUID of the learner session
            
        Returns:
            Dict with Live session information:
            - live_session_id: str - Unique Live session ID
            - status: str - Session status
            - slide_context: Dict - Current slide context
            - learner_profile: Dict - Learner profile data
            - metadata: Dict - Additional session metadata
        """
        try:
            logger.info(f"🚀 LIVE_CONVERSATION [START] Starting Live session for learner: {learner_session_id}")
            
            # Check if learner session already has an active Live session
            if learner_session_id in self.active_live_sessions:
                existing_session_id = self.active_live_sessions[learner_session_id]
                logger.warning(f"⚠️ LIVE_CONVERSATION [START] Learner already has active Live session: {existing_session_id}")
                # Close existing session first
                await self._close_existing_live_session(learner_session_id)
            
            # 1. Get learner session from repository
            learner_session = await self.learner_session_repo.get_by_id(learner_session_id)
            if not learner_session:
                raise LiveConversationError(f"Learner session not found: {learner_session_id}")
            
            # 2. Get current slide context
            slide_context = await self._get_current_slide_context(learner_session)
            
            # 3. Get training context
            training_context = await self._get_training_context(learner_session)
            
            # 4. Build enriched learner profile
            learner_profile = self._build_learner_profile(learner_session)
            
            # 5. Add conversation history for better context
            conversation_history = await self._get_recent_conversation_history(learner_session_id)
            
            # 6. Enhance slide context with training info
            enhanced_slide_context = {
                **slide_context,
                "training_name": training_context.get("training_name", "Formation"),
                "module_name": slide_context.get("module_name", "Module"),
                "conversation_history": conversation_history
            }
            
            # 7. Create Live API session
            live_session_id = await self.live_api_adapter.create_live_session(
                slide_context=enhanced_slide_context,
                learner_profile=learner_profile,
                learner_session_id=learner_session_id
            )
            
            # 8. Track the active session
            self.active_live_sessions[learner_session_id] = live_session_id
            
            logger.info(f"✅ LIVE_CONVERSATION [START] Live session created: {live_session_id} for learner: {learner_session_id}")
            
            return {
                "live_session_id": live_session_id,
                "status": "active",
                "slide_context": enhanced_slide_context,
                "learner_profile": learner_profile,
                "metadata": {
                    "learner_session_id": str(learner_session_id),
                    "current_slide_number": learner_session.current_slide_number,
                    "training_session_id": str(learner_session.training_session_id),
                    "conversation_history_length": len(conversation_history)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ LIVE_CONVERSATION [START] Error starting Live session for {learner_session_id}: {str(e)}")
            # Clean up if session was partially created
            if learner_session_id in self.active_live_sessions:
                del self.active_live_sessions[learner_session_id]
            raise LiveConversationError(f"Failed to start Live session: {str(e)}")
    
    async def process_live_interaction(
        self,
        learner_session_id: UUID,
        audio_data: bytes,
        mime_type: str = "audio/pcm;rate=16000"
    ) -> Dict[str, Any]:
        """
        Process audio interaction from learner in Live session
        
        Args:
            learner_session_id: UUID of the learner session
            audio_data: Raw audio data from learner
            mime_type: Audio MIME type
            
        Returns:
            Dict with interaction response:
            - audio_response: bytes - AI audio response
            - text_transcript: str - Text version of response (if available)
            - session_updated: bool - Whether session context was updated
            - metadata: Dict - Processing metadata
        """
        try:
            logger.info(f"🎙️ LIVE_CONVERSATION [PROCESS] Processing audio interaction for learner: {learner_session_id}")
            
            # Check if learner has an active Live session
            if learner_session_id not in self.active_live_sessions:
                raise LiveConversationError(f"No active Live session for learner: {learner_session_id}")
            
            live_session_id = self.active_live_sessions[learner_session_id]
            
            # Process audio through Live API
            response = await self.live_api_adapter.handle_live_conversation(
                session_id=live_session_id,
                audio_input=audio_data,
                mime_type=mime_type
            )
            
            # Check for errors in response
            if response.get("error"):
                logger.error(f"❌ LIVE_CONVERSATION [PROCESS] Live API error: {response['error']}")
                raise LiveConversationError(f"Live API error: {response['error']}")
            
            # Update learner session activity
            await self._update_learner_activity(learner_session_id)
            
            # Log the interaction for analytics (optional - could be done asynchronously)
            await self._log_live_interaction(
                learner_session_id=learner_session_id,
                audio_input_size=len(audio_data),
                response_data=response
            )
            
            logger.info(f"✅ LIVE_CONVERSATION [PROCESS] Interaction processed successfully for learner: {learner_session_id}")
            
            return {
                "audio_response": response.get("audio_response", b""),
                "text_transcript": response.get("text_transcript", ""),
                "session_updated": True,
                "metadata": {
                    "live_session_id": live_session_id,
                    "learner_session_id": str(learner_session_id),
                    "audio_input_size": len(audio_data),
                    "audio_response_size": len(response.get("audio_response", b"")),
                    "processing_metadata": response.get("metadata", {}),
                    "is_complete": response.get("is_complete", False)
                }
            }
            
        except LiveConversationError:
            # Re-raise Live conversation errors
            raise
        except Exception as e:
            logger.error(f"❌ LIVE_CONVERSATION [PROCESS] Unexpected error processing interaction for {learner_session_id}: {str(e)}")
            raise LiveConversationError(f"Failed to process Live interaction: {str(e)}")
    
    async def stop_live_session(self, learner_session_id: UUID) -> bool:
        """
        Stop Live API session for a learner
        
        Args:
            learner_session_id: UUID of the learner session
            
        Returns:
            bool: True if session stopped successfully
        """
        try:
            logger.info(f"🛑 LIVE_CONVERSATION [STOP] Stopping Live session for learner: {learner_session_id}")
            
            if learner_session_id not in self.active_live_sessions:
                logger.warning(f"⚠️ LIVE_CONVERSATION [STOP] No active Live session for learner: {learner_session_id}")
                return True  # Already stopped
            
            live_session_id = self.active_live_sessions[learner_session_id]
            
            # Close Live API session
            success = await self.live_api_adapter.close_live_session(live_session_id)
            
            # Remove from active sessions tracking
            del self.active_live_sessions[learner_session_id]
            
            if success:
                logger.info(f"✅ LIVE_CONVERSATION [STOP] Live session stopped successfully for learner: {learner_session_id}")
            else:
                logger.warning(f"⚠️ LIVE_CONVERSATION [STOP] Live session stop had issues for learner: {learner_session_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ LIVE_CONVERSATION [STOP] Error stopping Live session for {learner_session_id}: {str(e)}")
            # Clean up tracking even if close failed
            if learner_session_id in self.active_live_sessions:
                del self.active_live_sessions[learner_session_id]
            return False
    
    async def get_live_session_status(self, learner_session_id: UUID) -> Dict[str, Any]:
        """Get status of Live session for a learner"""
        has_active_session = learner_session_id in self.active_live_sessions
        
        status_info = {
            "has_active_session": has_active_session,
            "learner_session_id": str(learner_session_id)
        }
        
        if has_active_session:
            status_info["live_session_id"] = self.active_live_sessions[learner_session_id]
        
        return status_info
    
    async def cleanup_all_sessions(self) -> int:
        """Clean up all active Live sessions (useful for shutdown)"""
        logger.info("🧹 LIVE_CONVERSATION [CLEANUP] Cleaning up all active Live sessions...")
        
        learner_session_ids = list(self.active_live_sessions.keys())
        cleaned_count = 0
        
        for learner_session_id in learner_session_ids:
            success = await self.stop_live_session(learner_session_id)
            if success:
                cleaned_count += 1
        
        logger.info(f"🧹 LIVE_CONVERSATION [CLEANUP] Cleaned {cleaned_count}/{len(learner_session_ids)} Live sessions")
        return cleaned_count
    
    # Private helper methods
    
    async def _get_current_slide_context(self, learner_session: LearnerSession) -> Dict[str, Any]:
        """Get current slide context for the learner"""
        try:
            # Get current slide
            current_slide = await self.slide_repo.get_by_learner_session_and_slide_number(
                learner_session.id,
                learner_session.current_slide_number
            )
            
            if not current_slide:
                # Return a placeholder context if no slide found
                return {
                    "title": f"Slide {learner_session.current_slide_number}",
                    "content": "Contenu de la slide en cours de chargement...",
                    "slide_number": learner_session.current_slide_number,
                    "module_name": "Module en cours"
                }
            
            return {
                "title": current_slide.title,
                "content": current_slide.content,
                "slide_number": current_slide.slide_number,
                "module_name": getattr(current_slide, 'module_name', 'Module')
            }
            
        except Exception as e:
            logger.error(f"❌ LIVE_CONVERSATION [SLIDE_CONTEXT] Error getting slide context: {str(e)}")
            # Return fallback context
            return {
                "title": "Slide courante",
                "content": "Formation en cours...",
                "slide_number": learner_session.current_slide_number,
                "module_name": "Module"
            }
    
    async def _get_training_context(self, learner_session: LearnerSession) -> Dict[str, Any]:
        """Get training context for the learner"""
        try:
            # Get training session
            training_session = await self.training_session_repo.get_by_id(learner_session.training_session_id)
            
            if not training_session:
                return {"training_name": "Formation"}
            
            return {
                "training_name": getattr(training_session, 'name', 'Formation'),
                "training_description": getattr(training_session, 'description', ''),
                "training_session_id": str(training_session.id)
            }
            
        except Exception as e:
            logger.error(f"❌ LIVE_CONVERSATION [TRAINING_CONTEXT] Error getting training context: {str(e)}")
            return {"training_name": "Formation"}
    
    def _build_learner_profile(self, learner_session: LearnerSession) -> Dict[str, Any]:
        """Build complete learner profile for Live API"""
        profile = learner_session.get_learning_context()
        
        # Add enriched profile data if available
        if learner_session.enriched_profile:
            profile.update({
                "enriched_data": learner_session.enriched_profile,
                "has_enriched_profile": True
            })
        else:
            profile["has_enriched_profile"] = False
        
        # Add session progress info
        profile.update({
            "current_slide_number": learner_session.current_slide_number,
            "total_time_spent": learner_session.total_time_spent,
            "email": learner_session.email
        })
        
        return profile
    
    async def _get_recent_conversation_history(self, learner_session_id: UUID, limit: int = 5) -> list:
        """Get recent conversation history for context"""
        try:
            # Get recent chat messages
            chat_messages = await self.chat_message_repo.get_by_learner_session_id(learner_session_id)
            
            # Take the last few messages for context
            recent_messages = chat_messages[-limit:] if chat_messages else []
            
            # Format for Live API context
            history = []
            for message in recent_messages:
                history.append({
                    "role": message.sender_type,  # 'user' or 'assistant'
                    "content": message.content,
                    "timestamp": message.created_at.isoformat() if message.created_at else None
                })
            
            return history
            
        except Exception as e:
            logger.error(f"❌ LIVE_CONVERSATION [HISTORY] Error getting conversation history: {str(e)}")
            return []
    
    async def _update_learner_activity(self, learner_session_id: UUID) -> None:
        """Update learner session last activity"""
        try:
            learner_session = await self.learner_session_repo.get_by_id(learner_session_id)
            if learner_session:
                # This will update last_activity_at
                learner_session.add_time_spent(0)  # Just update timestamp
                await self.learner_session_repo.update(learner_session)
                
        except Exception as e:
            logger.error(f"❌ LIVE_CONVERSATION [ACTIVITY] Error updating learner activity: {str(e)}")
    
    async def _log_live_interaction(
        self,
        learner_session_id: UUID,
        audio_input_size: int,
        response_data: Dict[str, Any]
    ) -> None:
        """Log Live API interaction for analytics (optional)"""
        try:
            # This is optional logging - could be implemented later
            # For now, just log to system logger
            logger.info(f"📊 LIVE_CONVERSATION [ANALYTICS] Interaction logged - "
                       f"Learner: {learner_session_id}, "
                       f"Input: {audio_input_size} bytes, "
                       f"Output: {len(response_data.get('audio_response', b''))} bytes")
            
        except Exception as e:
            logger.error(f"❌ LIVE_CONVERSATION [ANALYTICS] Error logging interaction: {str(e)}")
    
    async def _close_existing_live_session(self, learner_session_id: UUID) -> None:
        """Close existing Live session for learner"""
        try:
            await self.stop_live_session(learner_session_id)
        except Exception as e:
            logger.error(f"❌ LIVE_CONVERSATION [CLOSE_EXISTING] Error closing existing session: {str(e)}")
    
    def get_active_sessions_count(self) -> int:
        """Get count of active Live sessions managed by this service"""
        return len(self.active_live_sessions)
    
    def get_active_sessions_info(self) -> Dict[str, str]:
        """Get information about active Live sessions"""
        return {
            str(learner_id): live_id 
            for learner_id, live_id in self.active_live_sessions.items()
        }