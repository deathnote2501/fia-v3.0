"""
FIA v3.0 - Plan Generation Controller (Simple)
Controller simple pour endpoint unique de génération de plans
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.plan_schemas import (
    PlanGenerationRequest,
    PlanGenerationResponse,
    ErrorResponse
)
from app.services.simple_plan_generation_service import SimplePlanGenerationService
from app.infrastructure.database import get_async_session
from app.infrastructure.models.training_model import TrainingModel

logger = logging.getLogger(__name__)

# Router pour les endpoints de génération de plans
router = APIRouter(prefix="/api", tags=["Plan Generation"])


def get_plan_generation_service() -> SimplePlanGenerationService:
    """Dependency pour obtenir le service de génération de plans"""
    return SimplePlanGenerationService()


@router.post(
    "/generate-plan",
    response_model=PlanGenerationResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse}, 
        500: {"model": ErrorResponse}
    },
    summary="Générer un plan de formation personnalisé",
    description="Génère un plan de formation personnalisé basé sur le profil apprenant et le contenu de formation"
)
async def generate_plan(
    request: PlanGenerationRequest,
    session: AsyncSession = Depends(get_async_session),
    plan_service: SimplePlanGenerationService = Depends(get_plan_generation_service)
) -> PlanGenerationResponse:
    """
    Générer un plan de formation personnalisé
    
    Args:
        request: Requête avec training_id et profil apprenant
        session: Session base de données
        plan_service: Service de génération de plans
        
    Returns:
        Plan de formation structuré en 5 étapes
    """
    try:
        logger.info(f"🚀 Starting plan generation for training {request.training_id}")
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
        
        # Convertir le profil Pydantic en dictionnaire
        learner_profile_dict = {
            "experience_level": request.learner_profile.experience_level,
            "learning_style": request.learner_profile.learning_style,
            "job_position": request.learner_profile.job_position,
            "activity_sector": request.learner_profile.activity_sector,
            "country": request.learner_profile.country,
            "language": request.learner_profile.language
        }
        
        # Générer le plan avec le service
        generated_plan = await plan_service.generate_plan(
            learner_profile=learner_profile_dict,
            file_path=training.file_path
        )
        
        # Valider la structure du plan généré
        if "training_plan" not in generated_plan:
            logger.error("❌ Invalid plan structure: missing 'training_plan' key")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid plan structure generated"
            )
        
        # Extraire le plan et créer les métadonnées
        training_plan_data = generated_plan["training_plan"]
        
        # Calculer les métadonnées
        total_stages = len(training_plan_data.get("stages", []))
        total_modules = sum(len(stage.get("modules", [])) for stage in training_plan_data.get("stages", []))
        total_submodules = sum(
            len(module.get("submodules", [])) 
            for stage in training_plan_data.get("stages", [])
            for module in stage.get("modules", [])
        )
        total_slides = sum(
            submodule.get("slide_count", 0)
            for stage in training_plan_data.get("stages", [])
            for module in stage.get("modules", [])
            for submodule in module.get("submodules", [])
        )
        
        generation_metadata = {
            "training_id": str(request.training_id),
            "training_name": training.name,
            "learner_profile": learner_profile_dict,
            "total_stages": total_stages,
            "total_modules": total_modules,
            "total_submodules": total_submodules,
            "total_slides": total_slides,
            "generation_method": "vertex_ai" if plan_service.client else "mock",
            "force_regenerate": request.force_regenerate
        }
        
        logger.info(f"✅ Plan generated successfully: {total_stages} stages, {total_modules} modules, {total_slides} slides")
        
        # Créer la réponse avec validation Pydantic
        response = PlanGenerationResponse(
            success=True,
            training_plan=training_plan_data,
            generation_metadata=generation_metadata,
            message=f"Plan généré avec succès: {total_stages} étapes, {total_modules} modules, {total_slides} slides"
        )
        
        return response
        
    except HTTPException:
        # Re-raise les HTTPException directement
        raise
        
    except Exception as e:
        logger.error(f"❌ Unexpected error during plan generation: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during plan generation"
        )


@router.get(
    "/generate-plan/health",
    summary="Health check du service de génération",
    description="Vérifier le statut du service de génération de plans"
)
async def health_check(
    plan_service: SimplePlanGenerationService = Depends(get_plan_generation_service)
) -> Dict[str, Any]:
    """Health check du service de génération de plans"""
    try:
        vertex_ai_configured = plan_service.client is not None
        
        return {
            "status": "healthy",
            "service": "plan_generation",
            "vertex_ai_configured": vertex_ai_configured,
            "model": plan_service.model_name if hasattr(plan_service, 'model_name') else "unknown"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "plan_generation",
            "error": str(e)
        }