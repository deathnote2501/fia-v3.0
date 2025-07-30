"""
FIA v3.0 - Vertex AI Adapter
Infrastructure adapter for Vertex AI/Gemini API operations
"""

import logging
import os
import json
import asyncio
import time
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timezone

from app.infrastructure.settings import settings

# Configure logger
logger = logging.getLogger(__name__)

# Import Vertex AI with error handling
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, Part
    from google import genai
    from google.genai import types
    import wave
    VERTEX_AI_AVAILABLE = True
    logger.info("🤖 VERTEX AI [ADAPTER] imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ VERTEX AI [ADAPTER] import failed: {e}")
    VERTEX_AI_AVAILABLE = False
    GenerativeModel = None
    Part = None
    genai = None
    types = None


class VertexAIError(Exception):
    """Exception for Vertex AI operations"""
    def __init__(self, message: str, api_response: Optional[str] = None, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.api_response = api_response
        self.original_error = original_error


class VertexAIAdapter:
    """Infrastructure adapter for Vertex AI operations"""
    
    def __init__(self):
        """Initialize Vertex AI adapter"""
        self.client = None
        self.model_name = settings.gemini_model_name
        self.max_retries = 3
        self.retry_delay = 2.0
        
        # Logging setup
        self.structured_logger = logging.getLogger(f"{__name__}.gemini_api")
        self.api_call_counter = 0
        
        # Configure Vertex AI
        self._configure_vertex_ai()
        
        logger.info(f"🤖 VERTEX AI [ADAPTER] initialized with model: {self.model_name}")
    
    def _configure_vertex_ai(self):
        """Configure Vertex AI with proper credentials"""
        try:
            if not VERTEX_AI_AVAILABLE or vertexai is None:
                logger.warning("⚠️ VERTEX AI [ADAPTER] Vertex AI module not available")
                self.client = None
                return
            
            # Set up project and location
            project_id = settings.google_cloud_project
            location = settings.google_cloud_region or "europe-west1"
            
            if not project_id:
                logger.error("⚠️ VERTEX AI [ADAPTER] GOOGLE_CLOUD_PROJECT not configured")
                self.client = None
                return
            
            # Setup credentials if provided as JSON
            if settings.google_credentials_json:
                import tempfile
                import json
                
                # Write credentials to temporary file
                credentials_dict = json.loads(settings.google_credentials_json)
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(credentials_dict, f)
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f.name
                    logger.info("🔑 VERTEX AI [ADAPTER] Using JSON credentials")
            elif settings.google_application_credentials:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.google_application_credentials
                logger.info("🔑 VERTEX AI [ADAPTER] Using credentials file")
            
            # Initialize Vertex AI
            vertexai.init(project=project_id, location=location)
            
            # Create generative model
            self.client = GenerativeModel(
                model_name=self.model_name,
                system_instruction=[
                    "Tu es un expert en pédagogie et formation professionnelle.",
                    "Tu crées des plans de formation personnalisés et structurés.",
                    "Tu réponds UNIQUEMENT en JSON valide selon le schéma fourni.",
                    "Tu adaptes le contenu au profil de l'apprenant (niveau, style, métier)."
                ]
            )
            
            logger.info(f"🤖 VERTEX AI [ADAPTER] configured successfully - Project: {project_id}, Location: {location}")
            
        except Exception as e:
            logger.error(f"❌ VERTEX AI [ADAPTER] configuration failed: {str(e)}")
            self.client = None
            raise VertexAIError(f"Failed to configure Vertex AI: {str(e)}", original_error=e)
    
    def _log_api_call(self, operation: str, request_data: Dict[str, Any], response_data: Dict[str, Any], 
                     duration: float, success: bool = True, error: Optional[str] = None):
        """Log Vertex AI API call in structured format"""
        self.api_call_counter += 1
        
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": operation,
            "call_id": f"vertex_ai_{self.api_call_counter}",
            "model": self.model_name,
            "duration_seconds": round(duration, 3),
            "success": success,
            "request": {
                "prompt_length": len(str(request_data.get("prompt", ""))),
                "has_file": "file_path" in request_data,
                "generation_config": request_data.get("generation_config", {})
            },
            "response": {
                "response_length": len(str(response_data)) if response_data else 0,
                "status": "success" if success else "error"
            }
        }
        
        if error:
            log_entry["error"] = error
        
        # Structured log for monitoring
        self.structured_logger.info(json.dumps(log_entry, ensure_ascii=False))
        
        # Human-readable log
        status_emoji = "✅" if success else "❌"
        logger.info(f"{status_emoji} VERTEX AI [API] {operation} - {duration:.2f}s - Call #{self.api_call_counter}")
    
    async def upload_file_with_retry(self, file_path: str, mime_type: str):
        """Read file locally for Vertex AI processing"""
        if not self.client:
            raise VertexAIError("Vertex AI client not configured")
        
        start_time = time.time()
        
        try:
            logger.info(f"📄 VERTEX AI [FILE] Reading local file - {Path(file_path).name}")
            
            # For Vertex AI, we read the file locally and create a Part
            with open(file_path, "rb") as f:
                file_data = f.read()
            
            # Create Part from data
            file_part = Part.from_data(
                data=file_data,
                mime_type=mime_type
            )
            
            duration = time.time() - start_time
            self._log_api_call(
                "file_read",
                {"file_path": file_path, "mime_type": mime_type, "size_bytes": len(file_data)},
                {"file_loaded": True},
                duration
            )
            
            logger.info(f"✅ VERTEX AI [FILE] File loaded - {Path(file_path).name} ({len(file_data)} bytes)")
            return file_part
            
        except Exception as e:
            duration = time.time() - start_time
            self._log_api_call(
                "file_read",
                {"file_path": file_path, "mime_type": mime_type},
                {},
                duration,
                success=False,
                error=str(e)
            )
            
            logger.error(f"❌ VERTEX AI [FILE] Failed to read {Path(file_path).name}: {str(e)}")
            raise VertexAIError(f"File reading failed: {str(e)}", original_error=e)
    
    async def generate_content_with_grounding(self, prompt, generation_config: Optional[Dict[str, Any]] = None, use_google_search: bool = False) -> tuple[str, Optional[Dict[str, Any]]]:
        """Generate content with optional Google Search grounding using genai.Client"""
        if not VERTEX_AI_AVAILABLE or not genai:
            raise VertexAIError("Vertex AI with grounding not available - missing dependencies")
        
        start_time = time.time()
        
        try:
            # Get project and location from settings
            project_id = settings.google_cloud_project
            location = settings.google_cloud_region or "europe-west1"
            
            if not project_id:
                raise VertexAIError("GOOGLE_CLOUD_PROJECT not configured for grounding")
            
            # Initialize Gemini client for grounding with proper Vertex AI configuration
            client = genai.Client(vertexai=True, project=project_id, location=location)
            
            # Prepare tools and config
            tools = []
            if use_google_search:
                grounding_tool = types.Tool(google_search=types.GoogleSearch())
                tools.append(grounding_tool)
                logger.info("🔍 VERTEX AI [GROUNDING] Google Search tool enabled")
            
            # Prepare generation config
            config_dict = generation_config or {
                "temperature": 0.3,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 4096,
                "response_mime_type": "application/json"
            }
            
            # Create GenerateContentConfig with tools passed separately
            if tools:
                config = types.GenerateContentConfig(
                    tools=tools,
                    **config_dict
                )
            else:
                config = types.GenerateContentConfig(**config_dict)
            
            logger.info(f"🚀 VERTEX AI [GROUNDING] Starting content generation with grounding...")
            logger.info(f"🔍 VERTEX AI [GROUNDING] Use search: {use_google_search}")
            logger.info(f"🔍 VERTEX AI [GROUNDING] Project: {project_id}, Location: {location}")
            logger.info(f"🔍 VERTEX AI [GROUNDING] Prompt length: {len(str(prompt))} characters")
            
            # Generate content with grounding
            response = await asyncio.to_thread(
                client.models.generate_content,
                model="gemini-2.5-flash",
                contents=prompt,
                config=config
            )
            
            duration = time.time() - start_time
            result = response.text
            
            # Extract grounding metadata if available
            grounding_metadata = None
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata'):
                    grounding_metadata = candidate.grounding_metadata
                    sources_count = len(grounding_metadata.grounding_chunks) if hasattr(grounding_metadata, 'grounding_chunks') and grounding_metadata.grounding_chunks else 0
                    logger.info(f"🔍 VERTEX AI [GROUNDING] Grounding metadata found with {sources_count} sources")
            
            # Clean response like in regular generate_content
            if result:
                result_cleaned = result.strip()
                if result_cleaned.startswith('```json'):
                    result_cleaned = result_cleaned[7:]
                if result_cleaned.endswith('```'):
                    result_cleaned = result_cleaned[:-3]
                result = result_cleaned.strip()
            
            self._log_api_call(
                "content_generation_with_grounding",
                {"prompt": str(prompt)[:100] + "...", "generation_config": config_dict, "use_google_search": use_google_search},
                {"response": result[:100] + "...", "has_grounding": grounding_metadata is not None},
                duration
            )
            
            logger.info(f"✅ VERTEX AI [GROUNDING] Success - {len(result)} characters generated with grounding")
            return result, grounding_metadata
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ VERTEX AI [GROUNDING] Exception: {str(e)}")
            
            self._log_api_call(
                "content_generation_with_grounding",
                {"prompt": str(prompt)[:100] + "...", "generation_config": generation_config, "use_google_search": use_google_search},
                {},
                duration,
                success=False,
                error=str(e)
            )
            
            raise VertexAIError(f"Content generation with grounding failed: {str(e)}", original_error=e)

    async def generate_content(self, prompt, generation_config: Optional[Dict[str, Any]] = None) -> str:
        """Generate content using Vertex AI with Structured Output"""
        if not self.client:
            raise VertexAIError("Vertex AI client not configured")
        
        start_time = time.time()
        
        try:
            # Prepare generation config - SIMPLE comme l'ancien service
            config = generation_config or {
                "temperature": 0.1,  # Plus bas pour consistance JSON
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json"  # Pas de response_schema complexe
            }
            
            # LOG DÉTAILLÉ INPUT
            logger.info(f"🚀 VERTEX AI [GENERATE] Starting content generation with Structured Output...")
            logger.info(f"🔍 VERTEX AI [INPUT] Generation config: {json.dumps(config, indent=2)}")
            logger.info(f"🔍 VERTEX AI [INPUT] Prompt type: {type(prompt)}")
            logger.info(f"🔍 VERTEX AI [INPUT] Prompt length: {len(str(prompt))} characters")
            logger.info(f"🔍 VERTEX AI [INPUT] === DÉBUT PROMPT COMPLET ===")
            logger.info(f"🔍 VERTEX AI [INPUT] {str(prompt)}")
            logger.info(f"🔍 VERTEX AI [INPUT] === FIN PROMPT COMPLET ===")
            
            # Generate content (synchronous call wrapped in asyncio.to_thread)
            response = await asyncio.to_thread(
                self.client.generate_content,
                prompt,
                generation_config=config
            )
            
            duration = time.time() - start_time
            result = response.text
            
            # LOG DÉTAILLÉ OUTPUT
            logger.info(f"🔍 VERTEX AI [OUTPUT] Response object type: {type(response)}")
            logger.info(f"🔍 VERTEX AI [OUTPUT] Response object attributes: {dir(response)}")
            logger.info(f"🔍 VERTEX AI [OUTPUT] Response text type: {type(result)}")
            logger.info(f"🔍 VERTEX AI [OUTPUT] Response text length: {len(result) if result else 0} characters")
            logger.info(f"🔍 VERTEX AI [OUTPUT] === DÉBUT RÉPONSE VERTEX AI COMPLÈTE ===")
            logger.info(f"🔍 VERTEX AI [OUTPUT] {result}")
            logger.info(f"🔍 VERTEX AI [OUTPUT] === FIN RÉPONSE VERTEX AI COMPLÈTE ===")
            
            # Vérifier si on a des métadonnées d'usage
            if hasattr(response, 'usage_metadata'):
                logger.info(f"🔍 VERTEX AI [METADATA] Usage metadata: {response.usage_metadata}")
            
            # Plus de duplication de logs, continuer avec le nettoyage
            
            # NETTOYER LA RÉPONSE comme dans l'ancien service
            if result:
                result_cleaned = result.strip()
                
                # Nettoyer les balises markdown JSON
                if result_cleaned.startswith('```json'):
                    result_cleaned = result_cleaned[7:]
                    logger.info(f"🧹 VERTEX AI [CLEAN] Removed ```json prefix")
                if result_cleaned.endswith('```'):
                    result_cleaned = result_cleaned[:-3]
                    logger.info(f"🧹 VERTEX AI [CLEAN] Removed ``` suffix")
                result_cleaned = result_cleaned.strip()
                
                logger.info(f"🔍 VERTEX AI [CLEANED] Cleaned length: {len(result_cleaned)}")
                logger.info(f"🔍 VERTEX AI [CLEANED_TEXT] Cleaned text: {repr(result_cleaned[:200])}")
                
                if result_cleaned:
                    try:
                        # Test JSON parsing sur texte nettoyé
                        parsed = json.loads(result_cleaned)
                        logger.info(f"✅ VERTEX AI [JSON_VALID] JSON parsing successful: {type(parsed)}")
                        result = result_cleaned  # Utiliser la version nettoyée
                    except json.JSONDecodeError as e:
                        logger.error(f"❌ VERTEX AI [JSON_INVALID] JSON parsing failed: {e}")
                        logger.error(f"❌ VERTEX AI [JSON_INVALID] Error at position {e.pos}")
                        logger.error(f"❌ VERTEX AI [JSON_INVALID] Problematic text around error: {repr(result_cleaned[max(0, e.pos-20):e.pos+20])}")
                else:
                    logger.error(f"❌ VERTEX AI [EMPTY] Response is empty after cleaning!")
            else:
                logger.error(f"❌ VERTEX AI [EMPTY] Response is empty or None!")
            
            self._log_api_call(
                "content_generation",
                {"prompt": str(prompt)[:100] + "...", "generation_config": config},
                {"response": result[:100] + "..."},
                duration
            )
            
            logger.info(f"✅ VERTEX AI [GENERATE] Success - {len(result)} characters generated with structured JSON")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            # DETAILED ERROR LOGGING
            logger.error(f"❌ VERTEX AI [EXCEPTION] Exception type: {type(e).__name__}")
            logger.error(f"❌ VERTEX AI [EXCEPTION] Exception message: {str(e)}")
            logger.error(f"❌ VERTEX AI [EXCEPTION] Exception args: {e.args}")
            
            self._log_api_call(
                "content_generation",
                {"prompt": str(prompt)[:100] + "...", "generation_config": generation_config},
                {},
                duration,
                success=False,
                error=str(e)
            )
            
            logger.error(f"❌ VERTEX AI [GENERATE] Failed: {str(e)}")
            raise VertexAIError(f"Content generation failed: {str(e)}", original_error=e)
    
    async def generate_with_file(self, prompt: str, file_path: str, mime_type: str, 
                                generation_config: Optional[Dict[str, Any]] = None) -> str:
        """Generate content with file context and Document AI"""
        if not self.client:
            raise VertexAIError("Vertex AI client not configured")
        
        try:
            # Upload file first
            file_part = await self.upload_file_with_retry(file_path, mime_type)
            
            # Create proper content structure for Vertex AI
            contents = [file_part, prompt]
            
            # Prepare generation config - for document analysis, return text not JSON
            config = generation_config or {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 8192
            }
            
            start_time = time.time()
            logger.info(f"🚀 VERTEX AI [FILE_GENERATE] Generating with file context and Document AI...")
            
            # Generate with file context using Vertex AI Document Understanding
            response = await asyncio.to_thread(
                self.client.generate_content,
                contents,  # Pass the list correctly 
                generation_config=config
            )
            
            duration = time.time() - start_time
            result = response.text
            
            self._log_api_call(
                "file_generation",
                {"file_path": file_path, "prompt": prompt[:100] + "...", "generation_config": generation_config or {}},
                {"response": result[:100] + "..."},
                duration
            )
            
            logger.info(f"✅ VERTEX AI [FILE_GENERATE] Success - {len(result)} characters generated with Document AI")
            return result
            
        except Exception as e:
            logger.error(f"❌ VERTEX AI [FILE_GENERATE] Failed: {str(e)}")
            raise VertexAIError(f"File-based generation failed: {str(e)}", original_error=e)
    
    def is_available(self) -> bool:
        """Check if Vertex AI is available and configured"""
        try:
            # Quick test to verify credentials
            if VERTEX_AI_AVAILABLE and self.client is not None:
                # Don't actually call API, just check if client exists
                return True
            return False
        except Exception:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics"""
        return {
            "available": self.is_available(),
            "model_name": self.model_name,
            "api_calls_made": self.api_call_counter,
            "max_retries": self.max_retries
        }
    
    async def generate_speech_audio(
        self,
        text: str,
        voice_name: str = "Kore",
        language_code: str = "fr"
    ) -> tuple[bytes, Dict[str, Any]]:
        """
        Generate speech audio using Vertex AI Gemini 2.5 TTS
        
        Args:
            text: Text to convert to speech
            voice_name: Voice name (e.g., 'Kore', 'Puck', 'Aoede')
            language_code: Language code (e.g., 'fr', 'en', 'es')
            
        Returns:
            Tuple of (audio_data_bytes, metadata_dict)
        """
        if not VERTEX_AI_AVAILABLE or not genai:
            raise VertexAIError("Vertex AI TTS not available - missing dependencies")
        
        start_time = time.time()
        
        try:
            # Initialize Gemini client for TTS
            client = genai.Client()
            
            # Prepare TTS prompt with voice style guidance
            tts_prompt = self._build_tts_prompt(text, voice_name, language_code)
            
            logger.info(f"🔊 VERTEX AI [TTS] Generating speech - Voice: {voice_name}, Lang: {language_code}, Text: {len(text)} chars")
            
            # Generate speech using Gemini 2.5 TTS
            response = await asyncio.to_thread(
                client.models.generate_content,
                model="gemini-2.5-flash-preview-tts",
                contents=tts_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice_name
                            )
                        )
                    )
                )
            )
            
            # Extract audio data
            if not response.candidates or not response.candidates[0].content.parts:
                raise VertexAIError("No audio data in TTS response")
            
            audio_part = response.candidates[0].content.parts[0]
            if not hasattr(audio_part, 'inline_data') or not audio_part.inline_data:
                raise VertexAIError("No inline audio data in TTS response")
            
            # Get raw PCM data from Gemini TTS
            pcm_data = audio_part.inline_data.data
            
            # Convert PCM to WAV format for browser compatibility
            audio_data = self._pcm_to_wav(pcm_data)
            
            duration = time.time() - start_time
            
            # Log API call
            self._log_api_call(
                "tts_generation",
                {
                    "text_length": len(text),
                    "voice_name": voice_name,
                    "language_code": language_code
                },
                {
                    "audio_size_bytes": len(audio_data),
                    "success": True
                },
                duration
            )
            
            metadata = {
                "voice_used": voice_name,
                "language": language_code,
                "generation_time_seconds": round(duration, 3),
                "audio_format": "wav",
                "audio_size_bytes": len(audio_data),
                "model": "gemini-2.5-flash-preview-tts"
            }
            
            logger.info(f"✅ VERTEX AI [TTS] Speech generated - {len(audio_data)} bytes in {duration:.2f}s")
            return audio_data, metadata
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Log failed API call
            self._log_api_call(
                "tts_generation",
                {
                    "text_length": len(text),
                    "voice_name": voice_name,
                    "language_code": language_code
                },
                {},
                duration,
                success=False,
                error=str(e)
            )
            
            logger.error(f"❌ VERTEX AI [TTS] Speech generation failed: {str(e)}")
            raise VertexAIError(f"TTS generation failed: {str(e)}", original_error=e)
    
    def _pcm_to_wav(self, pcm_data: bytes, sample_rate: int = 24000, channels: int = 1, sample_width: int = 2) -> bytes:
        """
        Convert PCM raw audio data to WAV format
        
        Args:
            pcm_data: Raw PCM audio data from Gemini TTS
            sample_rate: Sample rate (default 24000 Hz for Gemini TTS)
            channels: Number of channels (default 1 for mono)
            sample_width: Sample width in bytes (default 2 for 16-bit)
            
        Returns:
            WAV formatted audio data
        """
        import io
        
        try:
            # Create in-memory WAV file
            wav_buffer = io.BytesIO()
            
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(channels)
                wav_file.setsampwidth(sample_width)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(pcm_data)
            
            wav_data = wav_buffer.getvalue()
            wav_buffer.close()
            
            logger.info(f"🔊 VERTEX AI [TTS] PCM to WAV conversion: {len(pcm_data)} -> {len(wav_data)} bytes")
            return wav_data
            
        except Exception as e:
            logger.error(f"❌ VERTEX AI [TTS] PCM to WAV conversion failed: {str(e)}")
            raise VertexAIError(f"Audio format conversion failed: {str(e)}", original_error=e)
    
    def _build_tts_prompt(self, text: str, voice_name: str, language_code: str) -> str:
        """
        Build TTS prompt with appropriate voice style guidance
        
        Args:
            text: Text to convert to speech
            voice_name: Voice name to use
            language_code: Language code
            
        Returns:
            Formatted prompt for TTS
        """
        # Voice style mapping for better TTS results
        voice_styles = {
            "Kore": "in a firm, professional tone",
            "Puck": "in an upbeat, friendly tone", 
            "Aoede": "in a breezy, pleasant tone",
            "Orus": "in a firm, authoritative tone",
            "Charon": "in an informative, clear tone",
            "Algieba": "in a smooth, polished tone",
            "Fenrir": "in an excitable, energetic tone",
            "Leda": "in a youthful, engaging tone"
        }
        
        style_guidance = voice_styles.get(voice_name, "in a natural, pedagogical tone")
        
        # Language-specific prompt formatting
        if language_code == "fr":
            prompt = f"Dis de manière claire et pédagogique {style_guidance} : {text}"
        elif language_code == "en":
            prompt = f"Say clearly and pedagogically {style_guidance}: {text}"
        elif language_code == "es":
            prompt = f"Di de manera clara y pedagógica {style_guidance}: {text}"
        elif language_code == "de":
            prompt = f"Sage klar und pädagogisch {style_guidance}: {text}"
        else:
            # Fallback to English
            prompt = f"Say clearly and pedagogically {style_guidance}: {text}"
        
        return prompt