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
    
    # Level-based adaptations for learning complexity
    LEVEL_ADAPTATIONS = {
        'beginner': {
            'complexity': 'concepts simples avec explications détaillées',
            'pace': 'progression lente et méthodique',
            'slides_per_concept': '4-6 slides par concept',
            'examples': 'exemples concrets et quotidiens'
        },
        'intermediate': {
            'complexity': 'concepts modérés avec cas pratiques',
            'pace': 'progression standard',
            'slides_per_concept': '3-4 slides par concept', 
            'examples': 'exemples professionnels pertinents'
        },
        'advanced': {
            'complexity': 'concepts avancés et défis complexes',
            'pace': 'progression rapide et efficace',
            'slides_per_concept': '2-3 slides par concept',
            'examples': 'cas d\'études sophistiqués'
        }
    }
    
    # Learning style adaptations (legacy support)
    STYLE_ADAPTATIONS = {
        'visual': 'diagrammes, schémas, infographies et supports visuels',
        'auditory': 'discussions, présentations orales et explications audio',
        'kinesthetic': 'exercices pratiques, manipulations et activités hands-on',
        'reading': 'textes détaillés, documentation et ressources écrites'
    }
    
    # Training duration adaptations (new structure)
    DURATION_ADAPTATIONS = {
        '2h': {
            'modules_per_stage': '1-2 modules',
            'slides_per_module': '2-4 slides',
            'total_concept_depth': 'concepts essentiels uniquement',
            'pace': 'rapide et concentré'
        },
        '4h': {
            'modules_per_stage': '2-3 modules',
            'slides_per_module': '3-6 slides',
            'total_concept_depth': 'concepts principaux avec exemples',
            'pace': 'modéré avec pratique'
        },
        '6h': {
            'modules_per_stage': '2-4 modules',
            'slides_per_module': '4-8 slides',
            'total_concept_depth': 'concepts détaillés avec cas pratiques',
            'pace': 'approfondi avec exercices'
        },
        '1 jour': {
            'modules_per_stage': '3-4 modules',
            'slides_per_module': '5-8 slides',
            'total_concept_depth': 'exploration complète avec multiples exemples',
            'pace': 'méthodique avec temps de réflexion'
        },
        '1.5 jour': {
            'modules_per_stage': '3-5 modules',
            'slides_per_module': '6-10 slides',
            'total_concept_depth': 'maîtrise approfondie avec projets pratiques',
            'pace': 'progressif avec mise en application'
        },
        '2 jours': {
            'modules_per_stage': '4-6 modules',
            'slides_per_module': '8-12 slides',
            'total_concept_depth': 'expertise complète avec études de cas avancées',
            'pace': 'complet avec projets et évaluations'
        },
        '3 jours': {
            'modules_per_stage': '5-8 modules',
            'slides_per_module': '10-15 slides',
            'total_concept_depth': 'formation experte avec certification',
            'pace': 'intensif avec projets complexes et mentorat'
        }
    }
    
    # Required training plan stages (fixed structure)
    REQUIRED_STAGES = [
        {
            "stage_number": 1,
            "title": "Mise en contexte",
            "description": "Introduction, enjeux et objectifs"
        },
        {
            "stage_number": 2,
            "title": "Acquisition des fondamentaux", 
            "description": "Concepts de base essentiels"
        },
        {
            "stage_number": 3,
            "title": "Construction progressive",
            "description": "Approfondissement par étapes"
        },
        {
            "stage_number": 4,
            "title": "Maîtrise",
            "description": "Approfondissement et pratique autonome"
        },
        {
            "stage_number": 5,
            "title": "Validation",
            "description": "Évaluation finale et consolidation"
        }
    ]
    
    def __init__(self):
        """Initialize prompt builder"""
        logger.info("🎯 PROMPT [BUILDER] initialized")
    
    def extract_learner_profile(self, learner_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize learner profile data - Updated for new profile structure"""
        return {
            'experience_level': learner_data.get('experience_level', 'beginner'),
            'job_and_sector': learner_data.get('job_and_sector') or learner_data.get('job_position', 'professionnel'),
            'objectives': learner_data.get('objectives', 'développer mes compétences'),
            'training_duration': learner_data.get('training_duration', '4h'),
            'language': learner_data.get('language', 'fr'),
            # Legacy fields for backward compatibility
            'learning_style': learner_data.get('learning_style', 'visual'),
            'job_position': learner_data.get('job_position'),
            'activity_sector': learner_data.get('activity_sector'),
            'country': learner_data.get('country')
        }
    
    def get_level_config(self, experience_level: str) -> Dict[str, str]:
        """Get configuration based on experience level"""
        return self.LEVEL_ADAPTATIONS.get(
            experience_level, 
            self.LEVEL_ADAPTATIONS['beginner']
        )
    
    def get_style_preference(self, learning_style: str) -> str:
        """Get content style preference based on learning style (legacy support)"""
        return self.STYLE_ADAPTATIONS.get(
            learning_style, 
            self.STYLE_ADAPTATIONS['visual']
        )
    
    def get_duration_config(self, training_duration: str) -> Dict[str, str]:
        """Get configuration based on training duration"""
        return self.DURATION_ADAPTATIONS.get(
            training_duration,
            self.DURATION_ADAPTATIONS['4h']  # Default to 4h
        )
    
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
        Build personalized prompt optimized for plan generation
        
        Args:
            learner_profile: Normalized learner profile
            document_content: Extracted document content
            
        Returns:
            Optimized prompt for personalized plan generation
        """
        # Extract profile information (updated for new structure)
        level = learner_profile.get('experience_level', 'beginner')
        job_and_sector = learner_profile.get('job_and_sector', 'professionnel')
        objectives = learner_profile.get('objectives', 'développer mes compétences')
        training_duration = learner_profile.get('training_duration', '4h')
        
        # Legacy fields for compatibility
        style = learner_profile.get('learning_style', 'visual')
        
        # Get adaptations
        level_config = self.get_level_config(level)
        duration_config = self.get_duration_config(training_duration)
        style_preference = self.get_style_preference(style)
        
        # Build example structure
        example_structure = self.build_example_structure()
        
        # Construct the personalized prompt
        prompt = f"""Tu es un expert en ingénierie pédagogique spécialisé dans la création de plans de formation personnalisés.

PROFIL DE L'APPRENANT:
- Niveau d'expérience: {level}
- Poste et secteur: {job_and_sector}
- Objectifs de formation: {objectives}
- Durée souhaitée: {training_duration}
- Style d'apprentissage (legacy): {style}

CONTENU DU DOCUMENT DE FORMATION:
{document_content}

CONSIGNES DE PERSONNALISATION BASÉES SUR LA DURÉE ({training_duration}):
1. Adapte la complexité: {level_config['complexity']}
2. Structure par étape: {duration_config['modules_per_stage']}
3. Slides par module: {duration_config['slides_per_module']}
4. Profondeur des concepts: {duration_config['total_concept_depth']}
5. Rythme de progression: {duration_config['pace']}
6. Type de contenu privilégié: {style_preference}
7. Exemples à utiliser: {level_config['examples']} adaptés au contexte {job_and_sector}
8. Objectifs à atteindre: {objectives}

STRUCTURE OBLIGATOIRE - EXACTEMENT 5 ÉTAPES:
Étape 1: "Mise en contexte" - Introduction, enjeux et objectifs
Étape 2: "Acquisition des fondamentaux" - Concepts de base essentiels
Étape 3: "Construction progressive" - Approfondissement par étapes
Étape 4: "Maîtrise" - Approfondissement et pratique autonome
Étape 5: "Validation" - Évaluation finale et consolidation

EXEMPLE DE STRUCTURE ATTENDUE:
{example_structure}

CONTRAINTES STRICTES:
- Réponds UNIQUEMENT en JSON valide
- Exactement 5 stages numérotés de 1 à 5
- Chaque stage contient 1-3 modules
- Chaque module contient 1-4 sous-modules
- Chaque sous-module a un slide_count entre 2 et 8
- Chaque sous-module DOIT inclure "slide_titles": tableau avec le titre exact de chaque slide
- Chaque sous-module DOIT inclure "slide_types": tableau avec "content" pour chaque slide
- Le nombre de titres dans slide_titles DOIT égaler slide_count
- Le nombre d'éléments dans slide_types DOIT égaler slide_count
- NOUVELLE STRUCTURE OBLIGATOIRE:
  * 1 slide "plan" au début avec le plan global de formation
  * 1 slide "stage" avant chaque étape avec introduction de l'étape
  * 1 slide "module" avant chaque module avec introduction du module  
  * 1 slide "quiz" après chaque sous-module (quiz_slide)
  * 1 slide "quiz" après chaque module (module_quiz_slide)
  * 1 slide "quiz" après chaque étape (stage_quiz_slide)
- Adapte le contenu au profil {level}/{training_duration}/{job_and_sector}
- Utilise des exemples concrets adaptés au contexte {job_and_sector}
- Privilégie le style d'apprentissage {style} (legacy)
- RESPECTE IMPÉRATIVEMENT la durée {training_duration} avec {duration_config['modules_per_stage']} et {duration_config['slides_per_module']}
- INTÈGRE les objectifs de l'apprenant: {objectives}

GÉNÈRE MAINTENANT le plan de formation personnalisé en JSON strictement conforme au schéma."""
        
        logger.info(f"🎯 PROMPT [BUILT] Level: {level}, Duration: {training_duration}, Context: {job_and_sector}")
        
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
        level = learner_profile.get('experience_level', 'beginner')
        job_and_sector = learner_profile.get('job_and_sector', 'professionnel')
        objectives = learner_profile.get('objectives', 'développer mes compétences')
        
        # Legacy support
        style = learner_profile.get('learning_style', 'visual')
        
        style_preference = self.get_style_preference(style)
        level_config = self.get_level_config(level)
        
        prompt = f"""Tu es un expert formateur créant du contenu pédagogique personnalisé.

CONTEXTE:
- Titre de la slide: {slide_title}
- Module: {context.get('module_name', 'N/A')}
- Sous-module: {context.get('submodule_name', 'N/A')}
- Étape: {context.get('stage_title', 'N/A')}

PROFIL APPRENANT:
- Niveau: {level}
- Contexte professionnel: {job_and_sector}
- Objectifs: {objectives}
- Style (legacy): {style}

CONSIGNES:
1. Contenu adapté au niveau {level}: {level_config['complexity']}
2. Style privilégié: {style_preference}
3. Exemples adaptés au contexte {job_and_sector}
4. Contenu engageant et interactif
5. Aligné avec les objectifs: {objectives}

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
    
    def get_supported_levels(self) -> list[str]:
        """Get list of supported experience levels"""
        return list(self.LEVEL_ADAPTATIONS.keys())
    
    def get_supported_styles(self) -> list[str]:
        """Get list of supported learning styles"""
        return list(self.STYLE_ADAPTATIONS.keys())
    
    def get_required_stages(self) -> list[Dict[str, Any]]:
        """Get the required 5-stage structure"""
        return self.REQUIRED_STAGES.copy()
    
    def validate_profile(self, learner_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize learner profile
        
        Args:
            learner_profile: Raw learner profile data
            
        Returns:
            Validated and normalized profile
        """
        validated = self.extract_learner_profile(learner_profile)
        
        # Validate level
        if validated['experience_level'] not in self.LEVEL_ADAPTATIONS:
            logger.warning(f"Invalid experience level: {validated['experience_level']}, defaulting to 'beginner'")
            validated['experience_level'] = 'beginner'
        
        # Validate style
        if validated['learning_style'] not in self.STYLE_ADAPTATIONS:
            logger.warning(f"Invalid learning style: {validated['learning_style']}, defaulting to 'visual'")
            validated['learning_style'] = 'visual'
        
        return validated
    
    def get_prompt_stats(self) -> Dict[str, Any]:
        """Get prompt builder statistics"""
        return {
            "supported_levels": len(self.LEVEL_ADAPTATIONS),
            "supported_styles": len(self.STYLE_ADAPTATIONS),
            "required_stages": len(self.REQUIRED_STAGES),
            "levels": list(self.LEVEL_ADAPTATIONS.keys()),
            "styles": list(self.STYLE_ADAPTATIONS.keys())
        }