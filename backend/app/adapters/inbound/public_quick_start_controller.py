"""
FIA v3.0 - Public Quick Start Controller
Public endpoints for anonymous users to create AI training and sessions
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import logging
import secrets
from datetime import datetime, timedelta

from app.infrastructure.database import get_database_session
from app.infrastructure.settings import settings
from app.domain.entities.training import Training, FileType
from app.domain.entities.training_session import TrainingSession
from app.domain.schemas.training import TrainingResponse
from app.domain.schemas.training_session import TrainingSessionWithLink
from app.domain.services.ai_training_generation_service import AITrainingGenerationService
from app.domain.services.file_storage_service import FileStorageService
from app.adapters.repositories.training_repository import TrainingRepository
from app.adapters.repositories.training_session_repository import TrainingSessionRepository
from app.adapters.repositories.trainer_repository import TrainerRepository
from app.adapters.outbound.ai_adapter import AIAdapter
from app.adapters.outbound.settings_adapter import SettingsAdapter
from app.adapters.outbound.rate_limiter_adapter import RateLimiterAdapter
from pydantic import BaseModel, Field
import io

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/public", tags=["public"])


# ============================================================================
# SCHEMAS
# ============================================================================

class QuickStartRequest(BaseModel):
    """Request schema for quick start training creation"""
    topic: str = Field(..., min_length=5, max_length=500, description="Training topic")


class QuickStartResponse(BaseModel):
    """Response schema for quick start workflow"""
    training_id: str
    training_name: str
    session_token: str
    session_link: str
    message: str


# ============================================================================
# DEPENDENCY INJECTION FUNCTIONS
# ============================================================================

async def get_ai_training_generation_service(
    db: AsyncSession = Depends(get_database_session)
) -> AITrainingGenerationService:
    """Get AI training generation service with proper dependency injection"""
    ai_adapter = AIAdapter()
    settings_adapter = SettingsAdapter()
    rate_limiter_adapter = RateLimiterAdapter()
    
    return AITrainingGenerationService(ai_adapter, settings_adapter, rate_limiter_adapter)


async def get_file_storage_service() -> FileStorageService:
    """Get file storage service with proper dependency injection"""
    settings_adapter = SettingsAdapter()
    return FileStorageService(settings_adapter)


# ============================================================================
# PUBLIC ENDPOINTS
# ============================================================================

@router.post("/quick-start", response_model=QuickStartResponse, status_code=status.HTTP_201_CREATED)
async def create_quick_start_training(
    request: QuickStartRequest,
    db: AsyncSession = Depends(get_database_session),
    ai_service: AITrainingGenerationService = Depends(get_ai_training_generation_service),
    file_storage: FileStorageService = Depends(get_file_storage_service)
):
    """
    Create AI-generated training and session for anonymous users
    
    This endpoint creates:
    1. An AI-generated training based on the topic
    2. A training session with unique token
    3. Returns the session link for immediate access
    
    No authentication required - designed for landing page workflow.
    """
    
    try:
        logger.info(f"🚀 PUBLIC_QUICK_START [START] Creating training for topic: '{request.topic}'")
        
        # Step 1: Get or create anonymous trainer
        trainer_repo = TrainerRepository(db)
        anonymous_trainer = await trainer_repo.get_or_create_anonymous_trainer()
        
        logger.info(f"👤 PUBLIC_QUICK_START [TRAINER] Using anonymous trainer: {anonymous_trainer.id}")
        
        # Step 2: Generate training name and description
        training_name = f"Formation: {request.topic}"
        training_description = f"Formation IA personnalisée sur le sujet: {request.topic}"
        
        # Step 3: Create training entity (temporary for service call)
        temp_training = Training(
            trainer_id=anonymous_trainer.id,
            name=training_name,
            description=training_description,
            is_ai_generated=True
        )
        
        # Step 4: Generate AI content using existing service
        logger.info(f"🤖 PUBLIC_QUICK_START [AI] Generating content for '{training_name}'")
        
        try:
            ai_content = await ai_service.generate_training_content(
                name=training_name,
                description=training_description
            )
            
            logger.info(f"✅ PUBLIC_QUICK_START [AI] Content generated - {len(ai_content)} characters")
            
        except Exception as ai_error:
            logger.error(f"❌ PUBLIC_QUICK_START [AI] Generation failed: {ai_error}")
            # Fallback to basic content for testing
            logger.info("🔄 PUBLIC_QUICK_START [FALLBACK] Using minimal content for testing")
            ai_content = f"""# Formation : {request.topic}

## Introduction
Bienvenue dans cette formation sur : **{request.topic}**

## Objectifs
À la fin de cette formation, vous serez capable de :
- Comprendre les concepts fondamentaux
- Appliquer les bonnes pratiques
- Résoudre les problèmes courants

## Plan de formation
1. **Module 1 : Introduction**
   - Concepts de base
   - Terminologie

2. **Module 2 : Pratique**
   - Exercices pratiques
   - Cas d'usage

3. **Module 3 : Approfondissement**
   - Techniques avancées
   - Optimisation

## Conclusion
Cette formation vous donnera les bases nécessaires pour maîtriser {request.topic}.

---
*Formation générée par FIA v3.0*
"""
        
        # Step 5: Store AI-generated file
        try:
            file_content = io.BytesIO(ai_content.encode('utf-8'))
            generated_filename = f"{request.topic.replace(' ', '_').lower()}_ai_generated.md"
            
            file_path, file_size = await file_storage.store_training_file(
                trainer_id=anonymous_trainer.id,
                training_id=temp_training.id,
                file_content=file_content,
                original_filename=generated_filename,
                mime_type="text/markdown"
            )
            
            # Update training with file information
            temp_training.file_path = file_path
            temp_training.file_name = generated_filename
            temp_training.file_type = FileType.MARKDOWN
            temp_training.file_size = file_size
            temp_training.mime_type = "text/markdown"
            
            logger.info(f"💾 PUBLIC_QUICK_START [FILE] Stored at: {file_path}")
            
        except Exception as storage_error:
            logger.error(f"❌ PUBLIC_QUICK_START [STORAGE] Failed: {storage_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Échec du stockage du fichier. Veuillez réessayer."
            )
        
        # Step 6: Save training to database
        try:
            training_repo = TrainingRepository(db)
            created_training = await training_repo.create(temp_training)
            
            logger.info(f"📚 PUBLIC_QUICK_START [TRAINING] Created: {created_training.id}")
            
        except Exception as db_error:
            logger.error(f"❌ PUBLIC_QUICK_START [DB] Training creation failed: {db_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Échec de la création de formation. Veuillez réessayer."
            )
        
        # Step 7: Create training session
        try:
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(days=30)
            
            training_session = TrainingSession(
                training_id=created_training.id,
                name=f"Session: {training_name}",
                description="Session générée automatiquement pour formation IA",
                session_token=session_token,
                expires_at=expires_at
            )
            
            session_repo = TrainingSessionRepository(db)
            created_session = await session_repo.create(training_session)
            
            logger.info(f"🎯 PUBLIC_QUICK_START [SESSION] Created: {created_session.id}")
            
        except Exception as session_error:
            logger.error(f"❌ PUBLIC_QUICK_START [SESSION] Creation failed: {session_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Échec de la création de session. Veuillez réessayer."
            )
        
        # Step 8: Generate session link
        session_link = f"{settings.frontend_url}/frontend/public/training.html?token={session_token}&profile=required"
        
        logger.info(f"✅ PUBLIC_QUICK_START [SUCCESS] Workflow completed for topic: '{request.topic}'")
        
        return QuickStartResponse(
            training_id=str(created_training.id),
            training_name=created_training.name,
            session_token=session_token,
            session_link=session_link,
            message="Formation créée avec succès ! Vous allez être redirigé vers le formulaire de profil."
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions without wrapping
        raise
    except Exception as e:
        logger.error(f"❌ PUBLIC_QUICK_START [ERROR] Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur inattendue est survenue. Veuillez réessayer."
        )


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check for public quick start service"""
    return {
        "status": "healthy",
        "service": "public_quick_start",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }