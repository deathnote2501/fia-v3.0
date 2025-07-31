"""
FIA v3.0 - Text-to-Speech Outbound Adapter
Simple KISS implementation using only Gemini 2.5 Flash Preview TTS
"""

import logging
from typing import Dict, Any, List, Optional

from app.domain.ports.outbound_ports import TTSServicePort
from app.adapters.outbound.gemini_tts_adapter import GeminiTTSAdapter, GeminiTTSError

logger = logging.getLogger(__name__)


class TTSAdapter(TTSServicePort):
    """
    Simple KISS Text-to-Speech adapter using only Gemini 2.5 Flash Preview TTS
    No fallbacks, no complexity - just direct Gemini TTS
    """
    
    def __init__(self):
        """Initialize TTS adapter with Gemini TTS only"""
        try:
            self.gemini_tts_adapter = GeminiTTSAdapter()
            logger.info("✅ TTS [ADAPTER] Initialized with Gemini 2.5 Flash Preview TTS (KISS)")
        except GeminiTTSError as e:
            logger.error(f"❌ TTS [ADAPTER] Failed to initialize Gemini TTS: {e}")
            raise GeminiTTSError(f"TTS initialization failed: {e}")
        
    async def generate_speech(
        self,
        text: str,
        voice_name: str = "Kore",
        language_code: str = "fr"
    ) -> Dict[str, Any]:
        """
        Generate speech audio from text using Gemini 2.5 Flash Preview TTS
        
        Args:
            text: Text to convert to speech
            voice_name: Voice to use (from Gemini official voices)
            language_code: Language code (fr, en, es, de)
            
        Returns:
            Dict containing audio_data, duration_seconds, and metadata
        """
        try:
            logger.info(f"🔊 TTS [KISS] Generating speech - Voice: {voice_name}, Lang: {language_code}")
            return await self.gemini_tts_adapter.generate_speech(
                text=text,
                voice_name=voice_name,
                language_code=language_code
            )
        except Exception as e:
            logger.error(f"❌ TTS [GENERATE] Failed to generate speech: {str(e)}")
            raise GeminiTTSError(f"Speech generation failed: {str(e)}", e)
    
    async def get_available_voices(
        self,
        language_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get list of available voices from Gemini TTS
        
        Args:
            language_code: Optional language filter
            
        Returns:
            List of voice information dictionaries
        """
        try:
            logger.info(f"🔊 TTS [KISS] Getting available voices")
            return await self.gemini_tts_adapter.get_available_voices(language_code)
        except Exception as e:
            logger.error(f"❌ TTS [VOICES] Failed to get available voices: {str(e)}")
            raise GeminiTTSError(f"Failed to get available voices: {str(e)}", e)
    
