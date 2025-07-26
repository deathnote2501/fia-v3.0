"""
FIA v3.0 - Simple Plan Generation Service
Simplified service for generating personalized training plans using Gemini
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

import google.generativeai as genai

from app.infrastructure.settings import settings
from app.domain.entities.learner_session import LearnerSession
from app.domain.entities.training import Training
from app.domain.schemas.plan_generation import PlanGenerationResponse

# Configure logging
logger = logging.getLogger(__name__)


class PlanGenerationService:
    """Simple service for generating personalized training plans"""
    
    def __init__(self):
        """Initialize the plan generation service"""
        try:
            # Try to get API key from settings
            api_key = getattr(settings, 'gemini_api_key', None)
            if api_key:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.use_real_api = True
                logger.info("✅ Gemini API configured with API key")
            else:
                # Fallback to mock mode if no API key
                self.model = None
                self.use_real_api = False
                logger.warning("⚠️ No Gemini API key found, using mock mode")
        except Exception as e:
            logger.error(f"❌ Failed to configure Gemini API: {e}")
            self.model = None
            self.use_real_api = False
    
    async def generate_personalized_plan(
        self,
        learner_session_id: str,
        training_id: str,
        learner_profile: Dict[str, Any]
    ) -> PlanGenerationResponse:
        """
        Generate a personalized training plan for a learner
        
        Args:
            learner_session_id: ID of the learner session
            training_id: ID of the training
            learner_profile: Learner profile information
            
        Returns:
            PlanGenerationResponse with generated plan
        """
        try:
            start_time = datetime.utcnow()
            logger.info(f"🚀 STARTING plan generation for learner {learner_session_id}")
            
            # Build the prompt
            prompt = self._build_generation_prompt(learner_profile)
            
            # LOG: Raw prompt being sent to Gemini
            logger.info("=" * 80)
            logger.info("📝 PROMPT SENT TO GEMINI:")
            logger.info("=" * 80)
            logger.info(prompt)
            logger.info("=" * 80)
            
            if self.use_real_api and self.model:
                # Generate with real Gemini API
                logger.info("🔄 Calling real Gemini API...")
                response = await asyncio.to_thread(
                    self.model.generate_content,
                    prompt
                )
                
                # LOG: Raw response from Gemini
                logger.info("=" * 80)
                logger.info("📥 RAW RESPONSE FROM GEMINI:")
                logger.info("=" * 80)
                logger.info(f"Response text: {response.text}")
                logger.info(f"Usage metadata: {getattr(response, 'usage_metadata', 'N/A')}")
                logger.info("=" * 80)
                
                response_text = response.text
                tokens_used = getattr(response, 'usage_metadata', {}).get('total_token_count', 0) if hasattr(response, 'usage_metadata') else 0
                
            else:
                # Mock response for testing
                logger.warning("🤖 Using MOCK Gemini response (no API key configured)")
                response_text = f"""
# Plan de Formation Personnalisé - {learner_profile.get('job_position', 'Professionnel')}

## Phase 1: DÉCOUVERTE
**Objectif**: Introduction aux concepts fondamentaux pour un profil {learner_profile.get('experience_level', 'débutant')} avec un style d'apprentissage {learner_profile.get('learning_style', 'visuel')}.

### Module 1.1: Contextualisation Métier
- Adaptation spécifique au secteur {learner_profile.get('activity_sector', 'IT')}
- Exemples concrets pour le poste {learner_profile.get('job_position', 'développeur')}

## Phase 2: APPRENTISSAGE
**Objectif**: Acquisition des compétences théoriques avec méthodes adaptées au style {learner_profile.get('learning_style', 'visuel')}.

### Module 2.1: Concepts Avancés
- Progression adaptée au niveau {learner_profile.get('experience_level', 'débutant')}
- Applications pratiques dans le contexte {learner_profile.get('country', 'France')}

## Phase 3: APPLICATION
**Objectif**: Mise en pratique immédiate avec exercices métier.

## Phase 4: APPROFONDISSEMENT  
**Objectif**: Développement de l'expertise spécialisée.

## Phase 5: MAÎTRISE
**Objectif**: Expertise complète et capacité à former d'autres.

*Plan généré automatiquement pour {learner_profile.get('email', 'apprenant')} - Langue: {learner_profile.get('language', 'fr')}*
"""
                
                logger.info("=" * 80)
                logger.info("📥 MOCK RESPONSE FROM GEMINI:")
                logger.info("=" * 80)
                logger.info(f"Response text: {response_text}")
                logger.info("=" * 80)
                
                tokens_used = 150  # Mock token count
            
            # Create structured plan based on Gemini response
            generated_plan = {
                "plan_id": f"plan_{learner_session_id}",
                "learner_session_id": str(learner_session_id),
                "training_id": str(training_id),
                "gemini_response": response_text,
                "phases": [
                    {
                        "phase_name": "Découverte",
                        "phase_order": 1,
                        "description": "Phase d'introduction adaptée au profil apprenant",
                        "modules": [
                            {
                                "module_name": f"Introduction personnalisée - {learner_profile['experience_level']}",
                                "module_order": 1,
                                "submodules": [
                                    {
                                        "submodule_name": f"Concepts adaptés au style {learner_profile['learning_style']}",
                                        "submodule_order": 1,
                                        "slides": [
                                            {
                                                "slide_title": f"Bienvenue {learner_profile['job_position']} - Formation personnalisée",
                                                "slide_order": 1,
                                                "content": response_text[:500] + "..." if len(response_text) > 500 else response_text
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "generated_at": datetime.utcnow().isoformat(),
                "generation_metadata": {
                    "learner_profile": learner_profile,
                    "tokens_used": tokens_used,
                    "model_used": "gemini-1.5-flash"
                }
            }
            
            end_time = datetime.utcnow()
            generation_time = (end_time - start_time).total_seconds()
            
            logger.info(f"✅ Plan generation completed in {generation_time:.2f} seconds")
            logger.info(f"📊 Plan structure: {len(generated_plan['phases'])} phases generated")
            
            return PlanGenerationResponse(
                success=True,
                plan_content=generated_plan,
                generation_time_seconds=generation_time,
                tokens_used=tokens_used,
                cache_hit=False
            )
            
        except Exception as e:
            logger.error(f"Plan generation failed: {str(e)}")
            raise Exception(f"Failed to generate plan: {str(e)}")
    
    def _build_generation_prompt(self, learner_profile: Dict[str, Any]) -> str:
        """Build the generation prompt for the learner"""
        
        # Adaptation selon le niveau d'expérience
        experience_adaptation = {
            'beginner': "Privilégiez des explications simples, beaucoup d'exemples concrets et une progression graduelle.",
            'intermediate': "Incluez des concepts avancés avec des applications pratiques et des études de cas.",
            'advanced': "Concentrez-vous sur des sujets complexes, l'innovation et le leadership dans le domaine."
        }
        
        # Adaptation selon le style d'apprentissage  
        style_adaptation = {
            'visual': "Intégrez des diagrammes, schémas, infographies et supports visuels dans chaque module.",
            'auditory': "Prévoyez des podcasts, discussions, présentations orales et exercices d'écoute.",
            'kinesthetic': "Incluez des exercices pratiques, simulations, ateliers hands-on et projets concrets.",
            'reading': "Proposez des lectures approfondies, articles, études de cas écrites et résumés détaillés."
        }
        
        experience_text = experience_adaptation.get(learner_profile.get('experience_level', 'beginner'), experience_adaptation['beginner'])
        style_text = style_adaptation.get(learner_profile.get('learning_style', 'visual'), style_adaptation['visual'])
        
        return f"""
Vous êtes un expert en ingénierie pédagogique et IA. Créez un plan de formation personnalisé détaillé en français.

PROFIL DE L'APPRENANT :
━━━━━━━━━━━━━━━━━━━━━━━
• Niveau d'expérience : {learner_profile.get('experience_level', 'débutant')}
• Style d'apprentissage : {learner_profile.get('learning_style', 'visuel')}  
• Poste/Métier : {learner_profile.get('job_position', 'non spécifié')}
• Secteur d'activité : {learner_profile.get('activity_sector', 'non spécifié')}
• Pays : {learner_profile.get('country', 'France')}
• Langue : {learner_profile.get('language', 'fr')}

INSTRUCTIONS DE PERSONNALISATION :
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Niveau d'expérience : {experience_text}

🧠 Style d'apprentissage : {style_text}

💼 Contexte professionnel : Adaptez tous les exemples et cas d'usage au poste "{learner_profile.get('job_position', 'professionnel')}" dans le secteur "{learner_profile.get('activity_sector', 'général')}".

STRUCTURE DEMANDÉE :
━━━━━━━━━━━━━━━━━━━━
Créez un plan avec exactement 5 phases d'apprentissage :

📚 Phase 1 : DÉCOUVERTE
- Introduction aux concepts fondamentaux
- Contextualisation pour le secteur spécifique
- Motivation et objectifs personnalisés

🎓 Phase 2 : APPRENTISSAGE  
- Acquisition des connaissances théoriques
- Méthodes adaptées au style d'apprentissage
- Concepts clés avec exemples métier

⚡ Phase 3 : APPLICATION
- Mise en pratique immédiate
- Exercices concrets liés au poste
- Projets adaptés au niveau

🔬 Phase 4 : APPROFONDISSEMENT
- Concepts avancés et spécialisés
- Analyse de cas complexes du secteur
- Développement de l'expertise

🏆 Phase 5 : MAÎTRISE
- Synthèse et expertise complète
- Capacité à former d'autres
- Innovation et leadership

Pour chaque phase, détaillez :
- Objectifs pédagogiques spécifiques
- Modules et sous-modules
- Méthodes pédagogiques adaptées au style d'apprentissage
- Exemples concrets du secteur d'activité
- Durée estimée et progression

Répondez en français avec un ton professionnel et motivant.
"""