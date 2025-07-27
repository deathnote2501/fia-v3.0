"""
FIA v3.0 - Plan Generation Service (Unified)
Service unifié pour génération de plans personnalisés avec Vertex AI
Intègre Context Caching et architecture ports/adapters
"""

import logging
import os
import json
from typing import Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import asyncio
import time
from datetime import datetime, timezone

from app.infrastructure.settings import settings

# Optional ports support for architecture hexagonale
if TYPE_CHECKING:
    from app.domain.ports.outbound_ports import GeminiServicePort, ContextCacheServicePort
    from app.domain.entities.learner_session import LearnerSession
    from app.domain.entities.training import Training

try:
    from app.domain.ports.outbound_ports import GeminiServicePort, ContextCacheServicePort
    from app.domain.entities.learner_session import LearnerSession
    from app.domain.entities.training import Training
    PORTS_AVAILABLE = True
except ImportError:
    # Interface flexible pour ports optionnels
    PORTS_AVAILABLE = False
    GeminiServicePort = None
    ContextCacheServicePort = None
    LearnerSession = None
    Training = None

# Configure logger first
logger = logging.getLogger(__name__)

# Import Vertex AI with error handling for environment issues
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, Part
    VERTEX_AI_AVAILABLE = True
    logger.info("🤖 VERTEX AI [MODULE] imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ VERTEX AI [MODULE] import failed: {e}")
    logger.warning("⚠️ VERTEX AI [MODULE] service will not be functional")
    VERTEX_AI_AVAILABLE = False
    # Define dummy classes to prevent import errors
    GenerativeModel = None
    Part = None


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


class PlanGenerationService:
    """Service unifié pour génération de plans de formation personnalisés avec Vertex AI et Context Caching"""
    
    # Message d'erreur standardisé pour tous les apprenants
    LEARNER_ERROR_MESSAGE = "Le service de génération de contenu est temporairement indisponible. Veuillez réessayer plus tard ou contacter votre formateur."
    
    def __init__(
        self,
        gemini_service: Optional["GeminiServicePort"] = None,
        cache_service: Optional["ContextCacheServicePort"] = None
    ):
        """
        Initialiser le service de génération de plans avec configuration Vertex AI
        
        Args:
            gemini_service: Service Gemini optionnel (pour architecture ports/adapters)
            cache_service: Service de cache optionnel (pour optimisation des coûts)
        """
        self.client = None
        self.model_name = settings.gemini_model_name
        self.max_retries = 3
        self.retry_delay = 2.0  # secondes
        
        # Support optionnel pour architecture ports/adapters
        self.gemini_service = gemini_service
        self.cache_service = cache_service
        
        # Configuration logging structuré pour Gemini
        self.structured_logger = logging.getLogger(f"{__name__}.gemini_api")
        self.api_call_counter = 0
        
        # Configuration Vertex AI avec credentials
        self.client = None
        self._configure_vertex_ai()
        
        logger.info(f"🤖 VERTEX AI [SERVICE] initialized with model: {self.model_name}")
        logger.info(f"🤖 VERTEX AI [CACHE] {'enabled' if self.cache_service else 'disabled'}")
        logger.info(f"🤖 VERTEX AI [PORTS] {'enabled' if PORTS_AVAILABLE else 'disabled'}")
        logger.info(f"🤖 VERTEX AI [CONFIG] max_retries={self.max_retries}, vertex_ai_only_mode")
        logger.info("🤖 VERTEX AI [LOGGING] structured logging configured for Gemini API calls")
    
    def _configure_vertex_ai(self):
        """Configurer Vertex AI avec les credentials appropriés"""
        try:
            # Vérifier que Vertex AI est disponible
            if not VERTEX_AI_AVAILABLE or vertexai is None:
                logger.warning("⚠️ VERTEX AI [CONFIG] Vertex AI module not available")
                self.client = None
                return
            
            # Configurer les credentials GCP
            if settings.google_credentials_json:
                # Utiliser les credentials JSON directement depuis les variables d'environnement
                import tempfile
                import json
                
                # Créer un fichier temporaire avec les credentials
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                    credentials_data = json.loads(settings.google_credentials_json)
                    json.dump(credentials_data, temp_file, indent=2)
                    temp_credentials_path = temp_file.name
                
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_credentials_path
                logger.info(f"🔑 VERTEX AI [CREDENTIALS] using GCP credentials from environment variables")
                
            elif settings.google_application_credentials:
                # Fallback: utiliser le fichier de credentials si spécifié
                project_root = Path(__file__).parent.parent.parent.parent
                credentials_path = project_root / settings.google_application_credentials
                
                if credentials_path.exists():
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path)
                    logger.info(f"🔑 VERTEX AI [CREDENTIALS] using GCP credentials from file: {credentials_path}")
                else:
                    logger.error(f"❌ VERTEX AI [CREDENTIALS] file not found: {credentials_path}")
                    raise PlanGenerationError(
                        f"Credentials file not found: {credentials_path}",
                        "missing_credentials_file",
                        None
                    )
            else:
                logger.warning("⚠️ VERTEX AI [CREDENTIALS] No credentials configured")
                raise PlanGenerationError(
                    "No Google Cloud credentials configured. Please set GOOGLE_CREDENTIALS_JSON or GOOGLE_APPLICATION_CREDENTIALS",
                    "missing_credentials",
                    None
                )
            
            # Initialiser Vertex AI
            if settings.google_cloud_project and settings.google_cloud_region:
                vertexai.init(
                    project=settings.google_cloud_project,
                    location=settings.google_cloud_region
                )
                
                # Créer le modèle
                self.client = GenerativeModel(model_name=self.model_name)
                
                self._log_vertex_ai_operation("config", "success", "configured successfully")
                logger.info(f"📍 VERTEX AI [PROJECT] {settings.google_cloud_project}")
                logger.info(f"🌍 VERTEX AI [REGION] {settings.google_cloud_region}")
                logger.info(f"🤖 Model: {self.model_name}")
                
            else:
                logger.error("❌ VERTEX AI [CONFIG] Missing GCP project/region configuration")
                raise PlanGenerationError(
                    "Missing Google Cloud configuration - service unavailable",
                    "missing_gcp_configuration",
                    None
                )
                
        except Exception as e:
            self._log_vertex_ai_operation("config", "error", f"Failed to configure: {e}", level="error")
            self._log_vertex_ai_operation("config", "warning", "Service will not be functional without Vertex AI", level="warning")
            self.client = None
    
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
        
        # Structure standardisée du log Gemini API selon SPEC.md
        log_entry = {
            # Identification standardisée
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "call_id": f"gemini_call_{self.api_call_counter}",
            "operation_type": operation_type,
            "attempt_number": attempt_number,
            "success": success,
            "service_type": "vertex_ai_gemini",
            
            # Configuration API standardisée  
            "api_config": {
                "service": "gemini_flash_2.0",
                "model_name": self.model_name,
                "provider": "vertex_ai",
                "project": settings.google_cloud_project,
                "region": settings.google_cloud_region,
                "version": "1.5"
            },
            
            # Métadonnées de requête (sécurisées - sans contenu sensible)
            "request_metadata": {
                **{k: v for k, v in request_data.items() if k not in ["prompt", "content", "file_data"]},
                # Métadonnées calculées de sécurité
                "prompt_length": len(str(request_data.get("prompt", ""))) if "prompt" in request_data else 0,
                "has_file_upload": "file_path" in request_data or "uploaded_file" in request_data,
                "request_size_estimate": len(json.dumps(request_data, default=str)),
                "has_sensitive_data": any(key in request_data for key in ["prompt", "content", "file_data"])
            },
            
            # Métadonnées de réponse standardisées
            "response_metadata": {
                **(response_data or {}),
                "response_type": "structured_json" if response_data else "unknown"
            },
            
            # Performance et fiabilité
            "performance": {
                "duration_ms": duration_ms,
                "retry_count": attempt_number - 1,
                "max_retries": self.max_retries,
                "success_rate": 1.0 if success else 0.0
            },
            
            # Gestion d'erreurs
            "error": error_data,
            
            # Contexte service standardisé
            "service_context": {
                "environment": getattr(settings, 'environment', 'unknown'),
                "service_version": "3.0",
                "logging_version": "1.0"
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
        
        # Log simplifié standardisé pour debugging
        status_emoji = "✅" if success else "❌"
        status_text = "SUCCESS" if success else "ERROR" 
        duration_str = f" {duration_ms}ms" if duration_ms else ""
        
        logger.info(
            f"🤖 GEMINI API [{status_emoji} {status_text}] {operation_type.upper()} "
            f"attempt {attempt_number}/{self.max_retries}{duration_str}"
        )
    
    def _log_vertex_ai_operation(
        self,
        operation: str,
        status: str,
        details: str = "",
        attempt: int = None,
        duration_ms: int = None,
        level: str = "info"
    ) -> None:
        """
        Logging centralisé pour toutes les opérations Vertex AI
        
        Args:
            operation: Type d'opération (config, processing, generation, etc.)
            status: Statut de l'opération (success, error, warning, attempt)
            details: Détails supplémentaires
            attempt: Numéro de tentative si applicable
            duration_ms: Durée en millisecondes si applicable
            level: Niveau de log (info, warning, error)
        """
        # Emojis standardisés par status
        emoji_map = {
            "success": "✅",
            "error": "❌", 
            "warning": "⚠️",
            "attempt": "🔄",
            "processing": "📄",
            "upload": "📤",
            "generation": "🚀"
        }
        
        # Format uniforme pour tous les logs Vertex AI
        emoji = emoji_map.get(status, "🤖")
        attempt_str = f" (attempt {attempt})" if attempt else ""
        duration_str = f" ({duration_ms}ms)" if duration_ms else ""
        
        log_message = f"{emoji} VERTEX AI [{operation.upper()}] {details}{attempt_str}{duration_str}"
        
        # Logger selon le niveau approprié
        if level == "error":
            logger.error(log_message)
        elif level == "warning":
            logger.warning(log_message)
        else:
            logger.info(log_message)
    
    async def _process_document(self, file_path: str) -> str:
        """
        Traiter le document PDF/PPT avec Gemini Document API et gestion d'erreurs robuste
        
        Args:
            file_path: Chemin vers le fichier PDF ou PowerPoint
            
        Returns:
            Contenu extrait du document
            
        Raises:
            DocumentProcessingError: Si le traitement échoue
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
                
                logger.info(f"📄 VERTEX AI [DOCUMENT] processing: {file_path} (MIME: {mime_type}, Size: {file_size} bytes)")
                
                if self.client:
                    # Tentative de traitement avec Gemini
                    try:
                        self._log_vertex_ai_operation("document_processing", "attempt", "Using Gemini Document API", attempt=attempt + 1)
                        
                        # Process du fichier pour Vertex AI avec retry
                        file_part = await self._upload_file_to_gemini_with_retry(file_path, mime_type)
                        
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
                        
                        # Appel avec timeout (Vertex AI)
                        response = await asyncio.wait_for(
                            asyncio.to_thread(
                                self.client.generate_content,
                                [file_part, document_analysis_prompt]  # File part + prompt
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
                            
                            self._log_vertex_ai_operation("document_processing", "success", "Document processed successfully via Gemini API", attempt=attempt + 1)
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
                            self._log_vertex_ai_operation("document_processing", "warning", f"Gemini API error: {api_error}", attempt=attempt + 1, level="warning")
                            logger.info(f"🔄 VERTEX AI [RETRY] retrying in {wait_time} seconds...")
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
                    raise DocumentProcessingError(
                        "No Gemini client configured",
                        file_path
                    )
                
            except (DocumentProcessingError, VertexAIError):
                # Re-raise nos exceptions personnalisées
                raise
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"⚠️ VERTEX AI [ERROR] unexpected error (attempt {attempt + 1}): {e}")
                    logger.info(f"🔄 VERTEX AI [RETRY] retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    # Dernière tentative échouée
                    raise DocumentProcessingError(
                        f"Document processing failed after {self.max_retries} attempts",
                        file_path,
                        e
                    )
        
        # Ce point ne devrait jamais être atteint
        raise DocumentProcessingError(
            "Unexpected error: retry loop completed without result",
            file_path
        )
    
    async def _upload_file_to_gemini_with_retry(self, file_path: str, mime_type: str):
        """Upload fichier vers Vertex AI avec retry"""
        for attempt in range(self.max_retries):
            try:
                # Pour le MVP, utiliser file input direct avec Vertex AI
                self._log_vertex_ai_operation("file_upload", "processing", "Processing file for Vertex AI", attempt=attempt + 1)
                
                # Avec Vertex AI, nous utilisons Part.from_uri ou Part.from_data
                # Pour simplifier, lire le fichier directement
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                # Créer un Part avec les données du fichier
                file_part = Part.from_data(data=file_data, mime_type=mime_type)
                
                if file_part:
                    self._log_vertex_ai_operation("file_upload", "success", "File processed successfully for Vertex AI", attempt=attempt + 1)
                    return file_part
                else:
                    raise VertexAIError("File processing returned empty result")
                    
            except asyncio.TimeoutError:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"⚠️ VERTEX AI [TIMEOUT] file upload timeout (attempt {attempt + 1})")
                    logger.info(f"🔄 VERTEX AI [RETRY] retrying upload in {wait_time} seconds...")
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
        "title": "Mise en contexte",
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
                                    "title": {
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
                                "required": ["stage_number", "title", "modules"],
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
            
            # Vérifier que Vertex AI est disponible
            if self.client is None:
                self._log_vertex_ai_operation("generation", "error", "Vertex AI client not available", level="error")
                raise PlanGenerationError(
                    self.LEARNER_ERROR_MESSAGE,
                    "vertex_ai_unavailable",
                    None
                )
            
            # Vérifier que le fichier existe
            if not Path(file_path).exists():
                raise FileNotFoundError(f"Training file not found: {file_path}")
            
            # Document Processing avec Gemini Document API
            document_content = await self._process_document(file_path)
            logger.info(f"📄 Document processed, content length: {len(document_content)} chars")
            
            # Plan Generation avec Vertex AI uniquement
            return await self._generate_plan_with_vertex_ai(learner_profile, document_content)
                
        except (DocumentProcessingError, VertexAIError) as e:
            logger.error(f"❌ {e.error_type}: {e}")
            raise PlanGenerationError(
                f"Plan generation failed: {e}",
                e.error_type,
                e
            )
        except Exception as e:
            logger.error(f"❌ Unexpected error generating plan: {str(e)}")
            raise PlanGenerationError(
                f"Unexpected error during plan generation: {e}",
                "unexpected_error",
                e
            )
    
    async def _generate_plan_with_vertex_ai(self, learner_profile: Dict[str, Any], document_content: str) -> Dict[str, Any]:
        """
        Générer le plan avec Vertex AI uniquement
        """
        if not self.client:
            raise VertexAIError("Vertex AI client not configured - service unavailable")
        
        # Construire le prompt personnalisé
        personalized_prompt = self._build_personalized_prompt(learner_profile, document_content)
        logger.info("🧠 Generated personalized prompt")
        
        # Tentatives de génération avec retry
        for attempt in range(self.max_retries):
            try:
                self._log_vertex_ai_operation("plan_generation", "generation", "Calling Gemini for plan generation", attempt=attempt + 1)
                
                # Configuration du modèle avec JSON schema strict
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
                
                # Appel avec timeout (Vertex AI)
                response = await asyncio.wait_for(
                    asyncio.to_thread(self.client.generate_content, personalized_prompt),
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
                            
                            self._log_vertex_ai_operation("plan_generation", "success", "Plan generated and validated successfully via Vertex AI", attempt=attempt + 1)
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
                    self._log_vertex_ai_operation("plan_generation", "warning", "Vertex AI error", attempt=attempt + 1, level="warning")
                    logger.info(f"🔄 Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise
                    
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"⚠️ VERTEX AI [ERROR] unexpected error (attempt {attempt + 1}): {e}")
                    logger.info(f"🔄 VERTEX AI [RETRY] retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise VertexAIError(f"Plan generation failed after {self.max_retries} attempts", None, e)
        
        # Toutes les tentatives ont échoué
        raise VertexAIError(f"Plan generation failed after {self.max_retries} attempts - service unavailable")
    
    
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
                
                # Vérifier title correct
                stage_title = stage.get("title")
                expected_name = required_stage_names[stage_number]
                if stage_title != expected_name:
                    logger.error(f"❌ Stage {stage_number} title '{stage_title}' != expected '{expected_name}'")
                    return False
                
                if stage_number in found_stages:
                    logger.error(f"❌ Duplicate stage_number: {stage_number}")
                    return False
                
                found_stages[stage_number] = stage_title
                
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
    
    # ==========================================
    # NOUVELLES FONCTIONNALITÉS INTÉGRÉES
    # ==========================================
    
    async def generate_personalized_plan_with_caching(
        self,
        learner_session: Optional["LearnerSession"],
        training: Optional["Training"],
        learner_profile: Optional[Dict[str, Any]] = None,
        file_path: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Génération de plan avec support optionnel pour Context Caching et architecture ports/adapters
        
        Cette méthode unifie l'ancienne API (avec file_path) et la nouvelle (avec entités domain)
        """
        try:
            # Compatibilité avec ancienne API (file_path + learner_profile dict)
            if learner_profile and file_path:
                return await self.generate_plan(learner_profile, file_path)
            
            # Nouvelle API avec entités domain et caching
            if not (learner_session and training):
                raise PlanGenerationError("Either (learner_profile + file_path) or (learner_session + training) required")
            
            logger.info(f"Generating personalized plan for learner: {learner_session.email}")
            logger.info(f"Training: {training.name}, Use cache: {use_cache}")
            
            # Construire le profil apprenant depuis l'entité
            learner_profile_dict = self._build_learner_profile(learner_session)
            
            # Déterminer le contenu de formation
            content_to_use = f"Training: {training.name}"
            if training.description:
                content_to_use += f"\nDescription: {training.description}"
            
            # Utiliser le cache si disponible et demandé
            cache_id = None
            if self.cache_service and use_cache and training.has_file():
                cache_id = await self._get_or_create_cache(training, content_to_use)
            
            # Si un cache est disponible, utiliser la génération avec cache
            if cache_id and self.cache_service:
                plan_data = await self._generate_with_cache(
                    training_file_path=training.file_path,
                    learner_profile=learner_profile_dict,
                    cache_id=cache_id
                )
            else:
                # Génération standard sans cache
                plan_data = await self.generate_plan(learner_profile_dict, training.file_path)
            
            # Validation et structuration du plan
            validated_plan = self._validate_plan_structure_domain(plan_data)
            
            logger.info(f"Successfully generated personalized plan with {len(validated_plan.get('stages', []))} stages")
            return validated_plan
            
        except Exception as e:
            logger.error(f"Error generating personalized plan: {str(e)}")
            raise PlanGenerationError(self.LEARNER_ERROR_MESSAGE)
    
    def _build_learner_profile(self, learner_session: "LearnerSession") -> Dict[str, Any]:
        """Construire le profil apprenant depuis l'entité domain - Pure domain logic"""
        if not PORTS_AVAILABLE or not learner_session:
            # Configuration minimale si entités domain non disponibles
            return {}
            
        return {
            "email": learner_session.email,
            "experience_level": learner_session.experience_level,
            "learning_style": learner_session.learning_style,
            "job_position": learner_session.job_position,
            "activity_sector": learner_session.activity_sector,
            "country": learner_session.country,
            "language": learner_session.language,
            "preferences": self._derive_learning_preferences(learner_session)
        }
    
    def _derive_learning_preferences(self, learner_session: "LearnerSession") -> Dict[str, str]:
        """Dériver les préférences d'apprentissage depuis le profil - Business logic"""
        if not PORTS_AVAILABLE or not learner_session:
            return {}
            
        preferences = {}
        
        # Adaptations selon niveau d'expérience
        if learner_session.experience_level == "beginner":
            preferences["complexity"] = "simple_explanations"
            preferences["pace"] = "slow_progression"
            preferences["support"] = "detailed_examples"
        elif learner_session.experience_level == "intermediate":
            preferences["complexity"] = "moderate_concepts"
            preferences["pace"] = "standard_progression"
            preferences["support"] = "practical_examples"
        else:  # advanced
            preferences["complexity"] = "advanced_concepts"
            preferences["pace"] = "fast_progression"
            preferences["support"] = "challenging_cases"
        
        # Adaptations selon style d'apprentissage
        style_adaptations = {
            "visual": "diagrams_charts_infographics",
            "auditory": "discussions_audio_explanations",
            "kinesthetic": "hands_on_exercises_practice",
            "reading": "text_documentation_articles"
        }
        preferences["preferred_content_type"] = style_adaptations.get(
            learner_session.learning_style, 
            "mixed_content"
        )
        
        return preferences
    
    async def _get_or_create_cache(self, training: "Training", content: str) -> Optional[str]:
        """Obtenir ou créer un cache pour le contenu de formation"""
        if not self.cache_service or not PORTS_AVAILABLE:
            return None
            
        try:
            # Essayer d'obtenir un cache existant basé sur le fichier de formation
            cache_key = f"training_{training.id}"
            existing_cache = await self.cache_service.get_cache(cache_key)
            
            if existing_cache:
                logger.info(f"Using existing cache for training {training.id}")
                return cache_key
            
            # Créer un nouveau cache
            cache_id = await self.cache_service.create_cache(
                content=content,
                ttl_hours=12  # Règle métier : 12 heures TTL par défaut
            )
            
            logger.info(f"Created new cache {cache_id} for training {training.id}")
            return cache_id
            
        except Exception as e:
            logger.warning(f"Cache service error, proceeding without cache: {str(e)}")
            return None
    
    async def _generate_with_cache(
        self,
        training_file_path: str,
        learner_profile: Dict[str, Any],
        cache_id: str
    ) -> Dict[str, Any]:
        """Générer un plan en utilisant le contenu mis en cache"""
        if not self.cache_service:
            raise PlanGenerationError(
                self.LEARNER_ERROR_MESSAGE,
                "cache_service_unavailable"
            )
        
        try:
            # Construire le prompt personnalisé
            document_content = f"[Contenu mis en cache pour {training_file_path}]"
            personalized_prompt = self._build_personalized_prompt(learner_profile, document_content)
            
            # Utiliser le contenu mis en cache
            response = await self.cache_service.use_cached_content(
                cache_id=cache_id,
                prompt=personalized_prompt,
                max_output_tokens=8192,
                temperature=0.1,
                top_p=0.95
            )
            
            if not response['success']:
                raise PlanGenerationError("Failed to generate content with cache")
            
            # Parser la réponse JSON
            import json
            plan_data = json.loads(response['content'])
            
            logger.info(f"Generated plan using cache. Tokens used: {response.get('usage_metadata', {})}")
            return plan_data
            
        except Exception as e:
            logger.error(f"Cache generation failed: {e}")
            raise PlanGenerationError(
                self.LEARNER_ERROR_MESSAGE,
                "cache_generation_failed",
                e
            )
    
    def _validate_plan_structure_domain(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valider la structure du plan selon les exigences métier domain"""
        if not isinstance(plan_data, dict):
            raise PlanGenerationError("Plan data must be a dictionary")
        
        if "training_plan" not in plan_data:
            raise PlanGenerationError("Plan must contain training_plan")
        
        training_plan = plan_data["training_plan"]
        if "stages" not in training_plan:
            raise PlanGenerationError("Plan must contain stages")
        
        stages = training_plan["stages"]
        if not isinstance(stages, list):
            raise PlanGenerationError("Stages must be a list")
        
        # Règle métier : Doit avoir exactement 5 étapes
        if len(stages) != 5:
            raise PlanGenerationError(f"Plan must have exactly 5 stages, got {len(stages)}")
        
        # Valider chaque étape
        required_stage_numbers = {1, 2, 3, 4, 5}
        found_stage_numbers = set()
        
        for stage in stages:
            if not isinstance(stage, dict):
                raise PlanGenerationError("Each stage must be a dictionary")
            
            if "stage_number" not in stage:
                raise PlanGenerationError("Each stage must have a stage_number")
            
            stage_number = stage["stage_number"]
            if stage_number not in required_stage_numbers:
                raise PlanGenerationError(f"Invalid stage number: {stage_number}")
            
            found_stage_numbers.add(stage_number)
            
            # Valider que l'étape a les champs requis
            required_fields = ["title", "modules"]
            for field in required_fields:
                if field not in stage:
                    raise PlanGenerationError(f"Stage {stage_number} missing required field: {field}")
            
            # Valider modules
            modules = stage["modules"]
            if not isinstance(modules, list) or len(modules) == 0:
                raise PlanGenerationError(f"Stage {stage_number} must have at least one module")
        
        # S'assurer que tous les numéros d'étapes sont présents
        if found_stage_numbers != required_stage_numbers:
            missing = required_stage_numbers - found_stage_numbers
            raise PlanGenerationError(f"Missing stage numbers: {missing}")
        
        logger.info("Plan structure validation passed (domain)")
        return plan_data
    
    async def generate_slide_content(
        self,
        slide_title: str,
        module_context: str,
        learner_session: Optional["LearnerSession"] = None,
        learner_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Générer le contenu pour une slide spécifique"""
        try:
            # Construire le profil apprenant
            if learner_session and PORTS_AVAILABLE:
                profile = self._build_learner_profile(learner_session)
            elif learner_profile:
                profile = learner_profile
            else:
                profile = {"experience_level": "intermediate", "learning_style": "visual"}
            
            # Si service Gemini disponible, l'utiliser
            if self.gemini_service and PORTS_AVAILABLE:
                slide_content = await self.gemini_service.generate_slide_content(
                    slide_title=slide_title,
                    module_context=module_context,
                    learner_profile=profile
                )
                logger.info(f"Generated slide content for: {slide_title}")
                return slide_content
            
            # Service indisponible
            self._log_vertex_ai_operation("slide_generation", "error", "Gemini service not available for slide content generation", level="error")
            raise PlanGenerationError(self.LEARNER_ERROR_MESSAGE)
            
        except Exception as e:
            logger.error(f"Error generating slide content: {str(e)}")
            raise PlanGenerationError(self.LEARNER_ERROR_MESSAGE)
    
    def get_stage_names(self) -> list[str]:
        """Obtenir les noms des 5 étapes standard - Règle métier"""
        return [
            "Mise en contexte",
            "Acquisition des fondamentaux", 
            "Construction progressive",
            "Maîtrise",
            "Validation"
        ]
    
    def get_stage_descriptions(self) -> Dict[int, str]:
        """Obtenir les descriptions des étapes standard - Règle métier"""
        return {
            1: "Introduction, enjeux et objectifs - Mise en contexte",
            2: "Concepts clés et théorie principale - Fondamentaux",
            3: "Mise en pratique et exercices - Application", 
            4: "Concepts avancés et cas complexes - Approfondissement",
            5: "Synthèse, évaluation et perspectives - Validation"
        }