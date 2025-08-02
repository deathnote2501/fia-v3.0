"""
FIA v3.0 - Session Controller
FastAPI routes for training session management (formateur) and learner access (public)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
import secrets
import logging
from datetime import datetime, timedelta

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
from app.domain.services.plan_generation_service_v2 import PlanGenerationService
# from app.domain.services.plan_parser_service import PlanParserService

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["sessions"])



# ============================================================================
# TRAINER ROUTES (with JWT authentication)
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
        # Verify that training exists and belongs to trainer
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
        
        # Generate unique session token
        session_token = secrets.token_urlsafe(32)
        
        # Calculate expiration date (30 days from now)
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        # Create training session
        training_session = TrainingSession(
            training_id=session_data.training_id,
            name=session_data.name.strip(),
            description=session_data.description.strip() if session_data.description else None,
            session_token=session_token,
            expires_at=expires_at
        )
        
        # Sauvegarder en base
        session_repo = TrainingSessionRepository(db)
        created_session = await session_repo.create(training_session)
        
        # Generate session link
        session_link = f"{settings.frontend_url}/frontend/public/training.html?token={session_token}"
        
        # Build response with link
        response_data = TrainingSessionResponse.model_validate(created_session)
        return TrainingSessionWithLink(
            **response_data.model_dump(),
            session_link=session_link
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Session creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session creation failed"
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
        # Get all trainings for the trainer
        training_repo = TrainingRepository(db)
        trainings = await training_repo.get_by_trainer_id(current_trainer.id)
        
        # Get all sessions for these trainings
        session_repo = TrainingSessionRepository(db)
        all_sessions = []
        
        for training in trainings:
            sessions = await session_repo.get_by_training_id(training.id)
            all_sessions.extend(sessions)
        
        return all_sessions
        
    except Exception as e:
        logger.error(f"Failed to retrieve training sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sessions"
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
        
        # Verify that the training belongs to the trainer
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
        logger.error(f"Training session deletion failed for session_id {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session deletion failed"
        )


# ============================================================================
# LEARNER ROUTES (public, token validation)
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
        
        # Get training information
        training_repo = TrainingRepository(db)
        training = await training_repo.get_by_id(training_session.training_id)
        
        if not training:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training not found"
            )
        
        # Try to get learner session if it exists
        learner_session = None
        learner_repo = LearnerSessionRepository(db)
        
        # For now, we'll get the first learner session for this training session
        # In a real implementation, we'd identify the learner by some criteria
        learner_sessions = await learner_repo.get_by_training_session_id(training_session.id)
        if learner_sessions:
            # For demo purposes, take the most recent one
            learner_session = max(learner_sessions, key=lambda x: x.started_at)
        
        response_data = {
            "session_id": training_session.id,
            "session_name": training_session.name,
            "session_description": training_session.description,
            "training_name": training.name,
            "training_description": training.description,
            "training_session": {
                "id": training_session.id,
                "training_id": training_session.training_id,
                "name": training_session.name,
                "description": training_session.description
            },
            "is_valid": True
        }
        
        # Add learner session data if available
        if learner_session:
            response_data["learner_session"] = {
                "id": learner_session.id,
                "email": learner_session.email,
                "experience_level": learner_session.experience_level,
                "learning_style": learner_session.learning_style,
                "job_position": learner_session.job_position,
                "activity_sector": learner_session.activity_sector,
                "country": learner_session.country,
                "language": learner_session.language,
                "current_slide_number": learner_session.current_slide_number,
                "total_time_spent": learner_session.total_time_spent,
                "started_at": learner_session.started_at.isoformat() if learner_session.started_at else None,
                # New fields for profile refactoring
                "objectives": learner_session.objectives,
                "training_duration": learner_session.training_duration
            }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token validation failed for token {session_token}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token validation failed"
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
        
        # Check if learner already exists for this session
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
        
        # Create learner session with new profile structure
        learner_session = LearnerSession(
            training_session_id=training_session.id,
            email=profile_data.email,
            experience_level=profile_data.experience_level,
            # Legacy fields set to None for new profiles (keeping for backward compatibility)
            learning_style=None,
            job_position=profile_data.job_and_sector.strip(),  # Store combined value in job_position for now
            activity_sector=None,
            country=None,
            language=profile_data.language or "fr",
            # New fields for profile refactoring
            objectives=profile_data.objectives.strip(),
            training_duration=profile_data.training_duration
        )
        
        # Sauvegarder en base
        created_learner_session = await learner_repo.create(learner_session)
        
        # Temporarily disable automatic plan generation due to mapping issues
        # TODO: Re-enable when plan generation service is fixed
        """
        try:
            logger.info(f"Starting automatic plan generation for learner {created_learner_session.id}")
            
            # Get training to access content
            training_repo = TrainingRepository(db)
            training = await training_repo.get_by_id(training_session.training_id)
            
            if training:
                logger.info(f"Training found: {training.name} (ID: {training.id})")
                
                # Initialize plan generation service
                plan_service = PlanGenerationService()
                
                learner_profile = {
                    "email": created_learner_session.email,
                    "experience_level": created_learner_session.experience_level,
                    "learning_style": created_learner_session.learning_style,
                    "job_position": created_learner_session.job_position,
                    "activity_sector": created_learner_session.activity_sector,
                    "country": created_learner_session.country,
                    "language": created_learner_session.language
                }
                
                logger.debug(f"Learner profile: {learner_profile}")
                
                # Generate the plan
                logger.info("Calling plan generation service...")
                generated_plan = await plan_service.generate_personalized_plan(
                    learner_session_id=created_learner_session.id,
                    training_id=training.id,
                    learner_profile=learner_profile
                )
                
                logger.info(f"Plan generated successfully: {generated_plan.success}")
                logger.debug(f"Generation metadata: {generated_plan.generation_metadata}")
                
                # Update session with generated plan (temporary storage until plan_data is used)
                logger.info("Saving plan to database...")
                created_learner_session.enriched_profile = generated_plan.plan_data
                updated_session = await learner_repo.update(created_learner_session)
                
                logger.info(f"Plan saved to database. Session updated: {updated_session.id}")
                logger.debug(f"Plan content preview: {str(generated_plan.plan_data)[:200]}...")
                
            else:
                logger.warning(f"Training not found for session {training_session.training_id}")
                
        except Exception as plan_error:
            # Log error but don't fail profile creation
            logger.error(f"Plan generation failed: {str(plan_error)}", exc_info=True)
        """
        
        return created_learner_session
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Learner profile creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile creation failed"
        )