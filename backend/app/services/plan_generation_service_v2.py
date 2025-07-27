"""
FIA v3.0 - Plan Generation Service (Refactored)
Lightweight orchestration service using extracted domain services
"""

import logging
import json
import time
from typing import Dict, Any, Optional, TYPE_CHECKING
from datetime import datetime, timezone

# Domain services
from app.domain.services.document_processor import DocumentProcessor, DocumentProcessingError
from app.domain.services.prompt_builder import PromptBuilder
from app.domain.services.plan_validator import PlanValidator, PlanValidationError

# Infrastructure adapter
from app.infrastructure.adapters.vertex_ai_adapter import VertexAIAdapter, VertexAIError

# Optional architecture support
if TYPE_CHECKING:
    from app.domain.ports.outbound_ports import GeminiServicePort, ContextCacheServicePort
    from app.domain.entities.learner_session import LearnerSession
    from app.domain.entities.training import Training

# Configure logger
logger = logging.getLogger(__name__)


class PlanGenerationError(Exception):
    """Exception for plan generation errors"""
    def __init__(self, message: str, error_type: str = "generation_error", original_error: Optional[Exception] = None):
        super().__init__(message)
        self.error_type = error_type
        self.original_error = original_error


class PlanGenerationService:
    """Lightweight orchestration service for personalized training plan generation"""
    
    # Standard error message for learners
    LEARNER_ERROR_MESSAGE = "Le service de génération de contenu est temporairement indisponible. Veuillez réessayer plus tard ou contacter votre formateur."
    
    def __init__(
        self,
        gemini_service: Optional["GeminiServicePort"] = None,
        cache_service: Optional["ContextCacheServicePort"] = None
    ):
        """
        Initialize plan generation service with dependency injection
        
        Args:
            gemini_service: Optional Gemini service port (for hexagonal architecture)
            cache_service: Optional cache service port (for cost optimization)
        """
        # Initialize domain services
        self.vertex_ai_adapter = VertexAIAdapter()
        self.document_processor = DocumentProcessor(self.vertex_ai_adapter)
        self.prompt_builder = PromptBuilder()
        self.plan_validator = PlanValidator()
        
        # Optional ports for architecture flexibility
        self.gemini_service = gemini_service
        self.cache_service = cache_service
        
        # Service configuration
        self.max_retries = 3
        self.api_call_counter = 0
        
        logger.info("🚀 PLAN [SERVICE] initialized with extracted services")
        logger.info(f"🚀 PLAN [SERVICES] VertexAI: {self.vertex_ai_adapter.is_available()}")
        logger.info(f"🚀 PLAN [SERVICES] Cache: {'enabled' if cache_service else 'disabled'}")
    
    async def generate_personalized_plan(
        self,
        learner_session: "LearnerSession",
        training: "Training"
    ) -> Dict[str, Any]:
        """
        Generate personalized training plan using context caching
        
        Args:
            learner_session: Learner session entity
            training: Training entity
            
        Returns:
            Generated and validated training plan
            
        Raises:
            PlanGenerationError: If generation fails
        """
        start_time = time.time()
        
        try:
            logger.info(f"🎯 PLAN [GENERATION] Starting for learner {learner_session.email}")
            
            # Step 1: Build learner profile
            learner_profile = self._build_learner_profile(learner_session)
            logger.info(f"📋 PLAN [PROFILE] Level: {learner_profile['experience_level']}, Style: {learner_profile['learning_style']}")
            
            # Step 2: Process document (with caching if available)
            document_content = await self._get_document_content_with_cache(training)
            logger.info(f"📄 PLAN [DOCUMENT] Content extracted: {len(document_content)} characters")
            
            # Step 3: Generate plan with AI
            plan_data = await self._generate_plan_with_ai(learner_profile, document_content)
            logger.info(f"🤖 PLAN [GENERATED] Plan structure created")
            
            # Step 4: Validate and fix plan
            validated_plan = self.plan_validator.validate_and_fix_plan(plan_data)
            logger.info(f"✅ PLAN [VALIDATED] Plan is structurally valid")
            
            duration = time.time() - start_time
            logger.info(f"🎉 PLAN [SUCCESS] Generated in {duration:.2f}s for {learner_session.email}")
            
            return {
                "plan_data": validated_plan,
                "generation_metadata": {
                    "learner_id": str(learner_session.id),
                    "training_id": str(training.id),
                    "generation_time": datetime.now(timezone.utc).isoformat(),
                    "duration_seconds": round(duration, 2),
                    "profile": learner_profile,
                    "document_length": len(document_content),
                    "service_version": "2.0_refactored"
                }
            }
            
        except (DocumentProcessingError, VertexAIError, PlanValidationError) as e:
            duration = time.time() - start_time
            logger.error(f"❌ PLAN [FAILED] {type(e).__name__}: {str(e)} (after {duration:.2f}s)")
            raise PlanGenerationError(
                f"Plan generation failed: {str(e)}", 
                error_type=type(e).__name__.lower(),
                original_error=e
            )
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ PLAN [ERROR] Unexpected error: {str(e)} (after {duration:.2f}s)")
            raise PlanGenerationError(
                "An unexpected error occurred during plan generation",
                error_type="unexpected_error",
                original_error=e
            )
    
    async def generate_plan_simple(self, learner_profile: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """
        Simple plan generation without entities (for backward compatibility)
        
        Args:
            learner_profile: Learner profile dictionary
            file_path: Path to training document
            
        Returns:
            Generated training plan
        """
        try:
            # Validate and normalize profile
            normalized_profile = self.prompt_builder.validate_profile(learner_profile)
            
            # Process document
            document_content = await self.document_processor.process_document(file_path)
            
            # Generate plan
            plan_data = await self._generate_plan_with_ai(normalized_profile, document_content)
            
            # Validate plan
            validated_plan = self.plan_validator.validate_and_fix_plan(plan_data)
            
            return validated_plan
            
        except Exception as e:
            logger.error(f"❌ PLAN [SIMPLE] Generation failed: {str(e)}")
            raise PlanGenerationError(f"Simple plan generation failed: {str(e)}", original_error=e)
    
    async def generate_slide_content(
        self,
        slide_title: str,
        learner_profile: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate content for individual slide
        
        Args:
            slide_title: Title of slide to generate
            learner_profile: Learner profile for personalization
            context: Slide context (module, submodule, stage info)
            
        Returns:
            Generated slide content
        """
        try:
            # Build slide-specific prompt
            prompt = self.prompt_builder.build_slide_content_prompt(
                slide_title, learner_profile, context
            )
            
            # Generate content with AI
            response = await self.vertex_ai_adapter.generate_content(prompt)
            
            # Parse JSON response
            try:
                slide_content = json.loads(response)
                logger.info(f"📝 SLIDE [GENERATED] {slide_title}")
                return slide_content
            except json.JSONDecodeError:
                logger.warning(f"⚠️ SLIDE [JSON] Invalid JSON for slide: {slide_title}")
                return {
                    "slide_content": {
                        "introduction": "Contenu en cours de génération...",
                        "main_content": response[:500] + "..." if len(response) > 500 else response,
                        "example": "Exemple sera ajouté prochainement",
                        "key_point": "Point clé à retenir",
                        "engagement": "Question d'engagement"
                    }
                }
                
        except Exception as e:
            logger.error(f"❌ SLIDE [ERROR] Failed to generate slide '{slide_title}': {str(e)}")
            raise PlanGenerationError(f"Slide generation failed: {str(e)}", original_error=e)
    
    def _build_learner_profile(self, learner_session: "LearnerSession") -> Dict[str, Any]:
        """Build learner profile from session entity"""
        return self.prompt_builder.extract_learner_profile({
            'experience_level': learner_session.experience_level,
            'learning_style': learner_session.learning_style,
            'job_position': learner_session.job_position,
            'activity_sector': learner_session.activity_sector,
            'country': learner_session.country,
            'language': learner_session.language
        })
    
    async def _get_document_content_with_cache(self, training: "Training") -> str:
        """Get document content with optional caching"""
        if not training.has_file():
            raise PlanGenerationError("Training has no attached file")
        
        # Try cache first if available
        if self.cache_service:
            try:
                cached_content = await self._get_cached_content(training)
                if cached_content:
                    logger.info("📦 PLAN [CACHE] Using cached document content")
                    return cached_content
            except Exception as e:
                logger.warning(f"⚠️ PLAN [CACHE] Cache lookup failed: {str(e)}")
        
        # Process document directly
        return await self.document_processor.process_document(training.file_path)
    
    async def _get_cached_content(self, training: "Training") -> Optional[str]:
        """Get cached document content (placeholder for cache implementation)"""
        # This would integrate with actual cache service
        # For now, return None to always process documents
        return None
    
    async def _generate_plan_with_ai(self, learner_profile: Dict[str, Any], document_content: str) -> Dict[str, Any]:
        """Generate plan using AI with retry logic"""
        # Check if Vertex AI is available
        if not self.vertex_ai_adapter.is_available():
            raise PlanGenerationError("Le service de génération IA n'est pas disponible. Vérifiez la configuration Vertex AI.")  
            
        # Build personalized prompt
        prompt = self.prompt_builder.build_personalized_prompt(learner_profile, document_content)
        
        # Generate with retry
        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🤖 PLAN [AI] Generation attempt {attempt + 1}/{self.max_retries}")
                
                # Generate content
                self.api_call_counter += 1
                response = await self.vertex_ai_adapter.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "top_k": 40,
                        "max_output_tokens": 8192
                    }
                )
                
                # Parse JSON response
                try:
                    plan_data = json.loads(response)
                    logger.info(f"✅ PLAN [AI] Successfully generated and parsed JSON")
                    return plan_data
                except json.JSONDecodeError as e:
                    last_error = e
                    logger.warning(f"⚠️ PLAN [JSON] Invalid JSON on attempt {attempt + 1}: {str(e)}")
                    
                    if attempt < self.max_retries - 1:
                        await self._wait_before_retry(attempt)
                        continue
                    else:
                        raise PlanGenerationError(f"Invalid JSON response after {self.max_retries} attempts", original_error=e)
                
            except VertexAIError as e:
                last_error = e
                logger.warning(f"⚠️ PLAN [AI] Vertex AI error on attempt {attempt + 1}: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    await self._wait_before_retry(attempt)
                else:
                    raise
        
        raise PlanGenerationError(f"Plan generation failed after {self.max_retries} attempts", original_error=last_error)
    
    async def _wait_before_retry(self, attempt: int):
        """Wait before retry with exponential backoff"""
        import asyncio
        wait_time = 2.0 * (attempt + 1)
        logger.info(f"⏳ PLAN [RETRY] Waiting {wait_time}s before next attempt...")
        await asyncio.sleep(wait_time)
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information and statistics"""
        return {
            "service_version": "2.0_refactored",
            "api_calls_made": self.api_call_counter,
            "max_retries": self.max_retries,
            "vertex_ai_available": self.vertex_ai_adapter.is_available(),
            "cache_enabled": self.cache_service is not None,
            "services": {
                "document_processor": self.document_processor.get_processing_stats(),
                "prompt_builder": self.prompt_builder.get_prompt_stats(),
                "plan_validator": self.plan_validator.get_validation_stats(),
                "vertex_ai_adapter": self.vertex_ai_adapter.get_stats()
            }
        }
    
    def get_stage_names(self) -> list[str]:
        """Get required stage names"""
        return [stage["title"] for stage in self.prompt_builder.get_required_stages()]
    
    def get_stage_descriptions(self) -> Dict[int, str]:
        """Get stage descriptions"""
        return {
            stage["stage_number"]: stage["description"] 
            for stage in self.prompt_builder.get_required_stages()
        }