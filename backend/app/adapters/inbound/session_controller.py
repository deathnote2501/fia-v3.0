"""
FIA v3.0 - Session Controller
FastAPI routes for training session management (formateur) and learner access (public)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
import secrets

from app.infrastructure.database import get_database_session
from app.infrastructure.auth import get_current_trainer
from app.infrastructure.settings import settings
from app.domain.entities.trainer import Trainer
from app.domain.entities.training_session import TrainingSession
from app.domain.entities.learner_session import LearnerSession
from app.domain.schemas.training_session import (
    TrainingSessionCreate, 
    TrainingSessionResponse, 
    TrainingSessionWithLink
)
from app.domain.schemas.learner_session import (
    LearnerProfileCreate, 
    LearnerSessionResponse
)
from app.adapters.repositories.training_session_repository import TrainingSessionRepository
from app.adapters.repositories.learner_session_repository import LearnerSessionRepository
from app.adapters.repositories.training_repository import TrainingRepository


router = APIRouter(tags=["sessions"])



# ============================================================================
# ROUTES FORMATEUR (avec authentification JWT)
# ============================================================================

@router.post("/api/training-sessions", response_model=TrainingSessionWithLink, status_code=status.HTTP_201_CREATED)
async def create_training_session(
    session_data: TrainingSessionCreate,
    current_trainer: Trainer = Depends(get_current_trainer),
    db: AsyncSession = Depends(get_database_session)
):
    """
    Create new training session for a training
    
    Requires trainer authentication. Generates unique session token and returns session link.
    """
    
    try:
        # Vérifier que la formation existe et appartient au formateur
        training_repo = TrainingRepository(db)
        training = await training_repo.get_by_id(session_data.training_id)
        
        if not training:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training not found"
            )
        
        if training.trainer_id != current_trainer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only create sessions for your own trainings"
            )
        
        # Générer token de session unique
        session_token = secrets.token_urlsafe(32)
        
        # Créer la session de formation
        training_session = TrainingSession(
            training_id=session_data.training_id,
            name=session_data.name.strip(),
            description=session_data.description.strip() if session_data.description else None,
            session_token=session_token
        )
        
        # Sauvegarder en base
        session_repo = TrainingSessionRepository(db)
        created_session = await session_repo.create(training_session)
        
        # Générer le lien de session
        session_link = f"{settings.frontend_url}/session.html?token={session_token}"
        
        # Construire la réponse avec le lien
        response_data = TrainingSessionResponse.model_validate(created_session)
        return TrainingSessionWithLink(
            **response_data.model_dump(),
            session_link=session_link
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Session creation failed: {str(e)}"
        )


@router.get("/api/training-sessions", response_model=List[TrainingSessionResponse])
async def list_training_sessions(
    current_trainer: Trainer = Depends(get_current_trainer),
    db: AsyncSession = Depends(get_database_session)
):
    """
    List all training sessions for current trainer
    
    Returns sessions from all trainings belonging to the current trainer.
    """
    
    try:
        # Récupérer toutes les formations du formateur
        training_repo = TrainingRepository(db)
        trainings = await training_repo.get_by_trainer_id(current_trainer.id)
        
        # Récupérer toutes les sessions pour ces formations
        session_repo = TrainingSessionRepository(db)
        all_sessions = []
        
        for training in trainings:
            sessions = await session_repo.get_by_training_id(training.id)
            all_sessions.extend(sessions)
        
        return all_sessions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sessions: {str(e)}"
        )


@router.delete("/api/training-sessions/{session_id}")
async def delete_training_session(
    session_id: UUID,
    current_trainer: Trainer = Depends(get_current_trainer),
    db: AsyncSession = Depends(get_database_session)
):
    """
    Delete training session
    
    Only the trainer who owns the training can delete its sessions.
    """
    
    try:
        session_repo = TrainingSessionRepository(db)
        training_session = await session_repo.get_by_id(session_id)
        
        if not training_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training session not found"
            )
        
        # Vérifier que la formation appartient au formateur
        training_repo = TrainingRepository(db)
        training = await training_repo.get_by_id(training_session.training_id)
        
        if not training or training.trainer_id != current_trainer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only delete sessions from your own trainings"
            )
        
        # Supprimer la session
        success = await session_repo.delete(session_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete session"
            )
        
        return {"message": "Training session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Delete failed: {str(e)}"
        )


# ============================================================================
# ROUTES APPRENANT (publiques, validation par token)
# ============================================================================

@router.get("/api/session/{token}")
async def validate_session_token(
    token: str,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Validate session token and return session information
    
    Public endpoint for learners to access training session.
    Returns basic session info if token is valid.
    """
    
    try:
        session_repo = TrainingSessionRepository(db)
        training_session = await session_repo.get_by_token(token)
        
        if not training_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid session token"
            )
        
        if not training_session.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Session is no longer active"
            )
        
        # Récupérer les informations de la formation
        training_repo = TrainingRepository(db)
        training = await training_repo.get_by_id(training_session.training_id)
        
        if not training:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training not found"
            )
        
        return {
            "session_id": training_session.id,
            "session_name": training_session.name,
            "session_description": training_session.description,
            "training_name": training.name,
            "training_description": training.description,
            "is_valid": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token validation failed: {str(e)}"
        )


@router.post("/api/session/{token}/profile", response_model=LearnerSessionResponse, status_code=status.HTTP_201_CREATED)
async def save_learner_profile(
    token: str,
    profile_data: LearnerProfileCreate,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Save learner profile for a training session
    
    Public endpoint that creates or updates a learner session with profile information.
    Each learner (identified by email) can have only one session per training session.
    """
    
    try:
        # Valider le token de session
        session_repo = TrainingSessionRepository(db)
        training_session = await session_repo.get_by_token(token)
        
        if not training_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid session token"
            )
        
        if not training_session.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Session is no longer active"
            )
        
        # Vérifier si l'apprenant existe déjà pour cette session
        learner_repo = LearnerSessionRepository(db)
        existing_learner = await learner_repo.get_by_training_session_and_email(
            training_session.id, 
            profile_data.email
        )
        
        if existing_learner:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A profile already exists for this email in this training session"
            )
        
        # Créer la session apprenant
        learner_session = LearnerSession(
            training_session_id=training_session.id,
            email=profile_data.email,
            experience_level=profile_data.experience_level,
            learning_style=profile_data.learning_style,
            job_position=profile_data.job_position.strip(),
            activity_sector=profile_data.activity_sector.strip(),
            country=profile_data.country.strip(),
            language=profile_data.language or "fr"
        )
        
        # Sauvegarder en base
        created_learner_session = await learner_repo.create(learner_session)
        
        return created_learner_session
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile creation failed: {str(e)}"
        )