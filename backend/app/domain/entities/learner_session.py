"""
FIA v3.0 - Pure Domain Learner Session Entity
Business logic representation of a learner session without infrastructure dependencies
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4


class LearnerSession:
    """Pure domain entity representing a learner session in the system"""
    
    def __init__(
        self,
        training_session_id: UUID,
        email: str,
        experience_level: str,
        learning_style: str,
        job_position: str,
        activity_sector: str,
        country: str,
        language: str = 'fr',
        learner_session_id: Optional[UUID] = None,
        enriched_profile: Optional[Dict[str, Any]] = None,
        current_slide_number: int = 1,
        total_time_spent: int = 0,
        started_at: Optional[datetime] = None,
        last_activity_at: Optional[datetime] = None
    ):
        self.id = learner_session_id or uuid4()
        self.training_session_id = training_session_id
        self.email = email
        self.experience_level = experience_level
        self.learning_style = learning_style
        self.job_position = job_position
        self.activity_sector = activity_sector
        self.country = country
        self.language = language
        self.enriched_profile = enriched_profile
        self.current_slide_number = current_slide_number
        self.total_time_spent = total_time_spent
        self.started_at = started_at or datetime.utcnow()
        self.last_activity_at = last_activity_at or datetime.utcnow()
        
        # Validate business rules
        self._validate()
    
    def _validate(self) -> None:
        """Validate business rules for learner session"""
        if not self.email or '@' not in self.email:
            raise ValueError("Valid email is required")
        
        if self.experience_level not in ['beginner', 'intermediate', 'advanced']:
            raise ValueError("Experience level must be 'beginner', 'intermediate', or 'advanced'")
        
        if self.learning_style not in ['visual', 'auditory', 'kinesthetic', 'reading']:
            raise ValueError("Learning style must be 'visual', 'auditory', 'kinesthetic', or 'reading'")
        
        if not self.job_position.strip():
            raise ValueError("Job position is required")
        
        if not self.activity_sector.strip():
            raise ValueError("Activity sector is required")
        
        if not self.country.strip():
            raise ValueError("Country is required")
        
        if self.total_time_spent < 0:
            raise ValueError("Total time spent cannot be negative")
        
        if self.current_slide_number < 1:
            raise ValueError("Current slide number must be at least 1")
    
    def update_profile(
        self,
        experience_level: Optional[str] = None,
        learning_style: Optional[str] = None,
        job_position: Optional[str] = None,
        activity_sector: Optional[str] = None,
        country: Optional[str] = None,
        language: Optional[str] = None
    ) -> None:
        """Update learner profile information"""
        if experience_level is not None:
            self.experience_level = experience_level
        if learning_style is not None:
            self.learning_style = learning_style
        if job_position is not None:
            self.job_position = job_position
        if activity_sector is not None:
            self.activity_sector = activity_sector
        if country is not None:
            self.country = country
        if language is not None:
            self.language = language
        
        self.last_activity_at = datetime.utcnow()
        self._validate()
    
    def add_time_spent(self, seconds: int) -> None:
        """Add time spent in the session"""
        if seconds < 0:
            raise ValueError("Time spent cannot be negative")
        
        self.total_time_spent += seconds
        self.last_activity_at = datetime.utcnow()
    
    def set_current_slide(self, slide_number: int) -> None:
        """Set the current slide number"""
        if slide_number < 1:
            raise ValueError("Slide number must be at least 1")
        
        self.current_slide_number = slide_number
        self.last_activity_at = datetime.utcnow()
    
    def set_enriched_profile(self, profile: Dict[str, Any]) -> None:
        """Set the enriched learner profile data"""
        if not isinstance(profile, dict):
            raise ValueError("Profile must be a dictionary")
        
        self.enriched_profile = profile
        self.last_activity_at = datetime.utcnow()
    
    def get_profile_summary(self) -> Dict[str, Any]:
        """Get a summary of the learner profile"""
        return {
            "email": self.email,
            "experience_level": self.experience_level,
            "learning_style": self.learning_style,
            "job_position": self.job_position,
            "activity_sector": self.activity_sector,
            "country": self.country,
            "language": self.language,
            "progress": {
                "current_slide": self.current_slide_number,
                "total_time_spent": self.total_time_spent,
                "has_enriched_profile": self.enriched_profile is not None
            }
        }
    
    def is_active(self) -> bool:
        """Check if the learner session is still active (recent activity)"""
        if not self.last_activity_at:
            return False
        
        # Consider session active if last activity was within 24 hours
        hours_since_activity = (datetime.utcnow() - self.last_activity_at).total_seconds() / 3600
        return hours_since_activity < 24
    
    def get_learning_context(self) -> Dict[str, str]:
        """Get learning context for AI personalization"""
        return {
            "experience_level": self.experience_level,
            "learning_style": self.learning_style,
            "job_position": self.job_position,
            "activity_sector": self.activity_sector,
            "language": self.language
        }