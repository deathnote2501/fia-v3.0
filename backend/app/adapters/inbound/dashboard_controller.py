"""
FIA v3.0 - Dashboard Controller
API endpoints for trainer dashboard statistics
"""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.infrastructure.auth import get_current_trainer
from app.infrastructure.database import get_database_session
from app.infrastructure.models.trainer_model import TrainerModel
from app.infrastructure.models.training_model import TrainingModel
from app.infrastructure.models.training_session_model import TrainingSessionModel
from app.infrastructure.models.learner_session_model import LearnerSessionModel

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    current_trainer: TrainerModel = Depends(get_current_trainer),
    db: AsyncSession = Depends(get_database_session)
):
    """
    Get dashboard statistics for the current trainer
    
    Returns:
        Dashboard statistics including trainings count, active sessions, etc.
    """
    try:
        trainer_id = current_trainer.id
        
        # Count trainings for this trainer
        trainings_result = await db.execute(
            select(func.count(TrainingModel.id))
            .where(TrainingModel.trainer_id == trainer_id)
        )
        trainings_count = trainings_result.scalar() or 0
        
        # Count active training sessions for this trainer's trainings
        active_sessions_result = await db.execute(
            select(func.count(TrainingSessionModel.id))
            .join(TrainingModel, TrainingSessionModel.training_id == TrainingModel.id)
            .where(
                TrainingModel.trainer_id == trainer_id,
                TrainingSessionModel.is_active == True
            )
        )
        active_sessions_count = active_sessions_result.scalar() or 0
        
        # Count total learners across all trainer's sessions
        learners_result = await db.execute(
            select(func.count(LearnerSessionModel.id))
            .join(TrainingSessionModel, LearnerSessionModel.training_session_id == TrainingSessionModel.id)
            .join(TrainingModel, TrainingSessionModel.training_id == TrainingModel.id)
            .where(TrainingModel.trainer_id == trainer_id)
        )
        total_learners = learners_result.scalar() or 0
        
        # Calculate average session time (simplified to minutes)
        avg_time_result = await db.execute(
            select(func.avg(LearnerSessionModel.total_time_spent))
            .join(TrainingSessionModel, LearnerSessionModel.training_session_id == TrainingSessionModel.id)
            .join(TrainingModel, TrainingSessionModel.training_id == TrainingModel.id)
            .where(TrainingModel.trainer_id == trainer_id)
        )
        avg_time_seconds = avg_time_result.scalar() or 0
        avg_time_minutes = int(avg_time_seconds / 60) if avg_time_seconds else 0
        avg_session_time = f"{avg_time_minutes}m"
        
        return {
            "trainings_count": trainings_count,
            "active_sessions_count": active_sessions_count,
            "total_learners": total_learners,
            "avg_session_time": avg_session_time
        }
        
    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {e}")
        # Return default stats on error
        return {
            "trainings_count": 0,
            "active_sessions_count": 0,
            "total_learners": 0,
            "avg_session_time": "0m"
        }


@router.get("/recent-activity")
async def get_recent_activity(
    current_trainer: TrainerModel = Depends(get_current_trainer),
    db: AsyncSession = Depends(get_database_session)
):
    """
    Get recent activity for the trainer dashboard
    
    Returns:
        List of recent activities with icon, title, and timestamp
    """
    try:
        trainer_id = current_trainer.id
        activities = []
        
        # Get recent trainings
        recent_trainings = await db.execute(
            select(TrainingModel)
            .where(TrainingModel.trainer_id == trainer_id)
            .order_by(TrainingModel.created_at.desc())
            .limit(3)
        )
        
        for training in recent_trainings.scalars():
            activities.append({
                "icon": "file-earmark-plus",
                "title": f"Created training: {training.name}",
                "timestamp": training.created_at.strftime("%Y-%m-%d %H:%M")
            })
        
        # Get recent training sessions
        recent_sessions = await db.execute(
            select(TrainingSessionModel)
            .join(TrainingModel, TrainingSessionModel.training_id == TrainingModel.id)
            .where(TrainingModel.trainer_id == trainer_id)
            .order_by(TrainingSessionModel.created_at.desc())
            .limit(3)
        )
        
        for session in recent_sessions.scalars():
            activities.append({
                "icon": "calendar-plus",
                "title": f"Created session: {session.name}",
                "timestamp": session.created_at.strftime("%Y-%m-%d %H:%M")
            })
        
        # Get recent learner sessions
        recent_learners = await db.execute(
            select(LearnerSessionModel)
            .join(TrainingSessionModel, LearnerSessionModel.training_session_id == TrainingSessionModel.id)
            .join(TrainingModel, TrainingSessionModel.training_id == TrainingModel.id)
            .where(TrainingModel.trainer_id == trainer_id)
            .order_by(LearnerSessionModel.started_at.desc())
            .limit(3)
        )
        
        for learner in recent_learners.scalars():
            activities.append({
                "icon": "person-plus",
                "title": f"New learner joined: {learner.email}",
                "timestamp": learner.started_at.strftime("%Y-%m-%d %H:%M")
            })
        
        # Sort all activities by timestamp (most recent first)
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Return top 5 most recent activities
        return activities[:5]
        
    except Exception as e:
        logger.error(f"Failed to get recent activity: {e}")
        # Return empty activity list on error
        return []