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
from app.domain.services.admin_dashboard_service import AdminDashboardService

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/admin", tags=["Admin"])


async def get_current_admin_trainer(
    current_trainer: Trainer = Depends(get_current_trainer)
) -> Trainer:
    """Dependency to ensure current trainer has admin privileges"""
    logger.info(f"Admin check for trainer: {current_trainer.email}, superuser: {current_trainer.is_superuser}, active: {current_trainer.is_active}")
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
    Get overview of all trainers with their complete statistics
    """
    logger.info(f"Admin {admin_trainer.email} requested trainers overview")
    
    try:
        # Use the admin dashboard service to get real statistics
        admin_service = AdminDashboardService(session)
        trainers_overview = await admin_service.get_trainers_overview()
        
        logger.info(f"Successfully retrieved overview for {len(trainers_overview)} trainers")
        return trainers_overview
        
    except Exception as e:
        logger.error(f"Failed to get trainers overview: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve trainers overview")


@router.get("/trainees-overview")
async def get_trainees_overview(
    admin_trainer: Trainer = Depends(get_current_admin_trainer),
    session: AsyncSession = Depends(get_database_session)
) -> List[Dict[str, Any]]:
    """
    Get overview of all trainees with their learning statistics
    """
    logger.info(f"Admin {admin_trainer.email} requested trainees overview")
    
    try:
        # Use the admin dashboard service to get trainees statistics
        admin_service = AdminDashboardService(session)
        trainees_overview = await admin_service.get_trainees_overview()
        
        logger.info(f"Successfully retrieved overview for {len(trainees_overview)} trainees")
        return trainees_overview
        
    except Exception as e:
        logger.error(f"Failed to get trainees overview: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve trainees overview")


@router.get("/stats")
async def get_admin_stats(
    admin_trainer: Trainer = Depends(get_current_admin_trainer),
    session: AsyncSession = Depends(get_database_session)
) -> Dict[str, Any]:
    """
    Get global admin statistics
    """
    logger.info(f"Admin {admin_trainer.email} requested admin stats")
    
    try:
        # Use the admin dashboard service to get real global statistics
        admin_service = AdminDashboardService(session)
        global_stats = await admin_service.get_global_statistics()
        
        logger.info("Successfully retrieved admin stats")
        return global_stats
        
    except Exception as e:
        logger.error(f"Failed to get admin stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve admin statistics")


@router.get("/health")
async def get_platform_health(
    admin_trainer: Trainer = Depends(get_current_admin_trainer),
    session: AsyncSession = Depends(get_database_session)
) -> Dict[str, Any]:
    """
    Get platform health and performance metrics
    """
    logger.info(f"Admin {admin_trainer.email} requested platform health metrics")
    
    try:
        admin_service = AdminDashboardService(session)
        health_metrics = await admin_service.get_platform_health_metrics()
        
        logger.info("Successfully retrieved platform health metrics")
        return health_metrics
        
    except Exception as e:
        logger.error(f"Failed to get platform health metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve platform health metrics")


@router.get("/trainers/{trainer_id}/details")
async def get_trainer_details(
    trainer_id: str,
    admin_trainer: Trainer = Depends(get_current_admin_trainer),
    session: AsyncSession = Depends(get_database_session)
) -> Dict[str, Any]:
    """
    Get detailed statistics for a specific trainer
    """
    logger.info(f"Admin {admin_trainer.email} requested details for trainer {trainer_id}")
    
    try:
        admin_service = AdminDashboardService(session)
        trainer_details = await admin_service.get_trainer_detailed_stats(trainer_id)
        
        logger.info(f"Successfully retrieved details for trainer {trainer_id}")
        return trainer_details
        
    except ValueError as e:
        logger.warning(f"Trainer not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get trainer details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve trainer details")