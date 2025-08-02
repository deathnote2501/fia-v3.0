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
    
    async def get_trainees_overview_statistics(self) -> List[Dict[str, Any]]:
        """
        Get comprehensive statistics for all trainees with their learning metrics
        Returns: List of trainee statistics dictionaries
        """
        # Simplify the query to avoid complex subqueries that may cause errors
        query = select(
            LearnerSessionModel.email,
            LearnerSessionModel.experience_level,
            LearnerSessionModel.job_position,
            LearnerSessionModel.activity_sector,
            LearnerSessionModel.objectives,
            LearnerSessionModel.enriched_profile,
            
            # Count total sessions for this learner
            func.count(distinct(LearnerSessionModel.training_session_id)).label('total_sessions'),
            
            # Total slides viewed - using current_slide_number as proxy
            func.coalesce(func.max(LearnerSessionModel.current_slide_number), 0).label('total_slides_viewed'),
            
            # Total time spent across all sessions
            func.coalesce(func.sum(LearnerSessionModel.total_time_spent), 0).label('total_time_seconds')
            
        ).select_from(
            LearnerSessionModel
        ).group_by(
            LearnerSessionModel.email,
            LearnerSessionModel.experience_level,
            LearnerSessionModel.job_position,
            LearnerSessionModel.activity_sector,
            LearnerSessionModel.objectives,
            LearnerSessionModel.enriched_profile
        ).order_by(
            LearnerSessionModel.email
        )
        
        result = await self.session.execute(query)
        rows = result.fetchall()
        
        # Process results and format data
        trainees_stats = []
        for row in rows:
            # Format job and sector
            job_sector = []
            if row.job_position:
                job_sector.append(row.job_position)
            if row.activity_sector:
                job_sector.append(row.activity_sector)
            job_sector_str = " - ".join(job_sector) if job_sector else "N/A"
            
            # For now, set placeholder values for AI vs trainer sessions
            # This would require a separate query to get training type information
            ai_sessions = 0  # Placeholder
            trainer_sessions = row.total_sessions  # Placeholder
            
            # Format total time
            total_time_hours = row.total_time_seconds / 3600 if row.total_time_seconds else 0
            
            trainee_stats = {
                "email": row.email,
                "level": row.experience_level or "N/A",
                "job_sector": job_sector_str,
                "objective": row.objectives or "N/A",
                "enriched_profile": row.enriched_profile,
                "total_sessions": row.total_sessions,
                "ai_sessions": ai_sessions,
                "trainer_sessions": trainer_sessions,
                "total_time": self._format_duration(total_time_hours),
                "total_slides_viewed": row.total_slides_viewed
            }
            
            trainees_stats.append(trainee_stats)
        
        return trainees_stats
    
    async def get_trainings_overview_statistics(self) -> List[Dict[str, Any]]:
        """
        Get comprehensive statistics for all trainings with their metrics
        Returns: List of training statistics dictionaries
        """
        query = select(
            TrainingModel.id.label('training_id'),
            TrainingModel.name.label('training_name'),
            TrainingModel.is_ai_generated,
            
            # Count sessions for this training
            func.count(distinct(TrainingSessionModel.id)).label('total_sessions'),
            
            # Count unique learners across all sessions of this training
            func.count(distinct(LearnerSessionModel.email)).label('total_learners'),
            
            # Sum total time across all learner sessions for this training
            func.coalesce(func.sum(LearnerSessionModel.total_time_spent), 0).label('total_time_seconds'),
            
            # Get max slides viewed (proxy for total slides in training)
            func.coalesce(func.max(LearnerSessionModel.current_slide_number), 0).label('total_slides')
            
        ).select_from(
            TrainingModel
        ).outerjoin(
            TrainingSessionModel, TrainingModel.id == TrainingSessionModel.training_id
        ).outerjoin(
            LearnerSessionModel, TrainingSessionModel.id == LearnerSessionModel.training_session_id
        ).group_by(
            TrainingModel.id,
            TrainingModel.name,
            TrainingModel.is_ai_generated
        ).order_by(
            TrainingModel.name
        )
        
        result = await self.session.execute(query)
        rows = result.fetchall()
        
        # Process results and format data
        trainings_stats = []
        for row in rows:
            # Determine training type
            training_type = "IA" if row.is_ai_generated else "Humain"
            
            # Calculate averages
            avg_time_per_session_seconds = 0
            avg_slides_per_session = 0
            
            if row.total_sessions > 0:
                avg_time_per_session_seconds = row.total_time_seconds / row.total_sessions
                avg_slides_per_session = row.total_slides / row.total_sessions
            
            # Format total time
            total_time_hours = row.total_time_seconds / 3600 if row.total_time_seconds else 0
            avg_time_hours = avg_time_per_session_seconds / 3600 if avg_time_per_session_seconds else 0
            
            training_stats = {
                "training_id": str(row.training_id),
                "training_name": row.training_name,
                "training_type": training_type,
                "total_learners": row.total_learners,
                "total_sessions": row.total_sessions,
                "total_time": self._format_duration(total_time_hours),
                "avg_time_per_session": self._format_duration(avg_time_hours),
                "total_slides": row.total_slides,
                "avg_slides_per_session": round(avg_slides_per_session, 1) if avg_slides_per_session else 0
            }
            
            trainings_stats.append(training_stats)
        
        return trainings_stats
    
    async def get_sessions_overview_statistics(self) -> List[Dict[str, Any]]:
        """
        Get comprehensive statistics for all training sessions with their metrics
        Returns: List of session statistics dictionaries
        """
        query = select(
            TrainingSessionModel.id.label('session_id'),
            TrainingSessionModel.name.label('session_name'),
            TrainingSessionModel.is_active,
            TrainingSessionModel.created_at.label('session_date'),
            TrainingModel.name.label('training_name'),
            TrainingModel.is_ai_generated,
            
            # Count learners for this session
            func.count(distinct(LearnerSessionModel.email)).label('total_learners'),
            
            # Get max slides for this session (proxy for total slides)
            func.coalesce(func.max(LearnerSessionModel.current_slide_number), 0).label('total_slides'),
            
            # Get average current slide number for progress calculation
            func.coalesce(func.avg(LearnerSessionModel.current_slide_number), 0).label('avg_current_slide')
            
        ).select_from(
            TrainingSessionModel
        ).join(
            TrainingModel, TrainingSessionModel.training_id == TrainingModel.id
        ).outerjoin(
            LearnerSessionModel, TrainingSessionModel.id == LearnerSessionModel.training_session_id
        ).group_by(
            TrainingSessionModel.id,
            TrainingSessionModel.name,
            TrainingSessionModel.is_active,
            TrainingSessionModel.created_at,
            TrainingModel.name,
            TrainingModel.is_ai_generated
        ).order_by(
            TrainingSessionModel.created_at.desc()
        )
        
        result = await self.session.execute(query)
        rows = result.fetchall()
        
        # Process results and format data
        sessions_stats = []
        for row in rows:
            # Determine training type and status
            training_type = "IA" if row.is_ai_generated else "Humain"
            status = "Active" if row.is_active else "Inactive"
            
            # Calculate progress percentage (simple calculation)
            progress_percentage = 0
            if row.total_slides > 0 and row.avg_current_slide > 0:
                progress_percentage = min(100, (row.avg_current_slide / row.total_slides) * 100)
            
            # For token costs, use placeholder values for now
            # In a real implementation, these would come from API logs or a dedicated token tracking system
            input_tokens = row.total_learners * 150  # Placeholder calculation
            output_tokens = row.total_learners * 75   # Placeholder calculation
            cost_per_input_token = 0.00000125  # Gemini Flash pricing
            cost_per_output_token = 0.00000375  # Gemini Flash pricing
            total_cost = (input_tokens * cost_per_input_token) + (output_tokens * cost_per_output_token)
            
            session_stats = {
                "session_id": str(row.session_id),
                "session_name": row.session_name,
                "training_name": row.training_name,
                "training_type": training_type,
                "session_date": row.session_date.isoformat() if row.session_date else None,
                "status": status,
                "total_slides": row.total_slides,
                "progress_percentage": round(progress_percentage, 1),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "token_cost": f"${total_cost:.4f}"
            }
            
            sessions_stats.append(session_stats)
        
        return sessions_stats
    
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