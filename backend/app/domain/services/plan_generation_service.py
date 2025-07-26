"""
FIA v3.0 - Pure Domain Plan Generation Service
Clean domain service without infrastructure dependencies
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.domain.ports.outbound_ports import GeminiServicePort, ContextCacheServicePort
from app.domain.entities.learner_session import LearnerSession
from app.domain.entities.training import Training

logger = logging.getLogger(__name__)


class PlanGenerationError(Exception):
    """Custom exception for plan generation errors"""
    pass


class PlanGenerationService:
    """Pure domain service for generating personalized training plans"""
    
    def __init__(
        self, 
        gemini_service: GeminiServicePort,
        cache_service: Optional[ContextCacheServicePort] = None
    ):
        """Initialize the plan generation service with dependency injection"""
        self.gemini_service = gemini_service
        self.cache_service = cache_service
    
    async def generate_personalized_plan(
        self,
        learner_session: LearnerSession,
        training: Training,
        training_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a personalized training plan for a learner
        
        Business Logic:
        1. Build learner profile context
        2. Get or create context cache for training content
        3. Generate plan using AI service
        4. Validate and return structured plan
        """
        try:
            # Domain logic: Build learner profile
            learner_profile = self._build_learner_profile(learner_session)
            
            # Domain logic: Determine content source
            content_to_use = training_content or f"Training: {training.name}"
            if training.description:
                content_to_use += f"\nDescription: {training.description}"
            
            # Use cache service if available
            cache_id = None
            if self.cache_service and training.has_file():
                cache_id = await self._get_or_create_cache(training, content_to_use)
            
            # Generate plan using AI service
            plan_data = await self.gemini_service.generate_training_plan(
                learner_profile=learner_profile,
                training_content=content_to_use,
                context_cache_id=cache_id
            )
            
            # Domain validation: Ensure plan meets business requirements
            validated_plan = self._validate_plan_structure(plan_data)
            
            logger.info(f"Generated personalized plan for learner {learner_session.email}")
            return validated_plan
            
        except Exception as e:
            logger.error(f"Error generating personalized plan: {str(e)}")
            raise PlanGenerationError("Plan generation service temporarily unavailable")
    
    def _build_learner_profile(self, learner_session: LearnerSession) -> Dict[str, Any]:
        """Build learner profile for AI prompt - Pure domain logic"""
        return {
            "email": learner_session.email,
            "experience_level": learner_session.experience_level,
            "learning_style": learner_session.learning_style,
            "job_position": learner_session.job_position,
            "activity_sector": learner_session.activity_sector,
            "country": learner_session.country,
            "language": learner_session.language,
            "preferences": self._derive_learning_preferences(learner_session)
        }
    
    def _derive_learning_preferences(self, learner_session: LearnerSession) -> Dict[str, str]:
        """Derive learning preferences from profile - Business logic"""
        preferences = {}
        
        # Experience level adaptations
        if learner_session.experience_level == "beginner":
            preferences["complexity"] = "simple_explanations"
            preferences["pace"] = "slow_progression"
            preferences["support"] = "detailed_examples"
        elif learner_session.experience_level == "intermediate":
            preferences["complexity"] = "moderate_concepts"
            preferences["pace"] = "standard_progression"
            preferences["support"] = "practical_examples"
        else:  # advanced
            preferences["complexity"] = "advanced_concepts"
            preferences["pace"] = "fast_progression"
            preferences["support"] = "challenging_cases"
        
        # Learning style adaptations
        style_adaptations = {
            "visual": "diagrams_charts_infographics",
            "auditory": "discussions_audio_explanations",
            "kinesthetic": "hands_on_exercises_practice",
            "reading": "text_documentation_articles"
        }
        preferences["preferred_content_type"] = style_adaptations.get(
            learner_session.learning_style, 
            "mixed_content"
        )
        
        return preferences
    
    async def _get_or_create_cache(self, training: Training, content: str) -> Optional[str]:
        """Get existing cache or create new one for training content"""
        if not self.cache_service:
            return None
            
        try:
            # Try to get existing cache based on training file
            cache_key = f"training_{training.id}"
            existing_cache = await self.cache_service.get_cache(cache_key)
            
            if existing_cache:
                logger.info(f"Using existing cache for training {training.id}")
                return cache_key
            
            # Create new cache
            cache_id = await self.cache_service.create_cache(
                content=content,
                ttl_hours=12  # Business rule: 12 hours default TTL
            )
            
            logger.info(f"Created new cache {cache_id} for training {training.id}")
            return cache_id
            
        except Exception as e:
            logger.warning(f"Cache service error, proceeding without cache: {str(e)}")
            return None
    
    def _validate_plan_structure(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that generated plan meets business requirements"""
        if not isinstance(plan_data, dict):
            raise PlanGenerationError("Plan data must be a dictionary")
        
        if "stages" not in plan_data:
            raise PlanGenerationError("Plan must contain stages")
        
        stages = plan_data["stages"]
        if not isinstance(stages, list):
            raise PlanGenerationError("Stages must be a list")
        
        # Business rule: Must have exactly 5 stages
        if len(stages) != 5:
            raise PlanGenerationError(f"Plan must have exactly 5 stages, got {len(stages)}")
        
        # Validate each stage
        required_stage_numbers = {1, 2, 3, 4, 5}
        found_stage_numbers = set()
        
        for stage in stages:
            if not isinstance(stage, dict):
                raise PlanGenerationError("Each stage must be a dictionary")
            
            if "stage_number" not in stage:
                raise PlanGenerationError("Each stage must have a stage_number")
            
            stage_number = stage["stage_number"]
            if stage_number not in required_stage_numbers:
                raise PlanGenerationError(f"Invalid stage number: {stage_number}")
            
            found_stage_numbers.add(stage_number)
            
            # Validate stage has required fields
            required_fields = ["stage_title", "stage_description", "modules"]
            for field in required_fields:
                if field not in stage:
                    raise PlanGenerationError(f"Stage {stage_number} missing required field: {field}")
            
            # Validate modules
            modules = stage["modules"]
            if not isinstance(modules, list) or len(modules) == 0:
                raise PlanGenerationError(f"Stage {stage_number} must have at least one module")
        
        # Ensure all stage numbers are present
        if found_stage_numbers != required_stage_numbers:
            missing = required_stage_numbers - found_stage_numbers
            raise PlanGenerationError(f"Missing stage numbers: {missing}")
        
        logger.info("Plan structure validation passed")
        return plan_data
    
    async def generate_slide_content(
        self,
        slide_title: str,
        module_context: str,
        learner_session: LearnerSession
    ) -> Dict[str, Any]:
        """Generate content for a specific slide"""
        try:
            learner_profile = self._build_learner_profile(learner_session)
            
            slide_content = await self.gemini_service.generate_slide_content(
                slide_title=slide_title,
                module_context=module_context,
                learner_profile=learner_profile
            )
            
            logger.info(f"Generated slide content for: {slide_title}")
            return slide_content
            
        except Exception as e:
            logger.error(f"Error generating slide content: {str(e)}")
            raise PlanGenerationError("Slide content generation service temporarily unavailable")
    
    def get_stage_names(self) -> list[str]:
        """Get the standard 5 stage names - Business rule"""
        return [
            "Discovery and Introduction",
            "Fundamental Learning", 
            "Practical Application",
            "Deepening Knowledge",
            "Mastery and Evaluation"
        ]
    
    def get_stage_descriptions(self) -> Dict[int, str]:
        """Get standard stage descriptions - Business rule"""
        return {
            1: "Context setting and fundamental bases",
            2: "Key concepts and main theory",
            3: "Practical implementation and exercises", 
            4: "Advanced concepts and complex cases",
            5: "Synthesis, evaluation and perspectives"
        }