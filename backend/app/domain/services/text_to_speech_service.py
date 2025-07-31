"""
FIA v3.0 - Text-to-Speech Service
Domain service for converting text to speech using Vertex AI
"""

import logging
from typing import Dict, Any, List, Optional

from app.domain.ports.outbound_ports import TTSServicePort

logger = logging.getLogger(__name__)


class TextToSpeechService:
    """Domain service for text-to-speech operations"""
    
    # Voice mapping based on language and context
    VOICE_MAPPING = {
        "fr": {
            "default": "Kore",      # Firm, professional for French
            "friendly": "Aoede",    # Breezy, more casual
            "formal": "Orus"        # Firm, very professional
        },
        "en": {
            "default": "Puck",      # Upbeat, friendly for English
            "friendly": "Fenrir",   # Excitable, energetic
            "formal": "Charon"      # Informative, professional
        },
        "es": {
            "default": "Aoede",     # Breezy for Spanish
            "friendly": "Leda",     # Youthful
            "formal": "Kore"        # Firm, professional
        },
        "de": {
            "default": "Orus",      # Firm for German
            "friendly": "Autonoe",  # Bright
            "formal": "Algieba"     # Smooth, professional
        }
    }
    
    def __init__(self, tts_port: TTSServicePort):
        """Initialize TTS service with port dependency"""
        self.tts_port = tts_port
        logger.info("🔊 TTS [SERVICE] Initialized Text-to-Speech service")
        
    async def generate_speech_for_message(
        self,
        text: str,
        language_code: str = "fr",
        voice_style: str = "default",
        learner_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate speech for a chat message or response
        
        Args:
            text: Text to convert to speech
            language_code: Language code (fr, en, es, de)
            voice_style: Voice style (default, friendly, formal)
            learner_profile: Optional learner profile for voice adaptation
            
        Returns:
            Dict containing audio data and metadata
        """
        try:
            logger.info(f"🔊 TTS [GENERATE] Generating speech - Language: {language_code}, Style: {voice_style}")
            
            # Validate and clean text
            cleaned_text = self._prepare_text_for_speech(text)
            if not cleaned_text:
                raise ValueError("Text is empty or invalid after cleaning")
            
            # Select appropriate voice - use specific requested voice if provided
            if learner_profile and learner_profile.get("requested_voice"):
                voice_name = learner_profile["requested_voice"]
                logger.info(f"🎯 TTS [VOICE] Using specifically requested voice: {voice_name}")
            else:
                voice_name = self._select_voice(language_code, voice_style, learner_profile)
            
            # Generate speech using the port
            speech_result = await self.tts_port.generate_speech(
                text=cleaned_text,
                voice_name=voice_name,
                language_code=language_code
            )
            
            # Add service metadata
            speech_result["metadata"] = {
                **speech_result.get("metadata", {}),
                "service": "text_to_speech",
                "voice_selected": voice_name,
                "language": language_code,
                "style": voice_style,
                "text_length": len(cleaned_text),
                "original_text_length": len(text)
            }
            
            logger.info(f"✅ TTS [GENERATE] Speech generated successfully - Duration: {speech_result.get('duration_seconds', 0):.2f}s")
            return speech_result
            
        except Exception as e:
            logger.error(f"❌ TTS [GENERATE] Failed to generate speech: {str(e)}")
            # Don't provide fallback - let the error bubble up so message is displayed without audio
            raise Exception(f"Speech generation failed: {str(e)}")
    
    async def generate_speech_for_slide_content(
        self,
        slide_content: str,
        slide_title: str,
        learner_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate speech for slide content (introduction, summary, etc.)
        
        Args:
            slide_content: Full slide content in markdown
            slide_title: Title of the slide
            learner_profile: Learner profile for language/voice selection
            
        Returns:
            Dict containing audio data and metadata
        """
        try:
            logger.info(f"🔊 TTS [SLIDE] Generating speech for slide: '{slide_title}'")
            
            # Extract key content for speech (remove markdown formatting)
            speech_text = self._extract_speech_text_from_slide(slide_content, slide_title)
            
            # Get language from learner profile
            language_code = learner_profile.get("language", "fr")
            
            # Use formal style for slide content
            voice_style = "formal" if learner_profile.get("experience_level") == "advanced" else "default"
            
            return await self.generate_speech_for_message(
                text=speech_text,
                language_code=language_code,
                voice_style=voice_style,
                learner_profile=learner_profile
            )
            
        except Exception as e:
            logger.error(f"❌ TTS [SLIDE] Failed to generate slide speech: {str(e)}")
            raise Exception(f"Slide speech generation failed: {str(e)}")
    
    async def get_available_voices_for_language(
        self,
        language_code: str = "fr"
    ) -> List[Dict[str, Any]]:
        """
        Get available voices for a specific language
        
        Args:
            language_code: Language code to filter voices
            
        Returns:
            List of available voices with metadata
        """
        try:
            logger.info(f"🔊 TTS [VOICES] Getting available voices for language: {language_code}")
            
            voices = await self.tts_port.get_available_voices(language_code)
            
            # Add our service-level voice recommendations
            recommended_voices = self.VOICE_MAPPING.get(language_code, {})
            for voice in voices:
                voice_name = voice.get("name", "")
                if voice_name in recommended_voices.values():
                    voice["recommended"] = True
                    # Add context about when to use this voice
                    for style, recommended_name in recommended_voices.items():
                        if voice_name == recommended_name:
                            voice["recommended_for"] = style
                            break
            
            logger.info(f"✅ TTS [VOICES] Found {len(voices)} voices for {language_code}")
            return voices
            
        except Exception as e:
            logger.error(f"❌ TTS [VOICES] Failed to get voices: {str(e)}")
            raise Exception(f"Failed to get available voices: {str(e)}")
    
    def _prepare_text_for_speech(self, text: str) -> str:
        """
        Clean and prepare text for speech synthesis
        
        Args:
            text: Raw text input
            
        Returns:
            Cleaned text ready for TTS
        """
        if not text or not text.strip():
            return ""
        
        # Remove markdown formatting
        import re
        
        # Remove markdown headers
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # Remove markdown bold/italic
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        
        # Remove markdown links
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # Remove markdown code blocks
        text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Limit length for TTS (max 500 characters to avoid too long audio)
        if len(text) > 500:
            # Try to cut at sentence boundary
            sentences = text.split('. ')
            truncated = ""
            for sentence in sentences:
                if len(truncated + sentence + '. ') <= 480:  # Leave room for "..."
                    truncated += sentence + '. '
                else:
                    break
            text = truncated.strip() + "..."
        
        return text.strip()
    
    def _extract_speech_text_from_slide(self, slide_content: str, slide_title: str) -> str:
        """
        Extract key text from slide content for speech synthesis
        
        Args:
            slide_content: Full slide content in markdown
            slide_title: Title of the slide
            
        Returns:
            Key text suitable for speech
        """
        # Start with slide title
        speech_text = f"{slide_title}. "
        
        # Extract first paragraph or key points
        lines = slide_content.split('\n')
        content_lines = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('- ') or line.startswith('* '):
                # List item - clean and add
                clean_line = line[2:].strip()
                if clean_line:
                    content_lines.append(clean_line)
            elif not line.startswith('```') and not line.startswith('|'):
                # Regular paragraph line
                content_lines.append(line)
            
            # Limit content
            if len(content_lines) >= 3:
                break
        
        # Join content
        if content_lines:
            speech_text += " ".join(content_lines[:3])
        
        return self._prepare_text_for_speech(speech_text)
    
    def _select_voice(
        self,
        language_code: str,
        voice_style: str = "default",
        learner_profile: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Select appropriate voice based on language, style and learner profile
        
        Args:
            language_code: Language code
            voice_style: Voice style preference
            learner_profile: Optional learner profile
            
        Returns:
            Voice name to use
        """
        # Get voice mapping for language
        voices = self.VOICE_MAPPING.get(language_code, self.VOICE_MAPPING["fr"])
        
        # Adapt style based on learner profile
        if learner_profile:
            experience_level = learner_profile.get("experience_level", "beginner")
            
            # Adjust style based on experience level
            if experience_level == "beginner" and voice_style == "default":
                voice_style = "friendly"  # More approachable for beginners
            elif experience_level == "advanced" and voice_style == "default":
                voice_style = "formal"  # More professional for advanced users
        
        # Select voice
        selected_voice = voices.get(voice_style, voices["default"])
        
        logger.debug(f"🎯 TTS [VOICE] Selected voice '{selected_voice}' for {language_code}/{voice_style}")
        return selected_voice