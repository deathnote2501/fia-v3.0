"""
FIA v3.0 - Learner Training Plan Entity
Pure domain entity for learner training plans business logic
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4


@dataclass
class LearnerTrainingPlan:
    """Pure domain entity for learner training plans"""
    
    learner_session_id: UUID
    id: Optional[UUID] = None
    current_slide_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize defaults after dataclass creation"""
        if self.id is None:
            self.id = uuid4()
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def update_current_slide(self, slide_id: UUID) -> None:
        """Update the current slide and timestamp"""
        self.current_slide_id = slide_id
        self.updated_at = datetime.utcnow()
    
    def validate(self) -> None:
        """Validate the training plan data"""
        if not self.learner_session_id:
            raise ValueError("Learner session ID is required")
        if not isinstance(self.learner_session_id, UUID):
            raise ValueError("Learner session ID must be a valid UUID")