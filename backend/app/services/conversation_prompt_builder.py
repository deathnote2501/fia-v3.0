"""
FIA v3.0 - Conversation Prompt Builder
Service centralisé pour construire tous les prompts de conversation et chat IA
"""

import logging
import json
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ConversationPromptBuilder:
    """Service centralisé pour construire les prompts de conversation IA"""
    
    def __init__(self):
        """Initialize conversation prompt builder"""
        logger.info("💬 CONVERSATION PROMPT BUILDER [SERVICE] Initialized")
    
    def build_message_response_prompt(
        self,
        message: str,
        conversation_history: List[Dict[str, Any]],
        training_context: str,
        learner_profile: Any
    ) -> str:
        """
        Construire le prompt de réponse aux messages avec enrichissement profil
        
        Args:
            message: Message de l'apprenant
            conversation_history: Historique de conversation
            training_context: Contexte de la formation
            learner_profile: Profil de l'apprenant
            
        Returns:
            Prompt formaté pour la réponse conversationnelle
        """
        logger.info("💬 CONVERSATION PROMPT BUILDER [MESSAGE] Building message response prompt")
        
        # Extraire les informations nécessaires
        profile_info = self._extract_profile_info(learner_profile)
        enriched_profile = self._extract_enriched_profile(learner_profile)
        history_text = self._format_conversation_history(conversation_history)
        
        prompt = f"""[ROLE] :
Tu es un formateur IA spécialisé dans l'accompagnement pédagogique personnalisé en [FORMATION INTERACTIVE].

[OBJECTIF] :
Répondre au [MESSAGE APPRENANT] en adaptant ta pédagogie selon le [PROFIL APPRENANT] et enrichir continuellement ce profil pour personnaliser les futures slides.

[PROFIL APPRENANT] :
- Niveau d'expérience : {profile_info['niveau']}
- Poste et secteur : {profile_info['poste_et_secteur']}
- Objectifs de formation : {profile_info['objectifs']}
- Profil enrichi au fil de la formation : {enriched_profile}
- Langue : {profile_info['langue']}

[CONTEXTE FORMATION] :
{training_context[:1000]}...

[HISTORIQUE CONVERSATION] :
{history_text}

[MESSAGE APPRENANT] :
{message}

[STRUCTURE JSON ATTENDUE] :
Réponds en format JSON avec cette structure exacte :
{{
  "response": "Ta réponse pédagogique personnalisée à l'apprenant",
  "learner_profile": {{
    "learning_style_observed": "style d'apprentissage observé lors de cette interaction",
    "comprehension_level": "niveau de compréhension détecté",
    "interests": ["centre d'intérêt 1", "centre d'intérêt 2"],
    "blockers": ["difficulté 1", "difficulté 2"],
    "objectives": "objectifs personnels et professionnels affinés",
    "engagement_patterns": "patterns d'engagement observés"
  }}
}}

Génère maintenant la réponse au format JSON selon la [STRUCTURE JSON ATTENDUE]."""
        
        logger.info(f"✅ CONVERSATION PROMPT BUILDER [MESSAGE] Prompt built - {len(prompt)} characters")
        return prompt
    
    def build_slide_commentary_prompt(
        self,
        slide_content: str,
        slide_title: str,
        learner_profile: Any
    ) -> str:
        """
        Construire le prompt de commentaire de slide
        
        Args:
            slide_content: Contenu de la slide
            slide_title: Titre de la slide
            learner_profile: Profil de l'apprenant
            
        Returns:
            Prompt formaté pour le commentaire de slide
        """
        logger.info(f"💬 CONVERSATION PROMPT BUILDER [COMMENTARY] Building commentary prompt for: {slide_title}")
        
        # Extraire les informations nécessaires
        profile_info = self._extract_profile_info(learner_profile)
        enriched_profile = self._extract_enriched_profile(learner_profile)
        
        prompt = f"""[ROLE] :
Tu es un formateur IA spécialisé dans l'analyse pédagogique de [SLIDE DE FORMATION].

[OBJECTIF] :
Commenter et analyser la [SLIDE DE FORMATION] ci-dessous en adaptant ton analyse selon le [PROFIL APPRENANT].

[SLIDE DE FORMATION] :
Titre : {slide_title}
Contenu : {slide_content[:1500]}...

[PROFIL APPRENANT] :
- Niveau d'expérience : {profile_info['niveau']}
- Poste et secteur : {profile_info['poste_et_secteur']}
- Objectifs de formation : {profile_info['objectifs']}
- Profil enrichi au fil de la formation : {enriched_profile}
- Langue : {profile_info['langue']}

[STRUCTURE JSON ATTENDUE] :
Réponds en format JSON avec cette structure exacte :
{{
  "response": "Ton commentaire pédagogique personnalisé sur cette slide",
  "confidence_score": 0.85,
  "suggested_actions": ["Action 1", "Action 2"],
  "related_concepts": ["Concept 1", "Concept 2"],
  "generation_time_ms": 1200
}}

Génère maintenant le commentaire au format JSON selon la [STRUCTURE JSON ATTENDUE]."""
        
        logger.info(f"✅ CONVERSATION PROMPT BUILDER [COMMENTARY] Prompt built - {len(prompt)} characters")
        return prompt
    
    def build_example_generation_prompt(
        self,
        slide_content: str,
        slide_title: str,
        learner_profile: Any
    ) -> str:
        """
        Construire le prompt de génération d'exemples
        
        Args:
            slide_content: Contenu de la slide
            slide_title: Titre de la slide
            learner_profile: Profil de l'apprenant
            
        Returns:
            Prompt formaté pour la génération d'exemples
        """
        logger.info(f"💬 CONVERSATION PROMPT BUILDER [EXAMPLES] Building examples prompt for: {slide_title}")
        
        # Extraire les informations nécessaires
        profile_info = self._extract_profile_info(learner_profile)
        enriched_profile = self._extract_enriched_profile(learner_profile)
        
        prompt = f"""[ROLE] :
Tu es un formateur IA spécialisé dans la création d'[EXEMPLES PRATIQUES] personnalisés.

[OBJECTIF] :
Fournir des [EXEMPLES PRATIQUES] concrets qui illustrent la [SLIDE DE FORMATION] en les adaptant au [PROFIL APPRENANT].

[SLIDE DE FORMATION] :
Titre : {slide_title}
Contenu : {slide_content[:1500]}...

[PROFIL APPRENANT] :
- Niveau d'expérience : {profile_info['niveau']}
- Poste et secteur : {profile_info['poste_et_secteur']}
- Objectifs de formation : {profile_info['objectifs']}
- Profil enrichi au fil de la formation : {enriched_profile}
- Langue : {profile_info['langue']}

[STRUCTURE JSON ATTENDUE] :
Réponds en format JSON avec cette structure exacte :
{{
  "response": "Tes exemples pratiques personnalisés (2-3 exemples concrets)",
  "confidence_score": 0.85,
  "suggested_actions": ["Action 1", "Action 2"],
  "related_concepts": ["Concept 1", "Concept 2"],
  "generation_time_ms": 1200
}}

Génère maintenant les exemples au format JSON selon la [STRUCTURE JSON ATTENDUE]."""
        
        logger.info(f"✅ CONVERSATION PROMPT BUILDER [EXAMPLES] Prompt built - {len(prompt)} characters")
        return prompt
    
    def build_comprehension_question_prompt(
        self,
        slide_content: str,
        slide_title: str,
        learner_profile: Any
    ) -> str:
        """
        Construire le prompt de question de compréhension (remplace quiz)
        
        Args:
            slide_content: Contenu de la slide
            slide_title: Titre de la slide
            learner_profile: Profil de l'apprenant
            
        Returns:
            Prompt formaté pour les questions de compréhension
        """
        logger.info(f"💬 CONVERSATION PROMPT BUILDER [COMPREHENSION] Building comprehension prompt for: {slide_title}")
        
        # Extraire les informations nécessaires
        profile_info = self._extract_profile_info(learner_profile)
        enriched_profile = self._extract_enriched_profile(learner_profile)
        
        prompt = f"""[ROLE] :
Tu es un formateur IA spécialisé dans l'évaluation de [COMPRÉHENSION APPRENANT].

[OBJECTIF] :
Créer des [QUESTIONS DE COMPRÉHENSION] pour évaluer l'assimilation de la [SLIDE DE FORMATION] selon le [PROFIL APPRENANT].

[SLIDE DE FORMATION] :
Titre : {slide_title}
Contenu : {slide_content[:1500]}...

[PROFIL APPRENANT] :
- Niveau d'expérience : {profile_info['niveau']}
- Poste et secteur : {profile_info['poste_et_secteur']}
- Objectifs de formation : {profile_info['objectifs']}
- Profil enrichi au fil de la formation : {enriched_profile}
- Langue : {profile_info['langue']}

[STRUCTURE JSON ATTENDUE] :
Réponds en format JSON avec cette structure exacte :
{{
  "response": "Tes questions de compréhension personnalisées (2-3 questions adaptées)",
  "confidence_score": 0.85,
  "suggested_actions": ["Action 1", "Action 2"],
  "related_concepts": ["Concept 1", "Concept 2"],
  "generation_time_ms": 1200
}}

Génère maintenant les questions au format JSON selon la [STRUCTURE JSON ATTENDUE]."""
        
        logger.info(f"✅ CONVERSATION PROMPT BUILDER [COMPREHENSION] Prompt built - {len(prompt)} characters")
        return prompt
    
    def build_key_points_prompt(
        self,
        slide_content: str,
        slide_title: str,
        learner_profile: Any
    ) -> str:
        """
        Construire le prompt d'extraction des points clés ("le plus important")
        
        Args:
            slide_content: Contenu de la slide
            slide_title: Titre de la slide
            learner_profile: Profil de l'apprenant
            
        Returns:
            Prompt formaté pour l'extraction des points clés
        """
        logger.info(f"💬 CONVERSATION PROMPT BUILDER [KEY_POINTS] Building key points prompt for: {slide_title}")
        
        # Extraire les informations nécessaires
        profile_info = self._extract_profile_info(learner_profile)
        enriched_profile = self._extract_enriched_profile(learner_profile)
        
        prompt = f"""[ROLE] :
Tu es un formateur IA spécialisé dans l'identification des [POINTS CLÉS ESSENTIELS].

[OBJECTIF] :
Identifier les [POINTS CLÉS ESSENTIELS] de la [SLIDE DE FORMATION] - ce qui est LE PLUS IMPORTANT à retenir selon le [PROFIL APPRENANT].

[SLIDE DE FORMATION] :
Titre : {slide_title}
Contenu : {slide_content[:1500]}...

[PROFIL APPRENANT] :
- Niveau d'expérience : {profile_info['niveau']}
- Poste et secteur : {profile_info['poste_et_secteur']}
- Objectifs de formation : {profile_info['objectifs']}
- Profil enrichi au fil de la formation : {enriched_profile}
- Langue : {profile_info['langue']}

[STRUCTURE JSON ATTENDUE] :
Réponds en format JSON avec cette structure exacte :
{{
  "response": "Les 1-3 points ESSENTIELS à retenir absolument de cette slide",
  "confidence_score": 0.90,
  "suggested_actions": ["Action 1", "Action 2"],
  "related_concepts": ["Concept 1", "Concept 2"],
  "generation_time_ms": 1200
}}

Génère maintenant les points clés au format JSON selon la [STRUCTURE JSON ATTENDUE]."""
        
        logger.info(f"✅ CONVERSATION PROMPT BUILDER [KEY_POINTS] Prompt built - {len(prompt)} characters")
        return prompt
    
    # ===== Méthodes privées communes =====
    
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
            logger.warning(f"⚠️ CONVERSATION PROMPT BUILDER [PROFILE] Failed to parse enriched profile: {e}")
            return "Profil en cours d'enrichissement au fil des interactions"
    
    def _format_conversation_history(self, conversation_history: List[Dict[str, Any]]) -> str:
        """Formater l'historique de conversation"""
        if not conversation_history:
            return "Pas d'historique de conversation"
        
        history_text = ""
        for msg in conversation_history[-5:]:  # Derniers 5 messages pour le contexte
            role = "Apprenant" if msg["role"] == "user" else "Formateur IA"
            history_text += f"{role}: {msg['content']}\n"
        
        return history_text.strip()
    
    def get_supported_prompts(self) -> Dict[str, Any]:
        """Obtenir la liste des prompts supportés"""
        return {
            "message_response": {
                "description": "Prompt pour répondre aux messages avec enrichissement profil",
                "method": "build_message_response_prompt",
                "output_format": "JSON avec response et learner_profile",
                "features": ["chat", "profile_enrichment", "suggestions"]
            },
            "slide_commentary": {
                "description": "Prompt pour commenter et analyser une slide",
                "method": "build_slide_commentary_prompt",
                "output_format": "JSON avec response et metadata",
                "features": ["analysis", "personalization"]
            },
            "example_generation": {
                "description": "Prompt pour générer des exemples pratiques",
                "method": "build_example_generation_prompt",
                "output_format": "JSON avec exemples concrets",
                "features": ["examples", "practical_application"]
            },
            "comprehension_question": {
                "description": "Prompt pour créer des questions de compréhension",
                "method": "build_comprehension_question_prompt",
                "output_format": "JSON avec questions adaptées",
                "features": ["evaluation", "comprehension_check"]
            },
            "key_points": {
                "description": "Prompt pour extraire les points clés essentiels",
                "method": "build_key_points_prompt",
                "output_format": "JSON avec points prioritaires",
                "features": ["synthesis", "prioritization"]
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
            "message_response": ["message", "conversation_history", "training_context", "learner_profile"],
            "slide_commentary": ["slide_content", "slide_title", "learner_profile"],
            "example_generation": ["slide_content", "slide_title", "learner_profile"],
            "comprehension_question": ["slide_content", "slide_title", "learner_profile"],
            "key_points": ["slide_content", "slide_title", "learner_profile"]
        }
        
        if prompt_type not in required_params:
            logger.error(f"❌ CONVERSATION PROMPT BUILDER [VALIDATE] Unknown prompt type: {prompt_type}")
            return False
        
        missing_params = []
        for param in required_params[prompt_type]:
            if param not in kwargs or kwargs[param] is None:
                missing_params.append(param)
        
        if missing_params:
            logger.error(f"❌ CONVERSATION PROMPT BUILDER [VALIDATE] Missing required parameters for {prompt_type}: {missing_params}")
            return False
        
        logger.info(f"✅ CONVERSATION PROMPT BUILDER [VALIDATE] Parameters valid for {prompt_type}")
        return True