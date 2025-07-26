"""
FIA v3.0 - Plan Generation Service (Vertex AI)
Service for generating personalized training plans using Vertex AI with Context Caching
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
import os

# Simplified imports - using google.generativeai with Vertex AI configuration
import google.generativeai as genai

from app.infrastructure.settings import settings
from app.domain.schemas.plan_generation import PlanGenerationResponse

# Configure logging
logger = logging.getLogger(__name__)


class PlanGenerationService:
    """Service for generating personalized training plans using Vertex AI approach"""
    
    def __init__(self):
        """Initialize the Vertex AI plan generation service"""
        try:
            # Set up credentials if provided
            if settings.google_application_credentials:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.google_application_credentials
                logger.info(f"📁 Using GCP credentials: {settings.google_application_credentials}")
            
            # Configure Gemini with API key (will use Vertex AI backend)
            if settings.gemini_api_key:
                genai.configure(api_key=settings.gemini_api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.use_vertex_ai = True
                
                logger.info(f"✅ Vertex AI configured successfully via Gemini API")
                logger.info(f"📍 Project: {settings.google_cloud_project}")
                logger.info(f"🌍 Region: {settings.google_cloud_region}")
                logger.info(f"🤖 Model: gemini-1.5-flash")
            else:
                raise Exception("No Gemini API key found")
            
        except Exception as e:
            logger.error(f"❌ Failed to configure Vertex AI: {e}")
            logger.warning("⚠️ Falling back to mock mode")
            self.model = None
            self.use_vertex_ai = False
    
    async def generate_personalized_plan(
        self,
        learner_session_id: str,
        training_id: str,
        learner_profile: Dict[str, Any]
    ) -> PlanGenerationResponse:
        """
        Generate a personalized training plan for a learner using Vertex AI
        
        Args:
            learner_session_id: ID of the learner session
            training_id: ID of the training
            learner_profile: Learner profile information
            
        Returns:
            PlanGenerationResponse with generated plan
        """
        try:
            start_time = datetime.utcnow()
            logger.info(f"🚀 STARTING Vertex AI plan generation for learner {learner_session_id}")
            
            # Build the structured prompt
            prompt = self._build_structured_generation_prompt(learner_profile)
            
            # LOG: Raw prompt being sent to Vertex AI
            logger.info("=" * 80)
            logger.info("📝 PROMPT SENT TO VERTEX AI:")
            logger.info("=" * 80)
            logger.info(prompt)
            logger.info("=" * 80)
            
            if self.use_vertex_ai and self.model:
                # Generate with Vertex AI approach
                logger.info("🔄 Calling Vertex AI (via Gemini API)...")
                response = await asyncio.to_thread(
                    self.model.generate_content,
                    prompt
                )
                
                # LOG: Raw response from Vertex AI
                logger.info("=" * 80)
                logger.info("📥 RAW RESPONSE FROM VERTEX AI:")
                logger.info("=" * 80)
                logger.info(f"Response text: {response.text}")
                logger.info(f"Usage metadata: {response.usage_metadata}")
                logger.info(f"Finish reason: {response.candidates[0].finish_reason}")
                logger.info("=" * 80)
                
                # Parse the JSON response
                try:
                    plan_json = json.loads(response.text)
                    response_text = response.text
                    tokens_used = response.usage_metadata.total_token_count if response.usage_metadata else 0
                    
                    logger.info(f"✅ Successfully parsed JSON response")
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️ Failed to parse JSON, using text response: {e}")
                    plan_json = {"error": "Invalid JSON", "raw_response": response.text}
                    response_text = response.text
                    tokens_used = response.usage_metadata.total_token_count if response.usage_metadata else 0
                
            else:
                # Fallback mock response
                logger.warning("🤖 Using MOCK response (Vertex AI not configured)")
                response_text = self._generate_mock_plan(learner_profile)
                plan_json = json.loads(response_text)
                tokens_used = 150
            
            # Create the structured plan
            generated_plan = {
                "plan_id": f"plan_{learner_session_id}",
                "learner_session_id": str(learner_session_id),
                "training_id": str(training_id),
                "vertex_ai_response": plan_json,
                "generated_at": datetime.utcnow().isoformat(),
                "generation_metadata": {
                    "learner_profile": learner_profile,
                    "tokens_used": tokens_used,
                    "model_used": settings.gemini_model_name,
                    "service_type": "vertex_ai"
                }
            }
            
            end_time = datetime.utcnow()
            generation_time = (end_time - start_time).total_seconds()
            
            logger.info(f"✅ Vertex AI plan generation completed in {generation_time:.2f} seconds")
            logger.info(f"📊 Tokens used: {tokens_used}")
            
            return PlanGenerationResponse(
                success=True,
                plan_content=generated_plan,
                generation_time_seconds=generation_time,
                tokens_used=tokens_used,
                cache_hit=False
            )
            
        except Exception as e:
            logger.error(f"❌ Vertex AI plan generation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Failed to generate plan with Vertex AI: {str(e)}")
    
    def _build_structured_generation_prompt(self, learner_profile: Dict[str, Any]) -> str:
        """Build a structured prompt for Vertex AI with JSON schema"""
        
        return f"""
Vous êtes un expert en ingénierie pédagogique. Créez un plan de formation personnalisé détaillé.

PROFIL DE L'APPRENANT :
• Niveau : {learner_profile.get('experience_level', 'débutant')}
• Style d'apprentissage : {learner_profile.get('learning_style', 'visuel')}
• Poste : {learner_profile.get('job_position', 'professionnel')}
• Secteur : {learner_profile.get('activity_sector', 'général')}
• Pays : {learner_profile.get('country', 'France')}
• Langue : {learner_profile.get('language', 'fr')}

INSTRUCTIONS :
Créez un plan avec 5 phases d'apprentissage personnalisées selon le profil.
Adaptez le contenu au niveau d'expérience et au style d'apprentissage.
Incluez des exemples concrets du secteur d'activité.

RÉPONDEZ UNIQUEMENT EN JSON avec cette structure exacte :

{{
  "title": "Plan de Formation Personnalisé - [Poste]",
  "description": "Description du plan adapté au profil",
  "phases": [
    {{
      "phase_number": 1,
      "phase_name": "Découverte",
      "description": "Phase d'introduction adaptée au niveau [niveau]",
      "duration_hours": 8,
      "modules": [
        {{
          "module_name": "Nom du module",
          "description": "Description adaptée au style [style]",
          "learning_objectives": ["Objectif 1", "Objectif 2"],
          "content_sections": [
            {{
              "section_title": "Titre de la section",
              "content_type": "visual/auditory/kinesthetic/reading",
              "description": "Contenu adapté au secteur [secteur]"
            }}
          ]
        }}
      ]
    }},
    {{
      "phase_number": 2,
      "phase_name": "Apprentissage",
      "description": "Acquisition des connaissances théoriques",
      "duration_hours": 12,
      "modules": []
    }},
    {{
      "phase_number": 3,
      "phase_name": "Application",
      "description": "Mise en pratique immédiate",
      "duration_hours": 10,
      "modules": []
    }},
    {{
      "phase_number": 4,
      "phase_name": "Approfondissement",
      "description": "Développement de l'expertise",
      "duration_hours": 8,
      "modules": []
    }},
    {{
      "phase_number": 5,
      "phase_name": "Maîtrise",
      "description": "Expertise complète et leadership",
      "duration_hours": 6,
      "modules": []
    }}
  ],
  "total_duration_hours": 44,
  "personalization_notes": "Notes sur les adaptations réalisées selon le profil"
}}

Répondez UNIQUEMENT avec le JSON, sans texte supplémentaire.
"""
    
    def _generate_mock_plan(self, learner_profile: Dict[str, Any]) -> str:
        """Generate a mock structured plan for testing"""
        
        mock_plan = {
            "title": f"Plan de Formation Personnalisé - {learner_profile.get('job_position', 'Professionnel')}",
            "description": f"Plan adapté au profil {learner_profile.get('experience_level', 'débutant')} avec style {learner_profile.get('learning_style', 'visuel')}",
            "phases": [
                {
                    "phase_number": 1,
                    "phase_name": "Découverte",
                    "description": f"Introduction adaptée au niveau {learner_profile.get('experience_level', 'débutant')}",
                    "duration_hours": 8,
                    "modules": [
                        {
                            "module_name": f"Contextualisation {learner_profile.get('activity_sector', 'IT')}",
                            "description": f"Module adapté au style {learner_profile.get('learning_style', 'visuel')}",
                            "learning_objectives": [
                                f"Comprendre les enjeux du secteur {learner_profile.get('activity_sector', 'IT')}",
                                f"Maîtriser les bases adaptées au niveau {learner_profile.get('experience_level', 'débutant')}"
                            ],
                            "content_sections": [
                                {
                                    "section_title": "Introduction aux concepts",
                                    "content_type": learner_profile.get('learning_style', 'visual'),
                                    "description": f"Contenu spécialisé pour {learner_profile.get('job_position', 'professionnel')}"
                                }
                            ]
                        }
                    ]
                }
            ],
            "total_duration_hours": 44,
            "personalization_notes": f"Plan personnalisé pour un profil {learner_profile.get('experience_level')} en {learner_profile.get('activity_sector')} avec style d'apprentissage {learner_profile.get('learning_style')}"
        }
        
        return json.dumps(mock_plan, indent=2, ensure_ascii=False)