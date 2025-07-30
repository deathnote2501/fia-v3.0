"""
FIA v3.0 - Slide Prompt Builder
Service centralisé pour construire tous les prompts de génération de slides
"""

import logging
import json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SlidePromptBuilder:
    """Service centralisé pour construire les prompts de génération de slides"""
    
    def __init__(self):
        """Initialize slide prompt builder"""
        logger.info("📝 SLIDE PROMPT BUILDER [SERVICE] Initialized")
    
    def build_content_slide_prompt(
        self,
        slide_title: str,
        learner_profile: Any,
        training_plan: Any,
        slide_position: str = "middle"
    ) -> str:
        """
        Construire le prompt de création de slide CONTENT
        
        Args:
            slide_title: Titre de la slide
            learner_profile: Profil de l'apprenant
            training_plan: Plan de formation
            slide_position: Position dans la formation
            
        Returns:
            Prompt formaté pour la génération de contenu
        """
        logger.info(f"📝 SLIDE PROMPT BUILDER [CONTENT] Building prompt for: {slide_title}")
        
        # Extraire les informations nécessaires
        profile_info = self._extract_profile_info(learner_profile)
        enriched_profile = self._extract_enriched_profile(learner_profile)
        plan_context = self._extract_plan_context(training_plan)
        
        prompt = f"""[ROLE] : 
Tu es un formateur pédagogue spécialisé dans la création de [SLIDE DE FORMATION].

[OBJECTIF] :
Créer le contenu de la [SLIDE DE FORMATION] suivante : {slide_title}. Cette [SLIDE DE FORMATION] doit être personnalisée pour le [PROFIL APPRENANT].

[PROFIL APPRENANT]
- Niveau d'expérience : {profile_info['niveau']}
- Poste et secteur : {profile_info['poste_et_secteur']}
- Objectifs de formation : {profile_info['objectifs']}  
- Profil enrichi au fil de la formation de l'apprenant : {enriched_profile}
- Langue : {profile_info['langue']}

[INFORMATIONS SUPPLÉMENTAIRES SUR LA FORMATION] :
- Position de la slide dans la formation : {slide_position}
- Plan de la formation : {plan_context}

[CONTRAINTES] :
- Réponds UNIQUEMENT avec le contenu de la slide en Markdown pur
- Commence directement par le contenu, pas de préambule
- Utilise des éléments markdown : # ## ### - > ** *
- Utilise la structure suivante : 1 titre, entre 2 et 4 sous-titres MAXIMUM, entre 1 et 5 points clés MAXIMUM sous forme de liste à puces avec pour chaque puce 5 à 15 mots MAXIMUM

Génère maintenant le contenu de la [SLIDE DE FORMATION] qui respecte les [CONTRAINTES]."""
        
        logger.info(f"✅ SLIDE PROMPT BUILDER [CONTENT] Prompt built - {len(prompt)} characters")
        return prompt
    
    def build_quiz_slide_prompt(
        self,
        slide_title: str,
        learner_profile: Any,
        previous_content: Optional[str] = None
    ) -> str:
        """
        Construire le prompt de création de slide QUIZ
        
        Args:
            slide_title: Titre de la slide quiz
            learner_profile: Profil de l'apprenant
            previous_content: Contenu précédent pour contextualiser
            
        Returns:
            Prompt formaté pour la génération de quiz
        """
        logger.info(f"📝 SLIDE PROMPT BUILDER [QUIZ] Building prompt for: {slide_title}")
        
        # Extraire les informations nécessaires
        profile_info = self._extract_profile_info(learner_profile)
        enriched_profile = self._extract_enriched_profile(learner_profile)
        
        prompt = f"""[ROLE] : 
Tu es un formateur pédagogue spécialisé dans la création de [SLIDE DE FORMATION] de type quiz.

[OBJECTIF] :
Créer le contenu de la [SLIDE DE FORMATION] de type quiz. Cette [SLIDE DE FORMATION] doit être adaptée et personnalisée pour le [PROFIL APPRENANT].

[PROFIL APPRENANT] :
- Niveau : {profile_info['niveau']}
- Poste et secteur : {profile_info['poste_et_secteur']}
- Objectifs : {profile_info['objectifs']}
- Profil enrichi au fil de la formation de l'apprenant : {enriched_profile}
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
        
        logger.info(f"✅ SLIDE PROMPT BUILDER [QUIZ] Prompt built - {len(prompt)} characters")
        return prompt
    
    def build_modification_prompt(
        self,
        action: str,
        current_content: str,
        learner_profile: Any
    ) -> str:
        """
        Construire le prompt de modification (simplification/approfondissement)
        
        Args:
            action: "simplifier" ou "approfondir"
            current_content: Contenu actuel de la slide
            learner_profile: Profil de l'apprenant
            
        Returns:
            Prompt formaté pour la modification de contenu
        """
        logger.info(f"📝 SLIDE PROMPT BUILDER [MODIFY] Building {action} prompt")
        
        # Définir les objectifs selon l'action
        objective_map = {
            "simplifier": "Simplifier le [SLIDE DE FORMATION] ci-dessous pour le rendre plus accessible à l'apprenant selon son [PROFIL APPRENANT] sans perdre l'information essentielle.",
            "approfondir": "Approfondir le [SLIDE DE FORMATION] ci-dessous pour détailler plus en profondeur les concepts pour l'apprenant selon son [PROFIL APPRENANT] sans perdre l'information essentielle."
        }
        
        if action not in objective_map:
            raise ValueError(f"Action '{action}' non supportée. Utilisez 'simplifier' ou 'approfondir'.")
        
        # Extraire les informations nécessaires
        profile_info = self._extract_profile_info(learner_profile)
        enriched_profile = self._extract_enriched_profile(learner_profile)
        
        prompt = f"""[ROLE] : 
Tu es un formateur pédagogue spécialisé dans la réécriture de [SLIDE DE FORMATION].

[OBJECTIF] :
{objective_map[action]}

[SLIDE DE FORMATION] :
{current_content}

[PROFIL APPRENANT] :
- Niveau d'expérience : {profile_info['niveau']}
- Poste et secteur : {profile_info['poste_et_secteur']}
- Objectifs de formation : {profile_info['objectifs']}  
- Profil enrichi au fil de la formation de l'apprenant : {enriched_profile}
- Langue : {profile_info['langue']}

[STRUCTURE JSON ATTENDUE] :
- Réponds en format JSON avec la structure suivante :
{{
  "slide_content": "Le contenu Markdown {action} ici"
}}
- Le contenu dans slide_content doit être du Markdown pur
- Garde la même structure Markdown (titres, listes, etc.) mais adapte le texte
- Reste professionnel et pédagogique

Génère maintenant la réponse au format JSON selon la [STRUCTURE JSON ATTENDUE]."""
        
        logger.info(f"✅ SLIDE PROMPT BUILDER [MODIFY] {action.capitalize()} prompt built - {len(prompt)} characters")
        return prompt
    
    def build_module_introduction_prompt(
        self,
        module_name: str,
        learner_profile: Any,
        module_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Construire le prompt pour l'introduction d'un module
        
        Args:
            module_name: Nom du module
            learner_profile: Profil de l'apprenant
            module_context: Contexte du module (sous-modules, objectifs)
            
        Returns:
            Prompt formaté pour la génération d'introduction
        """
        logger.info(f"📝 SLIDE PROMPT BUILDER [MODULE] Building introduction prompt for: {module_name}")
        
        # Extraire les informations nécessaires
        profile_info = self._extract_profile_info(learner_profile)
        enriched_profile = self._extract_enriched_profile(learner_profile)
        
        # Contexte du module
        if module_context and module_context.get("submodules"):
            submodules_list = ", ".join(module_context["submodules"])
        else:
            submodules_list = "Les sous-modules de ce module"
        
        prompt = f"""[ROLE] :
Tu es un formateur pédagogue spécialisé dans la création d'introductions de modules.

[OBJECTIF] :
Créer une introduction personnalisée pour le module "{module_name}" selon le [PROFIL APPRENANT].

[PROFIL APPRENANT] :
- Niveau : {profile_info['niveau']}
- Poste et secteur : {profile_info['poste_et_secteur']}
- Objectifs : {profile_info['objectifs']}
- Profil enrichi : {enriched_profile}

[CONTEXTE DU MODULE] :
- Module : {module_name}
- Sous-modules inclus : {submodules_list}

[CONTRAINTES] :
- Réponds UNIQUEMENT avec le texte d'introduction (pas de Markdown)
- 2-3 phrases maximum (20-30 mots)
- Explique l'objectif et ce que l'apprenant va découvrir
- Adapte au profil professionnel de l'apprenant
- Ton engageant et motivant

Génère maintenant l'introduction du module."""
        
        logger.info(f"✅ SLIDE PROMPT BUILDER [MODULE] Introduction prompt built - {len(prompt)} characters")
        return prompt
    
    # ===== Méthodes privées d'extraction =====
    
    def _extract_profile_info(self, learner_profile: Any) -> Dict[str, str]:
        """Extraire les informations de base du profil apprenant"""
        return {
            'niveau': getattr(learner_profile, 'experience_level', 'beginner'),
            'poste_et_secteur': getattr(learner_profile, 'job_and_sector', None) or 
                              getattr(learner_profile, 'job_position', 'professionnel'),
            'objectifs': getattr(learner_profile, 'objectives', 'développer mes compétences'),
            'langue': getattr(learner_profile, 'language', 'fr')
        }
    
    def _extract_enriched_profile(self, learner_profile: Any) -> str:
        """Extraire et formater le profil enrichi de l'apprenant"""
        if not hasattr(learner_profile, 'enriched_profile') or not learner_profile.enriched_profile:
            return "Profil en cours d'enrichissement au fil des interactions"
        
        try:
            enriched_data = learner_profile.enriched_profile
            if isinstance(enriched_data, str):
                enriched_data = json.loads(enriched_data)
            
            # Construire un résumé structuré du profil enrichi
            enriched_parts = []
            
            if enriched_data.get("learning_style_observed"):
                enriched_parts.append(f"Style d'apprentissage observé: {enriched_data['learning_style_observed']}")
            
            if enriched_data.get("comprehension_level"):
                enriched_parts.append(f"Niveau de compréhension: {enriched_data['comprehension_level']}")
            
            if enriched_data.get("interests") and isinstance(enriched_data['interests'], list):
                interests = enriched_data['interests'][:3]  # Max 3 centres d'intérêt
                enriched_parts.append(f"Centres d'intérêt identifiés: {', '.join(interests)}")
            
            if enriched_data.get("blockers") and isinstance(enriched_data['blockers'], list):
                blockers = enriched_data['blockers'][:2]  # Max 2 difficultés
                enriched_parts.append(f"Difficultés identifiées: {', '.join(blockers)}")
            
            if enriched_data.get("objectives"):
                enriched_parts.append(f"Objectifs affinés: {enriched_data['objectives']}")
            
            if enriched_data.get("engagement_patterns"):
                enriched_parts.append(f"Patterns d'engagement: {enriched_data['engagement_patterns']}")
            
            return " | ".join(enriched_parts) if enriched_parts else "Profil en cours d'enrichissement au fil des interactions"
            
        except (json.JSONDecodeError, AttributeError, TypeError) as e:
            logger.warning(f"⚠️ SLIDE PROMPT BUILDER [PROFILE] Failed to parse enriched profile: {e}")
            return "Profil en cours d'enrichissement au fil des interactions"
    
    def _extract_plan_context(self, training_plan: Any) -> str:
        """Extraire le contexte global du plan de formation"""
        if not hasattr(training_plan, 'plan_data') or not training_plan.plan_data:
            return "Formation personnalisée selon le profil apprenant"
        
        try:
            plan_data = training_plan.plan_data
            if isinstance(plan_data, str):
                plan_data = json.loads(plan_data)
            
            # Extraire les informations contextuelles du plan
            training_plan_data = plan_data.get("training_plan", {})
            
            # Construire un contexte concis
            context_parts = []
            
            # Nombre d'étapes
            stages = training_plan_data.get("stages", [])
            if stages:
                context_parts.append(f"Formation en {len(stages)} étapes")
            
            # Premier titre d'étape pour donner le ton
            if stages and stages[0].get("title"):
                context_parts.append(f"commence par: {stages[0]['title']}")
            
            # Objectifs généraux si disponibles
            if training_plan_data.get("objectifs_generaux"):
                context_parts.append(f"Objectif: {training_plan_data['objectifs_generaux']}")
            
            return " - ".join(context_parts) if context_parts else "Formation personnalisée selon le profil apprenant"
            
        except (json.JSONDecodeError, KeyError, AttributeError, TypeError) as e:
            logger.warning(f"⚠️ SLIDE PROMPT BUILDER [PLAN] Failed to parse plan context: {e}")
            return "Formation personnalisée selon le profil apprenant"
    
    def get_supported_prompts(self) -> Dict[str, Any]:
        """Obtenir la liste des prompts supportés"""
        return {
            "content_slide": {
                "description": "Prompt pour générer le contenu des slides CONTENT",
                "method": "build_content_slide_prompt",
                "output_format": "Markdown pur",
                "word_limit": "50-100 mots"
            },
            "quiz_slide": {
                "description": "Prompt pour générer le contenu des slides QUIZ",
                "method": "build_quiz_slide_prompt", 
                "output_format": "Markdown pur",
                "word_limit": "50-100 mots"
            },
            "modification": {
                "description": "Prompt pour simplifier ou approfondir une slide existante",
                "method": "build_modification_prompt",
                "actions": ["simplifier", "approfondir"],
                "output_format": "JSON avec slide_content"
            },
            "module_introduction": {
                "description": "Prompt pour générer l'introduction d'un module",
                "method": "build_module_introduction_prompt",
                "output_format": "Texte pur",
                "word_limit": "30-50 mots"
            }
        }
    
    def validate_prompt_input(self, prompt_type: str, **kwargs) -> bool:
        """
        Valider les paramètres d'entrée pour un type de prompt
        
        Args:
            prompt_type: Type de prompt à valider
            **kwargs: Paramètres à valider
            
        Returns:
            True si les paramètres sont valides
        """
        required_params = {
            "content_slide": ["slide_title", "learner_profile", "training_plan"],
            "quiz_slide": ["slide_title", "learner_profile"],
            "modification": ["action", "current_content", "learner_profile"],
            "module_introduction": ["module_name", "learner_profile"]
        }
        
        if prompt_type not in required_params:
            logger.error(f"❌ SLIDE PROMPT BUILDER [VALIDATE] Unknown prompt type: {prompt_type}")
            return False
        
        missing_params = []
        for param in required_params[prompt_type]:
            if param not in kwargs or kwargs[param] is None:
                missing_params.append(param)
        
        if missing_params:
            logger.error(f"❌ SLIDE PROMPT BUILDER [VALIDATE] Missing required parameters for {prompt_type}: {missing_params}")
            return False
        
        # Validation spécifique pour modification
        if prompt_type == "modification":
            if kwargs["action"] not in ["simplifier", "approfondir"]:
                logger.error(f"❌ SLIDE PROMPT BUILDER [VALIDATE] Invalid action for modification: {kwargs['action']}")
                return False
        
        logger.info(f"✅ SLIDE PROMPT BUILDER [VALIDATE] Parameters valid for {prompt_type}")
        return True