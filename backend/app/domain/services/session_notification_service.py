"""
FIA v3.0 - Session Notification Service
Domain service for sending notifications to learners about their training sessions
"""

import logging
from typing import Optional
from uuid import UUID

from app.domain.entities.learner_session import LearnerSession
from app.domain.entities.training_session import TrainingSession
from app.domain.entities.training import Training
from app.domain.ports.outbound_ports import EmailServicePort
from app.domain.ports.settings_port import SettingsPort
from app.domain.ports.repositories import (
    LearnerSessionRepositoryPort,
    TrainingSessionRepositoryPort,
    TrainingRepositoryPort
)

logger = logging.getLogger(__name__)


class SessionNotificationService:
    """Service for sending session-related notifications to learners"""
    
    def __init__(
        self,
        email_service: EmailServicePort,
        settings_port: SettingsPort,
        learner_session_repository: LearnerSessionRepositoryPort,
        training_session_repository: TrainingSessionRepositoryPort,
        training_repository: TrainingRepositoryPort
    ):
        """
        Initialize session notification service with dependencies
        
        Args:
            email_service: Email service port for sending notifications
            settings_port: Settings port for configuration access
            learner_session_repository: Repository for learner sessions
            training_session_repository: Repository for training sessions
            training_repository: Repository for trainings
        """
        self.email_service = email_service
        self.settings = settings_port
        self.learner_session_repository = learner_session_repository
        self.training_session_repository = training_session_repository
        self.training_repository = training_repository
        logger.info("📧 SESSION_NOTIFICATION [SERVICE] Initialized")
    
    async def send_resume_link_to_learner(
        self,
        learner_session_id: UUID,
        recipient_email: str,
        language: str = "fr"
    ) -> bool:
        """
        Send session resume link email to learner
        
        Args:
            learner_session_id: ID of the learner session
            recipient_email: Email address of the learner
            language: Language for the email content (fr/en)
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            logger.info(f"📧 SESSION_NOTIFICATION [START] Sending resume link to {recipient_email} (language: {language})")
            
            # Get learner session
            learner_session = await self.learner_session_repository.get_by_id(learner_session_id)
            if not learner_session:
                logger.error(f"❌ SESSION_NOTIFICATION [ERROR] LearnerSession {learner_session_id} not found")
                return False
            
            # Get training session
            training_session = await self.training_session_repository.get_by_id(learner_session.training_session_id)
            if not training_session:
                logger.error(f"❌ SESSION_NOTIFICATION [ERROR] TrainingSession {learner_session.training_session_id} not found")
                return False
            
            # Get training
            training = await self.training_repository.get_by_id(training_session.training_id)
            if not training:
                logger.error(f"❌ SESSION_NOTIFICATION [ERROR] Training {training_session.training_id} not found")
                return False
            
            # Build session link
            session_link = self._build_session_link(training_session.session_token)
            
            # Send email
            email_sent = await self.email_service.send_session_resume_link(
                recipient_email=recipient_email,
                session_link=session_link,
                training_name=training.name,
                language=language
            )
            
            if email_sent:
                logger.info(f"✅ SESSION_NOTIFICATION [SUCCESS] Resume link sent to {recipient_email}")
                return True
            else:
                logger.error(f"❌ SESSION_NOTIFICATION [ERROR] Failed to send resume link to {recipient_email}")
                return False
                
        except Exception as e:
            logger.error(f"❌ SESSION_NOTIFICATION [ERROR] Failed to send resume link: {str(e)}")
            return False
    
    async def send_resume_link_by_session_id(
        self,
        session_id: UUID,
        email: str,
        language: str = "fr"
    ) -> bool:
        """
        Send resume link using session ID (alternative method signature)
        
        Args:
            session_id: ID of the learner session
            email: Email address of the learner
            language: Language for the email content
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        return await self.send_resume_link_to_learner(
            learner_session_id=session_id,
            recipient_email=email,
            language=language
        )
    
    def _build_session_link(self, session_token: str) -> str:
        """
        Build session link from token
        
        Args:
            session_token: Session token
            
        Returns:
            Complete session URL
        """
        frontend_base_url = self.settings.get_frontend_url()
        return f"{frontend_base_url}/frontend/public/training.html?token={session_token}"