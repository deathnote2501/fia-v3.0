"""
FIA v3.0 - Plan Generation Service
Service for generating personalized training plans using Gemini with Context Caching
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

import google.generativeai as genai

from app.infrastructure.settings import settings
from app.domain.services.context_cache_service import ContextCacheService, ContextCacheError
from app.domain.entities.learner_session import LearnerSession
from app.domain.entities.training import Training
from app.domain.schemas.learner_training_plan import GeminiTrainingPlanStructure

# Configure logging
logger = logging.getLogger(__name__)


class PlanGenerationError(Exception):
    """Custom exception for plan generation errors"""
    pass


class PlanGenerationService:
    """Service for generating personalized training plans using cached training content"""
    
    def __init__(self):
        """Initialize the plan generation service"""
        self.client = self._initialize_gemini_client()
        self.model_name = settings.gemini_model_name
        self.cache_service = ContextCacheService()
        
    def _initialize_gemini_client(self) -> genai.Client:
        """Initialize Gemini client with Vertex AI configuration"""
        try:
            if not settings.google_cloud_project:
                raise PlanGenerationError("Google Cloud Project not configured")
            
            client = genai.Client(
                vertexai=True,
                project=settings.google_cloud_project,
                location=settings.google_cloud_region
            )
            
            logger.info(f"Plan Generation client initialized for project: {settings.google_cloud_project}")
            return client
            
        except Exception as e:
            logger.error(f"Failed to initialize Plan Generation client: {e}")
            raise PlanGenerationError(f"Failed to initialize Plan Generation client: {e}")
    
    def _build_learner_profile_context(self, learner_session: LearnerSession) -> str:
        """
        Build comprehensive learner profile context for prompt
        
        Args:
            learner_session: Learner session with profile information
            
        Returns:
            Formatted learner profile context string
        """
        
        # Experience level descriptions
        experience_descriptions = {
            "beginner": "Débutant - Peu ou pas d'expérience dans le domaine, nécessite des explications détaillées et des exemples concrets",
            "intermediate": "Intermédiaire - Possède des bases solides, peut comprendre des concepts plus avancés avec des explications appropriées", 
            "advanced": "Avancé - Expérience significative, peut traiter des concepts complexes et des cas d'usage sophistiqués"
        }
        
        # Learning style descriptions
        learning_style_descriptions = {
            "visual": "Visuel - Apprend mieux avec des diagrammes, schémas, graphiques et supports visuels",
            "auditory": "Auditif - Préfère les explications orales, discussions et éléments audio",
            "kinesthetic": "Kinesthésique - Apprend par la pratique, les exercices et l'expérimentation",
            "reading": "Lecture/Écriture - Préfère les textes, notes et documentation écrite"
        }
        
        profile_context = f"""
PROFIL DE L'APPRENANT :
====================

📧 Email : {learner_session.email}
🎯 Niveau d'expérience : {experience_descriptions.get(learner_session.experience_level, learner_session.experience_level)}
🧠 Style d'apprentissage : {learning_style_descriptions.get(learner_session.learning_style, learner_session.learning_style)}
👔 Poste/Fonction : {learner_session.job_position}
🏢 Secteur d'activité : {learner_session.activity_sector}
🌍 Pays : {learner_session.country}
🗣️ Langue : {learner_session.language}

ADAPTATIONS REQUISES :
=====================

Niveau d'expérience :
- Adapter la complexité du vocabulaire et des concepts
- Ajuster la profondeur des explications
- Modifier le rythme de progression

Style d'apprentissage :
- Privilégier les méthodes pédagogiques adaptées
- Suggérer les supports les plus efficaces
- Organiser le contenu selon les préférences d'apprentissage

Contexte professionnel :
- Intégrer des exemples spécifiques au secteur d'activité
- Adapter les cas d'usage au poste occupé
- Tenir compte des contraintes géographiques et culturelles
"""
        
        return profile_context
    
    def _build_optimized_prompt(self, learner_profile_context: str) -> str:
        """
        Build optimized prompt for personalized plan generation
        
        Args:
            learner_profile_context: Formatted learner profile context
            
        Returns:
            Complete optimized prompt for Gemini
        """
        
        prompt = f"""
Tu es un expert en ingénierie pédagogique spécialisé dans la création de parcours de formation personnalisés.
Tu dois créer un plan de formation PARFAITEMENT adapté au profil de l'apprenant en analysant le support de formation fourni.

{learner_profile_context}

OBJECTIF :
=========
Créer un plan de formation personnalisé en 5 étapes (stages) fixes, avec des modules et sous-modules adaptés au profil de l'apprenant.

STRUCTURE OBLIGATOIRE :
======================
5 ÉTAPES FIXES :
1. "Découverte et Introduction" - Mise en contexte et bases fondamentales
2. "Apprentissage Fondamental" - Concepts clés et théorie principale  
3. "Application Pratique" - Mise en pratique et exercices
4. "Approfondissement" - Concepts avancés et cas complexes
5. "Maîtrise et Évaluation" - Synthèse, évaluation et perspectives

Pour CHAQUE étape :
- 2 à 4 modules adaptés au contenu du support
- Chaque module : 2 à 5 sous-modules
- Chaque sous-module : 3 à 8 slides (titres uniquement)

PERSONNALISATION SELON LE PROFIL :
================================

🎯 NIVEAU D'EXPÉRIENCE :
- Beginner : Plus de slides par sous-module, progression graduelle, exemples simples
- Intermediate : Rythme modéré, équilibre théorie/pratique
- Advanced : Moins de slides par sous-module, concepts directement, cas complexes

🧠 STYLE D'APPRENTISSAGE :
- Visual : Privilégier slides avec diagrammes, schémas, infographies
- Auditory : Inclure slides pour discussions, présentations orales, débriefs
- Kinesthetic : Accent sur exercices pratiques, simulations, ateliers
- Reading : Slides riches en contenu texte, ressources, documentation

👔 CONTEXTE PROFESSIONNEL :
- Adapter exemples et cas d'usage au secteur d'activité
- Intégrer des références spécifiques au poste
- Tenir compte des enjeux métier et contraintes du secteur

INSTRUCTIONS SPÉCIFIQUES :
=========================

1. ANALYSE APPROFONDIE du support fourni pour identifier :
   - Les concepts principaux et leur hiérarchie
   - Les niveaux de difficulté
   - Les éléments pratiques vs théoriques
   - Les prérequis et progressions logiques

2. ADAPTATION AU PROFIL pour :
   - Ajuster la granularité selon le niveau d'expérience
   - Organiser selon le style d'apprentissage préféré
   - Personnaliser exemples selon le contexte professionnel

3. OPTIMISATION PÉDAGOGIQUE :
   - Équilibrer théorie/pratique selon le profil
   - Créer une progression logique et motivante
   - Intégrer points de contrôle et évaluations adaptés

4. FORMAT DE RÉPONSE :
   Structure JSON strict avec les champs exacts attendus par le système.

GÉNÈRE MAINTENANT le plan personnalisé en analysant le support de formation et en l'adaptant parfaitement au profil de cet apprenant spécifique.
"""
        
        return prompt
    
    async def generate_personalized_plan(
        self,
        learner_session: LearnerSession,
        training: Training,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a personalized training plan for a learner
        
        Args:
            learner_session: Learner session with profile information
            training: Training containing the source material
            use_cache: Whether to use context caching for optimization
            
        Returns:
            Dictionary containing the generated personalized plan
            
        Raises:
            PlanGenerationError: If plan generation fails
        """
        try:
            logger.info(f"Generating personalized plan for learner: {learner_session.email}")
            logger.info(f"Training: {training.name}, Use cache: {use_cache}")
            
            # Build learner profile context
            learner_profile_context = self._build_learner_profile_context(learner_session)
            
            # Build optimized prompt
            optimized_prompt = self._build_optimized_prompt(learner_profile_context)
            
            # Generate plan using cached content if available
            if use_cache:
                plan_result = await self._generate_with_cache(
                    training_file_path=training.file_path,
                    training_mime_type=training.mime_type,
                    prompt=optimized_prompt,
                    training_name=training.name
                )
            else:
                plan_result = await self._generate_direct(
                    training_file_path=training.file_path,
                    training_mime_type=training.mime_type,
                    prompt=optimized_prompt
                )
            
            # Validate and structure the response
            structured_plan = self._process_plan_response(plan_result, learner_session, training)
            
            logger.info(f"Successfully generated personalized plan with {len(structured_plan.get('stages', []))} stages")
            return structured_plan
            
        except Exception as e:
            logger.error(f"Failed to generate personalized plan: {e}")
            raise PlanGenerationError(f"Plan generation failed: {e}")
    
    async def _generate_with_cache(
        self,
        training_file_path: str,
        training_mime_type: str,
        prompt: str,
        training_name: str
    ) -> str:
        """
        Generate plan using cached training content
        
        Args:
            training_file_path: Path to training file
            training_mime_type: MIME type of training file
            prompt: Generation prompt
            training_name: Training name for cache display
            
        Returns:
            Generated plan content
        """
        try:
            # Check for existing cache
            cache_info = await self.cache_service.find_cache_by_document(
                training_file_path, training_mime_type
            )
            
            # Create cache if doesn't exist
            if not cache_info:
                logger.info("Creating new cache for training document")
                cache_result = await self.cache_service.create_document_cache(
                    file_path=training_file_path,
                    mime_type=training_mime_type,
                    display_name=f"Training Plan Generation - {training_name}",
                    ttl_hours=24
                )
                
                if not cache_result['success']:
                    raise PlanGenerationError("Failed to create document cache")
                
                cache_id = cache_result['cache_id']
            else:
                cache_id = cache_info['cache_id']
                logger.info(f"Using existing cache: {cache_id}")
            
            # Generate using cached content
            response = await self.cache_service.use_cached_content(
                cache_id=cache_id,
                prompt=prompt,
                max_output_tokens=8192,
                temperature=0.3,  # Slightly higher for creativity in personalization
                top_p=0.95
            )
            
            if not response['success']:
                raise PlanGenerationError("Failed to generate content with cache")
            
            logger.info(f"Generated plan using cache. Tokens used: prompt={response['usage_metadata'].get('prompt_token_count', 0)}, response={response['usage_metadata'].get('candidates_token_count', 0)}, cached={response['usage_metadata'].get('cached_content_token_count', 0)}")
            
            return response['content']
            
        except ContextCacheError as e:
            logger.warning(f"Cache error, falling back to direct generation: {e}")
            return await self._generate_direct(training_file_path, training_mime_type, prompt)
    
    async def _generate_direct(
        self,
        training_file_path: str,
        training_mime_type: str,
        prompt: str
    ) -> str:
        """
        Generate plan with direct document processing (fallback)
        
        Args:
            training_file_path: Path to training file
            training_mime_type: MIME type of training file
            prompt: Generation prompt
            
        Returns:
            Generated plan content
        """
        try:
            logger.info("Generating plan with direct document processing")
            
            # Read file content
            file_content = await self._read_file_content(training_file_path)
            
            # Create content parts for Gemini
            content_parts = [
                genai.Part.from_bytes(
                    data=file_content,
                    mime_type=training_mime_type
                ),
                prompt
            ]
            
            # Generate content
            def make_request():
                return self.client.models.generate_content(
                    model=self.model_name,
                    contents=content_parts,
                    config=GenerateContentConfig(
                        max_output_tokens=8192,
                        temperature=0.3,
                        top_p=0.95,
                        response_mime_type="application/json",
                        response_schema=GeminiTrainingPlanStructure
                    )
                )
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, make_request)
            
            if not response or not response.text:
                raise PlanGenerationError("Empty response from Gemini API")
            
            logger.info(f"Generated plan with direct processing. Response length: {len(response.text)} characters")
            return response.text
            
        except Exception as e:
            logger.error(f"Direct plan generation failed: {e}")
            raise PlanGenerationError(f"Direct generation failed: {e}")
    
    async def _read_file_content(self, file_path: str) -> bytes:
        """
        Read file content asynchronously
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content as bytes
        """
        try:
            def read_file():
                with open(file_path, 'rb') as file:
                    return file.read()
            
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(None, read_file)
            
            if not content:
                raise PlanGenerationError("File is empty")
                
            return content
            
        except FileNotFoundError:
            raise PlanGenerationError(f"File not found: {file_path}")
        except PermissionError:
            raise PlanGenerationError(f"Permission denied reading file: {file_path}")
        except Exception as e:
            raise PlanGenerationError(f"Failed to read file {file_path}: {e}")
    
    def _process_plan_response(
        self,
        plan_content: str,
        learner_session: LearnerSession,
        training: Training
    ) -> Dict[str, Any]:
        """
        Process and validate the generated plan response
        
        Args:
            plan_content: Raw plan content from Gemini
            learner_session: Learner session information
            training: Training information
            
        Returns:
            Structured and validated plan dictionary
        """
        try:
            import json
            
            # Parse JSON response
            plan_data = json.loads(plan_content)
            
            # Validate structure
            if not isinstance(plan_data, dict) or 'stages' not in plan_data:
                raise ValueError("Invalid plan structure - missing stages")
            
            stages = plan_data.get('stages', [])
            if len(stages) != 5:
                raise ValueError(f"Invalid number of stages: {len(stages)} (expected 5)")
            
            # Add metadata
            structured_plan = {
                'success': True,
                'plan_data': plan_data,
                'generation_metadata': {
                    'learner_email': learner_session.email,
                    'learner_level': learner_session.experience_level,
                    'learner_style': learner_session.learning_style,
                    'learner_job': learner_session.job_position,
                    'learner_sector': learner_session.activity_sector,
                    'training_name': training.name,
                    'training_id': str(training.id),
                    'generated_at': datetime.utcnow().isoformat(),
                    'total_stages': len(stages),
                    'total_modules': sum(len(stage.get('modules', [])) for stage in stages),
                    'total_submodules': sum(
                        len(module.get('submodules', []))
                        for stage in stages
                        for module in stage.get('modules', [])
                    ),
                    'total_slides': sum(
                        len(submodule.get('slides', []))
                        for stage in stages
                        for module in stage.get('modules', [])
                        for submodule in module.get('submodules', [])
                    )
                }
            }
            
            logger.info(f"Plan validation successful: {structured_plan['generation_metadata']['total_stages']} stages, {structured_plan['generation_metadata']['total_modules']} modules, {structured_plan['generation_metadata']['total_submodules']} submodules, {structured_plan['generation_metadata']['total_slides']} slides")
            
            return structured_plan
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse plan JSON: {e}")
            raise PlanGenerationError(f"Invalid JSON response: {e}")
        except Exception as e:
            logger.error(f"Failed to process plan response: {e}")
            raise PlanGenerationError(f"Plan processing failed: {e}")
    
    async def regenerate_plan_section(
        self,
        learner_session: LearnerSession,
        training: Training,
        section_type: str,
        section_identifier: str,
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Regenerate a specific section of a training plan
        
        Args:
            learner_session: Learner session with profile
            training: Training information
            section_type: Type of section ('stage', 'module', 'submodule')
            section_identifier: Identifier for the section to regenerate
            custom_instructions: Optional custom instructions for regeneration
            
        Returns:
            Regenerated section data
        """
        try:
            logger.info(f"Regenerating {section_type} section: {section_identifier}")
            
            # Build focused prompt for section regeneration
            profile_context = self._build_learner_profile_context(learner_session)
            
            section_prompt = f"""
{profile_context}

RÉGÉNÉRATION DE SECTION SPÉCIFIQUE :
==================================

Type de section à régénérer : {section_type}
Identifiant : {section_identifier}
Instructions personnalisées : {custom_instructions or "Aucune instruction spécifique"}

Tu dois régénérer uniquement cette section en gardant le même niveau de personnalisation
que le plan original, mais en améliorant le contenu selon les instructions données.

Respecte exactement la structure attendue pour ce type de section.
"""
            
            # Use cache for regeneration
            cache_info = await self.cache_service.find_cache_by_document(
                training.file_path, training.mime_type
            )
            
            if cache_info:
                response = await self.cache_service.use_cached_content(
                    cache_id=cache_info['cache_id'],
                    prompt=section_prompt,
                    max_output_tokens=4096,
                    temperature=0.4,  # Higher temperature for variation
                    top_p=0.9
                )
                
                if response['success']:
                    return {
                        'success': True,
                        'section_type': section_type,
                        'section_identifier': section_identifier,
                        'regenerated_content': response['content'],
                        'regenerated_at': datetime.utcnow().isoformat()
                    }
            
            raise PlanGenerationError("Failed to regenerate section")
            
        except Exception as e:
            logger.error(f"Section regeneration failed: {e}")
            raise PlanGenerationError(f"Section regeneration failed: {e}")