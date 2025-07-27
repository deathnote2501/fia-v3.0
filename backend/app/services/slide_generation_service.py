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
                    slide_content = await self._generate_slide_content(
                        slide_title=first_slide.title,
                        learner_profile=learner_session,
                        training_plan=training_plan,
                        slide_position="first"
                    )
                    
                    # 5. Sauvegarder le contenu généré
                    await slide_repo.update_content(first_slide.id, slide_content)
                    first_slide.content = slide_content
                    first_slide.generated_at = datetime.now(timezone.utc)
                
                duration = time.time() - start_time
                
                result = {
                    "slide_id": str(first_slide.id),
                    "title": first_slide.title,
                    "content": first_slide.content,
                    "order_in_submodule": first_slide.order_in_submodule,
                    "generated_at": first_slide.generated_at.isoformat() if first_slide.generated_at else None,
                    "generation_duration": round(duration, 2)
                }
                
                logger.info(f"✅ SLIDE GENERATION [SUCCESS] First slide generated in {duration:.2f}s - {len(first_slide.content)} chars")
                return result
            
            except Exception as e:
                await session.rollback()
                duration = time.time() - start_time
                logger.error(f"❌ SLIDE GENERATION [ERROR] Failed after {duration:.2f}s: {str(e)}")
                raise
    
    async def _generate_slide_content(
        self,
        slide_title: str,
        learner_profile: Any,
        training_plan: Any,
        slide_position: str = "first"
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
            # Construire le prompt personnalisé
            prompt = self._build_slide_prompt(
                slide_title=slide_title,
                learner_profile=learner_profile,
                training_plan=training_plan,
                slide_position=slide_position
            )
            
            # Configuration pour génération de contenu markdown
            generation_config = {
                "temperature": 0.7,  # Créativité modérée pour contenu pédagogique
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 2048,  # Suffisant pour une slide
                # Pas de response_mime_type JSON car on veut du markdown
            }
            
            logger.info(f"🚀 SLIDE GENERATION [AI] Calling VertexAI for slide content generation...")
            
            # Appeler VertexAI pour générer le contenu
            content = await self.vertex_adapter.generate_content(
                prompt=prompt,
                generation_config=generation_config
            )
            
            # Nettoyer et valider le contenu
            cleaned_content = self._clean_markdown_content(content)
            
            logger.info(f"✅ SLIDE GENERATION [AI] Content generated - {len(cleaned_content)} characters")
            return cleaned_content
            
        except Exception as e:
            logger.error(f"❌ SLIDE GENERATION [AI] Failed to generate content: {str(e)}")
            raise VertexAIError(f"Slide content generation failed: {str(e)}", original_error=e)
    
    def _build_slide_prompt(
        self,
        slide_title: str,
        learner_profile: Any,
        training_plan: Any,
        slide_position: str
    ) -> str:
        """Construire le prompt personnalisé pour générer le contenu de la slide"""
        
        # Extraire les informations du profil apprenant
        profile_info = {
            "niveau": learner_profile.experience_level or "débutant",
            "style_apprentissage": learner_profile.learning_style or "visuel",
            "poste": learner_profile.job_position or "non spécifié",
            "secteur": learner_profile.activity_sector or "non spécifié",
            "langue": learner_profile.language or "français"
        }
        
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
    
    def _clean_markdown_content(self, content: str) -> str:
        """Nettoyer et valider le contenu markdown généré"""
        if not content:
            return "# Contenu en cours de génération...\n\nVeuillez patienter pendant que nous préparons votre contenu personnalisé."
        
        # Nettoyer les balises potentielles
        cleaned = content.strip()
        
        # Supprimer les balises markdown code si présentes
        if cleaned.startswith('```markdown'):
            cleaned = cleaned[11:]
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]
        
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        
        cleaned = cleaned.strip()
        
        # Validation basique : doit contenir au moins un titre markdown
        if not any(line.startswith('#') for line in cleaned.split('\n')):
            # Ajouter un titre si manquant
            cleaned = f"# Contenu de Formation\n\n{cleaned}"
        
        return cleaned
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques du service"""
        return {
            "service": "SlideGenerationService",
            "vertex_ai_available": self.vertex_adapter.is_available(),
            "vertex_ai_stats": self.vertex_adapter.get_stats()
        }