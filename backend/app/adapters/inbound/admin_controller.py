"""
FIA v3.0 - Admin Controller
API endpoints for admin dashboard and trainer management
"""

import logging
from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.auth import get_current_trainer
from app.infrastructure.database import get_database_session
from app.domain.entities.trainer import Trainer
from app.adapters.repositories.trainer_repository import TrainerRepository

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/admin", tags=["Admin"])


async def get_current_admin_trainer(
    current_trainer: Trainer = Depends(get_current_trainer)
) -> Trainer:
    """Dependency to ensure current trainer has admin privileges"""
    if not current_trainer.has_admin_privileges():
        logger.warning(f"Non-admin trainer {current_trainer.email} attempted to access admin endpoint")
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_trainer


@router.get("/trainers-overview")
async def get_trainers_overview(
    admin_trainer: Trainer = Depends(get_current_admin_trainer),
    session: AsyncSession = Depends(get_database_session)
) -> List[Dict[str, Any]]:
    """
    Get overview of all trainers with their statistics
    Returns mock data for now - will be replaced with real calculations in next phases
    """
    logger.info(f"Admin {admin_trainer.email} requested trainers overview")
    
    try:
        # Get all trainers using repository
        trainer_repo = TrainerRepository(session)
        trainers = await trainer_repo.get_all_for_admin_overview()
        
        # Mock data structure - will be replaced with real statistics
        trainers_overview = []
        
        for trainer in trainers:
            trainer_data = {
                "id": str(trainer.id),
                "first_name": trainer.first_name,
                "last_name": trainer.last_name,
                "email": trainer.email,
                "created_at": trainer.created_at.isoformat() if trainer.created_at else None,
                
                # Mock statistics - to be replaced with real calculations
                "trainings_with_support": 5,  # COUNT(trainings WHERE is_ai_generated = false)
                "trainings_ai_generated": 3,  # COUNT(trainings WHERE is_ai_generated = true)
                "active_sessions": 2,         # COUNT(training_sessions WHERE is_active = true)
                "total_sessions": 8,          # COUNT(training_sessions)
                "unique_learners": 12,        # COUNT(DISTINCT learner_sessions.email)
                "total_time_all_learners": "45h 30min",  # SUM(learner_sessions.total_time_spent)
                "average_time_per_slide": "2min 15s",    # Total time / total slides viewed
                "total_slides_generated": 156,           # COUNT(training_slides)
                "average_slides_per_training": 19.5,     # total_slides / total_trainings
                
                # Metadata
                "is_active": trainer.is_active,
                "is_superuser": trainer.is_superuser
            }
            trainers_overview.append(trainer_data)
        
        logger.info(f"Successfully retrieved overview for {len(trainers_overview)} trainers")
        return trainers_overview
        
    except Exception as e:
        logger.error(f"Failed to get trainers overview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve trainers overview")


@router.get("/stats")
async def get_admin_stats(
    admin_trainer: Trainer = Depends(get_current_admin_trainer),
    session: AsyncSession = Depends(get_database_session)
) -> Dict[str, Any]:
    """
    Get global admin statistics
    Returns mock data for now
    """
    logger.info(f"Admin {admin_trainer.email} requested admin stats")
    
    try:
        trainer_repo = TrainerRepository(session)
        all_trainers = await trainer_repo.get_all_for_admin_overview()
        
        # Mock global statistics
        stats = {
            "total_trainers": len(all_trainers),
            "active_trainers": len([t for t in all_trainers if t.is_active]),
            "superuser_trainers": len([t for t in all_trainers if t.is_superuser]),
            "total_trainings": 48,         # SUM of all trainings across all trainers
            "total_ai_trainings": 18,      # SUM of AI-generated trainings
            "total_sessions": 127,         # SUM of all sessions
            "active_sessions": 23,         # SUM of active sessions
            "total_learners": 89,          # COUNT DISTINCT learners across all sessions
            "total_slides": 1250,          # COUNT all slides generated
            "total_learning_time": "892h 45min"  # SUM of all learning time
        }
        
        logger.info("Successfully retrieved admin stats")
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get admin stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve admin statistics")