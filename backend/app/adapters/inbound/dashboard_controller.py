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
from app.infrastructure.models.training_slide_model import TrainingSlideModel
from app.infrastructure.models.training_submodule_model import TrainingSubmoduleModel
from app.infrastructure.models.training_module_model import TrainingModuleModel
from app.infrastructure.models.learner_training_plan_model import LearnerTrainingPlanModel
from app.infrastructure.models.chat_message_model import ChatMessageModel

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
        logger.info(f"Getting dashboard stats for trainer {trainer_id}")
        
        # Count trainings for this trainer
        trainings_result = await db.execute(
            select(func.count(TrainingModel.id))
            .where(TrainingModel.trainer_id == trainer_id)
        )
        trainings_count = trainings_result.scalar() or 0
        logger.info(f"Trainings count: {trainings_count}")
        
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
        logger.info(f"Active sessions count: {active_sessions_count}")
        
        # Count unique learners by email across all trainer's sessions
        unique_learners_result = await db.execute(
            select(func.count(func.distinct(LearnerSessionModel.email)))
            .join(TrainingSessionModel, LearnerSessionModel.training_session_id == TrainingSessionModel.id)
            .join(TrainingModel, TrainingSessionModel.training_id == TrainingModel.id)
            .where(TrainingModel.trainer_id == trainer_id)
        )
        unique_learners_count = unique_learners_result.scalar() or 0
        logger.info(f"Unique learners count: {unique_learners_count}")
        
        # Calculate total time spent by all learners (in hours)
        total_time_result = await db.execute(
            select(func.sum(LearnerSessionModel.total_time_spent))
            .join(TrainingSessionModel, LearnerSessionModel.training_session_id == TrainingSessionModel.id)
            .join(TrainingModel, TrainingSessionModel.training_id == TrainingModel.id)
            .where(TrainingModel.trainer_id == trainer_id)
        )
        total_time_seconds = total_time_result.scalar() or 0
        total_time_hours = int(total_time_seconds / 3600) if total_time_seconds else 0
        total_time_spent = f"{total_time_hours}h"
        logger.info(f"Total time spent: {total_time_seconds} seconds = {total_time_hours} hours")
        
        # Calculate total slides viewed (sum of current_slide_number)
        slides_viewed_result = await db.execute(
            select(func.sum(LearnerSessionModel.current_slide_number))
            .join(TrainingSessionModel, LearnerSessionModel.training_session_id == TrainingSessionModel.id)
            .join(TrainingModel, TrainingSessionModel.training_id == TrainingModel.id)
            .where(TrainingModel.trainer_id == trainer_id)
        )
        total_slides_viewed = slides_viewed_result.scalar() or 0
        logger.info(f"Total slides viewed: {total_slides_viewed}")
        
        # Count total slides with content for all trainer's trainings
        # Simplified approach: get slides for this trainer via learner sessions
        try:
            total_slides_result = await db.execute(
                select(func.count(TrainingSlideModel.id))
                .join(TrainingSubmoduleModel, TrainingSlideModel.submodule_id == TrainingSubmoduleModel.id)
                .join(TrainingModuleModel, TrainingSubmoduleModel.module_id == TrainingModuleModel.id)
                .join(LearnerTrainingPlanModel, TrainingModuleModel.plan_id == LearnerTrainingPlanModel.id)
                .join(LearnerSessionModel, LearnerTrainingPlanModel.learner_session_id == LearnerSessionModel.id)
                .join(TrainingSessionModel, LearnerSessionModel.training_session_id == TrainingSessionModel.id)
                .join(TrainingModel, TrainingSessionModel.training_id == TrainingModel.id)
                .where(
                    TrainingModel.trainer_id == trainer_id,
                    TrainingSlideModel.content.isnot(None)
                )
            )
            total_slides_count = total_slides_result.scalar() or 0
            logger.info(f"Total slides count: {total_slides_count}")
        except Exception as slides_error:
            logger.error(f"Error counting total slides: {slides_error}")
            total_slides_count = 0
        
        logger.info(f"Dashboard stats for trainer {trainer_id}: trainings={trainings_count}, sessions={active_sessions_count}, learners={unique_learners_count}, time={total_time_hours}h, slides_viewed={total_slides_viewed}, total_slides={total_slides_count}")
        
        return {
            "trainings_count": trainings_count,
            "active_sessions_count": active_sessions_count,
            "unique_learners_count": unique_learners_count,
            "total_time_spent": total_time_spent,
            "total_slides_viewed": total_slides_viewed,
            "total_slides_count": total_slides_count
        }
        
    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {e}")
        # Return default stats on error
        return {
            "trainings_count": 0,
            "active_sessions_count": 0,
            "unique_learners_count": 0,
            "total_time_spent": "0h",
            "total_slides_viewed": 0,
            "total_slides_count": 0
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


@router.get("/chat-history/{session_id}")
async def get_chat_history(
    session_id: str,
    current_trainer: TrainerModel = Depends(get_current_trainer),
    db: AsyncSession = Depends(get_database_session)
):
    """
    Get chat history for a specific training session
    
    Returns:
        List of chat messages with learner questions and AI responses
    """
    try:
        trainer_id = current_trainer.id
        logger.info(f"🔍 [DEBUG] Getting chat history for session {session_id} by trainer {trainer_id}")
        
        # STEP 1: Verify the session belongs to this trainer
        logger.info(f"🔍 [DEBUG] STEP 1: Verifying session ownership")
        session_result = await db.execute(
            select(TrainingSessionModel)
            .join(TrainingModel, TrainingSessionModel.training_id == TrainingModel.id)
            .where(
                TrainingSessionModel.id == session_id,
                TrainingModel.trainer_id == trainer_id
            )
        )
        session = session_result.scalar_one_or_none()
        
        if not session:
            logger.warning(f"❌ [DEBUG] Session {session_id} not found or access denied for trainer {trainer_id}")
            
            # EXTRA DEBUG: Check if session exists at all
            session_exists_result = await db.execute(
                select(TrainingSessionModel.id, TrainingModel.trainer_id)
                .join(TrainingModel, TrainingSessionModel.training_id == TrainingModel.id)
                .where(TrainingSessionModel.id == session_id)
            )
            session_exists = session_exists_result.first()
            
            if session_exists:
                logger.warning(f"❌ [DEBUG] Session exists but belongs to trainer {session_exists.trainer_id}, not {trainer_id}")
            else:
                logger.warning(f"❌ [DEBUG] Session {session_id} does not exist at all")
            
            return []
        
        logger.info(f"✅ [DEBUG] STEP 1: Session verified - belongs to trainer {trainer_id}")
        
        # STEP 2: Get learner sessions for this training session
        logger.info(f"🔍 [DEBUG] STEP 2: Getting learner sessions")
        learner_sessions_result = await db.execute(
            select(LearnerSessionModel)
            .where(LearnerSessionModel.training_session_id == session_id)
        )
        learner_sessions = learner_sessions_result.scalars().all()
        logger.info(f"📊 [DEBUG] Found {len(learner_sessions)} learner sessions")
        
        for ls in learner_sessions:
            logger.info(f"   - Learner session {ls.id} ({ls.email})")
        
        # STEP 3: Get chat messages for all learners in this session
        logger.info(f"🔍 [DEBUG] STEP 3: Getting chat messages")
        chat_messages_result = await db.execute(
            select(ChatMessageModel)
            .join(LearnerSessionModel, ChatMessageModel.learner_session_id == LearnerSessionModel.id)
            .where(LearnerSessionModel.training_session_id == session_id)
            .order_by(ChatMessageModel.created_at.asc())
        )
        chat_messages = chat_messages_result.scalars().all()
        logger.info(f"📊 [DEBUG] Raw query returned {len(chat_messages)} chat messages")
        
        # STEP 4: Alternative query - direct from chat_messages
        logger.info(f"🔍 [DEBUG] STEP 4: Alternative direct query")
        learner_session_ids = [str(ls.id) for ls in learner_sessions]
        if learner_session_ids:
            direct_messages_result = await db.execute(
                select(ChatMessageModel)
                .where(ChatMessageModel.learner_session_id.in_(learner_session_ids))
                .order_by(ChatMessageModel.created_at.asc())
            )
            direct_messages = direct_messages_result.scalars().all()
            logger.info(f"📊 [DEBUG] Direct query returned {len(direct_messages)} chat messages")
            
            for msg in direct_messages:
                logger.info(f"   - Message {msg.id}: \"{msg.message[:50] if msg.message else 'No message'}...\"")
                logger.info(f"     Response: \"{msg.response[:50] if msg.response else 'No response'}...\"")
                logger.info(f"     Learner session: {msg.learner_session_id}")
        
        # Format messages for display using the working query
        formatted_messages = []
        messages_to_use = direct_messages if learner_session_ids and len(direct_messages) > 0 else chat_messages
        
        logger.info(f"🔍 [DEBUG] STEP 5: Formatting {len(messages_to_use)} messages")
        for msg in messages_to_use:
            # Get learner email from learner session
            learner_email = "Unknown"
            for ls in learner_sessions:
                if str(ls.id) == str(msg.learner_session_id):
                    learner_email = ls.email
                    break
            
            formatted_message = {
                "id": str(msg.id),
                "learner_message": msg.message,
                "ai_response": msg.response,
                "message_type": msg.message_type,  # 'question' or 'answer'
                "created_at": msg.created_at.strftime("%Y-%m-%d %H:%M:%S") if msg.created_at else None,
                "learner_email": learner_email
            }
            formatted_messages.append(formatted_message)
            logger.info(f"   - Formatted message for {learner_email}")
        
        logger.info(f"✅ [DEBUG] Final result: {len(formatted_messages)} formatted messages for session {session_id}")
        return formatted_messages
        
    except Exception as e:
        logger.error(f"❌ [DEBUG] Failed to get chat history for session {session_id}: {e}")
        import traceback
        logger.error(f"❌ [DEBUG] Traceback: {traceback.format_exc()}")
        return []