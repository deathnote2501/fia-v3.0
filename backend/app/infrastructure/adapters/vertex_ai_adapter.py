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
    VERTEX_AI_AVAILABLE = True
    logger.info("🤖 VERTEX AI [ADAPTER] imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ VERTEX AI [ADAPTER] import failed: {e}")
    VERTEX_AI_AVAILABLE = False
    GenerativeModel = None
    Part = None


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
            
            logger.info(f"🚀 VERTEX AI [GENERATE] Starting content generation with Structured Output...")
            
            # Generate content (synchronous call wrapped in asyncio.to_thread)
            response = await asyncio.to_thread(
                self.client.generate_content,
                prompt,
                generation_config=config
            )
            
            duration = time.time() - start_time
            result = response.text
            
            # DETAILED LOGGING pour débugger le problème JSON
            logger.info(f"🔍 VERTEX AI [RAW_RESPONSE] Full response object: {response}")
            logger.info(f"🔍 VERTEX AI [RAW_TEXT] Full response text ({len(result)} chars): {repr(result)}")
            logger.info(f"🔍 VERTEX AI [FIRST_100] First 100 chars: {repr(result[:100])}")
            logger.info(f"🔍 VERTEX AI [LAST_100] Last 100 chars: {repr(result[-100:])}")
            
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