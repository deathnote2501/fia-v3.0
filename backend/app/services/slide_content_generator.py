"""
FIA v3.0 - Slide Content Generator
Service pour générer le contenu des slides CONTENT et QUIZ avec IA
"""

import logging
import json
import time
from typing import Dict, Any, Optional

from app.infrastructure.adapters.vertex_ai_adapter import VertexAIAdapter, VertexAIError

logger = logging.getLogger(__name__)


class SlideContentGenerator:
    """Service pour générer le contenu des slides avec VertexAI"""
    
    def __init__(self):
        """Initialize slide content generator"""
        self.vertex_adapter = VertexAIAdapter()
        logger.info("🤖 SLIDE CONTENT GENERATOR [SERVICE] Initialized")
    
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
            
            # Construire le prompt personnalisé
            prompt = self._build_content_slide_prompt(
                slide_title, learner_profile, training_plan, slide_position
            )
            
            # Configurer VertexAI pour réponse markdown pure
            vertex_config = {
                "temperature": 0.7,
                "max_output_tokens": 1024,
                "top_p": 0.9,
                "top_k": 40
            }
            
            # Générer le contenu avec VertexAI
            logger.info(f"🤖 SLIDE CONTENT GENERATOR [AI] Calling VertexAI for content generation")
            response = await self.vertex_adapter.generate_content(
                prompt=prompt,
                **vertex_config
            )
            
            # Extraire et nettoyer le contenu
            content = self._extract_markdown_content(response)
            
            duration = time.time() - start_time
            logger.info(f"✅ SLIDE CONTENT GENERATOR [SUCCESS] Content generated in {duration:.2f}s - {len(content)} chars")
            
            return content
            
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
            previous_content: Contenu précédent pour contextualiser le quiz
            
        Returns:
            Contenu markdown du quiz généré
        """
        start_time = time.time()
        
        try:
            logger.info(f"🤖 SLIDE CONTENT GENERATOR [QUIZ] Generating quiz for: {slide_title}")
            
            # Construire le prompt de quiz
            prompt = self._build_quiz_slide_prompt(
                slide_title, learner_profile, previous_content
            )
            
            # Configurer VertexAI pour quiz
            vertex_config = {
                "temperature": 0.8,
                "max_output_tokens": 800,
                "top_p": 0.9,
                "top_k": 40
            }
            
            # Générer le quiz avec VertexAI
            logger.info(f"🤖 SLIDE CONTENT GENERATOR [AI] Calling VertexAI for quiz generation")
            response = await self.vertex_adapter.generate_content(
                prompt=prompt,
                **vertex_config
            )
            
            # Extraire et nettoyer le contenu
            content = self._extract_markdown_content(response)
            
            duration = time.time() - start_time
            logger.info(f"✅ SLIDE CONTENT GENERATOR [SUCCESS] Quiz generated in {duration:.2f}s - {len(content)} chars")
            
            return content
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ SLIDE CONTENT GENERATOR [ERROR] Failed after {duration:.2f}s: {str(e)}")
            return self._generate_fallback_quiz(slide_title, learner_profile)
    
    async def generate_module_introduction(
        self,
        module_name: str,
        learner_profile: Any,
        module_context: Dict[str, Any]
    ) -> str:
        """
        Générer l'introduction IA pour une slide MODULE
        
        Args:
            module_name: Nom du module
            learner_profile: Profil de l'apprenant
            module_context: Contexte du module (sous-modules, objectifs)
            
        Returns:
            Introduction personnalisée en texte
        """
        start_time = time.time()
        
        try:
            logger.info(f"🤖 SLIDE CONTENT GENERATOR [MODULE] Generating introduction for: {module_name}")
            
            # Construire le prompt d'introduction
            prompt = self._build_module_introduction_prompt(
                module_name, learner_profile, module_context
            )
            
            # Configurer VertexAI pour introduction courte
            vertex_config = {
                "temperature": 0.6,
                "max_output_tokens": 400,
                "top_p": 0.8,
                "top_k": 30
            }
            
            # Générer l'introduction
            logger.info(f"🤖 SLIDE CONTENT GENERATOR [AI] Calling VertexAI for module introduction")
            response = await self.vertex_adapter.generate_content(
                prompt=prompt,
                **vertex_config
            )
            
            # Extraire le texte pur (pas de markdown)
            introduction = self._extract_text_content(response)
            
            duration = time.time() - start_time
            logger.info(f"✅ SLIDE CONTENT GENERATOR [SUCCESS] Introduction generated in {duration:.2f}s - {len(introduction)} chars")
            
            return introduction
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ SLIDE CONTENT GENERATOR [ERROR] Failed after {duration:.2f}s: {str(e)}")
            return self._generate_fallback_introduction(module_name, learner_profile)
    
    # ===== Méthodes de construction de prompts =====
    
    def _build_content_slide_prompt(
        self,
        slide_title: str,
        learner_profile: Any,
        training_plan: Any,
        slide_position: str
    ) -> str:
        """Construire le prompt pour une slide CONTENT"""
        # Extraire les informations du profil
        profile_info = self._extract_profile_info(learner_profile)
        enriched_profile_context = self._extract_enriched_profile(learner_profile)
        plan_context = self._extract_plan_context(training_plan)
        
        return f"""[ROLE] : 
Tu es un formateur pédagogue spécialisé dans la création de [SLIDE DE FORMATION].

[OBJECTIF] :
Créer le contenu de la [SLIDE DE FORMATION] suivante : {slide_title}. Cette [SLIDE DE FORMATION] doit être personnalisée pour le [PROFIL APPRENANT].

[PROFIL APPRENANT]
- Niveau d'expérience : {profile_info['niveau']}
- Poste et secteur : {profile_info['poste_et_secteur']}
- Objectifs de formation : {profile_info['objectifs']}  
- Profil enrichi au fil de la formation de l'apprenant : {enriched_profile_context}
- Langue : {profile_info['langue']}

[INFORMATIONS SUPPLÉMENTAIRES SUR LA FORMATION] :
- Position de la slide dans la formation : {slide_position}
- Plan de la formation : {plan_context}

[CONTRAINTES] :
- Réponds UNIQUEMENT avec le contenu de la slide en Markdown pur
- Commence directement par le contenu, pas de préambule
- Utilise des éléments markdown : # ## ### - > ** *
- Utilise la structure suivante : titre, sous-titres, points clés sous forme de liste à puces, textes courts (5 à 15 mots)
- La slide devra contenir en tout entre 50 et 100 mots maximum

Génère maintenant le contenu de la [SLIDE DE FORMATION] qui respecte les [CONTRAINTES]."""
    
    def _build_quiz_slide_prompt(
        self,
        slide_title: str,
        learner_profile: Any,
        previous_content: Optional[str] = None
    ) -> str:
        """Construire le prompt pour une slide QUIZ"""
        # Extraire les informations du profil
        profile_info = self._extract_profile_info(learner_profile)
        enriched_profile_context = self._extract_enriched_profile(learner_profile)
        
        return f"""[ROLE] : 
Tu es un formateur pédagogue spécialisé dans la création de [SLIDE DE FORMATION] de type quiz.

[OBJECTIF] :
Créer le contenu de la [SLIDE DE FORMATION] de type quiz. Cette [SLIDE DE FORMATION] doit être adaptée et personnalisée pour le [PROFIL APPRENANT].

[PROFIL APPRENANT] :
- Niveau : {profile_info['niveau']}
- Poste et secteur : {profile_info['poste_et_secteur']}
- Objectifs : {profile_info['objectifs']}
- Profil enrichi au fil de la formation de l'apprenant : {enriched_profile_context}
- Langue : {profile_info['langue']}

[CONTRAINTES] :
- La slide contiendra un titre et entre 3 et 5 questions de connaissance
- Réponds UNIQUEMENT avec le contenu de la slide en Markdown pur
- Commence directement par le contenu, pas de préambule
- Utilise des éléments markdown : # et -
- Utilise la structure suivante : titre, questions de connaissance sous forme de liste à puces, textes courts (5 à 15 mots)
- La slide devra contenir en tout entre 50 et 100 mots maximum
- Rappelle que l'apprenant peut répondre en utilisant le chat IA à gauche qui corrigera ses réponses

Génère maintenant le contenu de la [SLIDE DE FORMATION] de type quiz qui respecte les [CONTRAINTES]."""
    
    def _build_module_introduction_prompt(
        self,
        module_name: str,
        learner_profile: Any,
        module_context: Dict[str, Any]
    ) -> str:
        """Construire le prompt pour l'introduction d'un module"""
        profile_info = self._extract_profile_info(learner_profile)
        enriched_profile_context = self._extract_enriched_profile(learner_profile)
        
        submodules_list = ", ".join(module_context.get("submodules", []))
        
        return f"""[ROLE] :
Tu es un formateur pédagogue spécialisé dans la création d'introductions de modules.

[OBJECTIF] :
Créer une introduction personnalisée pour le module "{module_name}" selon le [PROFIL APPRENANT].

[PROFIL APPRENANT] :
- Niveau : {profile_info['niveau']}
- Poste et secteur : {profile_info['poste_et_secteur']}
- Objectifs : {profile_info['objectifs']}
- Profil enrichi : {enriched_profile_context}

[CONTEXTE DU MODULE] :
- Module : {module_name}
- Sous-modules inclus : {submodules_list}

[CONTRAINTES] :
- Réponds UNIQUEMENT avec le texte d'introduction (pas de markdown)
- 2-3 phrases maximum (30-50 mots)
- Explique l'objectif et ce que l'apprenant va découvrir
- Adapte au profil professionnel de l'apprenant
- Ton engageant et motivant

Génère maintenant l'introduction du module."""
    
    # ===== Méthodes d'extraction d'informations =====
    
    def _extract_profile_info(self, learner_profile: Any) -> Dict[str, str]:
        """Extraire les informations de base du profil apprenant"""
        return {
            'niveau': getattr(learner_profile, 'experience_level', 'beginner'),
            'poste_et_secteur': getattr(learner_profile, 'job_and_sector', 'professionnel'),
            'objectifs': getattr(learner_profile, 'objectives', 'développer mes compétences'),
            'langue': getattr(learner_profile, 'language', 'fr')
        }
    
    def _extract_enriched_profile(self, learner_profile: Any) -> str:
        """Extraire le profil enrichi de l'apprenant"""
        if not hasattr(learner_profile, 'enriched_profile') or not learner_profile.enriched_profile:
            return "Profil en cours d'enrichissement au fil des interactions"
        
        try:
            enriched_data = learner_profile.enriched_profile
            if isinstance(enriched_data, str):
                enriched_data = json.loads(enriched_data)
            
            # Construire un résumé du profil enrichi
            enriched_parts = []
            
            if enriched_data.get("learning_style_observed"):
                enriched_parts.append(f"Style observé: {enriched_data['learning_style_observed']}")
            
            if enriched_data.get("comprehension_level"):
                enriched_parts.append(f"Niveau de compréhension: {enriched_data['comprehension_level']}")
            
            if enriched_data.get("interests"):
                enriched_parts.append(f"Centres d'intérêt: {', '.join(enriched_data['interests'][:3])}")
            
            if enriched_data.get("blockers"):
                enriched_parts.append(f"Difficultés: {', '.join(enriched_data['blockers'][:2])}")
            
            return " | ".join(enriched_parts) if enriched_parts else "Profil en cours d'enrichissement"
            
        except (json.JSONDecodeError, AttributeError):
            return "Profil en cours d'enrichissement au fil des interactions"
    
    def _extract_plan_context(self, training_plan: Any) -> str:
        """Extraire le contexte du plan de formation"""
        if not hasattr(training_plan, 'plan_data') or not training_plan.plan_data:
            return "Formation personnalisée selon le profil apprenant"
        
        try:
            plan_data = training_plan.plan_data if isinstance(training_plan.plan_data, dict) else json.loads(training_plan.plan_data)
            
            # Extraire les objectifs généraux s'ils existent
            if 'formation_plan' in plan_data:
                plan_context = f"Contexte: {plan_data['formation_plan'].get('objectifs_generaux', 'Formation personnalisée')}"
            else:
                plan_context = "Formation personnalisée selon le profil apprenant"
            
            return plan_context
            
        except (json.JSONDecodeError, KeyError, AttributeError):
            return "Formation personnalisée selon le profil apprenant"
    
    # ===== Méthodes d'extraction de contenu =====
    
    def _extract_markdown_content(self, response: Any) -> str:
        """Extraire le contenu markdown de la réponse VertexAI"""
        try:
            if hasattr(response, 'text'):
                content = response.text.strip()
            elif isinstance(response, str):
                content = response.strip()
            else:
                content = str(response).strip()
            
            # Nettoyer le contenu
            content = self._clean_markdown_content(content)
            
            return content
            
        except Exception as e:
            logger.error(f"❌ SLIDE CONTENT GENERATOR [EXTRACT] Failed to extract content: {e}")
            return "# Erreur\n\nContenu indisponible temporairement."
    
    def _extract_text_content(self, response: Any) -> str:
        """Extraire le contenu texte pur de la réponse VertexAI"""
        try:
            if hasattr(response, 'text'):
                content = response.text.strip()
            elif isinstance(response, str):
                content = response.strip()
            else:
                content = str(response).strip()
            
            # Supprimer les éventuels markdowns
            content = content.replace('**', '').replace('*', '').replace('#', '').replace('-', '')
            content = ' '.join(content.split())  # Normaliser les espaces
            
            return content
            
        except Exception as e:
            logger.error(f"❌ SLIDE CONTENT GENERATOR [EXTRACT] Failed to extract text: {e}")
            return "Introduction indisponible temporairement."
    
    def _clean_markdown_content(self, content: str) -> str:
        """Nettoyer le contenu markdown"""
        # Supprimer les préambules courants
        unwanted_prefixes = [
            "Voici le contenu",
            "Contenu de la slide",
            "# Contenu de Formation",
            "```markdown",
            "```"
        ]
        
        for prefix in unwanted_prefixes:
            if content.startswith(prefix):
                content = content[len(prefix):].strip()
        
        # Supprimer les suffixes indésirables
        if content.endswith("```"):
            content = content[:-3].strip()
        
        return content
    
    # ===== Méthodes de fallback =====
    
    def _generate_fallback_content(self, slide_title: str, learner_profile: Any) -> str:
        """Générer un contenu de fallback pour une slide CONTENT"""
        profile_info = self._extract_profile_info(learner_profile)
        
        return f"""# {slide_title}

## Points clés
- Concept adapté à {profile_info['poste_et_secteur']}
- Application pratique
- Exercice d'intégration

## À retenir
> Les éléments essentiels pour {profile_info['objectifs']}"""
    
    def _generate_fallback_quiz(self, slide_title: str, learner_profile: Any) -> str:
        """Générer un quiz de fallback"""
        return f"""# {slide_title}

- Quel est le concept principal abordé ?
- Comment l'appliquer dans votre contexte ?
- Quels sont les bénéfices attendus ?

> Utilisez le chat IA à gauche pour obtenir les corrections"""
    
    def _generate_fallback_introduction(self, module_name: str, learner_profile: Any) -> str:
        """Générer une introduction de fallback pour un module"""
        profile_info = self._extract_profile_info(learner_profile)
        
        return f"Dans ce module, vous découvrirez les concepts essentiels de {module_name} adaptés à {profile_info['poste_et_secteur']}. Chaque section vous permettra de progresser vers {profile_info['objectifs']}."
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques du générateur"""
        return {
            "supported_types": ["CONTENT", "QUIZ", "MODULE_INTRO"],
            "ai_provider": "VertexAI (Google Gemini)",
            "content_limits": {
                "content_slide": "50-100 mots",
                "quiz_slide": "50-100 mots", 
                "module_intro": "30-50 mots"
            },
            "prompts_used": "Nouveaux prompts simplifiés"
        }