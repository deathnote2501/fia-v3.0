"""
FIA v3.0 - Outbound Ports
Interfaces for external services and infrastructure
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from uuid import UUID


class GeminiServicePort(ABC):
    """Port for Gemini AI service interactions (plan generation and content creation)"""
    
    @abstractmethod
    async def generate_training_plan(
        self, 
        learner_profile: Dict[str, Any], 
        training_content: str,
        context_cache_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate personalized training plan"""
        pass
    
    @abstractmethod
    async def generate_slide_content(
        self,
        slide_title: str,
        module_context: str,
        learner_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate slide content"""
        pass


class ConversationServicePort(ABC):
    """Port for AI conversation service with learners"""
    
    @abstractmethod
    async def chat_with_learner(
        self,
        message: str,
        conversation_history: List[Dict[str, Any]],
        training_context: str,
        learner_profile: Dict[str, Any],
        learner_session_id: UUID
    ) -> Dict[str, Any]:
        """Handle learner chat interactions and return structured response"""
        pass
    
    @abstractmethod
    async def generate_contextual_hint(
        self,
        current_slide: Dict[str, Any],
        learner_question: str,
        learner_profile: Dict[str, Any]
    ) -> str:
        """Generate contextual hints for learner questions"""
        pass
    
    @abstractmethod
    async def explain_concept(
        self,
        concept: str,
        training_context: str,
        learner_profile: Dict[str, Any]
    ) -> str:
        """Explain a specific concept to the learner"""
        pass


class EngagementAnalysisServicePort(ABC):
    """Port for learner engagement analysis service"""
    
    @abstractmethod
    async def analyze_session_engagement(
        self,
        learner_session_id: UUID,
        activity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze overall session engagement metrics"""
        pass
    
    @abstractmethod
    async def analyze_slide_engagement(
        self,
        slide_id: UUID,
        time_spent: float,
        interactions: List[Dict[str, Any]],
        learner_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze engagement for a specific slide"""
        pass
    
    @abstractmethod
    async def detect_learning_difficulties(
        self,
        learner_session_id: UUID,
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect potential learning difficulties and suggest interventions"""
        pass
    
    @abstractmethod
    async def generate_progress_insights(
        self,
        learner_session_id: UUID,
        completion_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate insights about learner progress and recommendations"""
        pass


class EmailServicePort(ABC):
    """Port for email service interactions"""
    
    @abstractmethod
    async def send_session_invitation(
        self,
        recipient_email: str,
        session_link: str,
        training_name: str,
        trainer_name: str
    ) -> bool:
        """Send session invitation email"""
        pass
    
    @abstractmethod
    async def send_completion_certificate(
        self,
        recipient_email: str,
        learner_name: str,
        training_name: str,
        completion_date: str
    ) -> bool:
        """Send training completion certificate"""
        pass
    
    @abstractmethod
    async def send_trainer_notification(
        self,
        trainer_email: str,
        notification_type: str,
        data: Dict[str, Any]
    ) -> bool:
        """Send notification to trainer"""
        pass


class FileStorageServicePort(ABC):
    """Port for file storage service interactions"""
    
    @abstractmethod
    async def store_training_file(
        self,
        file_content: bytes,
        file_name: str,
        trainer_id: UUID
    ) -> str:
        """Store training file and return path"""
        pass
    
    @abstractmethod
    async def retrieve_training_file(
        self,
        file_path: str
    ) -> Optional[bytes]:
        """Retrieve training file content"""
        pass
    
    @abstractmethod
    async def delete_training_file(
        self,
        file_path: str
    ) -> bool:
        """Delete training file"""
        pass
    
    @abstractmethod
    async def get_file_info(
        self,
        file_path: str
    ) -> Optional[Dict[str, Any]]:
        """Get file metadata"""
        pass


class ContextCacheServicePort(ABC):
    """Port for context caching service"""
    
    @abstractmethod
    async def create_cache(
        self,
        content: str,
        ttl_hours: int = 12
    ) -> str:
        """Create context cache and return cache ID"""
        pass
    
    @abstractmethod
    async def get_cache(
        self,
        cache_id: str
    ) -> Optional[str]:
        """Retrieve cached content"""
        pass
    
    @abstractmethod
    async def update_cache(
        self,
        cache_id: str,
        content: str,
        ttl_hours: int = 12
    ) -> bool:
        """Update cached content"""
        pass
    
    @abstractmethod
    async def delete_cache(
        self,
        cache_id: str
    ) -> bool:
        """Delete cached content"""
        pass


class LiveConversationServicePort(ABC):
    """Port for Live API conversation service"""
    
    @abstractmethod
    async def create_live_session(
        self,
        slide_context: Dict[str, Any],
        learner_profile: Dict[str, Any],
        learner_session_id: UUID
    ) -> str:
        """Create a Live API session and return session ID"""
        pass
    
    @abstractmethod
    async def handle_live_conversation(
        self,
        session_id: str,
        audio_input: bytes,
        mime_type: str = "audio/pcm;rate=16000"
    ) -> Dict[str, Any]:
        """Handle audio conversation and return response"""
        pass
    
    @abstractmethod
    async def close_live_session(
        self,
        session_id: str
    ) -> bool:
        """Close Live API session"""
        pass


class ImageGenerationServicePort(ABC):
    """Port for image generation service using OpenAI"""
    
    @abstractmethod
    async def generate_infographic(
        self,
        slide_content: str,
        learner_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate educational infographic from slide content
        
        Args:
            slide_content: The slide content to create infographic from
            learner_profile: Optional learner profile for personalization
            
        Returns:
            Dict containing:
            - image_data: str - Base64 encoded image data
            - revised_prompt: str - The revised prompt used by OpenAI
            - metadata: Dict - Additional metadata (size, format, etc.)
        """
        pass


class TTSServicePort(ABC):
    """Port for Text-to-Speech service using Vertex AI"""
    
    @abstractmethod
    async def generate_speech(
        self,
        text: str,
        voice_name: str = "Kore",
        language_code: str = "fr"
    ) -> Dict[str, Any]:
        """
        Generate speech audio from text
        
        Args:
            text: Text to convert to speech
            voice_name: Voice to use (e.g., 'Kore', 'Puck', 'Aoede')
            language_code: Language code (e.g., 'fr', 'en', 'es')
            
        Returns:
            Dict containing:
            - audio_data: bytes - Audio data in WAV format
            - duration_seconds: float - Duration of audio
            - metadata: Dict - Additional metadata
        """
        pass
    
    @abstractmethod
    async def get_available_voices(
        self,
        language_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get list of available voices
        
        Args:
            language_code: Optional language filter
            
        Returns:
            List of voice information dictionaries
        """
        pass