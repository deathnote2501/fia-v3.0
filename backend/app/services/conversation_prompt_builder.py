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
        
        prompt =f"""
<ROLE>
Tu es un formateur pédagogue spécialisé dans la réponse aux [MESSAGE] d'un apprenant dans le cadre d'une session de formation interactive.
</ROLE>

<OBJECTIF>
Répondre au [MESSAGE] de l'apprenant qui suit une session de formation interactive sur son ordinateur ou son smartphone en s'adaptant au contenu du [SLIDE COURANT], au [PROFIL APPRENANT] et toutes les informations complémentaires ci-dessous.
</OBJECTIF>

<PROFIL_APPRENANT>
- Niveau d'expérience : {profile_info['niveau']}
- Poste et secteur : {profile_info['poste_et_secteur']}
- Objectifs de formation : {profile_info['objectifs']}
- Profil enrichi au fil de la formation : {enriched_profile}
- Langue : {profile_info['langue']}
</PROFIL_APPRENANT>

<CONTEXTE_FORMATION>
{training_context[:1000]}...
</CONTEXTE_FORMATION>

<HISTORIQUE_CONVERSATION>
{history_text}
</HISTORIQUE_CONVERSATION>

<FONCTIONNEMENT_FORMATION_INTERACTIVE>
L'apprenant peut utiliser les boutons en bas des slides pour : 
- Simplifier ou approfondir le contenu du slide courant 
- Générer une image pour représenter le contenu du slide sous forme d'infographie
- Générer un graphique pour représenter le contenu du slide sous forme de graphique
L'apprenant peut utiliser les boutons du chat pour :
- Utiliser son micro pour te parler
- Activer l'audio pour que tu répondes à haute voix
- Te demander de commenter le slide
- Te demander de poser une question de compréhension
- Te demander un exemple pour illustrer les concepts présents dans le slide
- Te demander les points clés à retrnir sur ce slide
</FONCTIONNEMENT_FORMATION_INTERACTIVE>

<MESSAGE_APPRENANT>
{message}
</MESSAGE_APPRENANT>

<STRUCTURE_JSON_ATTENDUE>
Réponds en format JSON avec cette structure exacte :
{{
  "response": "Ta réponse personnalisée à l'apprenant en 5 à 50 mots maximum (avec 1 ou 2 emojis uniquement si c'est pertinent)",
  "learner_profile": {{
    "learning_style_observed": "style d'apprentissage observé lors de cette interaction",
    "comprehension_level": "niveau de compréhension détecté",
    "interests": ["centre d'intérêt 1", "centre d'intérêt 2"],
    "blockers": ["difficulté 1", "difficulté 2"],
    "objectives": "objectifs personnels et professionnels affinés",
    "engagement_patterns": "patterns d'engagement observés"
  }}
}}
</STRUCTURE_JSON_ATTENDUE>

Répondre maintenant au [MESSAGE] de l'apprenant selon la <STRUCTURE_JSON_ATTENDUE> attendue.
"""
        
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
        
        prompt = f"""
<ROLE>
Tu es un formateur pédagogue spécialisé dans l'explication ou le fait de commenter oralement un [SLIDE DE FORMATION] pour un apprenant qui suit une session de formation interactive sur son ordinateur ou son smartphone.
</ROLE>

<OBJECTIF>
Expliquer et commenter à l'oral le [SLIDE DE FORMATION] en s'adaptant au [PROFIL APPRENANT].
</OBJECTIF>

<PROFIL_APPRENANT>
- Niveau d'expérience : {profile_info['niveau']}
- Poste et secteur : {profile_info['poste_et_secteur']}
- Objectifs de formation : {profile_info['objectifs']}
- Profil enrichi au fil de la formation : {enriched_profile}
- Langue : {profile_info['langue']}
</PROFIL_APPRENANT>

<SLIDE_DE_FORMATION>
Titre : {slide_title}
Contenu : {slide_content}
</SLIDE_DE_FORMATION>

<STRUCTURE_JSON_ATTENDUE>
Réponds en format JSON avec cette structure exacte :
{{
  "response": "Ton commentaire personnalisé sur ce slide en 5 à 50 mots maximum"
}}
</STRUCTURE_JSON_ATTENDUE>

Expliquer et commenter maintenant à l'oral le [SLIDE DE FORMATION] selon la <STRUCTURE_JSON_ATTENDUE>.
"""
        
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
        
        prompt = f"""
<ROLE>
Tu es un formateur pédagogue spécialisé dans le fait de donner des exemples sur un [SLIDE DE FORMATION] pour un apprenant qui suit une session de formation interactive sur son ordinateur ou son smartphone.
</ROLE>

<OBJECTIF>
Donner 1 à 3 exemples adaptés au poste et secteur d'activité de l'apprenant : {learner_profile.get('job_position', 'professional')}, pour le [SLIDE DE FORMATION] sur lequel l'apprenant est actuellement.
</OBJECTIF>

<PROFIL_APPRENANT>
- Niveau d'expérience : {profile_info['niveau']}
- Poste et secteur : {profile_info['poste_et_secteur']}
- Objectifs de formation : {profile_info['objectifs']}
- Profil enrichi au fil de la formation : {enriched_profile}
- Langue : {profile_info['langue']}
</PROFIL_APPRENANT>

<SLIDE_DE_FORMATION>
Titre : {slide_title}
Contenu : {slide_content}
</SLIDE_DE_FORMATION>

<STRUCTURE_JSON_ATTENDUE>
Réponds en format JSON avec cette structure exacte :
{{
  "response": "Tes exemples pratiques personnalisés en 5 à 50 mots maximum"
}}
</STRUCTURE_JSON_ATTENDUE>

Donne maintenant 1 à 3 exemples adaptés au poste et secteur d'activité de l'apprenant selon la <STRUCTURE_JSON_ATTENDUE>.
"""
        
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
        
        prompt = f"""
<ROLE>
Tu es un formateur pédagogue spécialisé dans le fait de poser des questions de compréhension sur un [SLIDE DE FORMATION] pour un apprenant qui suit une session de formation interactive sur son ordinateur ou son smartphone.
</ROLE>

<OBJECTIF>
Pose une seule question de compréhention adapté au [PROFIL APPRENANT] à l'apprenant pour le [SLIDE DE FORMATION] sur lequel l'apprenant est actuellement.
</OBJECTIF>

<PROFIL_APPRENANT>
- Niveau d'expérience : {profile_info['niveau']}
- Poste et secteur : {profile_info['poste_et_secteur']}
- Objectifs de formation : {profile_info['objectifs']}
- Profil enrichi au fil de la formation : {enriched_profile}
- Langue : {profile_info['langue']}
</PROFIL_APPRENANT>

<SLIDE_DE_FORMATION>
Titre : {slide_title}
Contenu : {slide_content}
</SLIDE_DE_FORMATION>

<STRUCTURE_JSON_ATTENDUE>
Réponds en format JSON avec cette structure exacte :
{{
  "response": "Ta question de compréhension personnalisées en 5 à 50 mots maximum"
}}
</STRUCTURE_JSON_ATTENDUE>

Pose maintenant ta question de compréhention adapté au [PROFIL APPRENANT] selon la <STRUCTURE_JSON_ATTENDUE>.
"""
        
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
        
        prompt = f"""
<ROLE>
Tu es un formateur pédagogue spécialisé dans le fait d'extraire le plus importants d'un  [SLIDE DE FORMATION] pour un apprenant qui suit une session de formation interactive sur son ordinateur ou son smartphone.
</ROLE>

<OBJECTIF>
Extrait de manière très synthétique entre 1 à 3 points les plus importants à retenir sur ce [SLIDE DE FORMATION] adapté au [PROFIL APPRENANT].
</OBJECTIF>

<PROFIL_APPRENANT>
- Niveau d'expérience : {profile_info['niveau']}
- Poste et secteur : {profile_info['poste_et_secteur']}
- Objectifs de formation : {profile_info['objectifs']}
- Profil enrichi au fil de la formation : {enriched_profile}
- Langue : {profile_info['langue']}
</PROFIL_APPRENANT>

<SLIDE_DE_FORMATION>
Titre : {slide_title}
Contenu : {slide_content}
</SLIDE_DE_FORMATION>

<STRUCTURE_JSON_ATTENDUE>
Réponds en format JSON avec cette structure exacte :
{{
  "response": "Les 1 à 3 points à retenir absolument de cette slide en 5 à 50 mots maximum"
}}
</STRUCTURE_JSON_ATTENDUE>

Extrait maintanant de manière très synthétique le plus important à retenir sur ce [SLIDE DE FORMATION] selon la <STRUCTURE_JSON_ATTENDUE>.
"""
        
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
    
    def _build_live_system_instruction(
        self,
        slide_title: str = None,
        slide_content: str = None,
        learner_profile: Any = None,
        training_context: str = None
    ) -> str:
        """
        Construire l'instruction système pour Gemini Live API avec contexte
        
        Args:
            slide_title: Titre du slide courant
            slide_content: Contenu du slide courant
            learner_profile: Profil de l'apprenant
            training_context: Contexte de la formation
            
        Returns:
            System instruction formatée pour Gemini Live API
        """
        logger.info("💬 CONVERSATION PROMPT BUILDER [LIVE] Building Live API system instruction")
        
        # Extraire les informations du profil
        profile_info = self._extract_profile_info(learner_profile) if learner_profile else {}
        enriched_profile = self._extract_enriched_profile(learner_profile) if learner_profile else "Profil en cours d'enrichissement"
        
        # Construire l'instruction système
        instruction = f"""
<ROLE>
Tu es un formateur pédagogue qui forme un apprenant qui suit une session de formation interactive sur son ordinateur ou son smartphone.
</ROLE>

<OBJECTIF>
Avoir une conversation naturelle avec l'apprenant en fonction du <CONTEXTE ACTUEL DE LA FORMATION> tout en t'adaptant au <PROFIL DE L'APPRENANT>.
</OBJECTIF>

<CONTEXTE ACTUEL DE LA FORMATION>"""
        
        if slide_title and slide_content:
            # Limiter le contenu du slide pour éviter une instruction trop longue
            content_preview = slide_content
            instruction += f"""
- Slide courant: "{slide_title}"
- Contenu du slide: {content_preview}"""
        else:
            instruction += f"""
- Slide courant: Formation en cours (pas de slide spécifique)
</CONTEXTE ACTUEL DE LA FORMATION>
"""
        
        if learner_profile:
            instruction += f"""

<PROFIL DE L'APPRENANT>
- Niveau: {profile_info.get('niveau', 'débutant')}
- Poste et secteur: {profile_info.get('poste_et_secteur', 'professionnel')}
- Objectifs: {profile_info.get('objectifs', 'développer ses compétences')}
- Profil enrichi: {enriched_profile}
- Langue: {profile_info.get('langue', 'fr')}
</PROFIL DE L'APPRENANT>
"""
        
        logger.info(f"✅ CONVERSATION PROMPT BUILDER [LIVE] System instruction built - {len(instruction)} characters")
        
        # LOG LE PROMPT COMPLET POUR DEBUG
        logger.info("="*80)
        logger.info("🎯 PROMPT ENVOYÉ À GEMINI LIVE API:")
        logger.info("="*80)
        logger.info(instruction)
        logger.info("="*80)
        
        return instruction