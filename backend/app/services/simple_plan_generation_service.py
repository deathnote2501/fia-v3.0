"""
FIA v3.0 - Simple Plan Generation Service MVP
Service simplifié pour génération de plans personnalisés avec Vertex AI
"""

import logging
import os
from typing import Dict, Any, Optional
from pathlib import Path

import google.generativeai as genai

from app.infrastructure.settings import settings

logger = logging.getLogger(__name__)


class SimplePlanGenerationService:
    """Service simplifié pour génération de plans de formation personnalisés"""
    
    def __init__(self):
        """Initialiser le service de génération de plans avec configuration Vertex AI"""
        self.client = None
        self.model_name = settings.gemini_model_name
        
        # Configuration Vertex AI avec credentials
        self._configure_vertex_ai()
        
        logger.info(f"SimplePlanGenerationService initialized with model: {self.model_name}")
    
    def _configure_vertex_ai(self):
        """Configurer Vertex AI avec les credentials appropriés"""
        try:
            # Configurer les credentials GCP si fournis
            if settings.google_application_credentials:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.google_application_credentials
                logger.info(f"Using GCP credentials from: {settings.google_application_credentials}")
            
            # Configurer le client Vertex AI
            if settings.gemini_api_key:
                genai.configure(api_key=settings.gemini_api_key)
                
                # Configurer pour Vertex AI
                self.client = genai
                
                logger.info(f"✅ Vertex AI configured successfully")
                logger.info(f"📍 Project: {settings.google_cloud_project}")
                logger.info(f"🌍 Region: {settings.google_cloud_region}")
                logger.info(f"🤖 Model: {self.model_name}")
                
            else:
                logger.warning("⚠️ No Gemini API key found - service will use mock responses")
                
        except Exception as e:
            logger.error(f"❌ Failed to configure Vertex AI: {e}")
            logger.warning("⚠️ Falling back to mock mode")
            self.client = None
    
    async def _process_document(self, file_path: str) -> str:
        """
        Traiter le document PDF/PPT avec Gemini Document API
        
        Args:
            file_path: Chemin vers le fichier PDF ou PowerPoint
            
        Returns:
            Contenu extrait du document
        """
        try:
            file_path_obj = Path(file_path)
            
            # Vérifier que le fichier existe
            if not file_path_obj.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Déterminer le MIME type
            file_extension = file_path_obj.suffix.lower()
            mime_type_map = {
                '.pdf': 'application/pdf',
                '.ppt': 'application/vnd.ms-powerpoint',
                '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }
            
            mime_type = mime_type_map.get(file_extension)
            if not mime_type:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            logger.info(f"Processing document: {file_path} (MIME: {mime_type})")
            
            if self.client:
                # Utiliser Gemini Document API pour traitement intelligent
                logger.info("📄 Using Gemini Document API for processing...")
                
                # Upload du fichier via File API
                uploaded_file = await self._upload_file_to_gemini(file_path, mime_type)
                
                # Analyse du document avec prompt spécialisé
                document_analysis_prompt = """
                Analyse ce document de formation et extrais les informations clés :
                
                1. Sujet principal et objectifs
                2. Concepts clés abordés
                3. Structure du contenu (chapitres, sections)
                4. Niveau de complexité apparent
                5. Exemples ou cas pratiques mentionnés
                
                Fournis un résumé structuré du contenu de formation.
                """
                
                # Utiliser l'API classique pour l'instant
                response = self.client.generate_content([uploaded_file, document_analysis_prompt])
                
                if response and response.text:
                    logger.info(f"✅ Document processed successfully via Gemini API")
                    return response.text
                else:
                    logger.warning("⚠️ Empty response from Gemini API")
                    return self._fallback_document_content(file_path)
                    
            else:
                # Fallback: contenu basique basé sur le nom du fichier
                logger.info("📄 Using fallback document processing...")
                return self._fallback_document_content(file_path)
                
        except Exception as e:
            logger.error(f"❌ Error processing document {file_path}: {e}")
            return self._fallback_document_content(file_path)
    
    async def _upload_file_to_gemini(self, file_path: str, mime_type: str):
        """Upload fichier vers Gemini File API"""
        try:
            # Lire le fichier en bytes
            file_data = Path(file_path).read_bytes()
            
            # Pour le MVP, utiliser upload simple
            logger.info("📤 Uploading file to Gemini...")
            uploaded_file = genai.upload_file(file_path)
            return uploaded_file
                
        except Exception as e:
            logger.error(f"❌ Error uploading file to Gemini: {e}")
            raise
    
    def _fallback_document_content(self, file_path: str) -> str:
        """Contenu de fallback basé sur le nom du fichier"""
        file_name = Path(file_path).stem
        return f"""
        Document de formation: {file_name}
        
        Contenu simulé pour le développement:
        - Formation sur les concepts fondamentaux
        - Modules théoriques et pratiques
        - Exercices d'application
        - Évaluation des acquis
        
        Note: Ce contenu est généré automatiquement en mode fallback.
        La vraie analyse du document nécessite une configuration Vertex AI valide.
        """
    
    def _build_personalized_prompt(self, learner_profile: Dict[str, Any], document_content: str) -> str:
        """
        Construire un prompt personnalisé optimisé selon les prompting strategies
        
        Args:
            learner_profile: Profil de l'apprenant
            document_content: Contenu extrait du document
            
        Returns:
            Prompt optimisé pour génération de plan personnalisé
        """
        # Extraction des informations du profil
        level = learner_profile.get('experience_level', 'débutant')
        style = learner_profile.get('learning_style', 'visuel') 
        job = learner_profile.get('job_position', 'professionnel')
        sector = learner_profile.get('activity_sector', 'général')
        country = learner_profile.get('country', 'France')
        
        # Adaptations selon le niveau d'expérience
        level_adaptations = {
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
        
        # Adaptations selon le style d'apprentissage
        style_adaptations = {
            'visual': 'diagrammes, schémas, infographies et supports visuels',
            'auditory': 'discussions, présentations orales et explications audio',
            'kinesthetic': 'exercices pratiques, manipulations et activités hands-on',
            'reading': 'textes détaillés, documentation et ressources écrites'
        }
        
        # Récupérer les adaptations appropriées
        level_config = level_adaptations.get(level, level_adaptations['beginner'])
        style_preference = style_adaptations.get(style, style_adaptations['visual'])
        
        # Construire le prompt avec few-shot examples et contraintes claires
        prompt = f"""Tu es un expert en ingénierie pédagogique spécialisé dans la création de plans de formation personnalisés.

PROFIL DE L'APPRENANT:
- Niveau d'expérience: {level}
- Style d'apprentissage: {style}
- Poste occupé: {job}
- Secteur d'activité: {sector}
- Pays: {country}

CONTENU DU DOCUMENT DE FORMATION:
{document_content}

CONSIGNES DE PERSONNALISATION:
1. Adapte la complexité: {level_config['complexity']}
2. Rythme de progression: {level_config['pace']}
3. Nombre de slides: {level_config['slides_per_concept']}
4. Type de contenu privilégié: {style_preference}
5. Exemples à utiliser: {level_config['examples']} du secteur {sector}

STRUCTURE OBLIGATOIRE - EXACTEMENT 5 ÉTAPES:
Étape 1: "Mise en contexte" - Introduction, enjeux et objectifs
Étape 2: "Acquisition des fondamentaux" - Concepts de base essentiels
Étape 3: "Construction progressive" - Approfondissement par étapes
Étape 4: "Maîtrise" - Approfondissement et pratique autonome
Étape 5: "Validation" - Évaluation finale et consolidation

EXEMPLE DE STRUCTURE ATTENDUE:
{{
  "training_plan": {{
    "stages": [
      {{
        "stage_number": 1,
        "stage_name": "Mise en contexte",
        "modules": [
          {{
            "module_name": "Introduction au domaine",
            "submodules": [
              {{
                "submodule_name": "Présentation des enjeux",
                "slide_count": 4
              }}
            ]
          }}
        ]
      }}
    ]
  }}
}}

CONTRAINTES STRICTES:
- Réponds UNIQUEMENT en JSON valide
- Exactement 5 stages numérotés de 1 à 5
- Chaque stage contient 1-3 modules
- Chaque module contient 1-4 sous-modules
- Chaque sous-module a un slide_count entre 2 et 8
- Adapte le contenu au profil {level}/{style}/{sector}
- Utilise des exemples concrets du secteur {sector}
- Privilégie le style d'apprentissage {style}

INSTRUCTION FINALE:
Crée maintenant un plan de formation personnalisé en JSON qui respecte exactement cette structure et ces contraintes."""
        
        return prompt
    
    async def generate_plan(self, learner_profile: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """
        Générer un plan de formation personnalisé
        
        Args:
            learner_profile: Profil de l'apprenant avec niveau, style, poste, secteur
            file_path: Chemin vers le fichier PDF/PPT de formation
            
        Returns:
            Plan de formation structuré en JSON
        """
        try:
            logger.info(f"Generating plan for profile: {learner_profile.get('experience_level', 'unknown')}")
            logger.info(f"Using training file: {file_path}")
            
            # Vérifier que le fichier existe
            if not Path(file_path).exists():
                raise FileNotFoundError(f"Training file not found: {file_path}")
            
            # Document Processing avec Gemini Document API
            document_content = await self._process_document(file_path)
            logger.info(f"📄 Document processed, content length: {len(document_content)} chars")
            
            # Plan Generation avec prompt optimisé
            if self.client:
                # Construire le prompt personnalisé
                personalized_prompt = self._build_personalized_prompt(learner_profile, document_content)
                logger.info("🧠 Generated personalized prompt")
                
                try:
                    # Appel Gemini avec prompt optimisé (version simplifiée pour MVP)
                    logger.info("🚀 Calling Gemini for plan generation...")
                    
                    # Configuration du modèle pour JSON
                    model = self.client.GenerativeModel(
                        model_name=self.model_name,
                        generation_config={
                            "temperature": 0.1,
                            "response_mime_type": "application/json"
                        }
                    )
                    
                    response = model.generate_content(personalized_prompt)
                    
                    if response and response.text:
                        import json
                        # Parser la réponse JSON
                        try:
                            generated_plan = json.loads(response.text)
                            logger.info("✅ Plan generated successfully via Vertex AI")
                            return generated_plan
                        except json.JSONDecodeError as e:
                            logger.warning(f"⚠️ Invalid JSON response from Vertex AI: {e}")
                            logger.warning(f"Raw response: {response.text[:500]}...")
                            # Fallback sur plan mock
                            return self._generate_mock_plan(learner_profile)
                    else:
                        logger.warning("⚠️ Empty response from Vertex AI")
                        return self._generate_mock_plan(learner_profile)
                        
                except Exception as e:
                    logger.error(f"❌ Error calling Vertex AI: {e}")
                    return self._generate_mock_plan(learner_profile)
            else:
                logger.info("🤖 Using mock plan generation (Vertex AI not configured)")
                return self._generate_mock_plan(learner_profile)
                
        except Exception as e:
            logger.error(f"❌ Error generating plan: {str(e)}")
            return self._generate_mock_plan(learner_profile)
    
    def _generate_mock_plan(self, learner_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Générer un plan mock personnalisé pour fallback"""
        level = learner_profile.get('experience_level', 'débutant')
        style = learner_profile.get('learning_style', 'visuel')
        sector = learner_profile.get('activity_sector', 'général')
        
        # Adaptation du nombre de slides selon le niveau
        slide_counts = {
            'beginner': [5, 6, 5, 4, 3],
            'intermediate': [4, 4, 4, 3, 2], 
            'advanced': [3, 3, 3, 2, 2]
        }
        slides = slide_counts.get(level, slide_counts['beginner'])
        
        mock_plan = {
            "training_plan": {
                "stages": [
                    {
                        "stage_number": 1,
                        "stage_name": "Mise en contexte",
                        "modules": [
                            {
                                "module_name": f"Introduction pour {level} en {sector}",
                                "submodules": [
                                    {
                                        "submodule_name": f"Contextualisation {sector} - style {style}",
                                        "slide_count": slides[0]
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "stage_number": 2,
                        "stage_name": "Acquisition des fondamentaux",
                        "modules": [
                            {
                                "module_name": f"Concepts de base adaptés niveau {level}",
                                "submodules": [
                                    {
                                        "submodule_name": f"Théorie fondamentale - {style}",
                                        "slide_count": slides[1]
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "stage_number": 3,
                        "stage_name": "Construction progressive", 
                        "modules": [
                            {
                                "module_name": f"Approfondissement progressif {level}",
                                "submodules": [
                                    {
                                        "submodule_name": f"Application pratique {sector}",
                                        "slide_count": slides[2]
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "stage_number": 4,
                        "stage_name": "Maîtrise",
                        "modules": [
                            {
                                "module_name": f"Pratique autonome niveau {level}",
                                "submodules": [
                                    {
                                        "submodule_name": f"Exercices avancés {sector}",
                                        "slide_count": slides[3]
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "stage_number": 5,
                        "stage_name": "Validation",
                        "modules": [
                            {
                                "module_name": "Évaluation finale",
                                "submodules": [
                                    {
                                        "submodule_name": f"Assessment {level}",
                                        "slide_count": slides[4]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        
        logger.info(f"Generated mock plan for {level}/{style}/{sector}")
        return mock_plan