"""
FIA v3.0 - Prompt Builder Service
Pure domain service for building personalized AI prompts
"""

import logging
from typing import Dict, Any

# Configure logger
logger = logging.getLogger(__name__)


class PromptBuilder:
    """Pure domain service for building personalized prompts"""
    
    def __init__(self):
        """Initialize prompt builder"""
        logger.info("🎯 PROMPT [BUILDER] initialized")
    
    def extract_learner_profile(self, learner_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize learner profile data"""
        return {
            'experience_level': learner_data.get('experience_level', 'beginner'),
            'job_and_sector': learner_data.get('job_and_sector') or learner_data.get('job_position', 'professionnel'),
            'objectives': learner_data.get('objectives', 'développer mes compétences'),
            'training_duration': learner_data.get('training_duration', '4h'),
            'language': learner_data.get('language', 'fr')
        }
    
    def build_example_structure(self) -> Dict[str, Any]:
        """Build example JSON structure for the AI prompt with slide typologies"""
        return {
            "training_plan": {
                "plan_slide": {
                    "title": "Plan de Formation - Nom de la Formation",
                    "slide_type": "plan"
                },
                "stages": [
                    {
                        "stage_number": 1,
                        "title": "Mise en contexte",
                        "stage_slide": {
                            "title": "Étape 1: Mise en contexte",
                            "slide_type": "stage"
                        },
                        "modules": [
                            {
                                "module_name": "Introduction au domaine",
                                "module_slide": {
                                    "title": "Module: Introduction au domaine",
                                    "slide_type": "module"
                                },
                                "submodules": [
                                    {
                                        "submodule_name": "Présentation des enjeux",
                                        "slide_count": 4,
                                        "slide_titles": [
                                            "Contexte et importance du sujet",
                                            "Défis actuels du secteur", 
                                            "Objectifs de la formation",
                                            "Plan d'apprentissage personnalisé"
                                        ],
                                        "slide_types": [
                                            "content",
                                            "content",
                                            "content", 
                                            "content"
                                        ],
                                        "quiz_slide": {
                                            "title": "Quiz: Présentation des enjeux",
                                            "slide_type": "quiz"
                                        }
                                    }
                                ],
                                "module_quiz_slide": {
                                    "title": "Quiz: Introduction au domaine",
                                    "slide_type": "quiz"
                                }
                            }
                        ],
                        "stage_quiz_slide": {
                            "title": "Quiz: Mise en contexte",
                            "slide_type": "quiz"
                        }
                    }
                ]
            }
        }
    
    def build_personalized_prompt(self, learner_profile: Dict[str, Any], document_content: str) -> str:
        """
        Build personalized prompt for plan generation
        
        Args:
            learner_profile: Normalized learner profile
            document_content: Extracted document content
            
        Returns:
            Personalized prompt for plan generation
        """
        # Extract profile information
        experience_level = learner_profile.get('experience_level', 'beginner')
        job_and_sector = learner_profile.get('job_and_sector', 'professionnel')
        objectives = learner_profile.get('objectives', 'développer mes compétences')
        training_duration = learner_profile.get('training_duration', '4h')
        language = learner_profile.get('language', 'fr')
        
        # Build example structure
        example_structure = self.build_example_structure()
        
        # Construct the personalized prompt
        prompt = f"""# [ROLE] :
Tu es un formateur en ingénierie pédagogique spécialisé dans la création de plans de formation personnalisés.

# [OBJECTIF] :
Créer un [PLAN DE FORMATION PERSONNALISE] selon la [STRUCTURE DU PLAN] pour le [PROFIL DE L'APPRENANT] basé sur le [CONTENU DU SUPPORT DE FORMATION] qui doit durer {training_duration}. Ta réponse respectera la [STRUCTURE JSON ATTENDUE].

[PROFIL_DE_L'APPRENANT] :
- Niveau d'expérience: {experience_level}
- Poste et secteur: {job_and_sector}
- Objectifs de formation: {objectives}
- Langue: {language}

[STRUCTURE DU PLAN] :
Le [PLAN DE FORMATION PERSONNALISE] est découpé en 5 étapes ci-dessous :
- Étape 1 : "Mise en contexte" - Introduction, enjeux et objectifs
- Étape 2 : "Acquisition des fondamentaux" - Concepts de base essentiels
- Étape 3 : "Construction progressive" - Approfondissement par étapes
- Étape 4 : "Maîtrise" - Approfondissement et pratique autonome
- Étape 5 : "Validation" - Évaluation finale et consolidation

Il devra respecter les contraintes ci-dessous :
- 1 slide "plan" au début avec le plan global de formation
- 1 slide "stage" avant chaque étape avec introduction de l'étape
- 1 slide "module" avant chaque module avec introduction du module  
- 1 slide "quiz" après chaque sous-module (quiz_slide)
- 1 slide "quiz" après chaque module (module_quiz_slide)
- 1 slide "quiz" après chaque étape (stage_quiz_slide)
- Chaque sous-module DOIT inclure "slide_titles": tableau avec le titre exact de chaque slide
- Chaque sous-module DOIT inclure "slide_types": tableau avec "content" pour chaque slide
- Le nombre de titres dans slide_titles DOIT égaler slide_count
- Le nombre d'éléments dans slide_types DOIT égaler slide_count

[CONTENU DU SUPPORT DE FORMATION] :
{document_content}

[STRUCTURE JSON ATTENDUE] :
{example_structure}

GÉNÈRE le plan de formation personnalisé en JSON strictement conforme au schéma [STRUCTURE JSON ATTENDUE]."""
        
        logger.info(f"🎯 PROMPT [BUILT] Level: {experience_level}, Duration: {training_duration}, Context: {job_and_sector}")
        
        return prompt
    
    def build_slide_content_prompt(self, slide_title: str, learner_profile: Dict[str, Any], 
                                  context: Dict[str, Any]) -> str:
        """
        Build prompt for generating individual slide content
        
        Args:
            slide_title: Title of the slide to generate
            learner_profile: Learner profile for personalization
            context: Additional context (module, submodule, stage info)
            
        Returns:
            Prompt for slide content generation
        """
        experience_level = learner_profile.get('experience_level', 'beginner')
        job_and_sector = learner_profile.get('job_and_sector', 'professionnel')
        objectives = learner_profile.get('objectives', 'développer mes compétences')
        
        prompt = f"""Tu es un expert formateur créant du contenu pédagogique personnalisé.

CONTEXTE:
- Titre de la slide: {slide_title}
- Module: {context.get('module_name', 'N/A')}
- Sous-module: {context.get('submodule_name', 'N/A')}
- Étape: {context.get('stage_title', 'N/A')}

PROFIL APPRENANT:
- Niveau: {experience_level}
- Contexte professionnel: {job_and_sector}
- Objectifs: {objectives}

CONSIGNES:
1. Contenu adapté au niveau {experience_level}
2. Exemples adaptés au contexte {job_and_sector}
3. Contenu engageant et interactif
4. Aligné avec les objectifs: {objectives}

Créé le contenu de cette slide en format structuré avec:
- Introduction du concept
- Explication principale
- Exemple concret adapté au contexte {job_and_sector}
- Point clé à retenir
- Question ou exercice d'engagement

Format JSON attendu:
{{
  "slide_content": {{
    "introduction": "...",
    "main_content": "...",
    "example": "...",
    "key_point": "...",
    "engagement": "..."
  }}
}}"""
        
        return prompt