"""
FIA v3.0 - Gemini TTS Adapter
Direct implementation of Gemini 2.5 Flash Preview TTS according to official documentation
"""

import logging
import asyncio
import time
import struct
from typing import Dict, Any, Optional, List

from app.domain.ports.outbound_ports import TTSServicePort
from app.infrastructure.settings import settings
from app.infrastructure.rate_limiter import gemini_rate_limiter

# Configure logger
logger = logging.getLogger(__name__)

# Import Gemini with error handling
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
    logger.info("🤖 GEMINI TTS [ADAPTER] Imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ GEMINI TTS [ADAPTER] Import failed: {e}")
    GENAI_AVAILABLE = False
    genai = None
    types = None


class GeminiTTSError(Exception):
    """Exception for Gemini TTS operations"""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error


def pcm_to_wav(pcm_data: bytes, sample_rate: int = 24000, channels: int = 1, bits_per_sample: int = 16) -> bytes:
    """
    Convert raw PCM data to WAV format with proper headers
    """
    # Calculate sizes
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8
    data_size = len(pcm_data)
    file_size = 36 + data_size
    
    # WAV header structure
    wav_header = struct.pack('<4sI4s4sIHHIIHH4sI',
        b'RIFF',           # ChunkID
        file_size,         # ChunkSize
        b'WAVE',           # Format
        b'fmt ',           # Subchunk1ID
        16,                # Subchunk1Size (PCM)
        1,                 # AudioFormat (PCM = 1)
        channels,          # NumChannels
        sample_rate,       # SampleRate
        byte_rate,         # ByteRate
        block_align,       # BlockAlign
        bits_per_sample,   # BitsPerSample
        b'data',           # Subchunk2ID
        data_size          # Subchunk2Size
    )
    
    return wav_header + pcm_data


class GeminiTTSAdapter(TTSServicePort):
    """
    Direct Gemini 2.5 Flash Preview TTS implementation
    Based on official Google AI documentation
    """
    
    # Official voices from Gemini TTS documentation (30 voices available)
    OFFICIAL_VOICES = {
        # Bright voices
        "Zephyr": {"style": "Bright", "languages": ["fr", "en", "es", "de"]},
        "Autonoe": {"style": "Bright", "languages": ["fr", "en", "es", "de"]},
        
        # Firm voices
        "Kore": {"style": "Firm", "languages": ["fr", "en", "es", "de"]},
        "Orus": {"style": "Firm", "languages": ["fr", "en", "es", "de"]},
        "Alnilam": {"style": "Firm", "languages": ["fr", "en", "es", "de"]},
        
        # Upbeat voices
        "Puck": {"style": "Upbeat", "languages": ["en", "fr"]},
        "Laomedeia": {"style": "Upbeat", "languages": ["en", "fr"]},
        
        # Informative voices
        "Charon": {"style": "Informative", "languages": ["en", "fr", "de"]},
        "Rasalgethi": {"style": "Informative", "languages": ["en", "fr", "de"]},
        
        # Smooth voices
        "Algieba": {"style": "Smooth", "languages": ["fr", "en", "es"]},
        "Despina": {"style": "Smooth", "languages": ["fr", "en", "es"]},
        
        # Breezy voices
        "Aoede": {"style": "Breezy", "languages": ["fr", "en", "es"]},
        
        # Specialized voices
        "Fenrir": {"style": "Excitable", "languages": ["en"]},
        "Leda": {"style": "Youthful", "languages": ["es", "en"]},
        "Callirrhoe": {"style": "Easy-going", "languages": ["en", "fr"]},
        "Iapetus": {"style": "Clear", "languages": ["en", "fr"]},
        "Umbriel": {"style": "Easy-going", "languages": ["en", "fr"]},
        "Erinome": {"style": "Clear", "languages": ["en", "fr"]},
        "Enceladus": {"style": "Breathy", "languages": ["en"]},
        "Schedar": {"style": "Even", "languages": ["en"]},
        "Achird": {"style": "Friendly", "languages": ["en"]},
        "Zubenelgenubi": {"style": "Casual", "languages": ["en"]},
        "Sadachbia": {"style": "Lively", "languages": ["en"]},
        "Algenib": {"style": "Gravelly", "languages": ["en"]},
        "Achernar": {"style": "Soft", "languages": ["en"]},
        "Gacrux": {"style": "Mature", "languages": ["en"]},
        "Pulcherrima": {"style": "Forward", "languages": ["en"]},
        "Vindemiatrix": {"style": "Gentle", "languages": ["en"]},
        "Sadaltager": {"style": "Knowledgeable", "languages": ["en"]},
        "Sulafat": {"style": "Warm", "languages": ["en"]}
    }
    
    def __init__(self):
        """Initialize Gemini TTS adapter"""
        if not GENAI_AVAILABLE:
            raise GeminiTTSError("Gemini AI library not available")
            
        self.client = None
        self._initialize_client()
        logger.info("🔊 GEMINI TTS [ADAPTER] Initialized with official Gemini 2.5 Flash Preview TTS")
        
    def _initialize_client(self):
        """Initialize Gemini client according to official documentation"""
        try:
            if settings.gemini_api_key:
                # Use API key for direct Gemini API (preferred for TTS)
                self.client = genai.Client(api_key=settings.gemini_api_key)
                logger.info("✅ GEMINI TTS [CLIENT] Initialized with direct API key")
            else:
                logger.warning("⚠️ GEMINI TTS [CLIENT] GEMINI_API_KEY not configured")
                raise GeminiTTSError("GEMINI_API_KEY required for TTS Preview model - please configure it for optimal TTS")
            
        except Exception as e:
            logger.error(f"❌ GEMINI TTS [CLIENT] Failed to initialize: {str(e)}")
            raise GeminiTTSError(f"Failed to initialize Gemini client: {str(e)}", e)
    
    async def generate_speech(
        self,
        text: str,
        voice_name: str = "Kore",
        language_code: str = "fr"
    ) -> Dict[str, Any]:
        """
        Generate speech audio using Gemini 2.5 Flash Preview TTS
        Implementation based on official documentation
        
        Args:
            text: Text to convert to speech
            voice_name: Voice name (must be from OFFICIAL_VOICES)
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
            
            # Create styled prompt according to documentation
            styled_prompt = self._create_styled_prompt(text, language_code)
            
            logger.info(f"🔊 GEMINI TTS [GENERATE] Generating speech - Voice: {validated_voice}, Lang: {language_code}, Text: {len(text)} chars")
            
            # Generate speech using official Gemini 2.5 Flash Preview TTS API
            response = await asyncio.to_thread(
                self._call_gemini_tts,
                styled_prompt,
                validated_voice
            )
            
            # Extract audio data from Gemini TTS response with detailed debugging
            try:
                logger.info(f"🔍 GEMINI TTS [DEBUG] Response type: {type(response)}")
                logger.info(f"🔍 GEMINI TTS [DEBUG] Response attributes: {dir(response)}")
                
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    logger.info(f"🔍 GEMINI TTS [DEBUG] Candidate type: {type(candidate)}")
                    logger.info(f"🔍 GEMINI TTS [DEBUG] Candidate attributes: {dir(candidate)}")
                    
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        part = candidate.content.parts[0]
                        logger.info(f"🔍 GEMINI TTS [DEBUG] Part type: {type(part)}")
                        logger.info(f"🔍 GEMINI TTS [DEBUG] Part attributes: {dir(part)}")
                        
                        if hasattr(part, 'inline_data'):
                            logger.info(f"🔍 GEMINI TTS [DEBUG] inline_data type: {type(part.inline_data)}")
                            logger.info(f"🔍 GEMINI TTS [DEBUG] inline_data attributes: {dir(part.inline_data)}")
                            
                            # Get MIME type and data from inline_data
                            inline_data = part.inline_data
                            mime_type_from_response = getattr(inline_data, 'mime_type', 'audio/wav')
                            logger.info(f"🔍 GEMINI TTS [DEBUG] MIME type from response: {mime_type_from_response}")
                            
                            # Check if it's already base64 encoded or raw bytes
                            raw_data = inline_data.data
                            logger.info(f"🔍 GEMINI TTS [DEBUG] Raw data type: {type(raw_data)}")
                            logger.info(f"🔍 GEMINI TTS [DEBUG] Raw data length: {len(raw_data)}")
                            logger.info(f"🔍 GEMINI TTS [DEBUG] First 50 chars: {str(raw_data)[:50]}")
                            
                            import base64
                            
                            # Handle both bytes and string data from Gemini
                            if isinstance(raw_data, bytes):
                                # Check audio header to determine actual format
                                if raw_data.startswith(b'ID3') or (len(raw_data) > 8 and raw_data[4:8] == b'ftyp'):
                                    actual_format = "mp3"
                                    processed_data = raw_data
                                elif raw_data.startswith(b'RIFF'):
                                    actual_format = "wav"
                                    processed_data = raw_data
                                elif raw_data.startswith(b'OggS'):
                                    actual_format = "ogg"
                                    processed_data = raw_data
                                else:
                                    # Check if it's PCM based on MIME type
                                    if "L16" in mime_type_from_response or "pcm" in mime_type_from_response.lower():
                                        logger.info(f"🎵 GEMINI TTS [PCM] Converting raw PCM to WAV - {len(raw_data)} bytes")
                                        processed_data = pcm_to_wav(raw_data, sample_rate=24000, channels=1, bits_per_sample=16)
                                        actual_format = "wav"
                                        logger.info(f"✅ GEMINI TTS [PCM] Converted to WAV - {len(processed_data)} bytes")
                                    else:
                                        actual_format = "unknown"
                                        processed_data = raw_data
                                        logger.warning(f"⚠️ GEMINI TTS [FORMAT] Unknown audio format - first 20 bytes: {raw_data[:20]}")
                                
                                audio_data = base64.b64encode(processed_data).decode('utf-8')
                                logger.info(f"🔊 GEMINI TTS [CONVERT] Processed {actual_format} to base64 - {len(processed_data)} bytes -> {len(audio_data)} chars")
                                
                            elif isinstance(raw_data, str):
                                # Check if it's valid base64
                                try:
                                    # Test if it's valid base64 and decode
                                    decoded_test = base64.b64decode(raw_data)
                                    logger.info(f"🔊 GEMINI TTS [EXTRACT] Valid base64 string - {len(raw_data)} chars -> {len(decoded_test)} bytes")
                                    
                                    # Check audio header to determine actual format
                                    if decoded_test.startswith(b'ID3') or (len(decoded_test) > 8 and decoded_test[4:8] == b'ftyp'):
                                        actual_format = "mp3"
                                        processed_data = decoded_test
                                    elif decoded_test.startswith(b'RIFF'):
                                        actual_format = "wav"
                                        processed_data = decoded_test
                                    elif decoded_test.startswith(b'OggS'):
                                        actual_format = "ogg"
                                        processed_data = decoded_test
                                    else:
                                        # Check if it's PCM based on MIME type
                                        if "L16" in mime_type_from_response or "pcm" in mime_type_from_response.lower():
                                            logger.info(f"🎵 GEMINI TTS [PCM] Converting decoded PCM to WAV - {len(decoded_test)} bytes")
                                            processed_data = pcm_to_wav(decoded_test, sample_rate=24000, channels=1, bits_per_sample=16)
                                            actual_format = "wav"
                                            logger.info(f"✅ GEMINI TTS [PCM] Converted to WAV - {len(processed_data)} bytes")
                                        else:
                                            actual_format = "unknown"
                                            processed_data = decoded_test
                                            logger.warning(f"⚠️ GEMINI TTS [FORMAT] Unknown audio format - first 20 bytes: {decoded_test[:20]}")
                                    
                                    # Re-encode to base64
                                    audio_data = base64.b64encode(processed_data).decode('utf-8')
                                    logger.info(f"🎵 GEMINI TTS [FORMAT] Processed {actual_format} - final size: {len(audio_data)} chars")
                                    
                                except Exception as b64_error:
                                    # Not valid base64, treat as text and encode
                                    audio_data = base64.b64encode(raw_data.encode('utf-8')).decode('utf-8')
                                    actual_format = "unknown"
                                    logger.warning(f"🔊 GEMINI TTS [CONVERT] Invalid base64, encoded text: {b64_error}")
                            else:
                                # Handle other data types (e.g., buffer objects)
                                try:
                                    # Try to convert to bytes first
                                    audio_bytes = bytes(raw_data)
                                    audio_data = base64.b64encode(audio_bytes).decode('utf-8')
                                    actual_format = "unknown"
                                    logger.info(f"🔊 GEMINI TTS [CONVERT] Converted {type(raw_data)} to base64 - {len(audio_data)} chars")
                                except Exception as convert_error:
                                    logger.error(f"❌ GEMINI TTS [CONVERT] Failed to convert {type(raw_data)} to bytes: {convert_error}")
                                    raise GeminiTTSError(f"Unsupported audio data type: {type(raw_data)}", convert_error)
                                
                        elif hasattr(part, 'data'):
                            audio_data = part.data
                        else:
                            raise GeminiTTSError("No audio data found in response part")
                    else:
                        raise GeminiTTSError("No content.parts found in response candidate")
                else:
                    raise GeminiTTSError("No candidates found in response")
                    
                logger.info(f"🔊 GEMINI TTS [EXTRACT] Final audio data length: {len(audio_data)}")
                
            except Exception as e:
                logger.error(f"❌ GEMINI TTS [EXTRACT] Failed to extract audio data: {str(e)}")
                logger.error(f"❌ GEMINI TTS [EXTRACT] Response structure: {type(response)}")
                raise GeminiTTSError(f"Failed to extract audio data from response: {str(e)}", e)
                
            generation_time = time.time() - start_time
            
            # Calculate estimated duration (rough estimate: ~150 words per minute)
            word_count = len(text.split())
            estimated_duration = (word_count / 150) * 60  # seconds
            
            # Use detected format or fallback
            try:
                detected_audio_format = actual_format if 'actual_format' in locals() else "wav"
            except:
                detected_audio_format = "wav"
                
            result = {
                "audio_data": audio_data,
                "duration_seconds": estimated_duration,
                "metadata": {
                    "generation_time_seconds": round(generation_time, 3),
                    "voice_used": validated_voice,
                    "language": language_code,
                    "text_length": len(text),
                    "word_count": word_count,
                    "estimated_duration": estimated_duration,
                    "service": "gemini_2.5_flash_preview_tts",
                    "format": detected_audio_format,
                    "mime_type_from_response": mime_type_from_response if 'mime_type_from_response' in locals() else "audio/wav",
                    "sample_rate": 24000,
                    "channels": 1
                }
            }
            
            logger.info(f"✅ GEMINI TTS [GENERATE] Speech generated successfully - {len(audio_data)} bytes, ~{estimated_duration:.1f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ GEMINI TTS [GENERATE] Failed to generate speech: {str(e)}")
            raise GeminiTTSError(f"Speech generation failed: {str(e)}", e)
    
    def _call_gemini_tts(self, prompt: str, voice_name: str):
        """
        Call Gemini TTS API according to official documentation
        """
        return self.client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_name
                        )
                    )
                ),
            )
        )
    
    def _create_styled_prompt(self, text: str, language_code: str) -> str:
        """
        Create styled prompt according to official documentation
        """
        # Style instructions by language according to documentation
        style_instructions = {
            "fr": "Dis de manière claire et amicale :",
            "en": "Say in a friendly and clear voice:",
            "es": "Di de manera clara y amigable:",
            "de": "Sage freundlich und klar:"
        }
        
        instruction = style_instructions.get(language_code, style_instructions["en"])
        return f"{instruction} {text}"
    
    def _validate_voice_for_language(self, voice_name: str, language_code: str) -> str:
        """
        Validate that the requested voice supports the language
        """
        # Check if requested voice exists and supports the language
        if voice_name in self.OFFICIAL_VOICES:
            voice_info = self.OFFICIAL_VOICES[voice_name]
            if language_code in voice_info["languages"]:
                return voice_name
            else:
                logger.warning(f"⚠️ GEMINI TTS [VOICE] Voice '{voice_name}' doesn't support '{language_code}', finding fallback")
        else:
            logger.warning(f"⚠️ GEMINI TTS [VOICE] Unknown voice '{voice_name}', finding fallback")
        
        # Find fallback voice for this language
        fallback_voice = self._get_default_voice_for_language(language_code)
        logger.info(f"🔄 GEMINI TTS [VOICE] Using fallback voice '{fallback_voice}' for language '{language_code}'")
        return fallback_voice
    
    def _get_default_voice_for_language(self, language_code: str) -> str:
        """
        Get default voice for a specific language based on official voices
        """
        # Default voice preferences by language (from official documentation)
        language_defaults = {
            "fr": "Kore",      # Firm, professional for French
            "en": "Puck",      # Upbeat, friendly for English  
            "es": "Aoede",     # Breezy for Spanish
            "de": "Orus"       # Firm for German
        }
        
        preferred_voice = language_defaults.get(language_code, "Kore")
        
        # Verify the preferred voice actually supports this language
        if preferred_voice in self.OFFICIAL_VOICES:
            voice_info = self.OFFICIAL_VOICES[preferred_voice]
            if language_code in voice_info["languages"]:
                return preferred_voice
        
        # Find any voice that supports this language
        for voice_name, voice_info in self.OFFICIAL_VOICES.items():
            if language_code in voice_info["languages"]:
                logger.info(f"🔄 GEMINI TTS [FALLBACK] Using '{voice_name}' as fallback for '{language_code}'")
                return voice_name
        
        # Ultimate fallback - use Kore (supports most languages)
        logger.warning(f"⚠️ GEMINI TTS [FALLBACK] No specific voice found for '{language_code}', using Kore")
        return "Kore"
    
    async def get_available_voices(
        self,
        language_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get list of available voices from official documentation
        """
        try:
            logger.info(f"🔊 GEMINI TTS [VOICES] Getting available voices for language: {language_code or 'all'}")
            
            voices = []
            for voice_name, voice_info in self.OFFICIAL_VOICES.items():
                # Filter by language if specified
                if language_code and language_code not in voice_info["languages"]:
                    continue
                
                voice_data = {
                    "name": voice_name,
                    "style": voice_info["style"],
                    "supported_languages": voice_info["languages"],
                    "available": True  # All official voices are available
                }
                
                voices.append(voice_data)
            
            logger.info(f"✅ GEMINI TTS [VOICES] Found {len(voices)} available voices")
            return voices
            
        except Exception as e:
            logger.error(f"❌ GEMINI TTS [VOICES] Failed to get available voices: {str(e)}")
            raise GeminiTTSError(f"Failed to get available voices: {str(e)}", e)