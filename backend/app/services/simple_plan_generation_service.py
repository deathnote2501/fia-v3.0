"""
FIA v3.0 - Simple Plan Generation Service MVP
Service simplifié pour génération de plans personnalisés avec Vertex AI
"""

import logging
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
import asyncio
import time
from datetime import datetime, timezone

import google.generativeai as genai

from app.infrastructure.settings import settings

logger = logging.getLogger(__name__)


class PlanGenerationError(Exception):
    """Exception personnalisée pour la génération de plans"""
    def __init__(self, message: str, error_type: str = "generation_error", original_error: Optional[Exception] = None):
        super().__init__(message)
        self.error_type = error_type
        self.original_error = original_error


class DocumentProcessingError(PlanGenerationError):
    """Exception pour erreurs de traitement de documents"""
    def __init__(self, message: str, file_path: str, original_error: Optional[Exception] = None):
        super().__init__(message, "document_processing_error", original_error)
        self.file_path = file_path


class VertexAIError(PlanGenerationError):
    """Exception pour erreurs Vertex AI"""
    def __init__(self, message: str, api_response: Optional[str] = None, original_error: Optional[Exception] = None):
        super().__init__(message, "vertex_ai_error", original_error)
        self.api_response = api_response


class SimplePlanGenerationService:
    """Service simplifié pour génération de plans de formation personnalisés"""
    
    def __init__(self):
        """Initialiser le service de génération de plans avec configuration Vertex AI"""
        self.client = None
        self.model_name = settings.gemini_model_name
        self.max_retries = 3
        self.retry_delay = 2.0  # secondes
        self.fallback_enabled = True
        
        # Configuration logging structuré pour Gemini
        self.structured_logger = logging.getLogger(f"{__name__}.gemini_api")
        self.api_call_counter = 0
        
        # Configuration Vertex AI avec credentials
        self._configure_vertex_ai()
        
        logger.info(f"SimplePlanGenerationService initialized with model: {self.model_name}")
        logger.info(f"Error handling: max_retries={self.max_retries}, fallback_enabled={self.fallback_enabled}")
        logger.info(f"Structured logging configured for Gemini API calls")
    
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
            if self.fallback_enabled:
                logger.warning("⚠️ Falling back to mock mode")
                self.client = None
            else:
                raise PlanGenerationError(
                    "Failed to configure Vertex AI and fallback is disabled",
                    "configuration_error",
                    e
                )
    
    def _log_gemini_api_call(
        self,
        operation_type: str,
        request_data: Dict[str, Any],
        response_data: Dict[str, Any] = None,
        error_data: Dict[str, Any] = None,
        start_time: float = None,
        end_time: float = None,
        attempt_number: int = 1,
        success: bool = True
    ) -> None:
        """
        Logger structuré pour tous les appels à l'API Gemini
        
        Args:
            operation_type: Type d'opération (document_processing, plan_generation, file_upload)
            request_data: Données de la requête (sans contenu sensible)
            response_data: Données de la réponse (métadonnées uniquement)
            error_data: Données d'erreur si applicable
            start_time: Timestamp de début
            end_time: Timestamp de fin
            attempt_number: Numéro de tentative
            success: Si l'appel a réussi
        """
        self.api_call_counter += 1
        
        # Calculer la durée si timestamps fournis
        duration_ms = None
        if start_time and end_time:
            duration_ms = int((end_time - start_time) * 1000)
        
        # Structure du log Gemini API selon SPEC.md
        log_entry = {
            # Identification
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "call_id": f"gemini_call_{self.api_call_counter}",
            "operation_type": operation_type,
            "attempt_number": attempt_number,
            "success": success,
            
            # Configuration API
            "api_config": {
                "service": "gemini_flash_2.0",
                "model_name": self.model_name,
                "provider": "vertex_ai",
                "project": settings.google_cloud_project,
                "region": settings.google_cloud_region
            },
            
            # Métadonnées de requête (sans contenu sensible)
            "request_metadata": {
                **request_data,
                # Masquer le contenu des prompts pour le logging
                "prompt_length": len(str(request_data.get("prompt", ""))) if "prompt" in request_data else 0,
                "has_file_upload": "file_path" in request_data or "uploaded_file" in request_data,
                "request_size_estimate": len(json.dumps(request_data, default=str))
            },
            
            # Métadonnées de réponse
            "response_metadata": response_data or {},
            
            # Performance
            "performance": {
                "duration_ms": duration_ms,
                "retry_count": attempt_number - 1,
                "max_retries": self.max_retries
            },
            
            # Erreurs
            "error": error_data,
            
            # Contexte service
            "service_context": {
                "fallback_enabled": self.fallback_enabled,
                "environment": settings.environment
            }
        }
        
        # Log avec niveau approprié
        if success:
            self.structured_logger.info(
                f"GEMINI_API_CALL_SUCCESS: {operation_type}",
                extra={"gemini_api_call": log_entry}
            )
        else:
            self.structured_logger.error(
                f"GEMINI_API_CALL_ERROR: {operation_type}",
                extra={"gemini_api_call": log_entry}
            )
        
        # Log simplifié pour debugging
        status = "✅ SUCCESS" if success else "❌ ERROR"
        duration_str = f"({duration_ms}ms)" if duration_ms else ""
        
        logger.info(
            f"🤖 GEMINI API [{status}] {operation_type} "
            f"(attempt {attempt_number}/{self.max_retries}) {duration_str}"
        )
    
    async def _process_document(self, file_path: str) -> str:
        """
        Traiter le document PDF/PPT avec Gemini Document API et gestion d'erreurs robuste
        
        Args:
            file_path: Chemin vers le fichier PDF ou PowerPoint
            
        Returns:
            Contenu extrait du document
            
        Raises:
            DocumentProcessingError: Si le traitement échoue et fallback désactivé
        """
        for attempt in range(self.max_retries):
            try:
                file_path_obj = Path(file_path)
                
                # Vérifier que le fichier existe
                if not file_path_obj.exists():
                    raise DocumentProcessingError(
                        f"Training file not found: {file_path}",
                        file_path,
                        FileNotFoundError(f"File not found: {file_path}")
                    )
                
                # Vérifier la taille du fichier
                file_size = file_path_obj.stat().st_size
                max_size = 50 * 1024 * 1024  # 50MB
                if file_size > max_size:
                    raise DocumentProcessingError(
                        f"File too large: {file_size} bytes (max {max_size})",
                        file_path
                    )
                
                # Déterminer le MIME type
                file_extension = file_path_obj.suffix.lower()
                mime_type_map = {
                    '.pdf': 'application/pdf',
                    '.ppt': 'application/vnd.ms-powerpoint',
                    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
                }
                
                mime_type = mime_type_map.get(file_extension)
                if not mime_type:
                    raise DocumentProcessingError(
                        f"Unsupported file type: {file_extension}. Supported: PDF, PPT, PPTX",
                        file_path
                    )
                
                logger.info(f"Processing document: {file_path} (MIME: {mime_type}, Size: {file_size} bytes)")
                
                if self.client:
                    # Tentative de traitement avec Gemini
                    try:
                        logger.info(f"📄 Attempt {attempt + 1}/{self.max_retries} - Using Gemini Document API...")
                        
                        # Upload du fichier via File API avec retry
                        uploaded_file = await self._upload_file_to_gemini_with_retry(file_path, mime_type)
                        
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
                        
                        # Logging début appel
                        start_time = time.time()
                        request_data = {
                            "operation": "document_analysis",
                            "file_path": file_path,
                            "mime_type": mime_type,
                            "file_size": file_size,
                            "prompt": "document_analysis_prompt"
                        }
                        
                        # Appel avec timeout
                        response = await asyncio.wait_for(
                            asyncio.to_thread(
                                self.client.generate_content,
                                [uploaded_file, document_analysis_prompt]
                            ),
                            timeout=30.0  # 30 secondes timeout
                        )
                        
                        end_time = time.time()
                        
                        if response and response.text and len(response.text.strip()) > 10:
                            # Log succès
                            response_data = {
                                "response_length": len(response.text),
                                "response_preview": response.text[:100] + "..." if len(response.text) > 100 else response.text,
                                "usage_metadata": getattr(response, 'usage_metadata', None)
                            }
                            
                            self._log_gemini_api_call(
                                operation_type="document_processing",
                                request_data=request_data,
                                response_data=response_data,
                                start_time=start_time,
                                end_time=end_time,
                                attempt_number=attempt + 1,
                                success=True
                            )
                            
                            logger.info(f"✅ Document processed successfully via Gemini API (attempt {attempt + 1})")
                            return response.text.strip()
                        else:
                            # Log échec - réponse vide
                            error_data = {
                                "error_type": "empty_response",
                                "response_text": response.text if response else None
                            }
                            
                            self._log_gemini_api_call(
                                operation_type="document_processing",
                                request_data=request_data,
                                error_data=error_data,
                                start_time=start_time,
                                end_time=end_time,
                                attempt_number=attempt + 1,
                                success=False
                            )
                            
                            raise VertexAIError(
                                "Empty or invalid response from Gemini API",
                                response.text if response else None
                            )
                            
                    except asyncio.TimeoutError:
                        raise VertexAIError("Gemini API timeout after 30 seconds")
                    except Exception as api_error:
                        if attempt < self.max_retries - 1:
                            wait_time = self.retry_delay * (2 ** attempt)  # Backoff exponentiel
                            logger.warning(f"⚠️ Gemini API error (attempt {attempt + 1}): {api_error}")
                            logger.info(f"🔄 Retrying in {wait_time} seconds...")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            raise VertexAIError(
                                f"Gemini API failed after {self.max_retries} attempts",
                                None,
                                api_error
                            )
                else:
                    # Pas de client configuré
                    if self.fallback_enabled:
                        logger.info("📄 Using fallback document processing (no client)...")
                        return self._fallback_document_content(file_path)
                    else:
                        raise DocumentProcessingError(
                            "No Gemini client configured and fallback disabled",
                            file_path
                        )
                
            except (DocumentProcessingError, VertexAIError):
                # Re-raise nos exceptions personnalisées
                raise
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"⚠️ Unexpected error (attempt {attempt + 1}): {e}")
                    logger.info(f"🔄 Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    # Dernière tentative échouée
                    if self.fallback_enabled:
                        logger.warning(f"⚠️ All attempts failed, using fallback: {e}")
                        return self._fallback_document_content(file_path)
                    else:
                        raise DocumentProcessingError(
                            f"Document processing failed after {self.max_retries} attempts",
                            file_path,
                            e
                        )
        
        # Ce point ne devrait jamais être atteint
        if self.fallback_enabled:
            return self._fallback_document_content(file_path)
        else:
            raise DocumentProcessingError(
                "Unexpected error: retry loop completed without result",
                file_path
            )
    
    async def _upload_file_to_gemini_with_retry(self, file_path: str, mime_type: str):
        """Upload fichier vers Gemini File API avec retry"""
        for attempt in range(self.max_retries):
            try:
                # Pour le MVP, utiliser upload simple
                logger.info(f"📤 Uploading file to Gemini (attempt {attempt + 1}/{self.max_retries})...")
                
                # Upload avec timeout
                uploaded_file = await asyncio.wait_for(
                    asyncio.to_thread(genai.upload_file, file_path),
                    timeout=60.0  # 60 secondes pour upload
                )
                
                if uploaded_file:
                    logger.info(f"✅ File uploaded successfully to Gemini (attempt {attempt + 1})")
                    return uploaded_file
                else:
                    raise VertexAIError("File upload returned empty result")
                    
            except asyncio.TimeoutError:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"⚠️ File upload timeout (attempt {attempt + 1})")
                    logger.info(f"🔄 Retrying upload in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise VertexAIError("File upload timeout after multiple attempts")
                    
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"⚠️ File upload error (attempt {attempt + 1}): {e}")
                    logger.info(f"🔄 Retrying upload in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise VertexAIError(f"File upload failed after {self.max_retries} attempts", None, e)
    
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
    
    def _get_strict_json_schema(self) -> Dict[str, Any]:
        """
        Retourner le JSON schema strict pour les 5 étapes de formation
        
        Returns:
            Schema JSON strict pour validation Vertex AI
        """
        return {
            "type": "object",
            "properties": {
                "training_plan": {
                    "type": "object",
                    "properties": {
                        "stages": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "stage_number": {
                                        "type": "integer",
                                        "minimum": 1,
                                        "maximum": 5,
                                        "description": "Numéro d'étape (1-5)"
                                    },
                                    "stage_name": {
                                        "type": "string",
                                        "enum": [
                                            "Mise en contexte",
                                            "Acquisition des fondamentaux", 
                                            "Construction progressive",
                                            "Maîtrise",
                                            "Validation"
                                        ],
                                        "description": "Nom exact de l'étape"
                                    },
                                    "modules": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "module_name": {
                                                    "type": "string",
                                                    "minLength": 5,
                                                    "maxLength": 100,
                                                    "description": "Nom du module"
                                                },
                                                "submodules": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "submodule_name": {
                                                                "type": "string",
                                                                "minLength": 5,
                                                                "maxLength": 150,
                                                                "description": "Nom du sous-module"
                                                            },
                                                            "slide_count": {
                                                                "type": "integer",
                                                                "minimum": 2,
                                                                "maximum": 8,
                                                                "description": "Nombre de slides (2-8)"
                                                            }
                                                        },
                                                        "required": ["submodule_name", "slide_count"],
                                                        "additionalProperties": False
                                                    },
                                                    "minItems": 1,
                                                    "maxItems": 4,
                                                    "description": "1-4 sous-modules par module"
                                                }
                                            },
                                            "required": ["module_name", "submodules"],
                                            "additionalProperties": False
                                        },
                                        "minItems": 1,
                                        "maxItems": 3,
                                        "description": "1-3 modules par étape"
                                    }
                                },
                                "required": ["stage_number", "stage_name", "modules"],
                                "additionalProperties": False
                            },
                            "minItems": 5,
                            "maxItems": 5,
                            "description": "Exactement 5 étapes"
                        }
                    },
                    "required": ["stages"],
                    "additionalProperties": False
                }
            },
            "required": ["training_plan"],
            "additionalProperties": False
        }
    
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
            
            # Plan Generation avec prompt optimisé et gestion d'erreurs robuste
            return await self._generate_plan_with_fallback(learner_profile, document_content)
                
        except (DocumentProcessingError, VertexAIError) as e:
            logger.error(f"❌ {e.error_type}: {e}")
            if self.fallback_enabled:
                logger.info("🔄 Using fallback plan generation")
                return self._generate_mock_plan(learner_profile)
            else:
                raise PlanGenerationError(
                    f"Plan generation failed: {e}",
                    e.error_type,
                    e
                )
        except Exception as e:
            logger.error(f"❌ Unexpected error generating plan: {str(e)}")
            if self.fallback_enabled:
                logger.info("🔄 Using fallback plan generation")
                return self._generate_mock_plan(learner_profile)
            else:
                raise PlanGenerationError(
                    f"Unexpected error during plan generation: {e}",
                    "unexpected_error",
                    e
                )
    
    async def _generate_plan_with_fallback(self, learner_profile: Dict[str, Any], document_content: str) -> Dict[str, Any]:
        """
        Générer le plan avec gestion d'erreurs robuste et fallbacks
        """
        if not self.client:
            if self.fallback_enabled:
                logger.info("🤖 Using mock plan generation (no client configured)")
                return self._generate_mock_plan(learner_profile)
            else:
                raise VertexAIError("No Gemini client configured and fallback disabled")
        
        # Construire le prompt personnalisé
        personalized_prompt = self._build_personalized_prompt(learner_profile, document_content)
        logger.info("🧠 Generated personalized prompt")
        
        # Tentatives de génération avec retry
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🚀 Attempt {attempt + 1}/{self.max_retries} - Calling Gemini for plan generation...")
                
                # Configuration du modèle avec JSON schema strict
                json_schema = self._get_strict_json_schema()
                
                model = self.client.GenerativeModel(
                    model_name=self.model_name,
                    generation_config={
                        "temperature": 0.1,
                        "response_mime_type": "application/json",
                        "response_schema": json_schema
                    }
                )
                
                logger.info("📋 Using strict JSON schema for structured output")
                
                # Logging début appel
                start_time = time.time()
                request_data = {
                    "operation": "plan_generation",
                    "learner_profile": {
                        "experience_level": learner_profile.get('experience_level'),
                        "learning_style": learner_profile.get('learning_style'),
                        "job_position": learner_profile.get('job_position'),
                        "activity_sector": learner_profile.get('activity_sector')
                    },
                    "model_config": {
                        "temperature": 0.1,
                        "response_mime_type": "application/json",
                        "schema_validation": True
                    },
                    "prompt": "personalized_training_plan_prompt"
                }
                
                # Appel avec timeout
                response = await asyncio.wait_for(
                    asyncio.to_thread(model.generate_content, personalized_prompt),
                    timeout=45.0  # 45 secondes timeout
                )
                
                if response and response.text:
                    import json
                    # Parser la réponse JSON
                    try:
                        response_text = response.text.strip()
                        
                        # Nettoyer la réponse si nécessaire
                        if response_text.startswith('```json'):
                            response_text = response_text[7:]
                        if response_text.endswith('```'):
                            response_text = response_text[:-3]
                        response_text = response_text.strip()
                        
                        generated_plan = json.loads(response_text)
                        
                        # Validation stricte du schema généré
                        if self._validate_generated_plan(generated_plan):
                            end_time = time.time()
                            
                            # Log succès génération
                            response_data = {
                                "response_length": len(response.text),
                                "plan_structure": {
                                    "stages_count": len(generated_plan.get("training_plan", {}).get("stages", [])),
                                    "total_modules": sum(len(stage.get("modules", [])) for stage in generated_plan.get("training_plan", {}).get("stages", [])),
                                    "total_slides": sum(
                                        submodule.get("slide_count", 0)
                                        for stage in generated_plan.get("training_plan", {}).get("stages", [])
                                        for module in stage.get("modules", [])
                                        for submodule in module.get("submodules", [])
                                    )
                                },
                                "validation_status": "passed",
                                "usage_metadata": getattr(response, 'usage_metadata', None)
                            }
                            
                            self._log_gemini_api_call(
                                operation_type="plan_generation",
                                request_data=request_data,
                                response_data=response_data,
                                start_time=start_time,
                                end_time=end_time,
                                attempt_number=attempt + 1,
                                success=True
                            )
                            
                            logger.info(f"✅ Plan generated and validated successfully via Vertex AI (attempt {attempt + 1})")
                            return generated_plan
                        else:
                            end_time = time.time()
                            
                            # Log échec validation
                            error_data = {
                                "error_type": "validation_failed",
                                "validation_status": "failed",
                                "response_preview": response.text[:200] if response.text else None
                            }
                            
                            self._log_gemini_api_call(
                                operation_type="plan_generation",
                                request_data=request_data,
                                error_data=error_data,
                                start_time=start_time,
                                end_time=end_time,
                                attempt_number=attempt + 1,
                                success=False
                            )
                            
                            raise VertexAIError("Generated plan failed strict validation")
                            
                    except json.JSONDecodeError as e:
                        end_time = time.time()
                        
                        # Log erreur JSON
                        error_data = {
                            "error_type": "json_decode_error",
                            "json_error": str(e),
                            "response_preview": response.text[:500] if response.text else None
                        }
                        
                        self._log_gemini_api_call(
                            operation_type="plan_generation",
                            request_data=request_data,
                            error_data=error_data,
                            start_time=start_time,
                            end_time=end_time,
                            attempt_number=attempt + 1,
                            success=False
                        )
                        
                        raise VertexAIError(
                            f"Invalid JSON response from Vertex AI: {e}",
                            response.text[:500] if response.text else None
                        )
                else:
                    end_time = time.time()
                    
                    # Log réponse vide
                    error_data = {
                        "error_type": "empty_response",
                        "response_text": response.text if response else None
                    }
                    
                    self._log_gemini_api_call(
                        operation_type="plan_generation",
                        request_data=request_data,
                        error_data=error_data,
                        start_time=start_time,
                        end_time=end_time,
                        attempt_number=attempt + 1,
                        success=False
                    )
                    
                    raise VertexAIError("Empty response from Vertex AI")
                    
            except asyncio.TimeoutError:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"⚠️ Plan generation timeout (attempt {attempt + 1})")
                    logger.info(f"🔄 Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise VertexAIError("Plan generation timeout after multiple attempts")
                    
            except VertexAIError:
                # Re-raise VertexAIError
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"⚠️ Vertex AI error (attempt {attempt + 1})")
                    logger.info(f"🔄 Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise
                    
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"⚠️ Unexpected error (attempt {attempt + 1}): {e}")
                    logger.info(f"🔄 Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise VertexAIError(f"Plan generation failed after {self.max_retries} attempts", None, e)
        
        # Fallback si toutes les tentatives échouent
        if self.fallback_enabled:
            logger.warning("⚠️ All generation attempts failed, using mock plan")
            return self._generate_mock_plan(learner_profile)
        else:
            raise VertexAIError("Plan generation failed and fallback disabled")
    
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
    
    def _validate_generated_plan(self, plan: Dict[str, Any]) -> bool:
        """
        Valider strictement le plan généré selon les contraintes métier
        
        Args:
            plan: Plan généré à valider
            
        Returns:
            True si le plan est valide, False sinon
        """
        try:
            # Vérification structure de base
            if not isinstance(plan, dict) or "training_plan" not in plan:
                logger.error("❌ Missing 'training_plan' key")
                return False
            
            training_plan = plan["training_plan"]
            if not isinstance(training_plan, dict) or "stages" not in training_plan:
                logger.error("❌ Missing 'stages' key in training_plan")
                return False
            
            stages = training_plan["stages"]
            if not isinstance(stages, list):
                logger.error("❌ 'stages' must be a list")
                return False
            
            # Validation stricte: exactement 5 étapes
            if len(stages) != 5:
                logger.error(f"❌ Must have exactly 5 stages, got {len(stages)}")
                return False
            
            # Validation des noms d'étapes obligatoires
            required_stage_names = {
                1: "Mise en contexte",
                2: "Acquisition des fondamentaux", 
                3: "Construction progressive",
                4: "Maîtrise",
                5: "Validation"
            }
            
            found_stages = {}
            
            for stage in stages:
                if not isinstance(stage, dict):
                    logger.error("❌ Each stage must be a dict")
                    return False
                
                # Vérifier stage_number
                stage_number = stage.get("stage_number")
                if not isinstance(stage_number, int) or stage_number < 1 or stage_number > 5:
                    logger.error(f"❌ Invalid stage_number: {stage_number}")
                    return False
                
                # Vérifier stage_name correct
                stage_name = stage.get("stage_name")
                expected_name = required_stage_names[stage_number]
                if stage_name != expected_name:
                    logger.error(f"❌ Stage {stage_number} name '{stage_name}' != expected '{expected_name}'")
                    return False
                
                if stage_number in found_stages:
                    logger.error(f"❌ Duplicate stage_number: {stage_number}")
                    return False
                
                found_stages[stage_number] = stage_name
                
                # Vérifier modules
                modules = stage.get("modules", [])
                if not isinstance(modules, list) or len(modules) == 0:
                    logger.error(f"❌ Stage {stage_number} must have at least 1 module")
                    return False
                
                if len(modules) > 3:
                    logger.error(f"❌ Stage {stage_number} cannot have more than 3 modules")
                    return False
                
                # Vérifier chaque module
                for module in modules:
                    if not isinstance(module, dict):
                        logger.error("❌ Each module must be a dict")
                        return False
                    
                    if "module_name" not in module or not isinstance(module["module_name"], str):
                        logger.error("❌ Each module must have a string module_name")
                        return False
                    
                    if len(module["module_name"]) < 5:
                        logger.error("❌ Module name too short")
                        return False
                    
                    # Vérifier submodules
                    submodules = module.get("submodules", [])
                    if not isinstance(submodules, list) or len(submodules) == 0:
                        logger.error("❌ Each module must have at least 1 submodule")
                        return False
                    
                    if len(submodules) > 4:
                        logger.error("❌ Each module cannot have more than 4 submodules")
                        return False
                    
                    # Vérifier chaque sous-module
                    for submodule in submodules:
                        if not isinstance(submodule, dict):
                            logger.error("❌ Each submodule must be a dict")
                            return False
                        
                        if "submodule_name" not in submodule or not isinstance(submodule["submodule_name"], str):
                            logger.error("❌ Each submodule must have a string submodule_name")
                            return False
                        
                        if len(submodule["submodule_name"]) < 5:
                            logger.error("❌ Submodule name too short")
                            return False
                        
                        slide_count = submodule.get("slide_count")
                        if not isinstance(slide_count, int) or slide_count < 2 or slide_count > 8:
                            logger.error(f"❌ Invalid slide_count: {slide_count} (must be 2-8)")
                            return False
            
            # Vérifier que toutes les étapes sont présentes
            if set(found_stages.keys()) != {1, 2, 3, 4, 5}:
                missing = {1, 2, 3, 4, 5} - set(found_stages.keys())
                logger.error(f"❌ Missing stages: {missing}")
                return False
            
            logger.info("✅ Plan validation passed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Validation error: {e}")
            return False