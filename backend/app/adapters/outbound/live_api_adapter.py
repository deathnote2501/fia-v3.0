"""
FIA v3.0 - Live API Outbound Adapter
Implementation of Live API conversation service using Vertex AI Live API
"""

import logging
import uuid
from typing import Dict, Any, Optional
from uuid import UUID
import json

from app.domain.ports.outbound_ports import LiveConversationServicePort
from app.infrastructure.live_api_client import LiveAPIClient, AudioData, LiveResponse, LiveAPIError
from app.infrastructure.rate_limiter import gemini_rate_limiter

logger = logging.getLogger(__name__)


class LiveAPIAdapter(LiveConversationServicePort):
    """Outbound adapter for Live API conversation service using Vertex AI Live API"""
    
    def __init__(self):
        """Initialize Live API adapter"""
        self.active_sessions: Dict[str, LiveAPIClient] = {}
        self.session_contexts: Dict[str, Dict[str, Any]] = {}
        self.session_throttle: Dict[str, float] = {}  # Track last response time per session
        self.response_cooldown = 2.0  # Minimum seconds between responses
        
        logger.info("🎙️ LIVE_API [ADAPTER] Initialized")
    
    async def create_live_session(
        self,
        slide_context: Dict[str, Any],
        learner_profile: Dict[str, Any],
        learner_session_id: UUID
    ) -> str:
        """
        Create a Live API session with slide context and learner profile
        
        Args:
            slide_context: Current slide information
                - title: str - Slide title
                - content: str - Slide content  
                - module_name: str - Module name
                - training_name: str - Training name
            learner_profile: Learner profile information
                - experience_level: str
                - learning_style: str  
                - job_position: str
                - activity_sector: str
                - language: str
            learner_session_id: UUID of the learner session
            
        Returns:
            str: Live session ID
        """
        try:
            # Apply rate limiting
            await gemini_rate_limiter.acquire()
            
            # Generate unique session ID
            session_id = str(uuid.uuid4())
            
            logger.info(f"🚀 LIVE_API [CREATE_SESSION] Creating Live session: {session_id}")
            
            # Build system instruction with context
            system_instruction = self._build_system_instruction(slide_context, learner_profile)
            
            # Configure Live API session
            session_config = {
                "response_modalities": ["AUDIO"],
                "system_instruction": system_instruction,
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": self._select_voice_for_learner(learner_profile)
                        }
                    }
                },
                "context": {
                    "slide_context": slide_context,
                    "learner_profile": learner_profile,
                    "learner_session_id": str(learner_session_id)
                }
            }
            
            # MOCK MODE: Skip real Vertex AI connection for development testing
            logger.info("🎭 LIVE_API [MOCK] Using mock mode for development (no real Vertex AI connection)")
            
            # Simulate successful connection
            connection_success = True
            
            if connection_success:
                # Store mock session (no real client)
                self.active_sessions[session_id] = None  # Mock client 
                self.session_contexts[session_id] = {
                    "slide_context": slide_context,
                    "learner_profile": learner_profile,
                    "learner_session_id": learner_session_id,
                    "created_at": session_id,  # Mock session ID
                    "session_config": session_config,
                    "is_mock": True
                }
                
                logger.info(f"✅ LIVE_API [CREATE_SESSION] Session created successfully: {session_id}")
                return session_id
            else:
                logger.error(f"❌ LIVE_API [CREATE_SESSION] Failed to connect to Live API")
                raise LiveAPIError("Failed to establish Live API connection")
                
        except Exception as e:
            logger.error(f"❌ LIVE_API [CREATE_SESSION] Error: {str(e)}")
            # Clean up if session was partially created
            if session_id in self.active_sessions:
                await self._cleanup_session(session_id)
            raise LiveAPIError(f"Failed to create Live session: {str(e)}")
    
    async def handle_live_conversation(
        self,
        session_id: str,
        audio_input: bytes,
        mime_type: str = "audio/pcm;rate=16000"
    ) -> Dict[str, Any]:
        """
        Handle live audio conversation
        
        Args:
            session_id: Live session ID
            audio_input: Audio data bytes
            mime_type: Audio MIME type
            
        Returns:
            Dict with conversation response data:
            - audio_response: bytes - Audio response from AI
            - text_transcript: str - Text transcript (if available)
            - metadata: Dict - Response metadata
            - is_complete: bool - Whether response is complete
        """
        try:
            logger.info(f"🎙️ LIVE_API [HANDLE_CONVERSATION] Starting for session {session_id}, input size: {len(audio_input)} bytes")
            
            # Check if session exists
            if session_id not in self.active_sessions:
                raise LiveAPIError(f"Live session not found: {session_id}")
            
            session_context = self.session_contexts[session_id]
            
            # Throttle responses to prevent infinite loop
            import time
            current_time = time.time()
            last_response_time = self.session_throttle.get(session_id, 0)
            
            logger.info(f"🕐 LIVE_API [THROTTLE_CHECK] Session {session_id}: current={current_time:.3f}, last={last_response_time:.3f}, diff={current_time - last_response_time:.3f}s, cooldown={self.response_cooldown}s")
            
            if current_time - last_response_time < self.response_cooldown:
                time_remaining = self.response_cooldown - (current_time - last_response_time)
                logger.info(f"🕐 LIVE_API [THROTTLE] Session {session_id} throttled, {time_remaining:.1f}s remaining")
                return {
                    "audio_response": b"",  # Empty response during cooldown
                    "text_transcript": "",
                    "metadata": {"throttled": True, "cooldown_remaining": time_remaining},
                    "is_complete": True,
                    "error": None
                }
            
            logger.info(f"🎙️ LIVE_API [CONVERSATION] Processing audio input for session: {session_id} (MOCK MODE)")
            
            # MOCK: Simulate audio processing without real Vertex AI
            if session_context.get("is_mock"):
                logger.info("🎭 LIVE_API [MOCK] Generating mock audio response")
                
                # Update throttle timestamp
                self.session_throttle[session_id] = current_time
                
                # Get learner context for personalized response
                learner_profile = session_context["learner_profile"]
                slide_context = session_context["slide_context"]
                
                # Generate mock text response based on context
                mock_text = self._generate_mock_response(learner_profile, slide_context)
                
                # For development, don't send fake audio - just send text
                # In production, this would be real Vertex AI audio
                logger.info(f"🎭 LIVE_API [MOCK] Text-only response (no mock audio): {mock_text[:50]}...")
                
                response_data = {
                    "audio_response": b"",  # Empty audio for mock mode
                    "text_transcript": mock_text,
                    "metadata": {
                        "mock": True,
                        "text_only": True,  # Flag to indicate text-only mode
                        "audio_input_size": len(audio_input),
                        "mime_type": mime_type,
                        "session_id": session_id
                    },
                    "is_complete": True,
                    "error": None
            }
                
            logger.info(f"✅ LIVE_API [CONVERSATION] Mock response generated for session: {session_id}")
            return response_data
            
        except LiveAPIError:
            # Re-raise Live API errors
            raise
        except Exception as e:
            logger.error(f"❌ LIVE_API [CONVERSATION] Unexpected error: {str(e)}")
            raise LiveAPIError(f"Conversation handling failed: {str(e)}")
    
    async def close_live_session(self, session_id: str) -> bool:
        """
        Close Live API session and cleanup resources
        
        Args:
            session_id: Live session ID
            
        Returns:
            bool: True if session closed successfully
        """
        try:
            logger.info(f"🔌 LIVE_API [CLOSE_SESSION] Closing session: {session_id}")
            
            success = await self._cleanup_session(session_id)
            
            if success:
                logger.info(f"✅ LIVE_API [CLOSE_SESSION] Session closed successfully: {session_id}")
            else:
                logger.warning(f"⚠️ LIVE_API [CLOSE_SESSION] Session close had issues: {session_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ LIVE_API [CLOSE_SESSION] Error closing session {session_id}: {str(e)}")
            return False
    
    def _build_system_instruction(
        self, 
        slide_context: Dict[str, Any], 
        learner_profile: Dict[str, Any]
    ) -> str:
        """Build system instruction with slide context and learner profile"""
        
        slide_title = slide_context.get("title", "Slide actuelle")
        slide_content = slide_context.get("content", "")
        training_name = slide_context.get("training_name", "Formation")
        module_name = slide_context.get("module_name", "Module")
        
        experience_level = learner_profile.get("experience_level", "débutant")
        learning_style = learner_profile.get("learning_style", "visuel")
        job_position = learner_profile.get("job_position", "professionnel")
        language = learner_profile.get("language", "fr")
        
        instruction = f"""Tu es un formateur IA expert spécialisé en formation professionnelle. Tu conduis une conversation vocale interactive avec un apprenant.

CONTEXTE DE LA FORMATION:
- Formation: {training_name}
- Module: {module_name}
- Slide actuelle: {slide_title}

CONTENU DE LA SLIDE ACTUELLE:
{slide_content[:1000]}...

PROFIL DE L'APPRENANT:
- Niveau d'expérience: {experience_level}
- Style d'apprentissage préféré: {learning_style}
- Poste occupé: {job_position}
- Langue de communication: {language}

INSTRUCTIONS POUR LA CONVERSATION VOCALE:
1. Parle dans un ton naturel et conversationnel, comme un vrai formateur
2. Adapte ton niveau de langage à l'expérience de l'apprenant ({experience_level})
3. Utilise des exemples pertinents à son poste ({job_position})
4. Respecte son style d'apprentissage ({learning_style})
5. Réponds UNIQUEMENT en {language}
6. Sois encourageant et pédagogique
7. Pose des questions pour vérifier la compréhension
8. Relie toujours tes réponses au contenu de la slide actuelle
9. Si l'apprenant change de sujet, ramène-le gentiment au contenu
10. Garde tes réponses concises mais complètes (30-60 secondes de parole)

IMPORTANT: Tu es en conversation vocale Live. Parle naturellement comme si tu étais physiquement présent avec l'apprenant."""
        
        return instruction
    
    def _select_voice_for_learner(self, learner_profile: Dict[str, Any]) -> str:
        """Select appropriate voice based on learner profile"""
        
        # Simple voice selection based on language and preference
        language = learner_profile.get("language", "fr")
        
        # Default French voices for different contexts
        if language.startswith("fr"):
            return "Kore"  # Professional, clear French voice
        elif language.startswith("en"):
            return "Puck"  # Professional English voice
        else:
            return "Kore"  # Default fallback
    
    async def _cleanup_session(self, session_id: str) -> bool:
        """Clean up session resources"""
        try:
            success = True
            
            # Clean up mock session
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            # Remove session context
            if session_id in self.session_contexts:
                del self.session_contexts[session_id]
                
            # Clean up throttle data
            if session_id in self.session_throttle:
                del self.session_throttle[session_id]
            
            logger.info(f"🧹 LIVE_API [CLEANUP] Session cleaned up: {session_id}")
            return success
            
        except Exception as e:
            logger.error(f"❌ LIVE_API [CLEANUP] Error cleaning session {session_id}: {str(e)}")
            return False
    
    def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get information about active sessions"""
        return {
            session_id: {
                "connected": True,  # Mock always connected
                "context": self.session_contexts.get(session_id, {}),
                "session_info": {"mock": True, "session_id": session_id}
            }
            for session_id, client in self.active_sessions.items()
        }
    
    def get_session_count(self) -> int:
        """Get count of active sessions"""
        return len(self.active_sessions)
    
    async def cleanup_all_sessions(self) -> int:
        """Clean up all active sessions (useful for shutdown)"""
        logger.info("🧹 LIVE_API [CLEANUP_ALL] Cleaning up all active sessions...")
        
        session_ids = list(self.active_sessions.keys())
        cleaned_count = 0
        
        for session_id in session_ids:
            success = await self._cleanup_session(session_id)
            if success:
                cleaned_count += 1
        
        logger.info(f"🧹 LIVE_API [CLEANUP_ALL] Cleaned {cleaned_count}/{len(session_ids)} sessions")
        return cleaned_count
    
    def _generate_mock_response(self, learner_profile: Dict[str, Any], slide_context: Dict[str, Any]) -> str:
        """Generate mock text response based on context"""
        
        # Get learner info
        language = learner_profile.get("language", "fr")
        experience_level = learner_profile.get("experience_level", "intermediate")
        slide_title = slide_context.get("title", "cette slide")
        
        # Mock responses based on language
        if language == "fr":
            responses = [
                f"Bonjour ! Je vois que vous regardez '{slide_title}'. Avec votre niveau {experience_level}, je peux vous expliquer les concepts clés.",
                f"C'est une excellente question ! Sur '{slide_title}', les points essentiels sont bien présentés pour votre niveau {experience_level}.",
                f"Parfait ! Cette partie sur '{slide_title}' est importante. Voulez-vous que je détaille certains aspects ?",
                f"Je comprends votre question. En tant qu'apprenant {experience_level}, vous devriez retenir ces éléments clés de '{slide_title}'."
            ]
        else:
            responses = [
                f"Hello! I see you're looking at '{slide_title}'. With your {experience_level} level, I can explain the key concepts.",
                f"That's an excellent question! In '{slide_title}', the essential points are well presented for your {experience_level} level.",
                f"Perfect! This part about '{slide_title}' is important. Would you like me to detail certain aspects?",
                f"I understand your question. As an {experience_level} learner, you should remember these key elements from '{slide_title}'."
            ]
        
        # Return a random response
        import random
        return random.choice(responses)
    
    def _generate_mock_audio(self, text: str) -> bytes:
        """Generate mock audio response (placeholder)"""
        # In a real implementation, this would use TTS to convert text to audio
        # For now, return a placeholder byte sequence
        mock_audio_size = len(text) * 100  # Simulate audio size based on text length
        return b"MOCK_AUDIO_DATA" + text.encode('utf-8')[:min(50, len(text))] + b"\x00" * max(0, mock_audio_size - len(text) - 15)