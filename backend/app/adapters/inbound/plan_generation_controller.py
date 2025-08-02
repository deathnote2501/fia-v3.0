"""
FIA v3.0 - Integrated Plan Generation Controller
Controller avec intégration base de données complète pour génération de plans
"""

import logging
import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from app.schemas.plan_schemas import (
    PlanGenerationRequest,
    PlanGenerationResponse,
    ErrorResponse,
    TrainingPlanSchema,
    PlanValidationResult,
    ValidationErrorDetail
)
from app.domain.services.integrated_plan_generation_service import IntegratedPlanGenerationService
from app.adapters.repositories.learner_training_plan_repository import LearnerTrainingPlanRepository
from app.adapters.repositories.api_log_repository import ApiLogRepository
from app.adapters.repositories.learner_session_repository import LearnerSessionRepository
from app.domain.services.plan_generation_service_v2 import PlanGenerationError
from app.adapters.outbound.settings_adapter import SettingsAdapter
from app.domain.services.document_processor import DocumentProcessingError
from app.infrastructure.adapters.vertex_ai_adapter import VertexAIError
from app.infrastructure.database import get_async_session
from app.infrastructure.models.training_model import TrainingModel

logger = logging.getLogger(__name__)

# Router pour les endpoints de génération de plans intégrés
router = APIRouter(prefix="/api", tags=["Integrated Plan Generation"])


async def get_integrated_plan_generation_service(
    session: AsyncSession = Depends(get_async_session)
) -> IntegratedPlanGenerationService:
    """Dependency pour obtenir le service de génération de plans intégré"""
    # Créer les repositories
    plan_repository = LearnerTrainingPlanRepository(session)
    api_log_repository = ApiLogRepository(session)
    
    # Créer le service intégré avec la session DB
    return IntegratedPlanGenerationService(
        plan_repository=plan_repository,
        api_log_repository=api_log_repository,
        db_session=session
    )


@router.post(
    "/generate-plan-integrated",
    response_model=PlanGenerationResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse}, 
        500: {"model": ErrorResponse}
    },
    summary="Générer un plan de formation personnalisé avec persistance DB",
    description="Génère un plan de formation personnalisé basé sur le profil apprenant et le contenu de formation, avec sauvegarde en base de données"
)
async def generate_plan_integrated(
    request: PlanGenerationRequest,
    session: AsyncSession = Depends(get_async_session),
    integrated_service: IntegratedPlanGenerationService = Depends(get_integrated_plan_generation_service)
) -> PlanGenerationResponse:
    """
    Générer un plan de formation personnalisé avec intégration base de données
    
    Args:
        request: Requête avec training_id et profil apprenant
        session: Session base de données
        integrated_service: Service de génération intégré
        
    Returns:
        Plan de formation structuré en 5 étapes avec métadonnées de persistance
    """
    try:
        logger.info(f"🚀 Starting integrated plan generation for training {request.training_id}")
        logger.info(f"👤 Learner profile: {request.learner_profile.experience_level}/{request.learner_profile.learning_style}")
        
        # Récupérer la formation depuis la base de données
        training = await session.get(TrainingModel, request.training_id)
        if not training:
            logger.warning(f"❌ Training not found: {request.training_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Training with ID {request.training_id} not found"
            )
        
        # Vérifier que le fichier de formation existe
        if not training.file_path:
            logger.warning(f"❌ No file associated with training {request.training_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No training file associated with this training"
            )
        
        # Résoudre le chemin complet du fichier de formation
        from app.domain.services.file_storage_service import FileStorageService
        settings_adapter = SettingsAdapter()
        file_storage = FileStorageService(settings_adapter)
        full_file_path = await file_storage.get_training_file_path(training.file_path)
        
        # Vérifier que le fichier existe
        if not full_file_path.exists():
            logger.warning(f"❌ Training file not found: {full_file_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Training file not found: {training.file_path}"
            )
        
        logger.info(f"📄 Using training file: {full_file_path}")
        
        # Utiliser l'ID de session apprenant fourni dans la requête
        learner_session_id = request.learner_session_id
        logger.info(f"👤 Using learner session ID: {learner_session_id}")
        
        # Convertir le profil Pydantic en dictionnaire
        learner_profile_dict = {
            "experience_level": request.learner_profile.experience_level,
            "learning_style": request.learner_profile.learning_style,
            "job_position": request.learner_profile.job_position,
            "activity_sector": request.learner_profile.activity_sector,
            "country": request.learner_profile.country,
            "language": request.learner_profile.language
        }
        
        # Générer et persister le plan avec le service intégré
        persisted_plan = await integrated_service.generate_and_persist_plan(
            learner_session_id=learner_session_id,
            learner_profile=learner_profile_dict,
            file_path=str(full_file_path),
            force_regenerate=request.force_regenerate
        )
        
        # Validation stricte côté backend avec Pydantic
        try:
            # Valider la structure du plan généré
            if "training_plan" not in persisted_plan.plan_data:
                logger.error("❌ Invalid plan structure: missing 'training_plan' key")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Invalid plan structure generated"
                )
            
            # Validation Pydantic stricte avec mapping des champs
            training_plan_data = persisted_plan.plan_data["training_plan"]
            
            # Mapper stage_name vers title si nécessaire (compatibilité avec ancien format)
            for stage in training_plan_data.get("stages", []):
                if "stage_name" in stage and "title" not in stage:
                    stage["title"] = stage.pop("stage_name")
            
            validated_plan = TrainingPlanSchema(**training_plan_data)
            
            logger.info("✅ Plan passed Pydantic validation successfully")
            
            # Convertir back to dict pour la réponse
            training_plan_data = validated_plan.dict()
            
        except ValidationError as e:
            logger.error(f"❌ Plan validation failed: {e}")
            
            # Créer détails d'erreurs pour debugging
            validation_errors = []
            for error in e.errors():
                validation_errors.append(ValidationErrorDetail(
                    field='.'.join(str(x) for x in error['loc']),
                    message=error['msg'],
                    invalid_value=error.get('input', 'unknown')
                ))
            
            # Retourner erreur structurée
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error_type": "validation_error",
                    "error_message": "Generated plan failed strict validation",
                    "validation_errors": [err.dict() for err in validation_errors]
                }
            )
        
        # Calculer les métadonnées enrichies
        total_stages = persisted_plan.get_stage_count()
        total_modules = sum(len(stage.get("modules", [])) for stage in training_plan_data.get("stages", []))
        total_submodules = sum(
            len(module.get("submodules", [])) 
            for stage in training_plan_data.get("stages", [])
            for module in stage.get("modules", [])
        )
        total_slides = persisted_plan.get_total_slides()
        
        generation_metadata = {
            "training_id": str(request.training_id),
            "training_name": training.name,
            "learner_profile": learner_profile_dict,
            "total_stages": total_stages,
            "total_modules": total_modules,
            "total_submodules": total_submodules,
            "total_slides": total_slides,
            "generation_method": persisted_plan.generation_method,
            "force_regenerate": request.force_regenerate,
            
            # Métadonnées de persistance
            "database_integration": {
                "plan_id": str(persisted_plan.id),
                "persisted_at": persisted_plan.created_at.isoformat() if persisted_plan.created_at else None,
                "generation_time_seconds": persisted_plan.generation_time_seconds,
                "tokens_used": persisted_plan.tokens_used,
                "ai_generated": persisted_plan.is_ai_generated()
            }
        }
        
        logger.info(f"✅ Plan generated and persisted successfully: ID={persisted_plan.id}, {total_stages} stages, {total_modules} modules, {total_slides} slides")
        
        # Créer la réponse avec validation Pydantic
        response = PlanGenerationResponse(
            success=True,
            training_plan=training_plan_data,
            generation_metadata=generation_metadata,
            message=f"Plan généré et sauvegardé avec succès: {total_stages} étapes, {total_modules} modules, {total_slides} slides (ID: {persisted_plan.id})"
        )
        
        return response
        
    except HTTPException:
        # Re-raise les HTTPException directement
        raise
        
    except DocumentProcessingError as e:
        logger.error(f"❌ Document processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_type": "document_processing_error",
                "error_message": str(e),
                "file_path": getattr(e, 'file_path', None),
                "details": {
                    "supported_formats": ["PDF", "PPT", "PPTX"],
                    "max_file_size": "50MB"
                }
            }
        )
        
    except VertexAIError as e:
        logger.error(f"❌ Vertex AI error: {e}")
        error_id = f"vertex_ai_{int(time.time())}"
        technical_details = {
            "error_id": error_id,
            "error_type": "vertex_ai_error", 
            "error_message": str(e),
            "api_response": getattr(e, 'api_response', None),
            "timestamp": time.time(),
            "service": "vertex_ai"
        }
        logger.error(f"Technical details for support: {technical_details}")
        
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error_type": "service_unavailable",
                "user_message": "Le service de génération de plan de formation est temporairement indisponible. Veuillez contacter le support technique.",
                "support_contact": "jerome.iavarone@gmail.com",
                "error_id": error_id,
                "technical_details": f"VertexAI service error - Error ID: {error_id}. Please include this information when contacting support."
            }
        )
        
    except PlanGenerationError as e:
        logger.error(f"❌ Plan generation error: {e}")
        error_id = f"plan_gen_{int(time.time())}"
        technical_details = {
            "error_id": error_id,
            "error_type": e.error_type,
            "error_message": str(e),
            "original_error": str(e.original_error) if e.original_error else None,
            "timestamp": time.time()
        }
        logger.error(f"Technical details for support: {technical_details}")
        
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error_type": "plan_generation_failed",
                "user_message": "La génération du plan de formation a échoué. Veuillez contacter le support technique avec les détails de l'erreur.",
                "support_contact": "jerome.iavarone@gmail.com",
                "error_id": error_id,
                "technical_details": f"Plan generation error - Error ID: {error_id}, Type: {e.error_type}. Please include this information when contacting support."
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Unexpected error during integrated plan generation: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        error_id = f"internal_{int(time.time())}"
        technical_details = {
            "error_id": error_id,
            "error_type": "internal_server_error",
            "error_message": str(e),
            "traceback": traceback.format_exc(),
            "timestamp": time.time()
        }
        logger.error(f"Technical details for support: {technical_details}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_type": "internal_server_error",
                "user_message": "Une erreur technique inattendue s'est produite lors de la génération du plan de formation. Veuillez contacter le support technique.",
                "support_contact": "jerome.iavarone@gmail.com",
                "error_id": error_id,
                "technical_details": f"Internal server error - Error ID: {error_id}. Please include this information when contacting support."
            }
        )


@router.post(
    "/generate-plan",
    response_model=PlanGenerationResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse}, 
        500: {"model": ErrorResponse}
    },
    summary="Générer un plan de formation personnalisé (API compatible)",
    description="Génère un plan de formation personnalisé - Compatibility endpoint qui redirige vers l'API intégrée"
)
async def generate_plan_compatible(
    request: PlanGenerationRequest,
    session: AsyncSession = Depends(get_async_session),
    integrated_service: IntegratedPlanGenerationService = Depends(get_integrated_plan_generation_service)
) -> PlanGenerationResponse:
    """
    Endpoint de compatibilité qui redirige vers l'API intégrée
    
    Cette route assure la compatibilité avec l'ancienne API /generate-plan
    en redirigeant vers la nouvelle implémentation intégrée.
    """
    logger.info("🔄 Using compatibility endpoint, redirecting to integrated service")
    
    # Rediriger vers l'endpoint intégré
    return await generate_plan_integrated(request, session, integrated_service)


@router.get(
    "/plan/{plan_id}",
    summary="Récupérer un plan de formation par ID",
    description="Récupère un plan de formation persisté en base de données"
)
async def get_plan_by_id(
    plan_id: str,
    integrated_service: IntegratedPlanGenerationService = Depends(get_integrated_plan_generation_service)
) -> Dict[str, Any]:
    """Récupérer un plan de formation par son ID"""
    try:
        from uuid import UUID
        plan_uuid = UUID(plan_id)
        
        plan = await integrated_service.plan_repository.get_by_id(plan_uuid)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan with ID {plan_id} not found"
            )
        
        return {
            "id": str(plan.id),
            "learner_session_id": str(plan.learner_session_id),
            "plan_data": plan.plan_data,
            "generation_method": plan.generation_method,
            "tokens_used": plan.tokens_used,
            "generation_time_seconds": plan.generation_time_seconds,
            "total_slides": plan.get_total_slides(),
            "stage_count": plan.get_stage_count(),
            "created_at": plan.created_at.isoformat() if plan.created_at else None,
            "updated_at": plan.updated_at.isoformat() if plan.updated_at else None
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan ID format"
        )
    except Exception as e:
        logger.error(f"❌ Error retrieving plan {plan_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving plan"
        )


@router.get(
    "/generate-plan-integrated/health",
    summary="Health check du service intégré",
    description="Vérifier le statut du service de génération intégré avec base de données"
)
async def integrated_health_check(
    integrated_service: IntegratedPlanGenerationService = Depends(get_integrated_plan_generation_service)
) -> Dict[str, Any]:
    """Health check du service de génération intégré"""
    return await integrated_service.health_check()


@router.get(
    "/generation-statistics",
    summary="Statistiques de génération de plans",
    description="Obtenir des statistiques sur la génération de plans de formation"
)
async def get_generation_statistics(
    integrated_service: IntegratedPlanGenerationService = Depends(get_integrated_plan_generation_service)
) -> Dict[str, Any]:
    """Obtenir les statistiques de génération de plans"""
    try:
        stats = await integrated_service.get_generation_statistics()
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"❌ Error getting generation statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving generation statistics"
        )


@router.post(
    "/validate-plan",
    response_model=PlanValidationResult,
    summary="Valider un plan de formation",
    description="Valider strictement la structure et le contenu d'un plan de formation"
)
async def validate_plan(
    plan_data: Dict[str, Any]
) -> PlanValidationResult:
    """
    Valider un plan de formation selon les contraintes strictes
    
    Args:
        plan_data: Données du plan à valider
        
    Returns:
        Résultat de validation avec erreurs détaillées
    """
    try:
        logger.info("🔍 Starting plan validation")
        
        validation_errors = []
        warnings = []
        
        # Vérification structure de base
        if not isinstance(plan_data, dict):
            validation_errors.append(ValidationErrorDetail(
                field="root",
                message="Plan data must be a dictionary",
                invalid_value=type(plan_data).__name__
            ))
            return PlanValidationResult(
                is_valid=False,
                validation_errors=validation_errors
            )
        
        if "training_plan" not in plan_data:
            validation_errors.append(ValidationErrorDetail(
                field="training_plan",
                message="Missing required field 'training_plan'",
                invalid_value=None
            ))
            return PlanValidationResult(
                is_valid=False,
                validation_errors=validation_errors
            )
        
        try:
            # Validation Pydantic stricte
            training_plan = TrainingPlanSchema(**plan_data["training_plan"])
            
            # Calculer statistiques
            stages = training_plan.stages
            total_modules = sum(len(stage.modules) for stage in stages)
            total_submodules = sum(
                len(module.submodules) 
                for stage in stages 
                for module in stage.modules
            )
            total_slides = sum(
                submodule.slide_count
                for stage in stages
                for module in stage.modules
                for submodule in module.submodules
            )
            
            statistics = {
                "total_stages": len(stages),
                "total_modules": total_modules,
                "total_submodules": total_submodules,
                "total_slides": total_slides
            }
            
            # Avertissements optionnels
            if total_slides < 20:
                warnings.append(f"Plan relativement court: {total_slides} slides")
            elif total_slides > 40:
                warnings.append(f"Plan relativement long: {total_slides} slides")
            
            logger.info(f"✅ Plan validation successful: {statistics}")
            
            return PlanValidationResult(
                is_valid=True,
                validation_errors=[],
                warnings=warnings,
                statistics=statistics
            )
            
        except ValidationError as e:
            logger.warning(f"⚠️ Plan validation failed: {e}")
            
            # Convertir erreurs Pydantic
            for error in e.errors():
                field_path = "training_plan." + '.'.join(str(x) for x in error['loc'])
                validation_errors.append(ValidationErrorDetail(
                    field=field_path,
                    message=error['msg'],
                    invalid_value=error.get('input', 'unknown')
                ))
            
            return PlanValidationResult(
                is_valid=False,
                validation_errors=validation_errors,
                warnings=warnings
            )
            
    except Exception as e:
        logger.error(f"❌ Unexpected error during validation: {e}")
        return PlanValidationResult(
            is_valid=False,
            validation_errors=[ValidationErrorDetail(
                field="system",
                message=f"Internal validation error: {str(e)}",
                invalid_value=None
            )]
        )