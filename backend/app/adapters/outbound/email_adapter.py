"""
FIA v3.0 - Email Outbound Adapter
Implementation of email service interactions via Brevo
"""

import logging
from typing import Dict, Any
import aiohttp

from app.domain.ports.outbound_ports import EmailServicePort
from app.infrastructure.settings import settings


logger = logging.getLogger(__name__)


class EmailAdapter(EmailServicePort):
    """Outbound adapter for email service using Brevo"""
    
    def __init__(self):
        self.api_key = settings.brevo_api_key
        self.api_url = "https://api.brevo.com/v3/smtp/email"
        self.sender_email = settings.brevo_sender_email
        self.sender_name = settings.brevo_sender_name
        
    async def send_session_invitation(
        self,
        recipient_email: str,
        session_link: str,
        training_name: str,
        trainer_name: str
    ) -> bool:
        """Send session invitation email to learner"""
        try:
            subject = f"Training Invitation: {training_name}"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Training Invitation</title>
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #0d6efd;">Training Invitation</h2>
                    
                    <p>Hello,</p>
                    
                    <p>You have been invited by <strong>{trainer_name}</strong> to participate in the training:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin: 0; color: #0d6efd;">{training_name}</h3>
                    </div>
                    
                    <p>To start your personalized learning experience, please click the link below:</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{session_link}" 
                           style="background-color: #0d6efd; color: white; padding: 12px 30px; 
                                  text-decoration: none; border-radius: 5px; display: inline-block;">
                            Start Training Session
                        </a>
                    </div>
                    
                    <p>This link will take you to a personalized training experience adapted to your profile and learning style.</p>
                    
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
                    
                    <p style="font-size: 12px; color: #6c757d;">
                        This email was sent by FIA v3.0 - AI-Powered E-Learning Platform<br>
                        If you have any questions, please contact your trainer: {trainer_name}
                    </p>
                </div>
            </body>
            </html>
            """
            
            email_data = {
                "sender": {
                    "name": self.sender_name,
                    "email": self.sender_email
                },
                "to": [
                    {
                        "email": recipient_email,
                        "name": "Learner"
                    }
                ],
                "subject": subject,
                "htmlContent": html_content
            }
            
            success = await self._send_email(email_data)
            
            if success:
                logger.info(f"Session invitation sent successfully to {recipient_email}")
            else:
                logger.error(f"Failed to send session invitation to {recipient_email}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending session invitation: {str(e)}")
            return False
    
    async def send_completion_certificate(
        self,
        recipient_email: str,
        learner_name: str,
        training_name: str,
        completion_date: str
    ) -> bool:
        """Send training completion certificate"""
        try:
            subject = f"Training Completion Certificate: {training_name}"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Training Completion Certificate</title>
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #28a745; margin-bottom: 10px;">🎉 Congratulations!</h1>
                        <h2 style="color: #0d6efd;">Training Completion Certificate</h2>
                    </div>
                    
                    <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px; 
                                border-left: 5px solid #28a745; margin: 20px 0;">
                        <p style="font-size: 18px; margin-bottom: 15px;">
                            This certifies that
                        </p>
                        <h3 style="color: #0d6efd; margin: 10px 0; font-size: 24px;">
                            {learner_name}
                        </h3>
                        <p style="font-size: 18px; margin: 15px 0;">
                            has successfully completed the training:
                        </p>
                        <h4 style="color: #28a745; margin: 10px 0; font-size: 20px;">
                            {training_name}
                        </h4>
                        <p style="margin-top: 20px; color: #6c757d;">
                            Completion Date: {completion_date}
                        </p>
                    </div>
                    
                    <p>You have successfully completed all modules and demonstrated mastery of the training content. 
                       This achievement reflects your dedication to continuous learning and professional development.</p>
                    
                    <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p style="margin: 0; font-weight: bold; color: #0d6efd;">
                            ✨ Keep learning and growing in your professional journey!
                        </p>
                    </div>
                    
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
                    
                    <p style="font-size: 12px; color: #6c757d;">
                        Certificate generated by FIA v3.0 - AI-Powered E-Learning Platform<br>
                        This is an automated certificate based on your training completion.
                    </p>
                </div>
            </body>
            </html>
            """
            
            email_data = {
                "sender": {
                    "name": self.sender_name,
                    "email": self.sender_email
                },
                "to": [
                    {
                        "email": recipient_email,
                        "name": learner_name
                    }
                ],
                "subject": subject,
                "htmlContent": html_content
            }
            
            success = await self._send_email(email_data)
            
            if success:
                logger.info(f"Completion certificate sent successfully to {recipient_email}")
            else:
                logger.error(f"Failed to send completion certificate to {recipient_email}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending completion certificate: {str(e)}")
            return False
    
    async def send_trainer_notification(
        self,
        trainer_email: str,
        notification_type: str,
        data: Dict[str, Any]
    ) -> bool:
        """Send notification to trainer"""
        try:
            subject_map = {
                "session_completed": "Learner Completed Training Session",
                "new_session_started": "New Training Session Started",
                "engagement_alert": "Learner Engagement Alert"
            }
            
            subject = subject_map.get(notification_type, "Training Platform Notification")
            
            html_content = self._build_trainer_notification_content(notification_type, data)
            
            email_data = {
                "sender": {
                    "name": self.sender_name,
                    "email": self.sender_email
                },
                "to": [
                    {
                        "email": trainer_email,
                        "name": "Trainer"
                    }
                ],
                "subject": subject,
                "htmlContent": html_content
            }
            
            success = await self._send_email(email_data)
            
            if success:
                logger.info(f"Trainer notification sent successfully to {trainer_email}")
            else:
                logger.error(f"Failed to send trainer notification to {trainer_email}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending trainer notification: {str(e)}")
            return False
    
    async def send_session_resume_link(
        self,
        recipient_email: str,
        session_link: str,
        training_name: str,
        language: str = "fr"
    ) -> bool:
        """Send session resume link email to learner"""
        try:
            # Build i18n email content based on learner language
            email_content = self._build_resume_link_content(
                session_link, training_name, language
            )
            
            subject = email_content["subject"]
            html_content = email_content["html_content"]
            
            email_data = {
                "sender": {
                    "name": self.sender_name,
                    "email": self.sender_email
                },
                "to": [
                    {
                        "email": recipient_email,
                        "name": "Learner"
                    }
                ],
                "subject": subject,
                "htmlContent": html_content
            }
            
            success = await self._send_email(email_data)
            
            if success:
                logger.info(f"Session resume link sent successfully to {recipient_email} (language: {language})")
            else:
                logger.error(f"Failed to send session resume link to {recipient_email}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending session resume link: {str(e)}")
            return False
    
    def _build_trainer_notification_content(self, notification_type: str, data: Dict[str, Any]) -> str:
        """Build HTML content for trainer notifications"""
        base_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Trainer Notification</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #0d6efd;">Trainer Dashboard Notification</h2>
                {content}
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
                <p style="font-size: 12px; color: #6c757d;">
                    FIA v3.0 - AI-Powered E-Learning Platform
                </p>
            </div>
        </body>
        </html>
        """
        
        if notification_type == "session_completed":
            content = f"""
            <p>A learner has completed a training session:</p>
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px;">
                <p><strong>Training:</strong> {data.get('training_name', 'N/A')}</p>
                <p><strong>Learner:</strong> {data.get('learner_email', 'N/A')}</p>
                <p><strong>Completion Date:</strong> {data.get('completion_date', 'N/A')}</p>
                <p><strong>Duration:</strong> {data.get('duration', 'N/A')}</p>
            </div>
            """
        elif notification_type == "new_session_started":
            content = f"""
            <p>A new training session has been started:</p>
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px;">
                <p><strong>Training:</strong> {data.get('training_name', 'N/A')}</p>
                <p><strong>Learner:</strong> {data.get('learner_email', 'N/A')}</p>
                <p><strong>Start Date:</strong> {data.get('start_date', 'N/A')}</p>
            </div>
            """
        elif notification_type == "engagement_alert":
            content = f"""
            <p>Learner engagement alert:</p>
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107;">
                <p><strong>Training:</strong> {data.get('training_name', 'N/A')}</p>
                <p><strong>Learner:</strong> {data.get('learner_email', 'N/A')}</p>
                <p><strong>Engagement Level:</strong> {data.get('engagement_level', 'N/A')}</p>
                <p><strong>Recommendation:</strong> {data.get('recommendation', 'N/A')}</p>
            </div>
            """
        else:
            content = f"<p>Notification: {data}</p>"
        
        return base_template.format(content=content)
    
    def _build_resume_link_content(self, session_link: str, training_name: str, language: str) -> Dict[str, str]:
        """Build i18n email content for session resume link"""
        
        if language.lower() in ["en", "english"]:
            # English content
            subject = f"Your Training Session Link - {training_name}"
            
            greeting = "Hello,"
            intro = "We are happy to count you among our learners."
            link_text = "Your training link is the following:"
            resume_text = "It allows you to resume your training at any time."
            closing = "Have a great day!"
            button_text = "Resume My Training"
            
        else:
            # French content (default)
            subject = f"Votre lien de formation - {training_name}"
            
            greeting = "Bonjour,"
            intro = "Nous sommes heureux de vous compter parmi nos apprenants."
            link_text = "Votre lien de formation est le suivant :"
            resume_text = "Il vous permet de reprendre votre formation à tout moment."
            closing = "Bonne journée !"
            button_text = "Reprendre ma formation"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{subject}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #0d6efd;">FIA v3.0 - Formation IA</h2>
                
                <p>{greeting}</p>
                
                <p>{intro}</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin: 0; color: #0d6efd;">{training_name}</h3>
                </div>
                
                <p>{link_text}</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{session_link}" 
                       style="background-color: #0d6efd; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        {button_text}
                    </a>
                </div>
                
                <p>{resume_text}</p>
                
                <p>{closing}</p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
                
                <p style="font-size: 12px; color: #6c757d;">
                    FIA v3.0 - Plateforme d'apprentissage IA personnalisée<br>
                    Cet email a été envoyé automatiquement lors de votre inscription à la formation.
                </p>
            </div>
        </body>
        </html>
        """
        
        return {
            "subject": subject,
            "html_content": html_content
        }
    
    async def _send_email(self, email_data: Dict[str, Any]) -> bool:
        """Send email via Brevo API"""
        try:
            headers = {
                "accept": "application/json",
                "api-key": self.api_key,
                "content-type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=email_data,
                    headers=headers
                ) as response:
                    if response.status == 201:
                        logger.info("Email sent successfully via Brevo")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Brevo API error {response.status}: {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending email via Brevo: {str(e)}")
            return False