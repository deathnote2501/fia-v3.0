"""
FIA v3.0 - Slide Content Generator
Service pour générer le contenu des slides CONTENT et QUIZ avec IA
"""

import logging
import time
from typing import Dict, Any, Optional

from app.infrastructure.adapters.vertex_ai_adapter import VertexAIAdapter
from app.domain.services.slide_prompt_builder import SlidePromptBuilder

logger = logging.getLogger(__name__)


class SlideContentGenerator:
    """Service pour générer le contenu des slides avec VertexAI"""
    
    def __init__(self):
        """Initialize slide content generator"""
        self.vertex_adapter = VertexAIAdapter()
        self.prompt_builder = SlidePromptBuilder()
        logger.info("🤖 SLIDE CONTENT GENERATOR [SERVICE] Initialized with unified prompt builder")
    
    async def generate_content_slide(
        self,
        slide_title: str,
        learner_profile: Any,
        training_plan: Any,
        slide_position: str = "middle"
    ) -> str:
        """
        Générer le contenu d'une slide CONTENT avec IA
        
        Args:
            slide_title: Titre de la slide
            learner_profile: Profil de l'apprenant
            training_plan: Plan de formation
            slide_position: Position dans la formation
            
        Returns:
            Contenu markdown généré
        """
        start_time = time.time()
        
        try:
            logger.info(f"🤖 SLIDE CONTENT GENERATOR [CONTENT] Generating content for: {slide_title}")
            
            # Construire le prompt personnalisé avec le prompt builder unifié
            prompt = self.prompt_builder.build_content_slide_prompt(
                slide_title=slide_title,
                learner_profile=learner_profile,
                training_plan=training_plan,
                slide_position=slide_position
            )
            
            # Générer avec VertexAI
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 1024
            }
            
            content = await self.vertex_adapter.generate_content(
                prompt=prompt,
                generation_config=generation_config
            )
            
            duration = time.time() - start_time
            logger.info(f"✅ SLIDE CONTENT GENERATOR [SUCCESS] Content generated in {duration:.2f}s - {len(content)} chars")
            
            # ========== LOGS DÉTAILLÉS CONTENU GÉNÉRÉ PAR L'IA ==========
            logger.info(f"🤖🤖🤖 SLIDE CONTENT GENERATOR [AI_RESPONSE] ========== DÉBUT ANALYSE CONTENU IA ==========")
            logger.info(f"🤖🤖🤖 SLIDE CONTENT GENERATOR [AI_RESPONSE] Content TYPE: {type(content)}")
            logger.info(f"🤖🤖🤖 SLIDE CONTENT GENERATOR [AI_RESPONSE] Content LENGTH: {len(content) if content else 'N/A'}")
            logger.info(f"🤖🤖🤖 SLIDE CONTENT GENERATOR [AI_RESPONSE] Content PREVIEW (500 chars):")
            logger.info(f"🤖🤖🤖 SLIDE CONTENT GENERATOR [AI_RESPONSE] ---START AI CONTENT---")
            logger.info(f"{content[:500] + '...' if content and len(content) > 500 else content}")
            logger.info(f"🤖🤖🤖 SLIDE CONTENT GENERATOR [AI_RESPONSE] ---END AI CONTENT---")
            
            # Analyser le format du contenu
            stripped_content = content.strip() if content else ""
            logger.info(f"🤖🤖🤖 SLIDE CONTENT GENERATOR [AI_RESPONSE] Stripped content LENGTH: {len(stripped_content)}")
            logger.info(f"🤖🤖🤖 SLIDE CONTENT GENERATOR [AI_RESPONSE] Starts with '#': {stripped_content.startswith('#') if stripped_content else False}")
            logger.info(f"🤖🤖🤖 SLIDE CONTENT GENERATOR [AI_RESPONSE] Contains '##': {'##' in stripped_content if stripped_content else False}")
            logger.info(f"🤖🤖🤖 SLIDE CONTENT GENERATOR [AI_RESPONSE] Contains markdown lists '- ': {'- ' in stripped_content if stripped_content else False}")
            logger.info(f"🤖🤖🤖 SLIDE CONTENT GENERATOR [AI_RESPONSE] Contains double braces: {'{{' in stripped_content if stripped_content else False}")
            logger.info(f"🤖🤖🤖 SLIDE CONTENT GENERATOR [AI_RESPONSE] Contains 'slide': {'slide' in stripped_content.lower() if stripped_content else False}")
            logger.info(f"🤖🤖🤖 SLIDE CONTENT GENERATOR [AI_RESPONSE] ========== FIN ANALYSE CONTENU IA ==========")
            
            return stripped_content
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ SLIDE CONTENT GENERATOR [ERROR] Failed after {duration:.2f}s: {str(e)}")
            return self._generate_fallback_content(slide_title, learner_profile)
    
    async def generate_quiz_slide(
        self,
        slide_title: str,
        learner_profile: Any,
        previous_content: Optional[str] = None
    ) -> str:
        """
        Générer le contenu d'une slide QUIZ avec IA
        
        Args:
            slide_title: Titre de la slide quiz
            learner_profile: Profil de l'apprenant
            previous_content: Contenu précédent pour contextualiser
            
        Returns:
            Contenu markdown du quiz généré
        """
        start_time = time.time()
        
        try:
            logger.info(f"🤖 SLIDE CONTENT GENERATOR [QUIZ] Generating quiz for: {slide_title}")
            
            prompt = self.prompt_builder.build_quiz_slide_prompt(
                slide_title=slide_title,
                learner_profile=learner_profile,
                previous_content=previous_content
            )
            
            generation_config = {
                "temperature": 0.4,  # Lower temperature for more structured quiz
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 800
            }
            
            content = await self.vertex_adapter.generate_content(
                prompt=prompt,
                generation_config=generation_config
            )
            
            duration = time.time() - start_time
            logger.info(f"✅ SLIDE CONTENT GENERATOR [SUCCESS] Quiz generated in {duration:.2f}s - {len(content)} chars")
            
            return content.strip()
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ SLIDE CONTENT GENERATOR [ERROR] Failed after {duration:.2f}s: {str(e)}")
            return self._generate_fallback_quiz(slide_title, learner_profile)
    
    async def generate_module_introduction(
        self,
        module_name: str,
        learner_profile: Any,
        module_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Générer l'introduction d'un module avec IA
        
        Args:
            module_name: Nom du module
            learner_profile: Profil de l'apprenant
            module_context: Contexte du module (sous-modules, objectifs)
            
        Returns:
            Introduction textuelle générée
        """
        start_time = time.time()
        
        try:
            logger.info(f"🤖 SLIDE CONTENT GENERATOR [MODULE] Generating introduction for: {module_name}")
            
            prompt = self.prompt_builder.build_module_introduction_prompt(
                module_name=module_name,
                learner_profile=learner_profile,
                module_context=module_context
            )
            
            generation_config = {
                "temperature": 0.6,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 300
            }
            
            introduction = await self.vertex_adapter.generate_content(
                prompt=prompt,
                generation_config=generation_config
            )
            
            duration = time.time() - start_time
            logger.info(f"✅ SLIDE CONTENT GENERATOR [SUCCESS] Introduction generated in {duration:.2f}s - {len(introduction)} chars")
            
            return introduction.strip()
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ SLIDE CONTENT GENERATOR [ERROR] Failed after {duration:.2f}s: {str(e)}")
            return self._generate_fallback_introduction(module_name, learner_profile)
    
    # ===== Méthodes utilitaires privées =====
    
    def _generate_fallback_content(self, slide_title: str, learner_profile: Any) -> str:
        """Générer un contenu de fallback en cas d'erreur"""
        profile_info = self._extract_profile_info(learner_profile)
        
        return f"""# {slide_title}

## Points clés
- Contenu en cours de génération
- Concept adapté à votre niveau : {profile_info['niveau']}
- Application pratique pour votre poste : {profile_info['poste_et_secteur']}

> Cette slide sera bientôt enrichie avec du contenu personnalisé."""

    def _generate_fallback_quiz(self, slide_title: str, learner_profile: Any) -> str:
        """Générer un quiz de fallback en cas d'erreur"""
        profile_info = self._extract_profile_info(learner_profile)
        
        return f"""# {slide_title}

## Questions de compréhension
- Que retenez-vous des concepts présentés ?
- Comment appliquer ces notions dans votre contexte professionnel : {profile_info['poste_et_secteur']} ?
- Quels sont les points qui nécessitent un approfondissement ?

> Utilisez le chat IA pour échanger avec votre formateur virtuel."""

    def _generate_fallback_introduction(self, module_name: str, learner_profile: Any) -> str:
        """Générer une introduction de fallback en cas d'erreur"""
        profile_info = self._extract_profile_info(learner_profile)
        
        return f"Dans ce module '{module_name}', vous allez découvrir des concepts adaptés à votre niveau {profile_info['niveau']} et à votre domaine d'activité. Bonne formation !"
    
    def _extract_profile_info(self, learner_profile: Any) -> Dict[str, str]:
        """Extraire les informations de base du profil apprenant"""
        return {
            'niveau': getattr(learner_profile, 'experience_level', 'beginner'),
            'poste_et_secteur': getattr(learner_profile, 'job_and_sector', None) or 
                              getattr(learner_profile, 'job_position', 'professionnel'),
            'objectifs': getattr(learner_profile, 'objectives', 'développer mes compétences'),
            'langue': getattr(learner_profile, 'language', 'fr')
        }
    
    def get_service_info(self) -> Dict[str, Any]:
        """Obtenir les informations du service"""
        return {
            "service_name": "SlideContentGenerator",
            "version": "2.0",
            "supported_types": ["CONTENT", "QUIZ", "MODULE_INTRO"],
            "ai_provider": "VertexAI (Google Gemini)",
            "content_limits": {
                "content_slide": "50-100 mots",
                "quiz_slide": "50-100 mots", 
                "module_intro": "30-50 mots"
            },
            "prompts_used": "Nouveaux prompts simplifiés"
        }