"""
FIA v3.0 - Pure Domain Training Session Entity
Business logic representation of a training session without infrastructure dependencies
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class TrainingSession:
    """Pure domain entity representing a training session in the system"""
    
    def __init__(
        self,
        training_id: UUID,
        name: str,
        session_token: str,
        description: Optional[str] = None,
        training_session_id: Optional[UUID] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = training_session_id or uuid4()
        self.training_id = training_id
        self.name = name
        self.description = description
        self.session_token = session_token
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        
        # Validate business rules
        self._validate()
    
    def _validate(self) -> None:
        """Validate business rules for training session"""
        if not self.name.strip():
            raise ValueError("Session name is required")
        
        if len(self.name) > 200:
            raise ValueError("Session name cannot exceed 200 characters")
        
        if not self.session_token:
            raise ValueError("Session token is required")
        
        if len(self.session_token) < 10:
            raise ValueError("Session token must be at least 10 characters")
        
        if self.description and len(self.description) > 1000:
            raise ValueError("Description cannot exceed 1000 characters")
    
    def update_details(self, name: Optional[str] = None, description: Optional[str] = None) -> None:
        """Update session details"""
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        
        self.updated_at = datetime.utcnow()
        self._validate()
    
    def activate(self) -> None:
        """Activate the training session"""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate the training session"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def regenerate_token(self, new_token: str) -> None:
        """Regenerate the session token"""
        if not new_token or len(new_token) < 10:
            raise ValueError("New token must be at least 10 characters")
        
        self.session_token = new_token
        self.updated_at = datetime.utcnow()
    
    def get_session_info(self) -> dict:
        """Get basic session information"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "training_id": str(self.training_id)
        }
    
    def is_accessible(self) -> bool:
        """Check if the session is accessible for learners"""
        return self.is_active and bool(self.session_token)
    
    def get_display_name(self) -> str:
        """Get a display-friendly name for the session"""
        return self.name.strip()
    
    def get_session_url_fragment(self) -> str:
        """Get the URL fragment for accessing this session"""
        return f"?token={self.session_token}"