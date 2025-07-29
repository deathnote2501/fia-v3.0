"""
FIA v3.0 - Training Slide Entity
Pure domain entity for training slides business logic
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from enum import Enum


class SlideType(Enum):
    """Enumeration of slide types"""
    PLAN = "plan"
    STAGE = "stage"
    MODULE = "module"
    CONTENT = "content"
    QUIZ = "quiz"


@dataclass
class TrainingSlide:
    """Pure domain entity for training slides"""
    
    submodule_id: UUID
    order_in_submodule: int
    title: str
    slide_type: SlideType = SlideType.CONTENT
    id: Optional[UUID] = None
    content: Optional[str] = None
    generated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize defaults after dataclass creation"""
        if self.id is None:
            self.id = uuid4()
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def generate_content(self, content: str) -> None:
        """Mark slide content as generated"""
        self.content = content
        self.generated_at = datetime.utcnow()
    
    def has_content(self) -> bool:
        """Check if slide has generated content"""
        return self.content is not None and len(self.content.strip()) > 0
    
    def is_content_slide(self) -> bool:
        """Check if this is a regular content slide"""
        return self.slide_type == SlideType.CONTENT
    
    def is_navigation_slide(self) -> bool:
        """Check if this is a navigation slide (plan, stage, module)"""
        return self.slide_type in [SlideType.PLAN, SlideType.STAGE, SlideType.MODULE]
    
    def is_quiz_slide(self) -> bool:
        """Check if this is a quiz slide"""
        return self.slide_type == SlideType.QUIZ
    
    def get_slide_type_display(self) -> str:
        """Get display-friendly slide type"""
        type_display = {
            SlideType.PLAN: "Plan de Formation",
            SlideType.STAGE: "Étape",
            SlideType.MODULE: "Module",
            SlideType.CONTENT: "Contenu",
            SlideType.QUIZ: "Quiz"
        }
        return type_display.get(self.slide_type, "Inconnu")
    
    def validate(self) -> None:
        """Validate the training slide data"""
        if not self.submodule_id:
            raise ValueError("Submodule ID is required")
        if not isinstance(self.submodule_id, UUID):
            raise ValueError("Submodule ID must be a valid UUID")
        if not self.title or not self.title.strip():
            raise ValueError("Title is required")
        if len(self.title) > 500:
            raise ValueError("Title cannot exceed 500 characters")
        if self.order_in_submodule < 0:
            raise ValueError("Order in submodule must be non-negative")
        if not isinstance(self.slide_type, SlideType):
            raise ValueError("Slide type must be a valid SlideType enum")
    
    def to_dict(self) -> dict:
        """Convert entity to dictionary"""
        return {
            'id': str(self.id),
            'submodule_id': str(self.submodule_id),
            'order_in_submodule': self.order_in_submodule,
            'title': self.title,
            'slide_type': self.slide_type.value,
            'content': self.content,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'has_content': self.has_content()
        }