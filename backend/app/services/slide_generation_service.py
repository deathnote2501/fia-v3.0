"""
FIA v3.0 - Slide Generation Service
Service pour générer le contenu des slides individuelles avec VertexAI
"""

import logging
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from app.infrastructure.adapters.vertex_ai_adapter import VertexAIAdapter, VertexAIError
from app.adapters.repositories.learner_training_plan_repository import LearnerTrainingPlanRepository
from app.adapters.repositories.learner_session_repository import LearnerSessionRepository
from app.adapters.repositories.training_slide_repository import TrainingSlideRepository
from app.infrastructure.database import AsyncSessionLocal
from app.domain.services.learner_profile_enrichment_service import LearnerProfileEnrichmentService

logger = logging.getLogger(__name__)


class SlideGenerationService:
    """Service pour générer le contenu des slides avec VertexAI"""
    
    def __init__(self):
        """Initialize slide generation service"""
        self.vertex_adapter = VertexAIAdapter()
        
        logger.info("🎯 SLIDE GENERATION [SERVICE] Initialized")
    
    async def generate_first_slide_content(self, learner_session_id: str) -> Dict[str, Any]:
        """
        Générer le contenu de la première slide d'un apprenant
        
        Args:
            learner_session_id: ID de la session apprenant
            
        Returns:
            Dict contenant le contenu markdown de la slide
        """
        start_time = time.time()
        
        async with AsyncSessionLocal() as session:
            try:
                logger.info(f"🎯 SLIDE GENERATION [START] Generating first slide for session {learner_session_id}")
                
                # Initialize repositories with session
                learner_session_repo = LearnerSessionRepository(session)
                learner_plan_repo = LearnerTrainingPlanRepository(session)
                slide_repo = TrainingSlideRepository()
                slide_repo.set_session(session)
                
                # 1. Récupérer la session apprenant
                learner_session = await learner_session_repo.get_by_id(learner_session_id)
                if not learner_session:
                    raise ValueError(f"Learner session not found: {learner_session_id}")
                
                # 2. Récupérer le plan de formation personnalisé (le plus récent)
                training_plan = await learner_plan_repo.get_latest_by_learner_session_id(learner_session_id)
                if not training_plan:
                    raise ValueError(f"Training plan not found for session: {learner_session_id}")
                
                # 3. Récupérer la première slide
                first_slide = await slide_repo.get_first_slide(training_plan.id)
                if not first_slide:
                    raise ValueError(f"First slide not found for training plan: {training_plan.id}")
                
                # 4. Générer le contenu de la première slide si pas encore généré
                if not first_slide.content:
                    logger.info(f"📝📝📝 SLIDE GENERATION [MAIN] === GÉNÉRATION CONTENU SLIDE ===")
                    logger.info(f"📝📝📝 SLIDE GENERATION [MAIN] Slide title: {first_slide.title}")
                    logger.info(f"📝📝📝 SLIDE GENERATION [MAIN] Learner profile: {learner_session.email}")
                    
                    slide_content = await self._generate_slide_content(
                        slide_title=first_slide.title,
                        slide_type=first_slide.slide_type,
                        learner_profile=learner_session,
                        training_plan=training_plan,
                        slide_position="first",
                        current_slide_id=str(first_slide.id)
                    )
                    
                    logger.info(f"📝📝📝 SLIDE GENERATION [MAIN] === CONTENU GÉNÉRÉ REÇU ===")
                    logger.info(f"📝📝📝 SLIDE GENERATION [MAIN] Content TYPE: {type(slide_content)}")
                    logger.info(f"📝📝📝 SLIDE GENERATION [MAIN] Content LONGUEUR: {len(slide_content) if slide_content else 'NULL'}")
                    logger.info(f"📝📝📝 SLIDE GENERATION [MAIN] Content PREVIEW (500 chars): {slide_content[:500] if slide_content else 'NULL'}")
                    
                    # 5. Sauvegarder le contenu généré
                    logger.info(f"💾💾💾 SLIDE GENERATION [MAIN] === SAUVEGARDE EN BASE ===")
                    logger.info(f"💾💾💾 SLIDE GENERATION [MAIN] Slide ID: {first_slide.id}")
                    logger.info(f"💾💾💾 SLIDE GENERATION [MAIN] Content à sauvegarder: {slide_content[:200]}...")
                    
                    await slide_repo.update_content(first_slide.id, slide_content)
                    first_slide.content = slide_content
                    first_slide.generated_at = datetime.now(timezone.utc)
                    
                    logger.info(f"✅✅✅ SLIDE GENERATION [MAIN] SAUVEGARDE TERMINÉE!")
                else:
                    logger.info(f"♻️♻️♻️ SLIDE GENERATION [MAIN] Slide déjà générée - MAIS VÉRIFICATION CONTENU...")
                    logger.info(f"♻️♻️♻️ SLIDE GENERATION [MAIN] Contenu existant LONGUEUR: {len(first_slide.content)}")
                    logger.info(f"♻️♻️♻️ SLIDE GENERATION [MAIN] Contenu existant PREVIEW: {first_slide.content[:200]}...")
                    
                    # CORRECTION : Vérifier si le contenu existant contient du JSON mal parsé
                    if first_slide.content and (first_slide.content.startswith('# Contenu de Formation\n\n[') or 
                                                 '"slide_content"' in first_slide.content):
                        logger.warning(f"🔧🔧🔧 SLIDE GENERATION [MAIN] CONTENU CORROMPU DÉTECTÉ - PARSING JSON...")
                        
                        # Essayer d'extraire le vrai contenu du JSON mal parsé
                        corrected_content = self._fix_corrupted_content(first_slide.content)
                        
                        if corrected_content != first_slide.content:
                            logger.info(f"🔧🔧🔧 SLIDE GENERATION [MAIN] CORRECTION APPLIQUÉE - SAUVEGARDE...")
                            await slide_repo.update_content(first_slide.id, corrected_content)
                            first_slide.content = corrected_content
                            logger.info(f"✅✅✅ SLIDE GENERATION [MAIN] CONTENU CORRIGÉ ET SAUVEGARDÉ!")
                        else:
                            logger.warning(f"⚠️⚠️⚠️ SLIDE GENERATION [MAIN] IMPOSSIBLE DE CORRIGER LE CONTENU")
                
                duration = time.time() - start_time
                
                logger.info(f"🏁🏁🏁 SLIDE GENERATION [RESULT] === CONSTRUCTION RÉSULTAT FINAL ===")
                logger.info(f"🏁🏁🏁 SLIDE GENERATION [RESULT] Slide ID: {first_slide.id}")
                logger.info(f"🏁🏁🏁 SLIDE GENERATION [RESULT] Title: {first_slide.title}")
                logger.info(f"🏁🏁🏁 SLIDE GENERATION [RESULT] Content TYPE: {type(first_slide.content)}")
                logger.info(f"🏁🏁🏁 SLIDE GENERATION [RESULT] Content LONGUEUR: {len(first_slide.content) if first_slide.content else 'NULL'}")
                logger.info(f"🏁🏁🏁 SLIDE GENERATION [RESULT] Content FINAL PREVIEW (500 chars): {first_slide.content[:500] if first_slide.content else 'NULL'}")
                
                # Récupérer les informations de breadcrumb
                logger.info(f"🧭🧭🧭 SLIDE GENERATION [BREADCRUMB] === RÉCUPÉRATION BREADCRUMB ===")
                breadcrumb_info = await slide_repo.get_slide_breadcrumb(first_slide.id)
                logger.info(f"🧭🧭🧭 SLIDE GENERATION [BREADCRUMB] Breadcrumb info: {breadcrumb_info}")
                
                # Mettre à jour le numéro de slide courante de l'apprenant
                logger.info(f"📊📊📊 SLIDE GENERATION [PROGRESS] === MISE À JOUR PROGRESSION ===")
                slide_global_number = await slide_repo.get_slide_global_number(first_slide.id, training_plan.id)
                logger.info(f"📊📊📊 SLIDE GENERATION [PROGRESS] Slide global number: {slide_global_number}")
                
                # Mettre à jour current_slide_number dans learner_session
                from uuid import UUID
                update_success = await learner_session_repo.update_current_slide_number(
                    learner_session_id=UUID(learner_session_id),
                    slide_number=slide_global_number
                )
                logger.info(f"📊📊📊 SLIDE GENERATION [PROGRESS] Update success: {update_success}")
                
                result = {
                    "slide_id": str(first_slide.id),
                    "title": first_slide.title,
                    "content": first_slide.content,
                    "order_in_submodule": first_slide.order_in_submodule,
                    "generated_at": first_slide.generated_at.isoformat() if first_slide.generated_at else None,
                    "generation_duration": round(duration, 2),
                    "breadcrumb": breadcrumb_info,
                    "slide_number": slide_global_number
                }
                
                logger.info(f"🏁🏁🏁 SLIDE GENERATION [RESULT] RÉSULTAT DICT CRÉÉ:")
                logger.info(f"🏁🏁🏁 SLIDE GENERATION [RESULT] Result keys: {list(result.keys())}")
                logger.info(f"🏁🏁🏁 SLIDE GENERATION [RESULT] Result content field: {result.get('content', 'MISSING')[:200]}...")
                
                logger.info(f"✅ SLIDE GENERATION [SUCCESS] First slide generated in {duration:.2f}s - {len(first_slide.content)} chars")
                logger.info(f"🏁🏁🏁 SLIDE GENERATION [RESULT] === RETOUR RÉSULTAT FINAL ===")
                return result
            
            except Exception as e:
                await session.rollback()
                duration = time.time() - start_time
                logger.error(f"❌ SLIDE GENERATION [ERROR] Failed after {duration:.2f}s: {str(e)}")
                raise
    
    async def get_current_slide_content(self, learner_session_id: str) -> Dict[str, Any]:
        """
        Récupérer le contenu de la slide courante de l'apprenant (basé sur current_slide_number)
        Cette méthode est utilisée pour reprendre la formation où l'apprenant s'est arrêté
        
        Args:
            learner_session_id: ID de la session apprenant
            
        Returns:
            Dict contenant les informations de la slide courante
        """
        start_time = time.time()
        
        async with AsyncSessionLocal() as session:
            try:
                logger.info(f"🎯 SLIDE CURRENT [START] Getting current slide for session {learner_session_id}")
                
                # Initialize repositories with session
                learner_session_repo = LearnerSessionRepository(session)
                learner_plan_repo = LearnerTrainingPlanRepository(session)
                slide_repo = TrainingSlideRepository()
                slide_repo.set_session(session)
                
                # 1. Récupérer la session apprenant
                learner_session = await learner_session_repo.get_by_id(learner_session_id)
                if not learner_session:
                    raise ValueError(f"Learner session not found: {learner_session_id}")
                
                # 2. Récupérer le plan de formation personnalisé (le plus récent)
                training_plan = await learner_plan_repo.get_latest_by_learner_session_id(learner_session_id)
                if not training_plan:
                    raise ValueError(f"Training plan not found for session: {learner_session_id}")
                
                # 3. Récupérer la slide courante basée sur current_slide_number
                current_slide_number = learner_session.current_slide_number or 1
                logger.info(f"🎯 SLIDE CURRENT [NUMBER] Current slide number: {current_slide_number}")
                
                current_slide = await slide_repo.get_slide_by_global_number(current_slide_number, training_plan.id)
                if not current_slide:
                    logger.warning(f"⚠️ SLIDE CURRENT [FALLBACK] Slide {current_slide_number} not found, fallback to first slide")
                    current_slide = await slide_repo.get_first_slide(training_plan.id)
                    if not current_slide:
                        raise ValueError(f"No slides found for training plan: {training_plan.id}")
                
                # 4. Générer le contenu de la slide si pas encore généré
                if not current_slide.content:
                    logger.info(f"📝📝📝 SLIDE CURRENT [GENERATE] === GÉNÉRATION CONTENU SLIDE ===")
                    logger.info(f"📝📝📝 SLIDE CURRENT [GENERATE] Slide title: {current_slide.title}")
                    
                    slide_content = await self._generate_slide_content(
                        slide_title=current_slide.title,
                        slide_type=current_slide.slide_type,
                        learner_profile=learner_session,
                        training_plan=training_plan,
                        slide_position="current",
                        current_slide_id=str(current_slide.id)
                    )
                    
                    # 5. Sauvegarder le contenu généré
                    await slide_repo.update_content(current_slide.id, slide_content)
                    current_slide.content = slide_content
                    current_slide.generated_at = datetime.now(timezone.utc)
                    
                    logger.info(f"✅✅✅ SLIDE CURRENT [GENERATE] SAUVEGARDE TERMINÉE!")
                else:
                    logger.info(f"♻️♻️♻️ SLIDE CURRENT [REUSE] Slide déjà générée - réutilisation du contenu")
                
                # 6. Récupérer les informations de breadcrumb
                logger.info(f"🧭🧭🧭 SLIDE CURRENT [BREADCRUMB] === RÉCUPÉRATION BREADCRUMB ===")
                breadcrumb_info = await slide_repo.get_slide_breadcrumb(current_slide.id)
                logger.info(f"🧭🧭🧭 SLIDE CURRENT [BREADCRUMB] Breadcrumb info: {breadcrumb_info}")
                
                # 7. Récupérer les informations de position
                position_info = await slide_repo.get_slide_position(current_slide.id, training_plan.id)
                
                # 8. S'assurer que current_slide_number est bien à jour
                slide_global_number = await slide_repo.get_slide_global_number(current_slide.id, training_plan.id)
                if slide_global_number != current_slide_number:
                    logger.info(f"📊📊📊 SLIDE CURRENT [SYNC] Syncing current_slide_number: {current_slide_number} -> {slide_global_number}")
                    from uuid import UUID
                    await learner_session_repo.update_current_slide_number(
                        learner_session_id=UUID(learner_session_id),
                        slide_number=slide_global_number
                    )
                
                duration = time.time() - start_time
                
                result = {
                    "slide_id": str(current_slide.id),
                    "title": current_slide.title,
                    "content": current_slide.content,
                    "order_in_submodule": current_slide.order_in_submodule,
                    "generated_at": current_slide.generated_at.isoformat() if current_slide.generated_at else None,
                    "generation_duration": round(duration, 2),
                    "breadcrumb": breadcrumb_info,
                    "position": position_info,
                    "slide_number": slide_global_number,
                    "is_resuming": current_slide_number > 1  # Indique si on reprend une session
                }
                
                logger.info(f"✅ SLIDE CURRENT [SUCCESS] Current slide retrieved in {duration:.2f}s - slide #{slide_global_number}")
                return result
                
            except Exception as e:
                await session.rollback()
                duration = time.time() - start_time
                logger.error(f"❌ SLIDE CURRENT [ERROR] Failed after {duration:.2f}s: {str(e)}")
                raise
    
    async def _generate_slide_content(
        self,
        slide_title: str,
        slide_type: str,
        learner_profile: Any,
        training_plan: Any,
        slide_position: str = "first",
        current_slide_id: Optional[str] = None
    ) -> str:
        """
        Générer le contenu markdown d'une slide avec VertexAI
        
        Args:
            slide_title: Titre de la slide
            learner_profile: Profil de l'apprenant (LearnerSession)
            training_plan: Plan de formation (LearnerTrainingPlan)
            slide_position: Position de la slide ("first", "middle", "last")
            
        Returns:
            Contenu markdown de la slide
        """
        try:
            # LOGS SPÉCIFIQUES POUR SLIDES ÉTAPE - DÉBUT GÉNÉRATION
            if slide_type == "stage":
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] === DÉBUT GÉNÉRATION SLIDE ÉTAPE ===")
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] Slide title: {slide_title}")
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] Slide type: {slide_type}")
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] Slide position: {slide_position}")
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] Current slide ID: {current_slide_id}")
            
            # Construire le prompt personnalisé selon le type de slide
            if slide_type == "quiz":
                # Pour les quiz, on a besoin d'informations supplémentaires
                prompt = await self._build_slide_prompt_by_type_async(
                    slide_title=slide_title,
                    slide_type=slide_type,
                    learner_profile=learner_profile,
                    training_plan=training_plan,
                    slide_position=slide_position,
                    current_slide_id=current_slide_id
                )
            else:
                prompt = self._build_slide_prompt_by_type(
                    slide_title=slide_title,
                    slide_type=slide_type,
                    learner_profile=learner_profile,
                    training_plan=training_plan,
                    slide_position=slide_position
                )
            
            # LOGS SPÉCIFIQUES POUR SLIDES ÉTAPE - PROMPT GÉNÉRÉ
            if slide_type == "stage":
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] Prompt généré avec succès")
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] Prompt longueur: {len(prompt)}")
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] Prompt contient 'slide_content': {'slide_content' in prompt}")
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] Prompt contient 'JSON': {'JSON' in prompt}")
            
            # Configuration pour génération de contenu (VertexAI retourne du JSON)
            generation_config = {
                "temperature": 0.7,  # Créativité modérée pour contenu pédagogique
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 2048,  # Suffisant pour une slide
                "response_mime_type": "application/json"  # VertexAI retourne du JSON
            }
            
            logger.info(f"🚀 SLIDE GENERATION [AI] Calling VertexAI for slide content generation...")
            
            # LOGS SPÉCIFIQUES POUR SLIDES ÉTAPE - AVANT VERTEXAI
            if slide_type == "stage":
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] === APPEL VERTEXAI ===")
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] Generation config: {generation_config}")
            
            # Appeler VertexAI pour générer le contenu
            raw_content = await self.vertex_adapter.generate_content(
                prompt=prompt,
                generation_config=generation_config
            )
            
            # LOGS SPÉCIFIQUES POUR SLIDES ÉTAPE - RÉPONSE VERTEXAI
            if slide_type == "stage":
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] === RÉPONSE VERTEXAI REÇUE ===")
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] Raw content type: {type(raw_content)}")
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] Raw content longueur: {len(raw_content) if raw_content else 'NULL'}")
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] Raw content preview (500 chars): {raw_content[:500] if raw_content else 'NULL'}")
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] Raw content contient 'slide_content': {'slide_content' in raw_content if raw_content else False}")
            
            # Parser le JSON et extraire le content markdown
            content = self._extract_content_from_json(raw_content)
            
            # LOGS SPÉCIFIQUES POUR SLIDES ÉTAPE - APRÈS EXTRACTION JSON
            if slide_type == "stage":
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] === APRÈS EXTRACTION JSON ===")
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] Extracted content type: {type(content)}")
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] Extracted content longueur: {len(content) if content else 'NULL'}")
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] Extracted content preview (500 chars): {content[:500] if content else 'NULL'}")
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] Extracted content est markdown?: {content.startswith('#') if content else False}")
            
            # Nettoyer et valider le contenu
            cleaned_content = self._clean_markdown_content(content)
            
            # LOGS SPÉCIFIQUES POUR SLIDES ÉTAPE - APRÈS NETTOYAGE
            if slide_type == "stage":
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] === APRÈS NETTOYAGE MARKDOWN ===")
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] Cleaned content type: {type(cleaned_content)}")
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] Cleaned content longueur: {len(cleaned_content) if cleaned_content else 'NULL'}")
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] Cleaned content preview (500 chars): {cleaned_content[:500] if cleaned_content else 'NULL'}")
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] === GÉNÉRATION SLIDE ÉTAPE TERMINÉE ===")
                logger.info(f"🎭🎭🎭 STAGE SLIDE [GENERATION] Content final prêt pour retour: {len(cleaned_content)} caractères")
            
            logger.info(f"✅ SLIDE GENERATION [AI] Content generated - {len(cleaned_content)} characters")
            return cleaned_content
            
        except Exception as e:
            logger.error(f"❌ SLIDE GENERATION [AI] Failed to generate content: {str(e)}")
            raise VertexAIError(f"Slide content generation failed: {str(e)}", original_error=e)
    
    async def simplify_slide_content(self, learner_session_id: str, current_slide_content: str) -> Dict[str, Any]:
        """
        Simplifier le contenu d'une slide existante selon le profil de l'apprenant
        
        Args:
            learner_session_id: ID de la session apprenant
            current_slide_content: Contenu markdown actuel de la slide
            
        Returns:
            Dict contenant le contenu simplifié
        """
        start_time = time.time()
        
        async with AsyncSessionLocal() as session:
            try:
                logger.info(f"🎯 SLIDE SIMPLIFY [START] Simplifying slide for session {learner_session_id}")
                
                # Initialize repositories
                learner_session_repo = LearnerSessionRepository(session)
                
                # Récupérer la session apprenant pour le profil
                learner_session = await learner_session_repo.get_by_id(learner_session_id)
                if not learner_session:
                    raise ValueError(f"Learner session not found: {learner_session_id}")
                
                # Générer le contenu simplifié
                logger.info(f"📝 SLIDE SIMPLIFY [AI] Calling VertexAI for content simplification...")
                
                simplified_content = await self._generate_simplified_content(
                    current_content=current_slide_content,
                    learner_profile=learner_session
                )
                
                duration = time.time() - start_time
                
                result = {
                    "simplified_content": simplified_content,
                    "original_length": len(current_slide_content),
                    "simplified_length": len(simplified_content),
                    "processing_time": round(duration, 2),
                    "learner_session_id": learner_session_id
                }
                
                logger.info(f"✅ SLIDE SIMPLIFY [SUCCESS] Content simplified in {duration:.2f}s - {len(current_slide_content)} → {len(simplified_content)} chars")
                return result
                
            except Exception as e:
                await session.rollback()
                duration = time.time() - start_time
                logger.error(f"❌ SLIDE SIMPLIFY [ERROR] Failed after {duration:.2f}s: {str(e)}")
                raise
    
    async def more_details_slide_content(self, learner_session_id: str, current_slide_content: str) -> Dict[str, Any]:
        """
        Approfondir le contenu d'une slide existante selon le profil de l'apprenant
        
        Args:
            learner_session_id: ID de la session apprenant
            current_slide_content: Contenu markdown actuel de la slide
            
        Returns:
            Dict contenant le contenu approfondi
        """
        start_time = time.time()
        
        async with AsyncSessionLocal() as session:
            try:
                logger.info(f"🎯 SLIDE MORE_DETAILS [START] Adding more details for session {learner_session_id}")
                
                # Initialize repositories
                learner_session_repo = LearnerSessionRepository(session)
                
                # Récupérer la session apprenant pour le profil
                learner_session = await learner_session_repo.get_by_id(learner_session_id)
                if not learner_session:
                    raise ValueError(f"Learner session not found: {learner_session_id}")
                
                # Générer le contenu approfondi
                logger.info(f"📝 SLIDE MORE_DETAILS [AI] Calling VertexAI for content enhancement...")
                
                detailed_content = await self._generate_more_details_content(
                    current_content=current_slide_content,
                    learner_profile=learner_session
                )
                
                duration = time.time() - start_time
                
                result = {
                    "detailed_content": detailed_content,
                    "original_length": len(current_slide_content),
                    "detailed_length": len(detailed_content),
                    "processing_time": round(duration, 2),
                    "learner_session_id": learner_session_id
                }
                
                logger.info(f"✅ SLIDE MORE_DETAILS [SUCCESS] Content enhanced in {duration:.2f}s - {len(current_slide_content)} → {len(detailed_content)} chars")
                return result
                
            except Exception as e:
                await session.rollback()
                duration = time.time() - start_time
                logger.error(f"❌ SLIDE MORE_DETAILS [ERROR] Failed after {duration:.2f}s: {str(e)}")
                raise
    
    async def _generate_simplified_content(
        self,
        current_content: str,
        learner_profile: Any
    ) -> str:
        """
        Générer une version simplifiée du contenu avec VertexAI
        
        Args:
            current_content: Contenu markdown actuel
            learner_profile: Profil de l'apprenant (LearnerSession)
            
        Returns:
            Contenu markdown simplifié
        """
        try:
            # Construire le prompt de simplification
            prompt = self._build_simplify_prompt(
                current_content=current_content,
                learner_profile=learner_profile
            )
            
            # Configuration VertexAI pour simplification (même format JSON que la génération initiale)
            generation_config = {
                "temperature": 0.3,  # Température basse pour cohérence
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 2048,
                "response_mime_type": "application/json"  # JSON comme la génération initiale
            }
            
            logger.info(f"🚀 SLIDE SIMPLIFY [AI] Calling VertexAI for content simplification...")
            
            # Appeler VertexAI pour simplifier le contenu
            raw_content = await self.vertex_adapter.generate_content(
                prompt=prompt,
                generation_config=generation_config
            )
            
            # Parser le JSON et extraire le contenu markdown (même processus que la génération initiale)
            simplified_content = self._extract_content_from_json(raw_content)
            
            # Nettoyer et valider le contenu
            cleaned_content = self._clean_markdown_content(simplified_content)
            
            logger.info(f"✅ SLIDE SIMPLIFY [AI] Content simplified - {len(cleaned_content)} characters")
            return cleaned_content
            
        except Exception as e:
            logger.error(f"❌ SLIDE SIMPLIFY [AI] Failed to simplify content: {str(e)}")
            raise VertexAIError(f"Slide simplification failed: {str(e)}", original_error=e)
    
    async def _generate_more_details_content(
        self,
        current_content: str,
        learner_profile: Any
    ) -> str:
        """
        Générer une version approfondie du contenu avec VertexAI
        
        Args:
            current_content: Contenu markdown actuel
            learner_profile: Profil de l'apprenant (LearnerSession)
            
        Returns:
            Contenu markdown approfondi
        """
        try:
            # Construire le prompt d'approfondissement
            prompt = self._build_more_details_prompt(
                current_content=current_content,
                learner_profile=learner_profile
            )
            
            # Configuration VertexAI pour approfondissement (même format JSON que les autres)
            generation_config = {
                "temperature": 0.5,  # Température modérée pour créativité contrôlée
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 3072,  # Plus de tokens pour plus de détails
                "response_mime_type": "application/json"  # JSON comme les autres méthodes
            }
            
            logger.info(f"🚀 SLIDE MORE_DETAILS [AI] Calling VertexAI for content enhancement...")
            
            # Appeler VertexAI pour approfondir le contenu
            raw_content = await self.vertex_adapter.generate_content(
                prompt=prompt,
                generation_config=generation_config
            )
            
            # Parser le JSON et extraire le contenu markdown (même processus que les autres)
            detailed_content = self._extract_content_from_json(raw_content)
            
            # Nettoyer et valider le contenu
            cleaned_content = self._clean_markdown_content(detailed_content)
            
            logger.info(f"✅ SLIDE MORE_DETAILS [AI] Content enhanced - {len(cleaned_content)} characters")
            return cleaned_content
            
        except Exception as e:
            logger.error(f"❌ SLIDE MORE_DETAILS [AI] Failed to enhance content: {str(e)}")
            raise VertexAIError(f"Slide content enhancement failed: {str(e)}", original_error=e)
    
    def _build_simplify_prompt(
        self,
        current_content: str,
        learner_profile: Any
    ) -> str:
        """
        Construire le prompt pour simplifier le contenu d'une slide
        
        Args:
            current_content: Contenu markdown actuel de la slide
            learner_profile: Profil de l'apprenant (LearnerSession)
            
        Returns:
            Prompt optimisé pour la simplification
        """
        # Extraire les informations du profil apprenant
        profile_info = {
            "niveau": learner_profile.experience_level or "débutant", 
            "style_apprentissage": learner_profile.learning_style or "visuel",
            "poste": learner_profile.job_position or "non spécifié",
            "secteur": learner_profile.activity_sector or "non spécifié",
            "langue": learner_profile.language or "français"
        }
        
        prompt = f"""Tu es un expert pédagogue spécialisé dans la simplification de contenu éducatif.

MISSION :
Simplifie le contenu de slide de formation ci-dessous pour le rendre plus accessible à l'apprenant selon son profil.

CONTENU ACTUEL À SIMPLIFIER :
{current_content}

PROFIL APPRENANT :
- Niveau d'expérience : {profile_info['niveau']}
- Style d'apprentissage : {profile_info['style_apprentissage']}
- Poste : {profile_info['poste']}
- Secteur d'activité : {profile_info['secteur']}
- Langue : {profile_info['langue']}

RÈGLES DE SIMPLIFICATION :
1. **Langage accessible** : Utilise un vocabulaire simple et clair adapté au niveau {profile_info['niveau']}
2. **Structure claire** : Conserve la structure markdown mais simplifie la présentation
3. **Concepts essentiels** : Concentre-toi sur les points les plus importants
4. **Exemples concrets** : Remplace les concepts abstraits par des exemples pratiques du secteur {profile_info['secteur']}
5. **Format {profile_info['style_apprentissage']}** : Adapte au style d'apprentissage privilégié
6. **Phrases courtes** : Utilise des phrases courtes et directes
7. **Points clés** : Mets en évidence les informations essentielles

CONTRAINTES TECHNIQUES :
- Réponds en format JSON avec la structure suivante :
{{
  "slide_content": "Le contenu markdown simplifié ici"
}}
- Le contenu dans slide_content doit être du markdown pur
- Garde la même structure markdown (titres, listes, etc.) mais simplifie le texte
- Réduis la complexité sans perdre l'information essentielle
- Longueur cible : 50-70% du contenu original
- Reste professionnel et pédagogique

Génère maintenant la version simplifiée au format JSON :"""

        logger.info(f"🎯 SLIDE SIMPLIFY [PROMPT] Built simplify prompt for level: {profile_info['niveau']}, style: {profile_info['style_apprentissage']}")
        
        return prompt
    
    def _build_more_details_prompt(
        self,
        current_content: str,
        learner_profile: Any
    ) -> str:
        """
        Construire le prompt pour approfondir le contenu d'une slide
        
        Args:
            current_content: Contenu markdown actuel de la slide
            learner_profile: Profil de l'apprenant (LearnerSession)
            
        Returns:
            Prompt optimisé pour l'approfondissement
        """
        # Extraire les informations du profil apprenant
        profile_info = {
            "niveau": learner_profile.experience_level or "débutant", 
            "style_apprentissage": learner_profile.learning_style or "visuel",
            "poste": learner_profile.job_position or "non spécifié",
            "secteur": learner_profile.activity_sector or "non spécifié",
            "langue": learner_profile.language or "français"
        }
        
        prompt = f"""Tu es un expert pédagogue spécialisé dans l'approfondissement de contenu éducatif.

MISSION :
Approfondis le contenu de slide de formation ci-dessous pour le rendre plus détaillé et technique selon le profil de l'apprenant.

CONTENU ACTUEL À APPROFONDIR :
{current_content}

PROFIL APPRENANT :
- Niveau d'expérience : {profile_info['niveau']}
- Style d'apprentissage : {profile_info['style_apprentissage']}
- Poste : {profile_info['poste']}
- Secteur d'activité : {profile_info['secteur']}
- Langue : {profile_info['langue']}

RÈGLES D'APPROFONDISSEMENT :
1. **Vocabulaire technique** : Utilise des termes métier et concepts avancés adaptés au niveau {profile_info['niveau']}
2. **Détails techniques** : Ajoute des explications techniques, processus, mécanismes
3. **Concepts avancés** : Introduis des notions plus complexes et spécialisées
4. **Exemples techniques** : Inclus des exemples détaillés et cas d'usage du secteur {profile_info['secteur']}
5. **Format {profile_info['style_apprentissage']}** : Adapte au style d'apprentissage privilégié
6. **Approfondissements** : Ajoute des sections avec plus de détails, références, liens
7. **Précisions métier** : Inclus des spécificités techniques du domaine

CONTRAINTES TECHNIQUES :
- Réponds en format JSON avec la structure suivante :
{{
  "slide_content": "Le contenu markdown approfondi ici"
}}
- Le contenu dans slide_content doit être du markdown pur
- Garde la même structure markdown (titres, listes, etc.) mais ajoute du contenu
- Ajoute 30-50% de contenu supplémentaire avec plus de détails
- Utilise un niveau de langage plus technique et précis
- Reste professionnel et pédagogique mais plus avancé

Génère maintenant la version approfondie au format JSON :"""

        logger.info(f"🎯 SLIDE MORE_DETAILS [PROMPT] Built enhancement prompt for level: {profile_info['niveau']}, style: {profile_info['style_apprentissage']}")
        
        return prompt
    
    def _build_slide_prompt(
        self,
        slide_title: str,
        learner_profile: Any,
        training_plan: Any,
        slide_position: str
    ) -> str:
        """Construire le prompt personnalisé pour générer le contenu de la slide"""
        
        # Extraire les informations du profil apprenant de base
        profile_info = {
            "niveau": learner_profile.experience_level or "débutant",
            "style_apprentissage": learner_profile.learning_style or "visuel",
            "poste": learner_profile.job_position or "non spécifié",
            "secteur": learner_profile.activity_sector or "non spécifié",
            "langue": learner_profile.language or "français"
        }
        
        # Récupérer le profil enrichi s'il existe
        enriched_profile_context = ""
        if hasattr(learner_profile, 'enriched_profile') and learner_profile.enriched_profile:
            enriched_data = learner_profile.enriched_profile
            
            enriched_insights = []
            if enriched_data.get("learning_style_observed"):
                enriched_insights.append(f"Style d'apprentissage observé : {enriched_data['learning_style_observed']}")
            if enriched_data.get("comprehension_level"):
                enriched_insights.append(f"Niveau de compréhension : {enriched_data['comprehension_level']}")
            if enriched_data.get("interests"):
                enriched_insights.append(f"Centres d'intérêt : {', '.join(enriched_data['interests'])}")
            if enriched_data.get("blockers"):
                enriched_insights.append(f"Difficultés identifiées : {', '.join(enriched_data['blockers'])}")
            if enriched_data.get("objectives"):
                enriched_insights.append(f"Objectifs spécifiques : {enriched_data['objectives']}")
            if enriched_data.get("engagement_patterns"):
                enriched_insights.append(f"Style d'engagement : {enriched_data['engagement_patterns']}")
            
            if enriched_insights:
                enriched_profile_context = f"""
PROFIL ENRICHI OBSERVÉ :
{chr(10).join(f"- {insight}" for insight in enriched_insights)}

IMPORTANTE : Utilise ces insights pour personnaliser au maximum le contenu de cette slide !
"""
        
        # Extraire des informations du plan de formation
        plan_context = ""
        if hasattr(training_plan, 'plan_data') and training_plan.plan_data:
            try:
                plan_data = training_plan.plan_data if isinstance(training_plan.plan_data, dict) else json.loads(training_plan.plan_data)
                if 'formation_plan' in plan_data:
                    plan_context = f"Contexte du plan de formation : {plan_data['formation_plan'].get('objectifs_generaux', 'Formation personnalisée')}"
            except (json.JSONDecodeError, KeyError, AttributeError):
                plan_context = "Formation personnalisée selon le profil apprenant"
        
        prompt = f"""Tu es un expert pédagogue qui crée du contenu de formation personnalisé.

CONTEXTE :
- Titre de la slide : "{slide_title}"
- Position : {slide_position} slide de la formation
- {plan_context}

PROFIL APPRENANT :
- Niveau d'expérience : {profile_info['niveau']}
- Style d'apprentissage : {profile_info['style_apprentissage']}
- Poste : {profile_info['poste']}
- Secteur d'activité : {profile_info['secteur']}
- Langue : {profile_info['langue']}
{enriched_profile_context}

INSTRUCTIONS :
1. Crée le contenu d'une slide de formation en markdown
2. Adapte le contenu au profil de l'apprenant (niveau, style, contexte professionnel)
3. Structure pédagogique claire avec titre, sous-titres, points clés
4. Inclus des éléments visuels (listes, citations, exemples)
5. Longueur appropriée pour une slide (300-800 mots)
6. Style engageant et professionnel

CONTRAINTES :
- Réponds UNIQUEMENT avec le contenu markdown de la slide
- Commence directement par le contenu, pas de préambule
- Utilise des éléments markdown : # ## ### - > ** *
- Adapte les exemples au secteur d'activité si pertinent

Génère maintenant le contenu de la slide :"""

        return prompt
    
    def _build_slide_prompt_by_type(
        self,
        slide_title: str,
        slide_type: str,
        learner_profile: Any,
        training_plan: Any,
        slide_position: str
    ) -> str:
        """Construire le prompt selon le type de slide"""
        
        # Import de l'enum pour la validation
        from app.domain.entities.training_slide import SlideType
        
        # Valider le type de slide
        try:
            slide_type_enum = SlideType(slide_type)
        except ValueError:
            # Fallback vers content si type invalide
            slide_type_enum = SlideType.CONTENT
            logger.warning(f"⚠️ Invalid slide type '{slide_type}', using 'content' as fallback")
        
        # LOGS SPÉCIFIQUES POUR SLIDES ÉTAPE
        if slide_type_enum == SlideType.STAGE:
            logger.info(f"🎭🎭🎭 STAGE SLIDE [PROMPT] === GÉNÉRATION PROMPT SLIDE ÉTAPE ===")
            logger.info(f"🎭🎭🎭 STAGE SLIDE [PROMPT] Slide title: {slide_title}")
            logger.info(f"🎭🎭🎭 STAGE SLIDE [PROMPT] Slide type: {slide_type}")
            logger.info(f"🎭🎭🎭 STAGE SLIDE [PROMPT] Learner profile: {learner_profile.email if hasattr(learner_profile, 'email') else 'N/A'}")
        
        # Sélectionner le prompt selon le type
        if slide_type_enum == SlideType.PLAN:
            return self._build_plan_slide_prompt(slide_title, learner_profile, training_plan)
        elif slide_type_enum == SlideType.STAGE:
            prompt = self._build_stage_slide_prompt(slide_title, learner_profile, training_plan)
            logger.info(f"🎭🎭🎭 STAGE SLIDE [PROMPT] Prompt généré (longueur: {len(prompt)})")
            logger.info(f"🎭🎭🎭 STAGE SLIDE [PROMPT] Prompt preview (500 chars): {prompt[:500]}")
            return prompt
        elif slide_type_enum == SlideType.MODULE:
            return self._build_module_slide_prompt(slide_title, learner_profile, training_plan)
        elif slide_type_enum == SlideType.QUIZ:
            return self._build_quiz_slide_prompt(slide_title, learner_profile, training_plan)
        else:  # SlideType.CONTENT
            return self._build_slide_prompt(slide_title, learner_profile, training_plan, slide_position)
    
    def _build_plan_slide_prompt(self, slide_title: str, learner_profile: Any, training_plan: Any) -> str:
        """Construire le prompt pour une slide de type plan"""
        
        # Extraire les informations du profil apprenant
        profile_info = {
            "niveau": learner_profile.experience_level or "débutant",
            "style_apprentissage": learner_profile.learning_style or "visuel",
            "poste": learner_profile.job_position or "non spécifié",
            "secteur": learner_profile.activity_sector or "non spécifié",
            "langue": learner_profile.language or "français"
        }
        
        # Récupérer le profil enrichi s'il existe
        enriched_context = ""
        if hasattr(learner_profile, 'enriched_profile') and learner_profile.enriched_profile:
            enriched_data = learner_profile.enriched_profile
            if enriched_data.get("objectives"):
                enriched_context += f"- Objectifs spécifiques : {enriched_data['objectives']}\n"
            if enriched_data.get("interests"):
                enriched_context += f"- Centres d'intérêt : {', '.join(enriched_data['interests'])}\n"
        
        # Extraire et formater intelligemment la structure du plan
        plan_structure = self._extract_plan_structure(training_plan)
        
        prompt = f"""Tu es un expert pédagogue créant une slide de plan de formation personnalisée.

CONTEXTE :
- Type de slide : PLAN (vue d'ensemble complète de la formation)
- Titre : "{slide_title}"
- Formation personnalisée pour ce profil apprenant

PROFIL APPRENANT :
- Niveau : {profile_info['niveau']}
- Style d'apprentissage : {profile_info['style_apprentissage']}
- Poste : {profile_info['poste']}
- Secteur : {profile_info['secteur']}
- Langue : {profile_info['langue']}
{enriched_context}

STRUCTURE DE LA FORMATION :
{plan_structure}

CONSIGNES POUR SLIDE DE PLAN :
1. Crée une vue d'ensemble engageante et complète de la formation
2. Commence par une introduction personnalisée au profil apprenant
3. Structure markdown hiérarchique :
   - # Titre principal de la formation (adapté au secteur {profile_info['secteur']})
   - ## 👋 Bienvenue dans votre formation personnalisée
   - ## 📋 Plan de la formation
   - ### Étape 1: [Titre] → Modules → Objectifs principaux
   - ### Étape 2: [Titre] → Modules → Objectifs principaux
   - (etc. pour toutes les étapes)
   - ## 🎯 Ce que vous allez apprendre
   - ## ⏱️ Durée estimée et recommandations
4. Adapte le vocabulaire au niveau {profile_info['niveau']} et secteur {profile_info['secteur']}
5. Style {profile_info['style_apprentissage']} : privilégie les éléments visuels/pratiques/théoriques selon le style
6. Ton motivant et professionnel

CONTRAINTES STRICTES :
- Tu dois répondre avec un JSON qui contient le contenu markdown dans le champ "slide_content"
- Format JSON attendu : {{"slide_content": "le contenu markdown ici"}}
- Le contenu dans slide_content doit être du markdown pur sans balises JSON
- Utilise la structure fournie mais reformule de manière engageante
- Longueur : 500-800 mots
- Inclus des émojis discrets pour l'engagement (📚 🎯 ✨ etc.)
- Termine par une phrase encourageante personnalisée
- IMPORTANT: Le markdown ne doit pas contenir de structure JSON, juste du texte formaté markdown

Génère maintenant le contenu de la slide de plan au format JSON avec le markdown dans slide_content :"""
        
        return prompt
    
    def _extract_plan_structure(self, training_plan: Any) -> str:
        """Extraire et formater intelligemment la structure du plan de formation"""
        if not hasattr(training_plan, 'plan_data') or not training_plan.plan_data:
            return "Structure de formation personnalisée (5 étapes avec modules et sous-modules)"
        
        try:
            plan_data = training_plan.plan_data if isinstance(training_plan.plan_data, dict) else json.loads(training_plan.plan_data)
            training_plan_data = plan_data.get("training_plan", {})
            stages = training_plan_data.get("stages", [])
            
            if not stages:
                return "Structure de formation personnalisée (5 étapes avec modules et sous-modules)"
            
            structure_lines = []
            
            for stage in stages:
                stage_num = stage.get("stage_number", "?")
                stage_title = stage.get("title", "Étape sans titre")
                modules = stage.get("modules", [])
                
                structure_lines.append(f"ÉTAPE {stage_num}: {stage_title}")
                
                for module in modules:
                    module_name = module.get("module_name", "Module sans nom")
                    submodules = module.get("submodules", [])
                    structure_lines.append(f"  • Module: {module_name}")
                    
                    for submodule in submodules:
                        submodule_name = submodule.get("submodule_name", "Sous-module")
                        slide_count = submodule.get("slide_count", 0)
                        structure_lines.append(f"    - {submodule_name} ({slide_count} slides)")
                
                structure_lines.append("")  # Ligne vide entre les étapes
            
            return "\n".join(structure_lines)
            
        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            logger.warning(f"⚠️ Error extracting plan structure: {e}")
            return "Structure de formation personnalisée (5 étapes avec modules et sous-modules)"
    
    def _build_stage_slide_prompt(self, slide_title: str, learner_profile: Any, training_plan: Any) -> str:
        """Construire le prompt pour une slide de type étape"""
        
        profile_info = {
            "niveau": learner_profile.experience_level or "débutant",
            "style_apprentissage": learner_profile.learning_style or "visuel",
            "poste": learner_profile.job_position or "non spécifié",
            "secteur": learner_profile.activity_sector or "non spécifié"
        }
        
        # Extraire les informations de l'étape spécifique
        stage_context = self._extract_stage_context(slide_title, training_plan)
        
        # Récupérer le profil enrichi s'il existe
        enriched_context = ""
        if hasattr(learner_profile, 'enriched_profile') and learner_profile.enriched_profile:
            enriched_data = learner_profile.enriched_profile
            if enriched_data.get("learning_style_observed"):
                enriched_context += f"- Style d'apprentissage observé : {enriched_data['learning_style_observed']}\n"
            if enriched_data.get("blockers"):
                enriched_context += f"- Difficultés à éviter : {', '.join(enriched_data['blockers'])}\n"
        
        prompt = f"""Tu es un expert pédagogue créant une slide d'introduction d'étape motivante.

CONTEXTE :
- Type de slide : ÉTAPE (introduction et transition vers une nouvelle étape)
- Titre : "{slide_title}"
- Position dans la formation : Transition importante entre les étapes

PROFIL APPRENANT :
- Niveau : {profile_info['niveau']}
- Style d'apprentissage : {profile_info['style_apprentissage']}
- Poste : {profile_info['poste']}
- Secteur : {profile_info['secteur']}
{enriched_context}

CONTEXTE DE L'ÉTAPE :
{stage_context}

CONSIGNES POUR SLIDE D'ÉTAPE :
1. Crée une introduction motivante qui fait la transition depuis l'étape précédente
2. Structure markdown engageante :
   - # Titre de l'étape avec émoji approprié
   - ## 🎯 Pourquoi cette étape est importante pour vous
   - ## 📋 Ce que vous allez découvrir (modules principaux)
   - ## 🚀 Objectifs d'apprentissage spécifiques
   - ## ⏱️ Ce qui vous attend (durée et approche)
   - ## 💡 Conseil pour réussir cette étape
3. Adapte le vocabulaire au niveau {profile_info['niveau']} et secteur {profile_info['secteur']}
4. Style {profile_info['style_apprentissage']} : privilégie les éléments adaptés au style
5. Ton motivant et bienveillant qui donne envie de continuer
6. Personnalise selon le poste {profile_info['poste']}

CONTRAINTES STRICTES :
- Tu dois répondre avec un JSON qui contient le contenu markdown dans le champ "slide_content"
- Format JSON attendu : {{"slide_content": "le contenu markdown ici"}}
- Le contenu dans slide_content doit être du markdown pur sans balises JSON
- Longueur : 300-500 mots
- Utilise les émojis avec parcimonie mais de manière engageante
- Termine par une phrase de transition vers le premier module
- Reste professionnel mais chaleureux
- IMPORTANT: Le markdown ne doit pas contenir de structure JSON, juste du texte formaté markdown

Génère maintenant le contenu de la slide d'étape au format JSON avec le markdown dans slide_content :"""
        
        return prompt
    
    def _extract_stage_context(self, slide_title: str, training_plan: Any) -> str:
        """Extraire le contexte spécifique d'une étape depuis le training_plan"""
        if not hasattr(training_plan, 'plan_data') or not training_plan.plan_data:
            return f"Étape de formation basée sur le titre : {slide_title}"
        
        try:
            plan_data = training_plan.plan_data if isinstance(training_plan.plan_data, dict) else json.loads(training_plan.plan_data)
            stages = plan_data.get("training_plan", {}).get("stages", [])
            
            # Essayer de trouver l'étape correspondante au titre
            for stage in stages:
                stage_title = stage.get("title", "")
                stage_number = stage.get("stage_number", 0)
                
                # Vérifier si le titre de la slide correspond à cette étape
                if (stage_title.lower() in slide_title.lower() or 
                    f"étape {stage_number}" in slide_title.lower() or
                    f"stage {stage_number}" in slide_title.lower()):
                    
                    modules = stage.get("modules", [])
                    context_lines = [
                        f"Étape {stage_number}: {stage_title}",
                        f"Nombre de modules: {len(modules)}"
                    ]
                    
                    if modules:
                        context_lines.append("Modules inclus:")
                        for module in modules:
                            module_name = module.get("module_name", "Module")
                            submodules = module.get("submodules", [])
                            submodule_count = len(submodules)
                            context_lines.append(f"  • {module_name} ({submodule_count} sous-modules)")
                    
                    return "\n".join(context_lines)
            
            # Si aucune correspondance exacte, retourner une info générale
            return f"Étape de formation (parmi {len(stages)} étapes total)"
            
        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            logger.warning(f"⚠️ Error extracting stage context: {e}")
            return f"Étape de formation basée sur le titre : {slide_title}"
    
    def _build_module_slide_prompt(self, slide_title: str, learner_profile: Any, training_plan: Any) -> str:
        """Construire le prompt pour une slide de type module"""
        
        profile_info = {
            "niveau": learner_profile.experience_level or "débutant",
            "style_apprentissage": learner_profile.learning_style or "visuel",
            "poste": learner_profile.job_position or "non spécifié",
            "secteur": learner_profile.activity_sector or "non spécifié"
        }
        
        # Extraire le contexte spécifique du module
        module_context = self._extract_module_context(slide_title, training_plan)
        
        # Récupérer le profil enrichi s'il existe
        enriched_context = ""
        if hasattr(learner_profile, 'enriched_profile') and learner_profile.enriched_profile:
            enriched_data = learner_profile.enriched_profile
            if enriched_data.get("comprehension_level"):
                enriched_context += f"- Niveau de compréhension observé : {enriched_data['comprehension_level']}\n"
            if enriched_data.get("interests"):
                enriched_context += f"- Points d'intérêt : {', '.join(enriched_data['interests'])}\n"
        
        prompt = f"""Tu es un expert pédagogue créant une slide d'introduction de module pratique et engageante.

CONTEXTE :
- Type de slide : MODULE (introduction et structuration d'un module d'apprentissage)
- Titre : "{slide_title}"
- Position : Démarrage d'un nouveau module de formation

PROFIL APPRENANT :
- Niveau : {profile_info['niveau']}
- Style d'apprentissage : {profile_info['style_apprentissage']}
- Poste : {profile_info['poste']}
- Secteur : {profile_info['secteur']}
{enriched_context}

CONTEXTE DU MODULE :
{module_context}

CONSIGNES POUR SLIDE DE MODULE :
1. Crée une introduction pratique et concrète du module
2. Structure markdown claire et actionnable :
   - # Titre du module avec icône appropriée
   - ## 🎯 Objectif principal de ce module
   - ## 📚 Ce que vous allez découvrir (sous-modules)
   - ## 🛠️ Compétences pratiques à acquérir
   - ## 💼 Applications dans votre métier de {profile_info['poste']}
   - ## ⚡ Points clés à retenir
   - ## ⏭️ Comment aborder ce module
3. Adapte spécifiquement au secteur {profile_info['secteur']} avec exemples concrets
4. Style {profile_info['style_apprentissage']} : privilégie l'approche la plus adaptée
5. Ton professionnel mais accessible, avec focus sur l'application pratique
6. Connecte avec les besoins métier du poste {profile_info['poste']}

CONTRAINTES :
- Réponds UNIQUEMENT avec le contenu markdown pur (pas de JSON)
- Longueur : 250-400 mots
- Reste très concret et applicable
- Utilise des exemples du secteur {profile_info['secteur']}
- Termine par une accroche vers le premier sous-module

Génère maintenant le contenu de la slide de module :"""
        
        return prompt
    
    def _extract_module_context(self, slide_title: str, training_plan: Any) -> str:
        """Extraire le contexte spécifique d'un module depuis le training_plan"""
        if not hasattr(training_plan, 'plan_data') or not training_plan.plan_data:
            return f"Module de formation basé sur le titre : {slide_title}"
        
        try:
            plan_data = training_plan.plan_data if isinstance(training_plan.plan_data, dict) else json.loads(training_plan.plan_data)
            stages = plan_data.get("training_plan", {}).get("stages", [])
            
            # Parcourir toutes les étapes et modules pour trouver une correspondance
            for stage in stages:
                modules = stage.get("modules", [])
                for module in modules:
                    module_name = module.get("module_name", "")
                    
                    # Vérifier si le titre de la slide correspond à ce module
                    if (module_name.lower() in slide_title.lower() or 
                        any(word in slide_title.lower() for word in module_name.lower().split())):
                        
                        submodules = module.get("submodules", [])
                        context_lines = [
                            f"Module: {module_name}",
                            f"Étape parente: {stage.get('title', 'Non spécifiée')}",
                            f"Nombre de sous-modules: {len(submodules)}"
                        ]
                        
                        if submodules:
                            context_lines.append("Sous-modules inclus:")
                            for submodule in submodules:
                                submodule_name = submodule.get("submodule_name", "Sous-module")
                                slide_count = submodule.get("slide_count", 0)
                                context_lines.append(f"  • {submodule_name} ({slide_count} slides)")
                        
                        return "\n".join(context_lines)
            
            # Si aucune correspondance exacte, retourner une info générale
            total_modules = sum(len(stage.get("modules", [])) for stage in stages)
            return f"Module de formation (parmi {total_modules} modules au total)"
            
        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            logger.warning(f"⚠️ Error extracting module context: {e}")
            return f"Module de formation basé sur le titre : {slide_title}"
    
    def _build_quiz_slide_prompt(self, slide_title: str, learner_profile: Any, training_plan: Any) -> str:
        """Construire le prompt pour une slide de type quiz"""
        
        profile_info = {
            "niveau": learner_profile.experience_level or "débutant",
            "secteur": learner_profile.activity_sector or "non spécifié"
        }
        
        prompt = f"""Tu es un expert pédagogue créant une slide de quiz/évaluation.

CONTEXTE :
- Type de slide : QUIZ (évaluation des acquis)
- Titre : "{slide_title}"

PROFIL APPRENANT :
- Niveau : {profile_info['niveau']}
- Secteur : {profile_info['secteur']}

CONSIGNES POUR SLIDE DE QUIZ :
1. Crée une évaluation interactive des connaissances acquises
2. Structure markdown avec :
   - # Titre du quiz
   - ## Instructions pour le quiz
   - ### Question 1: [Type de question]
   - ### Question 2: [Type de question]
   - etc. (5 questions au total)
   - ## Comment utiliser le chat pour répondre
3. 5 questions variées : QCM, questions ouvertes, cas pratiques
4. Adapté au niveau {profile_info['niveau']} et secteur {profile_info['secteur']}
5. Instructions claires pour utiliser le chat IA pour les réponses
6. Longueur : 300-500 mots

IMPORTANT : Rappelle que l'apprenant peut répondre en utilisant le chat IA qui corrigera ses réponses.

Génère maintenant le contenu de la slide de quiz :"""
        
        return prompt
    
    async def _build_slide_prompt_by_type_async(
        self,
        slide_title: str,
        slide_type: str,
        learner_profile: Any,
        training_plan: Any,
        slide_position: str,
        current_slide_id: Optional[str] = None
    ) -> str:
        """Construire le prompt selon le type de slide de façon asynchrone (pour quiz)"""
        
        # Import de l'enum pour la validation
        from app.domain.entities.training_slide import SlideType
        
        # Valider le type de slide
        try:
            slide_type_enum = SlideType(slide_type)
        except ValueError:
            # Fallback vers content si type invalide
            slide_type_enum = SlideType.CONTENT
            logger.warning(f"⚠️ Invalid slide type '{slide_type}', using 'content' as fallback")
        
        # Sélectionner le prompt selon le type
        if slide_type_enum == SlideType.PLAN:
            return self._build_plan_slide_prompt(slide_title, learner_profile, training_plan)
        elif slide_type_enum == SlideType.STAGE:
            return self._build_stage_slide_prompt(slide_title, learner_profile, training_plan)
        elif slide_type_enum == SlideType.MODULE:
            return self._build_module_slide_prompt(slide_title, learner_profile, training_plan)
        elif slide_type_enum == SlideType.QUIZ:
            return await self._build_quiz_slide_prompt_async(slide_title, learner_profile, training_plan, current_slide_id)
        else:  # SlideType.CONTENT
            return self._build_slide_prompt(slide_title, learner_profile, training_plan, slide_position)
    
    async def _build_quiz_slide_prompt_async(
        self, 
        slide_title: str, 
        learner_profile: Any, 
        training_plan: Any, 
        current_slide_id: Optional[str] = None
    ) -> str:
        """Construire le prompt pour une slide de type quiz avec récupération du contenu précédent"""
        
        profile_info = {
            "niveau": learner_profile.experience_level or "débutant",
            "secteur": learner_profile.activity_sector or "non spécifié"
        }
        
        # Récupérer le contenu des slides précédentes pour le quiz
        previous_content = ""
        if current_slide_id:
            try:
                # Établir une session DB pour récupérer le contenu précédent
                async with AsyncSessionLocal() as session:
                    slide_repo = TrainingSlideRepository()
                    slide_repo.set_session(session)
                    
                    # Détecter la portée du quiz selon le titre
                    quiz_scope = self._detect_quiz_scope(slide_title)
                    
                    # Récupérer les slides de contenu précédentes
                    from uuid import UUID
                    current_slide_uuid = UUID(current_slide_id)
                    previous_slides = await slide_repo.get_previous_content_slides(
                        current_slide_id=current_slide_uuid,
                        training_plan_id=training_plan.id,
                        scope=quiz_scope
                    )
                    
                    # Compiler le contenu précédent
                    if previous_slides:
                        content_parts = []
                        for slide in previous_slides:
                            if slide.content:
                                content_parts.append(f"SLIDE: {slide.title}\n{slide.content}\n")
                        
                        if content_parts:
                            previous_content = f"""
CONTENU PRÉCÉDENT À UTILISER POUR LE QUIZ (Portée: {quiz_scope}):
{chr(10).join(content_parts)}

IMPORTANT: Base les questions du quiz sur ce contenu précédent !
"""
                        
                    logger.info(f"🎯 QUIZ PROMPT [CONTENT] Retrieved {len(previous_slides)} previous slides for scope '{quiz_scope}'")
                    
            except Exception as e:
                logger.warning(f"⚠️ QUIZ PROMPT [CONTENT] Failed to retrieve previous content: {e}")
                previous_content = "(Contenu précédent non disponible - génère un quiz générique)"
        
        prompt = f"""Tu es un expert pédagogue créant une slide de quiz/évaluation interactive.

CONTEXTE :
- Type de slide : QUIZ (évaluation des acquis)
- Titre : "{slide_title}"
- Portée détectée : {self._detect_quiz_scope(slide_title) if current_slide_id else "général"}

PROFIL APPRENANT :
- Niveau : {profile_info['niveau']}
- Secteur : {profile_info['secteur']}

{previous_content}

CONSIGNES POUR SLIDE DE QUIZ :
1. Crée une évaluation interactive basée sur le contenu précédent
2. Structure markdown avec :
   - # Titre du quiz avec émoji 📝
   - ## 🎯 Objectifs de ce quiz
   - ## 📋 Instructions
   - ### Question 1: [QCM] 
   - ### Question 2: [Question ouverte]
   - ### Question 3: [Cas pratique]
   - ### Question 4: [Vrai/Faux]
   - ### Question 5: [Application métier]
   - ## 💬 Comment répondre avec le chat IA
   - ## ✅ Ce que vous allez apprendre
3. 5 questions variées adaptées au niveau {profile_info['niveau']}
4. Questions basées spécifiquement sur le contenu précédent fourni
5. Adapté au secteur {profile_info['secteur']} avec exemples concrets
6. Instructions claires pour utiliser le chat IA pour obtenir des corrections
7. Longueur : 400-600 mots

CONTRAINTES :
- Réponds UNIQUEMENT avec le contenu markdown pur (pas de JSON)
- Base TOUTES les questions sur le contenu précédent fourni
- Inclus des questions de différents niveaux (rappel, compréhension, application)
- Termine par des encouragements et conseils pour réussir
- Style engageant et motivant

Génère maintenant le contenu de la slide de quiz :"""
        
        return prompt
    
    def _detect_quiz_scope(self, slide_title: str) -> str:
        """Détecter la portée d'un quiz selon son titre"""
        title_lower = slide_title.lower()
        
        if "étape" in title_lower or "stage" in title_lower:
            return "stage"
        elif "module" in title_lower:
            return "module"
        else:
            return "submodule"  # Par défaut, portée sous-module
    
    def _extract_content_from_json(self, json_response: str) -> str:
        """Extraire le contenu markdown du JSON retourné par VertexAI"""
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] === DÉBUT EXTRACTION ===")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] JSON brut TYPE: {type(json_response)}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] JSON brut LONGUEUR: {len(json_response) if json_response else 'NULL'}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] JSON brut PREVIEW (500 chars): {json_response[:500] if json_response else 'NULL'}")
        
        # LOGS SPÉCIFIQUES POUR DEBUGGING SLIDES ÉTAPE
        if json_response and '"slide_content"' in json_response:
            logger.info(f"🎭🎭🎭 STAGE SLIDE [JSON-EXTRACTION] === SLIDE_CONTENT DÉTECTÉ DANS JSON ===")
            logger.info(f"🎭🎭🎭 STAGE SLIDE [JSON-EXTRACTION] Le JSON contient 'slide_content' - traitement spécial")
        
        try:
            # Parser le JSON
            logger.info(f"🔄🔄🔄 SLIDE GENERATION [JSON-EXTRACTION] PARSING JSON avec json.loads()...")
            response_data = json.loads(json_response)
            logger.info(f"✅✅✅ SLIDE GENERATION [JSON-EXTRACTION] JSON PARSÉ AVEC SUCCÈS!")
            logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Parsed data TYPE: {type(response_data)}")
            logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Parsed data IS LIST?: {isinstance(response_data, list)}")
            logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Parsed data IS DICT?: {isinstance(response_data, dict)}")
            
            if isinstance(response_data, list):
                logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] ARRAY détecté - LONGUEUR: {len(response_data)}")
                logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] ARRAY COMPLET: {response_data}")
            elif isinstance(response_data, dict):
                logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] DICT détecté - KEYS: {list(response_data.keys())}")
                logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] DICT COMPLET: {response_data}")
            
            # Cas 1: Array avec slide_content (nouveau format détecté dans les logs)
            if isinstance(response_data, list) and len(response_data) > 0:
                logger.info(f"🎯🎯🎯 SLIDE GENERATION [JSON-EXTRACTION] BRANCHE 1: ARRAY avec {len(response_data)} éléments")
                first_item = response_data[0]
                logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Premier élément TYPE: {type(first_item)}")
                logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Premier élément: {first_item}")
                
                if isinstance(first_item, dict):
                    logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Premier élément KEYS: {list(first_item.keys())}")
                    
                    # Essayer différentes clés possibles
                    possible_keys = ['slide_content', 'content', 'markdown', 'text', 'slide', 'response']
                    
                    for key in possible_keys:
                        if key in first_item:
                            content = first_item[key]
                            logger.info(f"✅✅✅ SLIDE GENERATION [JSON-EXTRACTION] TROUVÉ '{key}' dans array[0]!")
                            logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Content TYPE: {type(content)}")
                            logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Content LONGUEUR: {len(content) if content else 'NULL'}")
                            logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Content PREVIEW (200 chars): {content[:200] if content else 'NULL'}")
                            logger.info(f"🎯🎯🎯 SLIDE GENERATION [JSON-EXTRACTION] RETOUR content depuis array[0].{key}")
                            
                            # Si c'est un dict avec une structure imbriquée, chercher plus profond
                            if isinstance(content, dict) and 'content' in content:
                                content = content['content']
                                logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Contenu imbriqué trouvé: {content[:200] if content else 'NULL'}")
                            
                            return content
                    
                    logger.warning(f"⚠️⚠️⚠️ SLIDE GENERATION [JSON-EXTRACTION] Aucune clé de contenu trouvée dans array[0]")
                    logger.warning(f"⚠️⚠️⚠️ SLIDE GENERATION [JSON-EXTRACTION] Clés disponibles: {list(first_item.keys())}")
                    
                    # Fallback: utiliser la première valeur qui semble être du texte
                    for key, value in first_item.items():
                        if isinstance(value, str) and len(value) > 50:  # Probablement du contenu
                            logger.info(f"🔄🔄🔄 SLIDE GENERATION [JSON-EXTRACTION] FALLBACK: utilisation de '{key}' comme contenu")
                            return value
                else:
                    logger.warning(f"⚠️⚠️⚠️ SLIDE GENERATION [JSON-EXTRACTION] Premier élément n'est pas un dict")
                    
            # Cas 2: Dict avec structure classique
            elif isinstance(response_data, dict):
                logger.info(f"🎯🎯🎯 SLIDE GENERATION [JSON-EXTRACTION] BRANCHE 2: DICT avec keys: {list(response_data.keys())}")
                
                # 2a: Structure avec slide.content
                if 'slide' in response_data and isinstance(response_data['slide'], dict) and 'content' in response_data['slide']:
                    content = response_data['slide']['content']
                    logger.info(f"✅✅✅ SLIDE GENERATION [JSON-EXTRACTION] TROUVÉ slide.content!")
                    logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Content: {content[:200] if content else 'NULL'}")
                    logger.info(f"🎯🎯🎯 SLIDE GENERATION [JSON-EXTRACTION] RETOUR content depuis slide.content")
                    return content
                    
                # 2b: Structure avec slide_content direct
                elif 'slide_content' in response_data:
                    content = response_data['slide_content']
                    logger.info(f"✅✅✅ SLIDE GENERATION [JSON-EXTRACTION] TROUVÉ root.slide_content!")
                    logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Content: {content[:200] if content else 'NULL'}")
                    logger.info(f"🎯🎯🎯 SLIDE GENERATION [JSON-EXTRACTION] RETOUR content depuis root.slide_content")
                    
                    # LOGS SPÉCIFIQUES SLIDES ÉTAPE - SUCCESS PATH
                    if content and content.startswith('#'):
                        logger.info(f"🎭🎭🎭 STAGE SLIDE [JSON-EXTRACTION] === MARKDOWN EXTRAIT AVEC SUCCÈS ===")
                        logger.info(f"🎭🎭🎭 STAGE SLIDE [JSON-EXTRACTION] Content est du markdown valide (commence par #)")
                        logger.info(f"🎭🎭🎭 STAGE SLIDE [JSON-EXTRACTION] Content markdown longueur: {len(content)}")
                    
                    return content
                    
                # 2c: Structure avec content direct
                elif 'content' in response_data:
                    content = response_data['content']
                    logger.info(f"✅✅✅ SLIDE GENERATION [JSON-EXTRACTION] TROUVÉ root.content!")
                    logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Content: {content[:200] if content else 'NULL'}")
                    logger.info(f"🎯🎯🎯 SLIDE GENERATION [JSON-EXTRACTION] RETOUR content depuis root.content")
                    return content
                else:
                    logger.warning(f"⚠️⚠️⚠️ SLIDE GENERATION [JSON-EXTRACTION] AUCUN champ content trouvé dans le dict")
                    logger.warning(f"⚠️⚠️⚠️ SLIDE GENERATION [JSON-EXTRACTION] FALLBACK: utilisation réponse brute")
                    return json_response
            else:
                logger.warning(f"⚠️⚠️⚠️ SLIDE GENERATION [JSON-EXTRACTION] Type non supporté: {type(response_data)}")
                logger.warning(f"⚠️⚠️⚠️ SLIDE GENERATION [JSON-EXTRACTION] FALLBACK: utilisation réponse brute")
                return json_response
                
        except json.JSONDecodeError as e:
            logger.error(f"❌❌❌ SLIDE GENERATION [JSON-EXTRACTION] ERREUR PARSING JSON: {e}")
            logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] JSON brut qui a échoué: {json_response[:500]}...")
            # Fallback: utiliser la réponse brute
            logger.info(f"🔄🔄🔄 SLIDE GENERATION [JSON-EXTRACTION] FALLBACK: utilisation réponse brute")
            return json_response
        except Exception as e:
            logger.error(f"❌❌❌ SLIDE GENERATION [JSON-EXTRACTION] ERREUR INATTENDUE: {e}")
            logger.error(f"❌❌❌ SLIDE GENERATION [JSON-EXTRACTION] STACK: {str(e)}")
            logger.info(f"🔄🔄🔄 SLIDE GENERATION [JSON-EXTRACTION] FALLBACK: utilisation réponse brute")
            return json_response
    
    def _clean_markdown_content(self, content: str) -> str:
        """Nettoyer et valider le contenu markdown généré"""
        logger.info(f"🧹🧹🧹 SLIDE GENERATION [MARKDOWN-CLEAN] === DÉBUT NETTOYAGE ===")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Content INPUT TYPE: {type(content)}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Content INPUT NULL?: {content is None}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Content INPUT LONGUEUR: {len(content) if content else 'NULL'}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Content INPUT PREVIEW (300 chars): {content[:300] if content else 'NULL'}")
        
        if not content:
            logger.warning(f"⚠️⚠️⚠️ SLIDE GENERATION [MARKDOWN-CLEAN] CONTENU VIDE - Retour message par défaut")
            default_content = "# Contenu en cours de génération...\n\nVeuillez patienter pendant que nous préparons votre contenu personnalisé."
            logger.info(f"🔄🔄🔄 SLIDE GENERATION [MARKDOWN-CLEAN] DEFAULT CONTENT: {default_content}")
            return default_content
        
        # NOUVELLE ÉTAPE: Détecter et traiter le JSON avant le nettoyage markdown
        logger.info(f"🔄🔄🔄 SLIDE GENERATION [MARKDOWN-CLEAN] ÉTAPE 0: Détection JSON...")
        content_stripped = content.strip()
        
        # Détecter si le contenu est un JSON avec slide_content
        if ((content_stripped.startswith('{') and '"slide_content"' in content_stripped) or 
            (content_stripped.startswith('[') and '"slide_content"' in content_stripped)):
            logger.info(f"🎭🎭🎭 STAGE SLIDE [MARKDOWN-CLEAN] === JSON DÉTECTÉ AVEC SLIDE_CONTENT ===")
            logger.info(f"🎭🎭🎭 STAGE SLIDE [MARKDOWN-CLEAN] Tentative d'extraction du contenu markdown...")
            
            try:
                # Essayer d'extraire le contenu markdown du JSON
                extracted_content = self._extract_content_from_json(content_stripped)
                logger.info(f"🎭🎭🎭 STAGE SLIDE [MARKDOWN-CLEAN] Contenu extrait: {extracted_content[:200] if extracted_content else 'NULL'}")
                
                # Si l'extraction a réussi et renvoie du markdown valide, l'utiliser
                if extracted_content and extracted_content != content_stripped and extracted_content.startswith('#'):
                    logger.info(f"✅✅✅ SLIDE GENERATION [MARKDOWN-CLEAN] JSON EXTRAIT AVEC SUCCÈS - MARKDOWN DÉTECTÉ")
                    logger.info(f"🎯🎯🎯 SLIDE GENERATION [MARKDOWN-CLEAN] UTILISATION DU CONTENU EXTRAIT")
                    content = extracted_content
                    logger.info(f"🎭🎭🎭 STAGE SLIDE [MARKDOWN-CLEAN] Contenu remplacé par markdown extrait: {content[:200]}")
                else:
                    logger.warning(f"⚠️⚠️⚠️ SLIDE GENERATION [MARKDOWN-CLEAN] EXTRACTION JSON ÉCHOUÉE - CONTENU INCHANGÉ")
            except Exception as e:
                logger.error(f"❌❌❌ SLIDE GENERATION [MARKDOWN-CLEAN] ERREUR EXTRACTION JSON: {e}")
                logger.info(f"🔄🔄🔄 SLIDE GENERATION [MARKDOWN-CLEAN] FALLBACK - CONTENU INCHANGÉ")
        
        # Nettoyer les balises potentielles
        logger.info(f"🔄🔄🔄 SLIDE GENERATION [MARKDOWN-CLEAN] ÉTAPE 1: strip()...")
        cleaned = content.strip()
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Après strip - LONGUEUR: {len(cleaned)}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Après strip - PREVIEW: {cleaned[:200]}")
        
        # Supprimer les balises markdown code si présentes
        logger.info(f"🔄🔄🔄 SLIDE GENERATION [MARKDOWN-CLEAN] ÉTAPE 2: Vérification balises markdown...")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Commence par ```markdown?: {cleaned.startswith('```markdown')}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Commence par ```?: {cleaned.startswith('```')}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Finit par ```?: {cleaned.endswith('```')}")
        
        if cleaned.startswith('```markdown'):
            logger.info(f"🔄🔄🔄 SLIDE GENERATION [MARKDOWN-CLEAN] SUPPRESSION ```markdown au début")
            cleaned = cleaned[11:]
        elif cleaned.startswith('```'):
            logger.info(f"🔄🔄🔄 SLIDE GENERATION [MARKDOWN-CLEAN] SUPPRESSION ``` au début")
            cleaned = cleaned[3:]
        
        if cleaned.endswith('```'):
            logger.info(f"🔄🔄🔄 SLIDE GENERATION [MARKDOWN-CLEAN] SUPPRESSION ``` à la fin")
            cleaned = cleaned[:-3]
        
        logger.info(f"🔄🔄🔄 SLIDE GENERATION [MARKDOWN-CLEAN] ÉTAPE 3: strip() final...")
        cleaned = cleaned.strip()
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Après suppression balises - LONGUEUR: {len(cleaned)}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Après suppression balises - PREVIEW: {cleaned[:300]}")
        
        # Validation basique : doit contenir au moins un titre markdown
        logger.info(f"🔄🔄🔄 SLIDE GENERATION [MARKDOWN-CLEAN] ÉTAPE 4: Validation titre markdown...")
        lines = cleaned.split('\n')
        has_title = any(line.startswith('#') for line in lines)
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Contient titre markdown?: {has_title}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Nombre de lignes: {len(lines)}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Premières lignes: {lines[:5]}")
        
        # MODIFICATION CRITIQUE: Ne pas ajouter de titre par défaut si le contenu semble être du JSON
        is_json_like = (cleaned.startswith('{') or cleaned.startswith('[')) and ('"' in cleaned)
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Semble être du JSON?: {is_json_like}")
        
        if not has_title and not is_json_like:
            logger.info(f"🔄🔄🔄 SLIDE GENERATION [MARKDOWN-CLEAN] AJOUT titre par défaut (contenu non-JSON)")
            # Ajouter un titre si manquant (seulement si ce n'est pas du JSON)
            cleaned = f"# Contenu de Formation\n\n{cleaned}"
            logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Après ajout titre - LONGUEUR: {len(cleaned)}")
        elif not has_title and is_json_like:
            logger.warning(f"⚠️⚠️⚠️ SLIDE GENERATION [MARKDOWN-CLEAN] CONTENU JSON DÉTECTÉ - PAS D'AJOUT DE TITRE")
            logger.warning(f"⚠️⚠️⚠️ SLIDE GENERATION [MARKDOWN-CLEAN] Le contenu nécessite une extraction JSON appropriée")
        
        logger.info(f"✅✅✅ SLIDE GENERATION [MARKDOWN-CLEAN] NETTOYAGE TERMINÉ!")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] RÉSULTAT FINAL - TYPE: {type(cleaned)}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] RÉSULTAT FINAL - LONGUEUR: {len(cleaned)}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] RÉSULTAT FINAL - PREVIEW (400 chars): {cleaned[:400]}")
        logger.info(f"🧹🧹🧹 SLIDE GENERATION [MARKDOWN-CLEAN] === FIN NETTOYAGE ===")
        
        return cleaned
    
    def _fix_corrupted_content(self, corrupted_content: str) -> str:
        """Corriger le contenu corrompu qui contient du JSON au lieu de markdown pur"""
        logger.info(f"🔧🔧🔧 SLIDE GENERATION [FIX] === DÉBUT CORRECTION CONTENU CORROMPU ===")
        logger.info(f"🔧🔧🔧 SLIDE GENERATION [FIX] Contenu corrompu LONGUEUR: {len(corrupted_content)}")
        logger.info(f"🔧🔧🔧 SLIDE GENERATION [FIX] Contenu corrompu PREVIEW: {corrupted_content[:300]}")
        
        try:
            # Cas 1: Contenu commence par "# Contenu de Formation\n\n[" 
            if corrupted_content.startswith('# Contenu de Formation\n\n['):
                logger.info(f"🔧🔧🔧 SLIDE GENERATION [FIX] DÉTECTION: Format avec titre par défaut + JSON")
                
                # Extraire la partie JSON (tout après "# Contenu de Formation\n\n")
                json_part = corrupted_content[len('# Contenu de Formation\n\n'):]
                logger.info(f"🔧🔧🔧 SLIDE GENERATION [FIX] JSON part: {json_part[:200]}...")
                
                # Parser le JSON
                parsed_json = json.loads(json_part)
                logger.info(f"🔧🔧🔧 SLIDE GENERATION [FIX] JSON parsé: {type(parsed_json)}")
                
                if isinstance(parsed_json, list) and len(parsed_json) > 0:
                    first_item = parsed_json[0]
                    if isinstance(first_item, dict) and 'slide_content' in first_item:
                        markdown_content = first_item['slide_content']
                        logger.info(f"✅✅✅ SLIDE GENERATION [FIX] MARKDOWN EXTRAIT: {markdown_content[:200]}...")
                        return self._clean_markdown_content(markdown_content)
            
            # Cas 2: Contenu contient directement "slide_content" dans le JSON
            elif '"slide_content"' in corrupted_content:
                logger.info(f"🔧🔧🔧 SLIDE GENERATION [FIX] DÉTECTION: Format JSON direct avec slide_content")
                
                # Essayer de parser tout le contenu comme JSON
                parsed_json = json.loads(corrupted_content)
                logger.info(f"🔧🔧🔧 SLIDE GENERATION [FIX] JSON parsé: {type(parsed_json)}")
                
                if isinstance(parsed_json, list) and len(parsed_json) > 0:
                    first_item = parsed_json[0]
                    if isinstance(first_item, dict) and 'slide_content' in first_item:
                        markdown_content = first_item['slide_content']
                        logger.info(f"✅✅✅ SLIDE GENERATION [FIX] MARKDOWN EXTRAIT: {markdown_content[:200]}...")
                        return self._clean_markdown_content(markdown_content)
                elif isinstance(parsed_json, dict) and 'slide_content' in parsed_json:
                    markdown_content = parsed_json['slide_content']
                    logger.info(f"✅✅✅ SLIDE GENERATION [FIX] MARKDOWN EXTRAIT: {markdown_content[:200]}...")
                    return self._clean_markdown_content(markdown_content)
            
            logger.warning(f"⚠️⚠️⚠️ SLIDE GENERATION [FIX] FORMAT NON RECONNU - Retour contenu original")
            return corrupted_content
            
        except json.JSONDecodeError as e:
            logger.error(f"❌❌❌ SLIDE GENERATION [FIX] ERREUR JSON: {e}")
            return corrupted_content
        except Exception as e:
            logger.error(f"❌❌❌ SLIDE GENERATION [FIX] ERREUR INATTENDUE: {e}")
            return corrupted_content
    
    async def get_next_slide_content(self, current_slide_id: str, learner_session_id: str) -> Dict[str, Any]:
        """
        Obtenir le contenu de la slide suivante (génération ou récupération)
        
        Args:
            current_slide_id: ID de la slide actuelle
            learner_session_id: ID de la session apprenant
            
        Returns:
            Dict contenant les informations de la slide suivante
        """
        start_time = time.time()
        
        async with AsyncSessionLocal() as session:
            try:
                logger.info(f"🎯 SLIDE NAVIGATION [NEXT] Getting next slide after {current_slide_id}")
                
                # Initialize repositories
                learner_session_repo = LearnerSessionRepository(session)
                learner_plan_repo = LearnerTrainingPlanRepository(session)
                slide_repo = TrainingSlideRepository()
                slide_repo.set_session(session)
                
                # Récupérer la session apprenant
                learner_session = await learner_session_repo.get_by_id(learner_session_id)
                if not learner_session:
                    raise ValueError(f"Learner session not found: {learner_session_id}")
                
                # Récupérer le plan de formation
                training_plan = await learner_plan_repo.get_latest_by_learner_session_id(learner_session_id)
                if not training_plan:
                    raise ValueError(f"Training plan not found for session: {learner_session_id}")
                
                # Obtenir la slide suivante (convertir string en UUID)
                from uuid import UUID
                current_slide_uuid = UUID(current_slide_id)
                next_slide = await slide_repo.get_next_slide(current_slide_uuid, training_plan.id)
                if not next_slide:
                    return {
                        "has_next": False,
                        "message": "You have reached the end of the training"
                    }
                
                # Si la slide n'a pas de contenu, le générer
                if not next_slide.content:
                    logger.info(f"📝 SLIDE NAVIGATION [NEXT] Generating content for slide: {next_slide.title}")
                    
                    slide_content = await self._generate_slide_content(
                        slide_title=next_slide.title,
                        slide_type=next_slide.slide_type,
                        learner_profile=learner_session,
                        training_plan=training_plan,
                        slide_position="middle",  # Toutes les slides suivantes sont "middle"
                        current_slide_id=str(next_slide.id)
                    )
                    
                    # Sauvegarder le contenu généré
                    await slide_repo.update_content(next_slide.id, slide_content)
                    next_slide.content = slide_content
                    next_slide.generated_at = datetime.now(timezone.utc)
                
                # Obtenir les informations de position
                position_info = await slide_repo.get_slide_position(next_slide.id, training_plan.id)
                
                # Récupérer les informations de breadcrumb
                logger.info(f"🧭🧭🧭 SLIDE NAVIGATION [NEXT] === RÉCUPÉRATION BREADCRUMB ===")
                breadcrumb_info = await slide_repo.get_slide_breadcrumb(next_slide.id)
                logger.info(f"🧭🧭🧭 SLIDE NAVIGATION [NEXT] Breadcrumb info: {breadcrumb_info}")
                
                # Mettre à jour le numéro de slide courante de l'apprenant
                logger.info(f"📊📊📊 SLIDE NAVIGATION [NEXT] === MISE À JOUR PROGRESSION ===")
                slide_global_number = await slide_repo.get_slide_global_number(next_slide.id, training_plan.id)
                logger.info(f"📊📊📊 SLIDE NAVIGATION [NEXT] Slide global number: {slide_global_number}")
                
                # Mettre à jour current_slide_number dans learner_session
                from uuid import UUID
                update_success = await learner_session_repo.update_current_slide_number(
                    learner_session_id=UUID(learner_session_id),
                    slide_number=slide_global_number
                )
                logger.info(f"📊📊📊 SLIDE NAVIGATION [NEXT] Update success: {update_success}")
                
                duration = time.time() - start_time
                
                result = {
                    "slide_id": str(next_slide.id),
                    "title": next_slide.title,
                    "content": next_slide.content,
                    "order_in_submodule": next_slide.order_in_submodule,
                    "generated_at": next_slide.generated_at.isoformat() if next_slide.generated_at else None,
                    "navigation_duration": round(duration, 2),
                    "position": position_info,
                    "has_next": position_info["has_next"],
                    "has_previous": position_info["has_previous"],
                    "breadcrumb": breadcrumb_info,
                    "slide_number": slide_global_number
                }
                
                logger.info(f"✅ SLIDE NAVIGATION [NEXT] Next slide retrieved/generated in {duration:.2f}s")
                return result
                
            except Exception as e:
                await session.rollback()
                duration = time.time() - start_time
                logger.error(f"❌ SLIDE NAVIGATION [NEXT] Failed after {duration:.2f}s: {str(e)}")
                raise
    
    async def get_previous_slide_content(self, current_slide_id: str, learner_session_id: str) -> Dict[str, Any]:
        """
        Obtenir le contenu de la slide précédente (toujours en récupération)
        
        Args:
            current_slide_id: ID de la slide actuelle
            learner_session_id: ID de la session apprenant
            
        Returns:
            Dict contenant les informations de la slide précédente
        """
        start_time = time.time()
        
        async with AsyncSessionLocal() as session:
            try:
                logger.info(f"🎯 SLIDE NAVIGATION [PREV] Getting previous slide before {current_slide_id}")
                
                # Initialize repositories
                learner_session_repo = LearnerSessionRepository(session)
                learner_plan_repo = LearnerTrainingPlanRepository(session)
                slide_repo = TrainingSlideRepository()
                slide_repo.set_session(session)
                
                # Récupérer la session apprenant
                learner_session = await learner_session_repo.get_by_id(learner_session_id)
                if not learner_session:
                    raise ValueError(f"Learner session not found: {learner_session_id}")
                
                # Récupérer le plan de formation
                training_plan = await learner_plan_repo.get_latest_by_learner_session_id(learner_session_id)
                if not training_plan:
                    raise ValueError(f"Training plan not found for session: {learner_session_id}")
                
                # Obtenir la slide précédente (convertir string en UUID)
                from uuid import UUID
                current_slide_uuid = UUID(current_slide_id)
                previous_slide = await slide_repo.get_previous_slide(current_slide_uuid, training_plan.id)
                if not previous_slide:
                    return {
                        "has_previous": False,
                        "message": "You are at the beginning of the training"
                    }
                
                # Si la slide précédente n'a pas de contenu, le générer (cas où elle n'a jamais été consultée)
                if not previous_slide.content:
                    logger.info(f"📝 SLIDE NAVIGATION [PREV] Generating content for previous slide: {previous_slide.title}")
                    
                    slide_content = await self._generate_slide_content(
                        slide_title=previous_slide.title,
                        slide_type=previous_slide.slide_type,
                        learner_profile=learner_session,
                        training_plan=training_plan,
                        slide_position="middle",  # Les slides précédentes sont généralement "middle"
                        current_slide_id=str(previous_slide.id)
                    )
                    
                    # Sauvegarder le contenu généré
                    await slide_repo.update_content(previous_slide.id, slide_content)
                    previous_slide.content = slide_content
                    previous_slide.generated_at = datetime.now(timezone.utc)
                
                # Obtenir les informations de position basées sur la slide actuelle, pas la précédente
                current_slide_uuid = UUID(current_slide_id)
                position_info = await slide_repo.get_slide_position(current_slide_uuid, training_plan.id)
                
                # Récupérer les informations de breadcrumb pour la slide précédente
                logger.info(f"🧭🧭🧭 SLIDE NAVIGATION [PREV] === RÉCUPÉRATION BREADCRUMB ===")
                breadcrumb_info = await slide_repo.get_slide_breadcrumb(previous_slide.id)
                logger.info(f"🧭🧭🧭 SLIDE NAVIGATION [PREV] Breadcrumb info: {breadcrumb_info}")
                
                # Mettre à jour le numéro de slide courante de l'apprenant
                logger.info(f"📊📊📊 SLIDE NAVIGATION [PREV] === MISE À JOUR PROGRESSION ===")
                slide_global_number = await slide_repo.get_slide_global_number(previous_slide.id, training_plan.id)
                logger.info(f"📊📊📊 SLIDE NAVIGATION [PREV] Slide global number: {slide_global_number}")
                
                # Mettre à jour current_slide_number dans learner_session
                from uuid import UUID
                update_success = await learner_session_repo.update_current_slide_number(
                    learner_session_id=UUID(learner_session_id),
                    slide_number=slide_global_number
                )
                logger.info(f"📊📊📊 SLIDE NAVIGATION [PREV] Update success: {update_success}")
                
                duration = time.time() - start_time
                
                result = {
                    "slide_id": str(previous_slide.id),
                    "title": previous_slide.title,
                    "content": previous_slide.content,
                    "order_in_submodule": previous_slide.order_in_submodule,
                    "generated_at": previous_slide.generated_at.isoformat() if previous_slide.generated_at else None,
                    "navigation_duration": round(duration, 2),
                    "position": position_info,
                    "has_next": position_info["has_next"],
                    "has_previous": position_info["has_previous"],
                    "breadcrumb": breadcrumb_info,
                    "slide_number": slide_global_number
                }
                
                logger.info(f"✅ SLIDE NAVIGATION [PREV] Previous slide retrieved in {duration:.2f}s")
                return result
                
            except Exception as e:
                await session.rollback()
                duration = time.time() - start_time
                logger.error(f"❌ SLIDE NAVIGATION [PREV] Failed after {duration:.2f}s: {str(e)}")
                raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques du service"""
        return {
            "service": "SlideGenerationService",
            "vertex_ai_available": self.vertex_adapter.is_available(),
            "vertex_ai_stats": self.vertex_adapter.get_stats()
        }