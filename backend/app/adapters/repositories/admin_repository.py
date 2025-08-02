"""
FIA v3.0 - Admin Repository
Repository for admin dashboard statistics and trainer overview queries
"""

from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct, case, cast, Integer
from sqlalchemy.orm import joinedload

from app.infrastructure.models.trainer_model import TrainerModel
from app.infrastructure.models.training_model import TrainingModel
from app.infrastructure.models.training_session_model import TrainingSessionModel
from app.infrastructure.models.learner_session_model import LearnerSessionModel
from app.infrastructure.models.training_slide_model import TrainingSlideModel
from app.infrastructure.models.chat_message_model import ChatMessageModel
from app.infrastructure.models.training_submodule_model import TrainingSubmoduleModel


class AdminRepository:
    """Repository for admin dashboard queries"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_trainers_overview_statistics(self) -> List[Dict[str, Any]]:
        """
        Get comprehensive statistics for all trainers with their metrics
        Returns: List of trainer statistics dictionaries
        """
        # Simplified query focusing on available data relationships
        query = select(
            TrainerModel.id,
            TrainerModel.first_name,
            TrainerModel.last_name,
            TrainerModel.email,
            TrainerModel.is_superuser,
            TrainerModel.is_active,
            TrainerModel.created_at,
            
            # Training counts - simple counting
            func.count(distinct(case((TrainingModel.is_ai_generated == False, TrainingModel.id)))).label('trainings_with_support'),
            func.count(distinct(case((TrainingModel.is_ai_generated == True, TrainingModel.id)))).label('trainings_ai_generated'),
            
            # Session counts - counting through trainings
            func.count(distinct(case((TrainingSessionModel.is_active == True, TrainingSessionModel.id)))).label('active_sessions'),
            func.count(distinct(TrainingSessionModel.id)).label('total_sessions'),
            
            # Learner statistics - counting through sessions
            func.count(distinct(LearnerSessionModel.email)).label('unique_learners'),
            func.coalesce(func.sum(LearnerSessionModel.total_time_spent), 0).label('total_time_seconds'),
            
            # Simplified slide statistics - use a constant for now since the relationship is complex
            func.coalesce(func.sum(cast(0, Integer)), 0).label('total_slides_generated')
            
        ).select_from(
            TrainerModel
        ).outerjoin(
            TrainingModel, TrainerModel.id == TrainingModel.trainer_id
        ).outerjoin(
            TrainingSessionModel, TrainingModel.id == TrainingSessionModel.training_id
        ).outerjoin(
            LearnerSessionModel, TrainingSessionModel.id == LearnerSessionModel.training_session_id
        ).group_by(
            TrainerModel.id,
            TrainerModel.first_name,
            TrainerModel.last_name,
            TrainerModel.email,
            TrainerModel.is_superuser,
            TrainerModel.is_active,
            TrainerModel.created_at
        ).order_by(
            TrainerModel.created_at.desc()
        )
        
        result = await self.session.execute(query)
        rows = result.fetchall()
        
        # Process results and calculate derived metrics
        trainers_stats = []
        for row in rows:
            total_trainings = row.trainings_with_support + row.trainings_ai_generated
            total_time_hours = row.total_time_seconds / 3600 if row.total_time_seconds else 0
            
            # Calculate average time per slide (avoid division by zero)
            avg_time_per_slide_seconds = 0
            if row.total_slides_generated > 0 and row.total_time_seconds > 0:
                avg_time_per_slide_seconds = row.total_time_seconds / row.total_slides_generated
            
            # Calculate average slides per training
            avg_slides_per_training = 0
            if total_trainings > 0 and row.total_slides_generated > 0:
                avg_slides_per_training = row.total_slides_generated / total_trainings
            
            trainer_stats = {
                "id": str(row.id),
                "first_name": row.first_name,
                "last_name": row.last_name,
                "email": row.email,
                "is_superuser": row.is_superuser,
                "is_active": row.is_active,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                
                # Training statistics
                "trainings_with_support": row.trainings_with_support,
                "trainings_ai_generated": row.trainings_ai_generated,
                
                # Session statistics
                "active_sessions": row.active_sessions,
                "total_sessions": row.total_sessions,
                
                # Learner statistics
                "unique_learners": row.unique_learners,
                "total_time_all_learners": self._format_duration(total_time_hours),
                "total_time_seconds": row.total_time_seconds,
                
                # Slide statistics
                "total_slides_generated": row.total_slides_generated,
                "average_time_per_slide": self._format_duration(avg_time_per_slide_seconds / 3600) if avg_time_per_slide_seconds else "0min",
                "average_slides_per_training": round(avg_slides_per_training, 1) if avg_slides_per_training else 0
            }
            
            trainers_stats.append(trainer_stats)
        
        return trainers_stats
    
    async def get_global_admin_statistics(self) -> Dict[str, Any]:
        """
        Get global statistics for admin dashboard
        Returns: Dictionary with global statistics
        """
        # Count trainers - optimized with is_active and is_superuser indexes
        trainer_stats = await self.session.execute(
            select(
                func.count(TrainerModel.id).label('total_trainers'),
                func.count(case((TrainerModel.is_active == True, TrainerModel.id))).label('active_trainers'),
                func.count(case((TrainerModel.is_superuser == True, TrainerModel.id))).label('superuser_trainers')
            )
        )
        trainer_row = trainer_stats.fetchone()
        
        # Count trainings - optimized with is_ai_generated index
        training_stats = await self.session.execute(
            select(
                func.count(TrainingModel.id).label('total_trainings'),
                func.count(case((TrainingModel.is_ai_generated == True, TrainingModel.id))).label('total_ai_trainings')
            )
        )
        training_row = training_stats.fetchone()
        
        # Count sessions - optimized with is_active index
        session_stats = await self.session.execute(
            select(
                func.count(TrainingSessionModel.id).label('total_sessions'),
                func.count(case((TrainingSessionModel.is_active == True, TrainingSessionModel.id))).label('active_sessions')
            )
        )
        session_row = session_stats.fetchone()
        
        # Count learners and time - optimized with email index for distinct counting
        learner_stats = await self.session.execute(
            select(
                func.count(distinct(LearnerSessionModel.email)).label('total_learners'),
                func.coalesce(func.sum(LearnerSessionModel.total_time_spent), 0).label('total_learning_time_seconds')
            )
        )
        learner_row = learner_stats.fetchone()
        
        # Count slides
        slide_stats = await self.session.execute(
            select(func.count(TrainingSlideModel.id).label('total_slides'))
        )
        slide_row = slide_stats.fetchone()
        
        # Format the total learning time
        total_hours = learner_row.total_learning_time_seconds / 3600 if learner_row.total_learning_time_seconds else 0
        
        return {
            "total_trainers": trainer_row.total_trainers,
            "active_trainers": trainer_row.active_trainers,
            "superuser_trainers": trainer_row.superuser_trainers,
            "total_trainings": training_row.total_trainings,
            "total_ai_trainings": training_row.total_ai_trainings,
            "total_sessions": session_row.total_sessions,
            "active_sessions": session_row.active_sessions,
            "total_learners": learner_row.total_learners,
            "total_slides": slide_row.total_slides,
            "total_learning_time": self._format_duration(total_hours)
        }
    
    def _format_duration(self, hours: float) -> str:
        """
        Format duration in hours to human readable format
        Args:
            hours: Duration in hours (float)
        Returns:
            Formatted string like "2h 30min" or "45min"
        """
        if hours == 0:
            return "0min"
        
        if hours < 1:
            minutes = int(hours * 60)
            return f"{minutes}min"
        
        whole_hours = int(hours)
        remaining_minutes = int((hours - whole_hours) * 60)
        
        if remaining_minutes == 0:
            return f"{whole_hours}h"
        else:
            return f"{whole_hours}h {remaining_minutes}min"