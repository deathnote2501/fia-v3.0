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
from app.services.integrated_plan_generation_service import IntegratedPlanGenerationService
from app.adapters.repositories.learner_training_plan_repository import LearnerTrainingPlanRepository
from app.adapters.repositories.api_log_repository import ApiLogRepository
from app.adapters.repositories.learner_session_repository import LearnerSessionRepository
from app.services.simple_plan_generation_service import (
    PlanGenerationError,
    DocumentProcessingError,
    VertexAIError
)
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
    
    # Créer le service intégré
    return IntegratedPlanGenerationService(
        plan_repository=plan_repository,
        api_log_repository=api_log_repository
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
        
        logger.info(f"📄 Using training file: {training.file_path}")
        
        # Vérifier si une session apprenant existe déjà ou en créer une temporaire
        # Pour ce MVP, on utilise l'ID de training comme session temporaire
        learner_session_id = request.training_id  # Temporaire pour le MVP
        
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
            file_path=training.file_path,
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
            
            # Validation Pydantic stricte
            training_plan_data = persisted_plan.plan_data["training_plan"]
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
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error_type": "vertex_ai_error",
                "error_message": str(e),
                "api_response": getattr(e, 'api_response', None),
                "details": {
                    "service": "vertex_ai",
                    "retry_suggested": True
                }
            }
        )
        
    except PlanGenerationError as e:
        logger.error(f"❌ Plan generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error_type": e.error_type,
                "error_message": str(e),
                "original_error": str(e.original_error) if e.original_error else None
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Unexpected error during integrated plan generation: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_type": "internal_server_error",
                "error_message": "An unexpected error occurred during plan generation",
                "details": {
                    "contact_support": True,
                    "error_id": f"integrated_plan_gen_{int(time.time())}"
                }
            }
        )


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