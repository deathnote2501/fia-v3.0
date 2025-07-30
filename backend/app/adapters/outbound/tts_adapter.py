"""
FIA v3.0 - Text-to-Speech Outbound Adapter
Implementation of TTS service using Vertex AI Gemini 2.5 TTS
"""

import logging
import time
from typing import Dict, Any, List, Optional

from app.domain.ports.outbound_ports import TTSServicePort
from app.infrastructure.adapters.vertex_ai_adapter import VertexAIAdapter
from app.infrastructure.rate_limiter import gemini_rate_limiter

logger = logging.getLogger(__name__)


class TTSAdapter(TTSServicePort):
    """Outbound adapter for Text-to-Speech service using Vertex AI Gemini 2.5 TTS"""
    
    # Voice configurations based on Gemini 2.5 TTS documentation
    AVAILABLE_VOICES = {
        # Bright voices
        "Zephyr": {"style": "Bright", "languages": ["fr", "en", "es", "de"], "recommended_for": "friendly"},
        "Autonoe": {"style": "Bright", "languages": ["fr", "en", "es", "de"], "recommended_for": "friendly"},
        
        # Firm voices (professional)
        "Kore": {"style": "Firm", "languages": ["fr", "en", "es", "de"], "recommended_for": "formal"},
        "Orus": {"style": "Firm", "languages": ["fr", "en", "es", "de"], "recommended_for": "formal"},
        "Alnilam": {"style": "Firm", "languages": ["fr", "en", "es", "de"], "recommended_for": "formal"},
        
        # Upbeat voices
        "Puck": {"style": "Upbeat", "languages": ["en", "fr"], "recommended_for": "default"},
        "Laomedeia": {"style": "Upbeat", "languages": ["en", "fr"], "recommended_for": "friendly"},
        
        # Informative voices
        "Charon": {"style": "Informative", "languages": ["en", "fr", "de"], "recommended_for": "formal"},
        "Rasalgethi": {"style": "Informative", "languages": ["en", "fr", "de"], "recommended_for": "formal"},
        
        # Smooth voices
        "Algieba": {"style": "Smooth", "languages": ["fr", "en", "es"], "recommended_for": "default"},
        "Despina": {"style": "Smooth", "languages": ["fr", "en", "es"], "recommended_for": "default"},
        
        # Breezy voices
        "Aoede": {"style": "Breezy", "languages": ["fr", "en", "es"], "recommended_for": "friendly"},
        
        # Other specialized voices
        "Fenrir": {"style": "Excitable", "languages": ["en"], "recommended_for": "friendly"},
        "Leda": {"style": "Youthful", "languages": ["es", "en"], "recommended_for": "friendly"}
    }
    
    def __init__(self):
        """Initialize TTS adapter with Vertex AI"""
        self.vertex_adapter = VertexAIAdapter()
        logger.info("🔊 TTS [ADAPTER] Initialized with Vertex AI Gemini 2.5 TTS")
        
    async def generate_speech(
        self,
        text: str,
        voice_name: str = "Kore",
        language_code: str = "fr"
    ) -> Dict[str, Any]:
        """
        Generate speech audio from text using Vertex AI Gemini 2.5 TTS
        
        Args:
            text: Text to convert to speech
            voice_name: Voice to use (must be from AVAILABLE_VOICES)
            language_code: Language code (fr, en, es, de)
            
        Returns:
            Dict containing audio_data, duration_seconds, and metadata
        """
        try:
            # Apply rate limiting
            await gemini_rate_limiter.acquire()
            
            start_time = time.time()
            
            # Validate voice and language
            validated_voice = self._validate_voice_for_language(voice_name, language_code)
            
            logger.info(f"🔊 TTS [GENERATE] Generating speech - Text: {len(text)} chars, Voice: {validated_voice}, Lang: {language_code}")
            
            # Generate speech using Vertex AI TTS
            audio_data, metadata = await self.vertex_adapter.generate_speech_audio(
                text=text,
                voice_name=validated_voice,
                language_code=language_code
            )
            
            duration = time.time() - start_time
            
            # Calculate estimated audio duration (rough estimate: ~150 words per minute)
            word_count = len(text.split())
            estimated_audio_duration = (word_count / 150) * 60  # seconds
            
            result = {
                "audio_data": audio_data,
                "duration_seconds": estimated_audio_duration,
                "metadata": {
                    **metadata,
                    "generation_time_seconds": round(duration, 3),
                    "voice_used": validated_voice,
                    "language": language_code,
                    "text_length": len(text),
                    "word_count": word_count,
                    "estimated_duration": estimated_audio_duration,
                    "service": "vertex_ai_tts",
                    "model": "gemini-2.5-flash-preview-tts"
                }
            }
            
            logger.info(f"✅ TTS [GENERATE] Speech generated successfully - {len(audio_data)} bytes, ~{estimated_audio_duration:.1f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ TTS [GENERATE] Failed to generate speech: {str(e)}")
            raise Exception(f"Speech generation failed: {str(e)}")
    
    async def get_available_voices(
        self,
        language_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get list of available voices, optionally filtered by language
        
        Args:
            language_code: Optional language filter
            
        Returns:
            List of voice information dictionaries
        """
        try:
            logger.info(f"🔊 TTS [VOICES] Getting available voices for language: {language_code or 'all'}")
            
            voices = []
            for voice_name, voice_info in self.AVAILABLE_VOICES.items():
                # Filter by language if specified
                if language_code and language_code not in voice_info["languages"]:
                    continue
                
                voice_data = {
                    "name": voice_name,
                    "style": voice_info["style"],
                    "supported_languages": voice_info["languages"],
                    "recommended_for": voice_info["recommended_for"],
                    "available": True  # All voices should be available in Gemini 2.5 TTS
                }
                
                voices.append(voice_data)
            
            logger.info(f"✅ TTS [VOICES] Found {len(voices)} available voices")
            return voices
            
        except Exception as e:
            logger.error(f"❌ TTS [VOICES] Failed to get available voices: {str(e)}")
            raise Exception(f"Failed to get available voices: {str(e)}")
    
    def _validate_voice_for_language(self, voice_name: str, language_code: str) -> str:
        """
        Validate that the requested voice supports the language, fallback if needed
        
        Args:
            voice_name: Requested voice name
            language_code: Target language code
            
        Returns:
            Valid voice name for the language
        """
        # Check if requested voice exists and supports the language
        if voice_name in self.AVAILABLE_VOICES:
            voice_info = self.AVAILABLE_VOICES[voice_name]
            if language_code in voice_info["languages"]:
                return voice_name
            else:
                logger.warning(f"⚠️ TTS [VOICE] Voice '{voice_name}' doesn't support '{language_code}', finding fallback")
        else:
            logger.warning(f"⚠️ TTS [VOICE] Unknown voice '{voice_name}', finding fallback")
        
        # Find fallback voice for this language
        fallback_voice = self._get_default_voice_for_language(language_code)
        logger.info(f"🔄 TTS [VOICE] Using fallback voice '{fallback_voice}' for language '{language_code}'")
        return fallback_voice
    
    def _get_default_voice_for_language(self, language_code: str) -> str:
        """
        Get default voice for a specific language
        
        Args:
            language_code: Language code
            
        Returns:
            Default voice name for the language
        """
        # Default voice preferences by language
        language_defaults = {
            "fr": "Kore",      # Firm, professional for French
            "en": "Puck",      # Upbeat, friendly for English  
            "es": "Aoede",     # Breezy for Spanish
            "de": "Orus"       # Firm for German
        }
        
        preferred_voice = language_defaults.get(language_code, "Kore")
        
        # Verify the preferred voice actually supports this language
        if preferred_voice in self.AVAILABLE_VOICES:
            voice_info = self.AVAILABLE_VOICES[preferred_voice]
            if language_code in voice_info["languages"]:
                return preferred_voice
        
        # Find any voice that supports this language
        for voice_name, voice_info in self.AVAILABLE_VOICES.items():
            if language_code in voice_info["languages"]:
                logger.info(f"🔄 TTS [FALLBACK] Using '{voice_name}' as fallback for '{language_code}'")
                return voice_name
        
        # Ultimate fallback - use Kore (should support most languages)
        logger.warning(f"⚠️ TTS [FALLBACK] No specific voice found for '{language_code}', using Kore")
        return "Kore"
    
    def get_voice_recommendations(self, language_code: str, context: str = "default") -> List[str]:
        """
        Get recommended voices for a specific language and context
        
        Args:
            language_code: Target language
            context: Context for voice selection (default, friendly, formal)
            
        Returns:
            List of recommended voice names
        """
        recommendations = []
        
        for voice_name, voice_info in self.AVAILABLE_VOICES.items():
            if language_code in voice_info["languages"]:
                if voice_info["recommended_for"] == context:
                    recommendations.append(voice_name)
        
        # If no specific recommendations, get default voices for language
        if not recommendations:
            default_voice = self._get_default_voice_for_language(language_code)
            recommendations = [default_voice]
        
        return recommendations