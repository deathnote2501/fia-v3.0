"""
FIA v3.0 - Slide Generation Service (Orchestrateur)
Service principal pour la navigation et coordination des slides
"""

import logging
import time
from typing import Dict, Any
from datetime import datetime, timezone
from uuid import UUID

from app.infrastructure.database import AsyncSessionLocal
from app.adapters.repositories.learner_training_plan_repository import LearnerTrainingPlanRepository
from app.adapters.repositories.learner_session_repository import LearnerSessionRepository
from app.adapters.repositories.training_slide_repository import TrainingSlideRepository

logger = logging.getLogger(__name__)


class SlideGenerationServiceOrchestrator:
    """Service orchestrateur pour la navigation et coordination des slides"""
    
    def __init__(self):
        """Initialize slide generation orchestrator"""
        logger.info("🎯 SLIDE ORCHESTRATOR [SERVICE] Initialized")
    
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
                logger.info(f"🎯 SLIDE ORCHESTRATOR [START] Generating first slide for session {learner_session_id}")
                
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
                    logger.info(f"📝 SLIDE ORCHESTRATOR [GENERATION] Generating content for slide: {first_slide.title}")
                    
                    # TODO: Appeler le service de génération de contenu approprié
                    # selon le type de slide (plan/étape/module/content/quiz)
                    slide_content = await self._coordinate_slide_generation(
                        slide=first_slide,
                        learner_session=learner_session,
                        training_plan=training_plan,
                        slide_position="first"
                    )
                    
                    # 5. Sauvegarder le contenu généré
                    await self._save_slide_content(slide_repo, first_slide.id, slide_content)
                    first_slide.content = slide_content
                    first_slide.generated_at = datetime.now(timezone.utc)
                
                else:
                    logger.info(f"♻️ SLIDE ORCHESTRATOR [CACHE] Using existing content for slide: {first_slide.title}")
                    
                    # Vérifier et corriger le contenu si nécessaire
                    corrected_content = self._fix_corrupted_content(first_slide.content)
                    if corrected_content != first_slide.content:
                        logger.info(f"🔧 SLIDE ORCHESTRATOR [FIX] Correcting content for slide: {first_slide.id}")
                        await self._save_slide_content(slide_repo, first_slide.id, corrected_content)
                        first_slide.content = corrected_content
                
                # 6. Mettre à jour la progression de l'apprenant
                await self._update_learner_progress(
                    learner_session_repo, slide_repo, 
                    learner_session_id, first_slide.id, training_plan.id
                )
                
                # 7. Construire la réponse
                result = await self._build_slide_response(
                    slide_repo, first_slide, time.time() - start_time
                )
                
                logger.info(f"✅ SLIDE ORCHESTRATOR [SUCCESS] First slide generated in {time.time() - start_time:.2f}s")
                return result
            
            except Exception as e:
                await session.rollback()
                duration = time.time() - start_time
                logger.error(f"❌ SLIDE ORCHESTRATOR [ERROR] Failed after {duration:.2f}s: {str(e)}")
                raise
    
    async def get_current_slide_content(self, learner_session_id: str) -> Dict[str, Any]:
        """
        Récupérer le contenu de la slide courante de l'apprenant
        
        Args:
            learner_session_id: ID de la session apprenant
            
        Returns:
            Dict contenant les informations de la slide courante
        """
        start_time = time.time()
        
        async with AsyncSessionLocal() as session:
            try:
                logger.info(f"🎯 SLIDE ORCHESTRATOR [CURRENT] Getting current slide for session {learner_session_id}")
                
                # Initialize repositories with session
                learner_session_repo = LearnerSessionRepository(session)
                learner_plan_repo = LearnerTrainingPlanRepository(session)
                slide_repo = TrainingSlideRepository()
                slide_repo.set_session(session)
                
                # 1. Récupérer la session apprenant
                learner_session = await learner_session_repo.get_by_id(learner_session_id)
                if not learner_session:
                    raise ValueError(f"Learner session not found: {learner_session_id}")
                
                # 2. Récupérer le plan de formation personnalisé
                training_plan = await learner_plan_repo.get_latest_by_learner_session_id(learner_session_id)
                if not training_plan:
                    raise ValueError(f"Training plan not found for session: {learner_session_id}")
                
                # 3. Récupérer la slide courante
                current_slide = await slide_repo.get_slide_by_number(
                    training_plan.id, learner_session.current_slide_number or 1
                )
                if not current_slide:
                    raise ValueError(f"Current slide not found for session: {learner_session_id}")
                
                # 4. Générer le contenu si nécessaire
                if not current_slide.content:
                    logger.info(f"📝 SLIDE ORCHESTRATOR [GENERATION] Generating content for current slide: {current_slide.title}")
                    
                    slide_content = await self._coordinate_slide_generation(
                        slide=current_slide,
                        learner_session=learner_session,
                        training_plan=training_plan,
                        slide_position="current"
                    )
                    
                    await self._save_slide_content(slide_repo, current_slide.id, slide_content)
                    current_slide.content = slide_content
                    current_slide.generated_at = datetime.now(timezone.utc)
                
                # 5. Construire la réponse
                result = await self._build_slide_response(
                    slide_repo, current_slide, time.time() - start_time
                )
                
                logger.info(f"✅ SLIDE ORCHESTRATOR [SUCCESS] Current slide retrieved in {time.time() - start_time:.2f}s")
                return result
            
            except Exception as e:
                await session.rollback()
                duration = time.time() - start_time
                logger.error(f"❌ SLIDE ORCHESTRATOR [ERROR] Failed after {duration:.2f}s: {str(e)}")
                raise
    
    async def get_next_slide_content(self, current_slide_id: str, learner_session_id: str) -> Dict[str, Any]:
        """
        Obtenir le contenu de la slide suivante
        
        Args:
            current_slide_id: ID de la slide actuelle
            learner_session_id: ID de la session apprenant
            
        Returns:
            Dict contenant les informations de la slide suivante
        """
        start_time = time.time()
        
        async with AsyncSessionLocal() as session:
            try:
                logger.info(f"🎯 SLIDE ORCHESTRATOR [NEXT] Getting next slide after {current_slide_id}")
                
                # Initialize repositories
                learner_session_repo = LearnerSessionRepository(session)
                learner_plan_repo = LearnerTrainingPlanRepository(session)
                slide_repo = TrainingSlideRepository()
                slide_repo.set_session(session)
                
                # 1. Récupérer les données de base
                learner_session, training_plan = await self._get_session_and_plan(
                    learner_session_repo, learner_plan_repo, learner_session_id
                )
                
                # 2. Obtenir la slide suivante
                current_slide_uuid = UUID(current_slide_id)
                next_slide = await slide_repo.get_next_slide(current_slide_uuid, training_plan.id)
                
                if not next_slide:
                    return {
                        "has_next": False,
                        "message": "You have reached the end of the training"
                    }
                
                # 3. Générer le contenu si nécessaire
                if not next_slide.content:
                    logger.info(f"📝 SLIDE ORCHESTRATOR [GENERATION] Generating content for next slide: {next_slide.title}")
                    
                    slide_content = await self._coordinate_slide_generation(
                        slide=next_slide,
                        learner_session=learner_session,
                        training_plan=training_plan,
                        slide_position="next"
                    )
                    
                    await self._save_slide_content(slide_repo, next_slide.id, slide_content)
                    next_slide.content = slide_content
                    next_slide.generated_at = datetime.now(timezone.utc)
                
                # 4. Mettre à jour la progression
                await self._update_learner_progress(
                    learner_session_repo, slide_repo,
                    learner_session_id, next_slide.id, training_plan.id
                )
                
                # 5. Construire la réponse
                result = await self._build_slide_response(
                    slide_repo, next_slide, time.time() - start_time
                )
                result["has_next"] = True
                
                logger.info(f"✅ SLIDE ORCHESTRATOR [SUCCESS] Next slide retrieved in {time.time() - start_time:.2f}s")
                return result
            
            except Exception as e:
                await session.rollback()
                duration = time.time() - start_time
                logger.error(f"❌ SLIDE ORCHESTRATOR [ERROR] Failed after {duration:.2f}s: {str(e)}")
                raise
    
    async def get_previous_slide_content(self, current_slide_id: str, learner_session_id: str) -> Dict[str, Any]:
        """
        Obtenir le contenu de la slide précédente
        
        Args:
            current_slide_id: ID de la slide actuelle
            learner_session_id: ID de la session apprenant
            
        Returns:
            Dict contenant les informations de la slide précédente
        """
        start_time = time.time()
        
        async with AsyncSessionLocal() as session:
            try:
                logger.info(f"🎯 SLIDE ORCHESTRATOR [PREV] Getting previous slide before {current_slide_id}")
                
                # Initialize repositories
                learner_session_repo = LearnerSessionRepository(session)
                learner_plan_repo = LearnerTrainingPlanRepository(session)
                slide_repo = TrainingSlideRepository()
                slide_repo.set_session(session)
                
                # 1. Récupérer les données de base
                learner_session, training_plan = await self._get_session_and_plan(
                    learner_session_repo, learner_plan_repo, learner_session_id
                )
                
                # 2. Obtenir la slide précédente
                current_slide_uuid = UUID(current_slide_id)
                previous_slide = await slide_repo.get_previous_slide(current_slide_uuid, training_plan.id)
                
                if not previous_slide:
                    return {
                        "has_previous": False,
                        "message": "You are at the beginning of the training"
                    }
                
                # 3. Générer le contenu si nécessaire (cas rare)
                if not previous_slide.content:
                    logger.info(f"📝 SLIDE ORCHESTRATOR [GENERATION] Generating content for previous slide: {previous_slide.title}")
                    
                    slide_content = await self._coordinate_slide_generation(
                        slide=previous_slide,
                        learner_session=learner_session,
                        training_plan=training_plan,
                        slide_position="previous"
                    )
                    
                    await self._save_slide_content(slide_repo, previous_slide.id, slide_content)
                    previous_slide.content = slide_content
                    previous_slide.generated_at = datetime.now(timezone.utc)
                
                # 4. Mettre à jour la progression
                await self._update_learner_progress(
                    learner_session_repo, slide_repo,
                    learner_session_id, previous_slide.id, training_plan.id
                )
                
                # 5. Construire la réponse
                result = await self._build_slide_response(
                    slide_repo, previous_slide, time.time() - start_time
                )
                result["has_previous"] = True
                
                logger.info(f"✅ SLIDE ORCHESTRATOR [SUCCESS] Previous slide retrieved in {time.time() - start_time:.2f}s")
                return result
            
            except Exception as e:
                await session.rollback()
                duration = time.time() - start_time
                logger.error(f"❌ SLIDE ORCHESTRATOR [ERROR] Failed after {duration:.2f}s: {str(e)}")
                raise
    
    # ===== Méthodes privées utilitaires =====
    
    async def _coordinate_slide_generation(
        self, 
        slide: Any, 
        learner_session: Any, 
        training_plan: Any, 
        slide_position: str
    ) -> str:
        """
        Coordonner la génération de contenu selon le type de slide
        
        Args:
            slide: Slide entity
            learner_session: Learner session entity
            training_plan: Training plan entity
            slide_position: Position in training
            
        Returns:
            Generated slide content
        """
        # TODO: Implémenter la coordination selon le type de slide
        # - PLAN: Utiliser le formatage de plan JSON
        # - STAGE: Utiliser le formatage d'étape JSON
        # - MODULE: Utiliser le formatage de module + intro IA
        # - CONTENT: Utiliser le générateur de contenu IA
        # - QUIZ: Utiliser le générateur de quiz IA
        
        logger.info(f"🔄 SLIDE ORCHESTRATOR [COORDINATE] Slide type: {slide.slide_type}, Title: {slide.title}")
        
        # Temporaire : retourner un contenu par défaut
        return f"# {slide.title}\n\nContenu en cours de génération..."
    
    async def _get_session_and_plan(
        self, 
        learner_session_repo: LearnerSessionRepository,
        learner_plan_repo: LearnerTrainingPlanRepository,
        learner_session_id: str
    ) -> tuple[Any, Any]:
        """Récupérer la session apprenant et le plan de formation"""
        learner_session = await learner_session_repo.get_by_id(learner_session_id)
        if not learner_session:
            raise ValueError(f"Learner session not found: {learner_session_id}")
        
        training_plan = await learner_plan_repo.get_latest_by_learner_session_id(learner_session_id)
        if not training_plan:
            raise ValueError(f"Training plan not found for session: {learner_session_id}")
        
        return learner_session, training_plan
    
    async def _save_slide_content(
        self, 
        slide_repo: TrainingSlideRepository, 
        slide_id: Any, 
        content: str
    ) -> None:
        """Sauvegarder le contenu de la slide"""
        logger.info(f"💾 SLIDE ORCHESTRATOR [SAVE] Saving content for slide: {slide_id}")
        await slide_repo.update_content(slide_id, content)
    
    async def _update_learner_progress(
        self,
        learner_session_repo: LearnerSessionRepository,
        slide_repo: TrainingSlideRepository,
        learner_session_id: str,
        slide_id: Any,
        training_plan_id: Any
    ) -> None:
        """Mettre à jour la progression de l'apprenant"""
        slide_global_number = await slide_repo.get_slide_global_number(slide_id, training_plan_id)
        
        update_success = await learner_session_repo.update_current_slide_number(
            learner_session_id=UUID(learner_session_id),
            slide_number=slide_global_number
        )
        
        logger.info(f"📊 SLIDE ORCHESTRATOR [PROGRESS] Updated slide number to {slide_global_number}: {update_success}")
    
    async def _build_slide_response(
        self,
        slide_repo: TrainingSlideRepository,
        slide: Any,
        duration: float
    ) -> Dict[str, Any]:
        """Construire la réponse standardisée pour une slide"""
        # Récupérer les informations de breadcrumb
        breadcrumb_info = await slide_repo.get_slide_breadcrumb(slide.id)
        
        return {
            "slide_id": str(slide.id),
            "title": slide.title,
            "content": slide.content,
            "order_in_submodule": slide.order_in_submodule,
            "generated_at": slide.generated_at.isoformat() if slide.generated_at else None,
            "generation_duration": round(duration, 2),
            "breadcrumb": breadcrumb_info,
            "slide_number": await slide_repo.get_slide_global_number(slide.id, slide.submodule.module.plan_id)
        }
    
    def _fix_corrupted_content(self, content: str) -> str:
        """
        Corriger le contenu corrompu (JSON mal parsé)
        
        Args:
            content: Contenu potentiellement corrompu
            
        Returns:
            Contenu corrigé
        """
        if not content:
            return content
        
        # Détecter le contenu JSON mal parsé
        if content.startswith('# Contenu de Formation\n\n[') or '"slide_content"' in content:
            logger.info("🔧 SLIDE ORCHESTRATOR [FIX] Attempting to fix corrupted JSON content")
            
            try:
                # Tenter d'extraire le JSON
                if '"slide_content":' in content:
                    start_idx = content.find('"slide_content":') + len('"slide_content":')
                    end_idx = content.rfind('}')
                    
                    if end_idx > start_idx:
                        json_part = content[start_idx:end_idx].strip()
                        if json_part.startswith('"') and json_part.endswith('"'):
                            # Nettoyer les échappements JSON
                            cleaned_content = json_part[1:-1].replace('\\"', '"').replace('\\n', '\n')
                            logger.info("✅ SLIDE ORCHESTRATOR [FIX] Successfully extracted content from JSON")
                            return cleaned_content
                
            except Exception as e:
                logger.warning(f"⚠️ SLIDE ORCHESTRATOR [FIX] Failed to fix content: {e}")
        
        return content