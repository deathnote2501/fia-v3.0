"""
FIA v3.0 - AI Training Generation Service
Service for generating training content using VertexAI Gemini 2.5 Flash
"""

import logging
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone

# Domain ports
from app.domain.ports.ai_adapter_port import AIAdapterPort, AIError, RateLimitExceededException
from app.domain.ports.settings_port import SettingsPort
from app.domain.ports.rate_limiter_port import RateLimiterPort

# Vertex AI imports for specialized model
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    import os
    import tempfile
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    GenerativeModel = None

# Configure logger
logger = logging.getLogger(__name__)

# Model configuration for AI training generation
AI_TRAINING_MODEL = "gemini-2.5-flash"  # Thinking mode for complex training content generation


class AITrainingGenerationError(Exception):
    """Exception for AI training generation errors"""
    def __init__(self, message: str, error_type: str = "generation_error", original_error: Optional[Exception] = None):
        super().__init__(message)
        self.error_type = error_type
        self.original_error = original_error


class AITrainingGenerationService:
    """Service for generating training content using VertexAI"""
    
    # Standard error message for users
    USER_ERROR_MESSAGE = "AI training generation is temporarily unavailable. Please try again later or contact support."
    
    def __init__(
        self, 
        ai_adapter: AIAdapterPort, 
        settings_port: SettingsPort, 
        rate_limiter: RateLimiterPort
    ):
        """Initialize AI training generation service with dependency injection"""
        self.ai_adapter = ai_adapter
        self.settings = settings_port
        self.rate_limiter = rate_limiter
        self.api_call_counter = 0
        self.model_name = AI_TRAINING_MODEL  # Use specialized model for training generation
        self.specialized_client = None
        
        # Initialize specialized client for AI training generation
        self._initialize_specialized_client()
        
        logger.info(f"🤖 AI_TRAINING_GEN [SERVICE] Initialized with model: {self.model_name}")
    
    def _initialize_specialized_client(self):
        """Initialize specialized Vertex AI client with Gemini 2.5 Flash"""
        try:
            if not VERTEX_AI_AVAILABLE or not vertexai:
                logger.warning("⚠️ AI_TRAINING_GEN [CLIENT] Vertex AI module not available")
                self.specialized_client = None
                return
            
            # Set up project and location
            project_id = self.settings.get_google_cloud_project()
            location = self.settings.get_google_cloud_region() or "europe-west1"
            
            if not project_id:
                logger.error("⚠️ AI_TRAINING_GEN [CLIENT] GOOGLE_CLOUD_PROJECT not configured")
                self.specialized_client = None
                return
            
            # Setup credentials if provided as JSON
            google_credentials_json = self.settings.get_setting('GOOGLE_CREDENTIALS_JSON')
            if google_credentials_json:
                import json
                
                # Write credentials to temporary file
                credentials_dict = json.loads(google_credentials_json)
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(credentials_dict, f)
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f.name
                    logger.info("🔑 AI_TRAINING_GEN [CLIENT] Using JSON credentials")
            elif self.settings.get_setting('GOOGLE_APPLICATION_CREDENTIALS'):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.settings.get_setting('GOOGLE_APPLICATION_CREDENTIALS')
                logger.info("🔑 AI_TRAINING_GEN [CLIENT] Using credentials file")
            
            # Initialize Vertex AI
            vertexai.init(project=project_id, location=location)
            
            # Create specialized generative model for training content
            self.specialized_client = GenerativeModel(
                model_name=self.model_name,
                system_instruction=[
                    "Tu es un expert pédagogue et créateur de contenu de formation professionnelle.",
                    "Tu crées du contenu de formation détaillé, structuré et engageant.",
                    "Tu utilises le format Markdown avec une hiérarchie claire.",
                    "Tu inclus des exemples concrets et des cas pratiques."
                ]
            )
            
            logger.info(f"🤖 AI_TRAINING_GEN [CLIENT] Specialized client configured - Model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"❌ AI_TRAINING_GEN [CLIENT] Failed to initialize specialized client: {str(e)}")
            self.specialized_client = None
    
    async def _generate_with_specialized_client(self, prompt: str, generation_config: Dict[str, Any]):
        """Generate content using the specialized Gemini 2.5 Flash client"""
        try:
            # Create generation config for the specialized client
            config = {
                "temperature": generation_config.get("temperature", 0.7),
                "top_p": generation_config.get("top_p", 0.9),
                "top_k": generation_config.get("top_k", 40),
                "max_output_tokens": generation_config.get("max_output_tokens", 8192),
            }
            
            logger.info(f"🎯 AI_TRAINING_GEN [SPECIALIZED] Generating with {self.model_name}")
            
            # Generate content using the specialized client
            response = self.specialized_client.generate_content(
                prompt,
                generation_config=config
            )
            
            logger.info(f"✅ AI_TRAINING_GEN [SPECIALIZED] Content generated successfully")
            return response
            
        except Exception as e:
            logger.error(f"❌ AI_TRAINING_GEN [SPECIALIZED] Generation failed: {str(e)}")
            raise AITrainingGenerationError(
                f"Specialized model generation failed: {str(e)}",
                error_type="specialized_generation_error",
                original_error=e
            ) from e
    
    def _build_training_generation_prompt(self, name: str, description: str) -> str:
        """
        Build optimized prompt for training content generation
        
        Args:
            name: Training name
            description: Training description/topic
            
        Returns:
            Formatted prompt for VertexAI
        """
        prompt = f"""
<ROLE>
Tu es un expert pédagogue ecréateur de contenu de formation professionnelle.
</ROLE>

<OBJECTIF>
Créer une [BASE DE CONNAISSANCE] qui sera utilisée pour créer une formation complete.
</OBJECTIF>

<INFORMATIONS_BASE_DE_CONNAISSANCE>
- Nom : {name}
- Description/Sujet : {description}
</INFORMATIONS_BASE_DE_CONNAISSANCE>

<INSTRUCTIONS>
1. Structure obligatoire : Utilise la structure Markdown avec titres hiérarchiques (# ## ###)
2. Contenu pédagogique : Crée du contenu détaillé, pratique et engageant
3. Exemples concrets : Inclus des exemples réels et des cas pratiques
4. Interactivité : Ajoute des exercices, questions de réflexion et points clés
5. Longueur appropriée : Génère suffisamment de contenu pour une formation complète (minimum 1500 mots)
</INSTRUCTIONS>

<RECAP>
POINTS ESSENTIELS À RESPECTER :
- Formation complète sur : {name} - {description}
- Structure Markdown hiérarchique obligatoire
- Contenu entre 4500 et 7500 mots
- Format Markdown pur sans balises de code
</RECAP>

Génère maintenant la [BASE DE CONNAISSANCE] complète au format Markdown pur."""

        return prompt
    
    async def generate_training_content(self, name: str, description: str) -> str:
        """
        Generate training content using VertexAI
        
        Args:
            name: Training name
            description: Training description/topic
            
        Returns:
            Generated markdown content
            
        Raises:
            AITrainingGenerationError: If generation fails
        """
        start_time = time.time()
        self.api_call_counter += 1
        
        try:
            logger.info(f"🚀 AI_TRAINING_GEN [START] Generating content for '{name}' - Call #{self.api_call_counter}")
            
            # Build the generation prompt
            prompt = self._build_training_generation_prompt(name, description)
            
            # Prepare generation config for training content (not JSON, but markdown text)
            generation_config = {
                "temperature": 0.7,  # Higher for creative training content
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 8192,
                # No response_mime_type since we want markdown text, not JSON
            }
            
            logger.info(f"📝 AI_TRAINING_GEN [PROMPT] Prompt length: {len(prompt)} characters")
            logger.info(f"⚙️ AI_TRAINING_GEN [CONFIG] Generation config: {generation_config}")
            
            # Apply rate limiting before VertexAI call
            logger.info(f"🚦 AI_TRAINING_GEN [RATE_LIMIT] Acquiring rate limit slot...")
            await gemini_rate_limiter.acquire(wait=True, max_wait_seconds=300)
            logger.info(f"✅ AI_TRAINING_GEN [RATE_LIMIT] Rate limit slot acquired")
            
            # Generate content using specialized Gemini 2.5 Flash client
            if not self.specialized_client:
                raise AITrainingGenerationError(
                    "Specialized AI client not available",
                    error_type="client_unavailable"
                )
            
            logger.info(f"🚀 AI_TRAINING_GEN [GENERATE] Using specialized model: {self.model_name}")
            
            # Generate content with specialized client
            response = await self._generate_with_specialized_client(prompt, generation_config)
            result = response.text if hasattr(response, 'text') else str(response)
            
            if not result or not result.strip():
                raise AITrainingGenerationError(
                    "Empty response from VertexAI",
                    error_type="empty_response"
                )
            
            # Validate and clean the result
            cleaned_content = self._validate_and_clean_content(result, name)
            
            duration = time.time() - start_time
            
            logger.info(f"✅ AI_TRAINING_GEN [SUCCESS] Content generated in {duration:.2f}s - {len(cleaned_content)} characters")
            logger.info(f"📊 AI_TRAINING_GEN [STATS] Total calls: {self.api_call_counter}")
            
            return cleaned_content
            
        except RateLimitExceeded as e:
            duration = time.time() - start_time
            logger.error(f"🚦 AI_TRAINING_GEN [RATE_LIMIT_ERROR] Rate limit exceeded after {duration:.2f}s: {str(e)}")
            raise AITrainingGenerationError(
                "AI training generation is temporarily busy. Please try again in a few minutes.",
                error_type="rate_limit_exceeded",
                original_error=e
            ) from e
            
        except VertexAIError as e:
            duration = time.time() - start_time
            logger.error(f"❌ AI_TRAINING_GEN [VERTEX_ERROR] VertexAI error after {duration:.2f}s: {str(e)}")
            raise AITrainingGenerationError(
                self.USER_ERROR_MESSAGE,
                error_type="vertex_error",
                original_error=e
            ) from e
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ AI_TRAINING_GEN [UNEXPECTED_ERROR] Unexpected error after {duration:.2f}s: {str(e)}")
            raise AITrainingGenerationError(
                self.USER_ERROR_MESSAGE,
                error_type="unexpected_error",
                original_error=e
            ) from e
    
    def _validate_and_clean_content(self, content: str, training_name: str) -> str:
        """
        Validate and clean the generated training content
        
        Args:
            content: Raw content from VertexAI
            training_name: Name of the training for validation
            
        Returns:
            Cleaned and validated content
            
        Raises:
            AITrainingGenerationError: If content is invalid
        """
        try:
            # Clean the content
            cleaned = content.strip()
            
            # Remove any markdown code blocks if present
            if cleaned.startswith('```markdown'):
                cleaned = cleaned[11:]
                logger.info("🧹 AI_TRAINING_GEN [CLEAN] Removed ```markdown prefix")
            elif cleaned.startswith('```'):
                cleaned = cleaned[3:]
                logger.info("🧹 AI_TRAINING_GEN [CLEAN] Removed ``` prefix")
                
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
                logger.info("🧹 AI_TRAINING_GEN [CLEAN] Removed ``` suffix")
            
            cleaned = cleaned.strip()
            
            # Basic validation
            if len(cleaned) < 500:
                raise AITrainingGenerationError(
                    "Generated content too short",
                    error_type="content_too_short"
                )
            
            # Ensure it starts with a title
            if not cleaned.startswith('#'):
                logger.info("🔧 AI_TRAINING_GEN [FIX] Adding missing title")
                cleaned = f"# {training_name}\n\n{cleaned}"
            
            # Basic markdown structure validation
            if '##' not in cleaned:
                logger.warning("⚠️ AI_TRAINING_GEN [VALIDATION] Content may lack proper structure (no ## headings)")
            
            logger.info(f"✅ AI_TRAINING_GEN [VALIDATED] Content validated - {len(cleaned)} characters")
            return cleaned
            
        except Exception as e:
            logger.error(f"❌ AI_TRAINING_GEN [VALIDATION_ERROR] Content validation failed: {str(e)}")
            raise AITrainingGenerationError(
                "Generated content validation failed",
                error_type="validation_error",
                original_error=e
            ) from e
    
    def is_available(self) -> bool:
        """Check if AI training generation service is available"""
        try:
            return self.vertex_adapter.is_available()
        except Exception as e:
            logger.error(f"❌ AI_TRAINING_GEN [AVAILABILITY] Service availability check failed: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        vertex_stats = self.vertex_adapter.get_stats()
        rate_limit_status = gemini_rate_limiter.get_status()
        
        return {
            "service_name": "AITrainingGenerationService",
            "available": self.is_available(),
            "api_calls_made": self.api_call_counter,
            "vertex_adapter_stats": vertex_stats,
            "rate_limit_status": rate_limit_status,
            "last_check": datetime.now(timezone.utc).isoformat()
        }