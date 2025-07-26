"""
FIA v3.0 - Pure Domain Slide Entity
Business logic representation of a slide without infrastructure dependencies
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4


class Slide:
    """Pure domain entity representing a slide in the system"""
    
    def __init__(
        self,
        learner_session_id: UUID,
        slide_number: int,
        title: str,
        slide_id: Optional[UUID] = None,
        content: Optional[Dict[str, Any]] = None,
        time_spent: int = 0,
        completed: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = slide_id or uuid4()
        self.learner_session_id = learner_session_id
        self.slide_number = slide_number
        self.title = title
        self.content = content or {}
        self.time_spent = time_spent
        self.completed = completed
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        
        # Validate business rules
        self._validate()
    
    def _validate(self) -> None:
        """Validate business rules for slide"""
        if not self.title.strip():
            raise ValueError("Slide title is required")
        
        if len(self.title) > 200:
            raise ValueError("Slide title cannot exceed 200 characters")
        
        if self.slide_number < 1:
            raise ValueError("Slide number must be at least 1")
        
        if self.time_spent < 0:
            raise ValueError("Time spent cannot be negative")
    
    def add_time_spent(self, seconds: int) -> None:
        """Add time spent on this slide"""
        if seconds < 0:
            raise ValueError("Time spent cannot be negative")
        
        self.time_spent += seconds
        self.updated_at = datetime.utcnow()
    
    def mark_completed(self) -> None:
        """Mark slide as completed"""
        self.completed = True
        self.updated_at = datetime.utcnow()
    
    def mark_incomplete(self) -> None:
        """Mark slide as incomplete"""
        self.completed = False
        self.updated_at = datetime.utcnow()
    
    def update_content(self, content: Dict[str, Any]) -> None:
        """Update slide content"""
        if not isinstance(content, dict):
            raise ValueError("Content must be a dictionary")
        
        self.content = content
        self.updated_at = datetime.utcnow()
    
    def get_slide_info(self) -> Dict[str, Any]:
        """Get basic slide information"""
        return {
            "id": str(self.id),
            "slide_number": self.slide_number,
            "title": self.title,
            "time_spent": self.time_spent,
            "completed": self.completed,
            "content_available": bool(self.content),
            "learner_session_id": str(self.learner_session_id)
        }
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get progress summary for this slide"""
        return {
            "slide_number": self.slide_number,
            "title": self.title,
            "time_spent_minutes": round(self.time_spent / 60, 1),
            "completed": self.completed,
            "engagement_level": self._calculate_engagement_level()
        }
    
    def _calculate_engagement_level(self) -> str:
        """Calculate engagement level based on time spent"""
        if self.time_spent == 0:
            return "not_viewed"
        elif self.time_spent < 30:
            return "low"
        elif self.time_spent < 120:
            return "medium"
        else:
            return "high"
    
    def is_viewed(self) -> bool:
        """Check if slide has been viewed"""
        return self.time_spent > 0
    
    def get_display_title(self) -> str:
        """Get display-friendly title"""
        return f"{self.slide_number}. {self.title}"