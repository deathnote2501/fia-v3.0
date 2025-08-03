"""
FIA v3.0 - Session Type Detection Service
Service for detecting session type (B2C vs B2B) based on session token
"""

import logging
import time
from typing import Optional
from app.domain.ports.repositories import (
    TrainingSessionRepositoryPort,
    TrainingRepositoryPort, 
    TrainerRepositoryPort
)

logger = logging.getLogger(__name__)


class SessionTypeDetectionService:
    """Service for detecting session type (B2C vs B2B) based on trainer ownership"""
    
    # Anonymous trainer identifier for B2C sessions
    ANONYMOUS_TRAINER_EMAIL = "anonymous@fia-v3.system"
    
    def __init__(
        self, 
        training_session_repository: TrainingSessionRepositoryPort,
        training_repository: TrainingRepositoryPort,
        trainer_repository: TrainerRepositoryPort
    ):
        self.training_session_repo = training_session_repository
        self.training_repo = training_repository  
        self.trainer_repo = trainer_repository
    
    async def detect_session_type(self, token: str) -> str:
        """
        Detect if session is B2C or B2B based on trainer type
        
        Args:
            token: Session token to analyze
            
        Returns:
            "B2C" if session created by anonymous trainer (from landing page)
            "B2B" if session created by authenticated trainer
            
        Raises:
            ValueError: If token is invalid or session not found
        """
        start_time = time.time()
        
        try:
            logger.info(f"🔍 SESSION_TYPE_DETECTION [START] Analyzing token: {token[:8]}...")
            
            # Step 1: Get training session by token
            training_session = await self.training_session_repo.get_by_token(token)
            if not training_session:
                raise ValueError(f"Invalid session token: {token}")
            
            logger.debug(f"🎯 SESSION_TYPE_DETECTION [SESSION] Found training_session: {training_session.id}")
            
            # Step 2: Get training by training_id
            training = await self.training_repo.get_by_id(training_session.training_id)
            if not training:
                raise ValueError(f"Training not found for session: {training_session.id}")
            
            logger.debug(f"📚 SESSION_TYPE_DETECTION [TRAINING] Found training: {training.id} (trainer: {training.trainer_id})")
            
            # Step 3: Get trainer by trainer_id
            trainer = await self.trainer_repo.get_by_id(training.trainer_id)
            if not trainer:
                raise ValueError(f"Trainer not found: {training.trainer_id}")
            
            logger.debug(f"👤 SESSION_TYPE_DETECTION [TRAINER] Found trainer: {trainer.email}")
            
            # Step 4: Determine session type based on trainer email
            session_type = "B2C" if trainer.email == self.ANONYMOUS_TRAINER_EMAIL else "B2B"
            
            duration = time.time() - start_time
            logger.info(f"✅ SESSION_TYPE_DETECTION [SUCCESS] Session type: {session_type} (duration: {duration:.2f}s)")
            
            return session_type
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ SESSION_TYPE_DETECTION [ERROR] Failed after {duration:.2f}s: {e}")
            raise ValueError(f"Session type detection failed: {e}")
    
    async def is_b2c_session(self, token: str) -> bool:
        """
        Convenience method to check if session is B2C
        
        Args:
            token: Session token to check
            
        Returns:
            True if session is B2C (anonymous trainer), False otherwise
        """
        try:
            session_type = await self.detect_session_type(token)
            return session_type == "B2C"
        except Exception:
            # Default to B2B (safer assumption for paid features)
            return False
    
    async def get_session_limits(self, token: str) -> dict:
        """
        Get session limits based on session type
        
        Args:
            token: Session token to analyze
            
        Returns:
            Dictionary with session limits and metadata
        """
        try:
            session_type = await self.detect_session_type(token)
            
            if session_type == "B2C":
                return {
                    "session_type": "B2C",
                    "max_slides": 2,
                    "has_slide_limit": True,
                    "upgrade_required": True,
                    "contact_email": "jerome.iavarone@gmail.com"
                }
            else:
                return {
                    "session_type": "B2B", 
                    "max_slides": None,
                    "has_slide_limit": False,
                    "upgrade_required": False,
                    "contact_email": None
                }
                
        except Exception as e:
            logger.warning(f"⚠️ SESSION_TYPE_DETECTION [WARNING] Failed to get limits for {token}: {e}")
            # Default to B2B limits (safer)
            return {
                "session_type": "B2B",
                "max_slides": None, 
                "has_slide_limit": False,
                "upgrade_required": False,
                "contact_email": None
            }