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
        prompt = f"""
<ROLE>
Tu es un formateur en ingénierie pédagogique spécialisé dans la création de plans de formation personnalisés.
</ROLE>

<OBJECTIF>
Créer un [PLAN DE FORMATION PERSONNALISE] selon la [STRUCTURE DU PLAN] pour le [PROFIL DE L'APPRENANT] basé sur le [CONTENU DU SUPPORT DE FORMATION].
Cette formation qui doit durer {training_duration} : il faut compter entre 3 et 7mn par slide en fonction du type de slide : menu, contenu, quiz, etc. Comme le nombre de slide de chaque sous-module est compris entre 2 et 8 slides, tu dois ajuster avec le nombre de modules et le nombre de sous-modules par module.
Ta réponse respectera la [STRUCTURE JSON ATTENDUE].
</OBJECTIF>

<PROFIL_DE_L_APPRENANT>
- Niveau d'expérience: {experience_level}
- Poste et secteur: {job_and_sector}
- Objectifs de formation: {objectives}
- Langue: {language}
</PROFIL_DE_L_APPRENANT>

<STRUCTURE_DU_PLAN>
Le [PLAN DE FORMATION PERSONNALISE] est découpé en 5 étapes ci-dessous :
- Étape 1 : "Mise en contexte" - Introduction, enjeux et objectifs
- Étape 2 : "Acquisition des fondamentaux" - Concepts de base essentiels
- Étape 3 : "Construction progressive" - Approfondissement par étapes
- Étape 4 : "Maîtrise" - Approfondissement et pratique autonome
- Étape 5 : "Validation" - Évaluation finale et consolidation
</STRUCTURE_DU_PLAN>

<INSTRUCTIONS>
1. ANALYSER le <PROFIL_DE_L_APPRENANT> pour adapter le niveau et le vocabulaire
2. ÉTUDIER le [CONTENU DU SUPPORT DE FORMATION] pour identifier les concepts clés et respecter l’intention pédagogique du formateur qui anime ce [CONTENU DU SUPPORT DE FORMATION]
3. STRUCTURER le plan selon les 5 étapes obligatoires
4. RESPECTER toutes les contraintes de slides et de structure JSON
5. ADAPTER la complexité selon le niveau d'expérience de l'apprenant
6. INTÉGRER des éléments spécifiques au poste et secteur de l'apprenant
7. VÉRIFIER que chaque sous-module a exactement le bon nombre de slides
</INSTRUCTIONS>

<CONSTRAINTS>
- 1 slide "plan" au début avec le plan global de formation
- 1 slide "stage" avant chaque étape avec introduction de l'étape
- 1 slide "module" avant chaque module avec introduction du module  
- 1 slide "quiz" après chaque sous-module (quiz_slide)
- 1 slide "quiz" après chaque module (module_quiz_slide)
- 1 slide "quiz" après chaque étape (stage_quiz_slide)
- OBLIGATOIRE: Chaque sous-module DOIT avoir entre 2 et 8 slides (slide_count entre 2 et 8)
- Chaque sous-module DOIT inclure "slide_titles": tableau avec le titre exact de chaque slide
- Chaque sous-module DOIT inclure "slide_types": tableau avec "content" pour chaque slide
- Le nombre de titres dans slide_titles DOIT égaler slide_count
- Le nombre d'éléments dans slide_types DOIT égaler slide_count
- JAMAIS de slide_count inférieur à 2 ou supérieur à 8
- Tous les tableaux slide_titles et slide_types doivent avoir la même longueur que slide_count
</CONSTRAINTS>

<CONTENU_DU_SUPPORT_DE_FORMATION>
{document_content}
</CONTENU_DU_SUPPORT_DE_FORMATION>

<EXAMPLES>
<EXAMPLE_SOUS_MODULE>
{{
  "submodule_name": "Introduction aux concepts de base",
  "slide_count": 4,
  "slide_titles": [
    "Qu'est-ce que l'IA Générative ?",
    "Les différents types de modèles",
    "Applications dans votre secteur",
    "Enjeux et opportunités"
  ],
  "slide_types": ["content", "content", "content", "content"]
}}
Remarque: slide_count = 4, slide_titles contient 4 éléments, slide_types contient 4 éléments ✅
</EXAMPLE_SOUS_MODULE>

<EXAMPLE_MAUVAIS>
{{
  "submodule_name": "Exemple incorrect",
  "slide_count": 3,
  "slide_titles": ["Titre 1", "Titre 2"],
  "slide_types": ["content", "content", "content", "content"]
}}
Remarque: Incohérence - slide_count=3 mais slide_titles=2 éléments et slide_types=4 éléments ❌
</EXAMPLE_MAUVAIS>
</EXAMPLES>

<STRUCTURE_JSON_ATTENDUE>
{example_structure}
</STRUCTURE_JSON_ATTENDUE>

<RECAP>
POINTS CRITIQUES À RESPECTER ABSOLUMENT :
- Plan en 5 étapes obligatoires selon la structure définie
- Adaptation au niveau {experience_level} et secteur {job_and_sector}
- Chaque sous-module : slide_count entre 2 et 8 (jamais 1, jamais 9+)
- Cohérence parfaite : slide_count = longueur de slide_titles = longueur de slide_types
- Structure JSON strictement conforme à l'exemple fourni
- Contenu personnalisé selon les objectifs : {objectives}
- Respect de la durée : {training_duration}
</RECAP>

Créer maintenant le [PLAN DE FORMATION PERSONNALISE]."""
        
        logger.info(f"🎯 PROMPT [BUILT] Level: {experience_level}, Duration: {training_duration}, Context: {job_and_sector}")
        
        return prompt