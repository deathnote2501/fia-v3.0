"""
FIA v3.0 - Admin Dashboard Service
Business logic for admin dashboard statistics and trainer overview
"""

import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.repositories.admin_repository import AdminRepository


logger = logging.getLogger(__name__)


class AdminDashboardService:
    """Service for admin dashboard operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.admin_repository = AdminRepository(session)
    
    async def get_trainers_overview(self) -> List[Dict[str, Any]]:
        """
        Get comprehensive overview of all trainers with their statistics
        
        Returns:
            List of trainer dictionaries with complete statistics
        """
        try:
            logger.info("Fetching trainers overview statistics")
            
            trainers_stats = await self.admin_repository.get_trainers_overview_statistics()
            
            logger.info(f"Successfully retrieved statistics for {len(trainers_stats)} trainers")
            
            return trainers_stats
            
        except Exception as e:
            logger.error(f"Failed to get trainers overview: {str(e)}")
            raise
    
    async def get_trainees_overview(self) -> List[Dict[str, Any]]:
        """
        Get comprehensive overview of all trainees with their learning statistics
        
        Returns:
            List of trainee dictionaries with complete learning statistics
        """
        try:
            logger.info("Fetching trainees overview statistics")
            
            trainees_stats = await self.admin_repository.get_trainees_overview_statistics()
            
            logger.info(f"Successfully retrieved statistics for {len(trainees_stats)} trainees")
            
            return trainees_stats
            
        except Exception as e:
            logger.error(f"Failed to get trainees overview: {str(e)}")
            raise
    
    async def get_trainings_overview(self) -> List[Dict[str, Any]]:
        """
        Get comprehensive overview of all trainings with their statistics
        
        Returns:
            List of training dictionaries with complete statistics
        """
        try:
            logger.info("Fetching trainings overview statistics")
            
            trainings_stats = await self.admin_repository.get_trainings_overview_statistics()
            
            logger.info(f"Successfully retrieved statistics for {len(trainings_stats)} trainings")
            
            return trainings_stats
            
        except Exception as e:
            logger.error(f"Failed to get trainings overview: {str(e)}")
            raise
    
    async def get_sessions_overview(self) -> List[Dict[str, Any]]:
        """
        Get comprehensive overview of all training sessions with their statistics
        
        Returns:
            List of session dictionaries with complete statistics
        """
        try:
            logger.info("Fetching sessions overview statistics")
            
            sessions_stats = await self.admin_repository.get_sessions_overview_statistics()
            
            logger.info(f"Successfully retrieved statistics for {len(sessions_stats)} sessions")
            
            return sessions_stats
            
        except Exception as e:
            logger.error(f"Failed to get sessions overview: {str(e)}")
            raise
    
    async def get_global_statistics(self) -> Dict[str, Any]:
        """
        Get global platform statistics for admin dashboard
        
        Returns:
            Dictionary with global platform statistics
        """
        try:
            logger.info("Fetching global admin statistics")
            
            global_stats = await self.admin_repository.get_global_admin_statistics()
            
            logger.info("Successfully retrieved global admin statistics")
            
            return global_stats
            
        except Exception as e:
            logger.error(f"Failed to get global statistics: {str(e)}")
            raise
    
    async def get_trainer_detailed_stats(self, trainer_id: str) -> Dict[str, Any]:
        """
        Get detailed statistics for a specific trainer
        
        Args:
            trainer_id: UUID of the trainer
            
        Returns:
            Dictionary with detailed trainer statistics
        """
        try:
            logger.info(f"Fetching detailed statistics for trainer {trainer_id}")
            
            # For now, get the trainer from the overview and return it
            # In the future, this could be expanded with more detailed metrics
            trainers_overview = await self.admin_repository.get_trainers_overview_statistics()
            
            trainer_stats = next(
                (trainer for trainer in trainers_overview if trainer['id'] == trainer_id),
                None
            )
            
            if not trainer_stats:
                raise ValueError(f"Trainer with ID {trainer_id} not found")
            
            # Could add additional detailed metrics here:
            # - Monthly activity trends
            # - Most popular trainings
            # - Learner engagement metrics
            # - Chat interaction statistics
            
            logger.info(f"Successfully retrieved detailed statistics for trainer {trainer_id}")
            
            return trainer_stats
            
        except Exception as e:
            logger.error(f"Failed to get detailed trainer stats for {trainer_id}: {str(e)}")
            raise
    
    async def get_platform_health_metrics(self) -> Dict[str, Any]:
        """
        Get platform health and performance metrics
        
        Returns:
            Dictionary with platform health metrics
        """
        try:
            logger.info("Fetching platform health metrics")
            
            # Get basic global stats
            global_stats = await self.admin_repository.get_global_admin_statistics()
            
            # Calculate health metrics
            activity_rate = 0
            if global_stats['total_trainers'] > 0:
                activity_rate = (global_stats['active_trainers'] / global_stats['total_trainers']) * 100
            
            session_utilization = 0
            if global_stats['total_sessions'] > 0:
                session_utilization = (global_stats['active_sessions'] / global_stats['total_sessions']) * 100
            
            ai_adoption_rate = 0
            if global_stats['total_trainings'] > 0:
                ai_adoption_rate = (global_stats['total_ai_trainings'] / global_stats['total_trainings']) * 100
            
            health_metrics = {
                **global_stats,
                "trainer_activity_rate": round(activity_rate, 1),
                "session_utilization_rate": round(session_utilization, 1),
                "ai_adoption_rate": round(ai_adoption_rate, 1),
                "avg_learners_per_trainer": round(global_stats['total_learners'] / max(global_stats['active_trainers'], 1), 1),
                "avg_sessions_per_trainer": round(global_stats['total_sessions'] / max(global_stats['total_trainers'], 1), 1),
                "avg_slides_per_trainer": round(global_stats['total_slides'] / max(global_stats['total_trainers'], 1), 1)
            }
            
            logger.info("Successfully calculated platform health metrics")
            
            return health_metrics
            
        except Exception as e:
            logger.error(f"Failed to get platform health metrics: {str(e)}")
            raise