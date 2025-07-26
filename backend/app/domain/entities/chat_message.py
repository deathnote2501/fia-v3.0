"""
FIA v3.0 - Pure Domain Chat Message Entity
Business logic representation of a chat message without infrastructure dependencies
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class ChatMessage:
    """Pure domain entity representing a chat message in the system"""
    
    def __init__(
        self,
        learner_session_id: UUID,
        message_type: str,
        content: str,
        chat_message_id: Optional[UUID] = None,
        slide_number: Optional[int] = None,
        created_at: Optional[datetime] = None
    ):
        self.id = chat_message_id or uuid4()
        self.learner_session_id = learner_session_id
        self.slide_number = slide_number
        self.message_type = message_type
        self.content = content
        self.created_at = created_at or datetime.utcnow()
        
        # Validate business rules
        self._validate()
    
    def _validate(self) -> None:
        """Validate business rules for chat message"""
        if not self.content.strip():
            raise ValueError("Message content is required")
        
        if len(self.content) > 2000:
            raise ValueError("Message content cannot exceed 2000 characters")
        
        if self.message_type not in ['question', 'answer']:
            raise ValueError("Message type must be 'question' or 'answer'")
        
        if self.slide_number is not None and self.slide_number < 1:
            raise ValueError("Slide number must be at least 1")
    
    def is_question(self) -> bool:
        """Check if this message is a question from learner"""
        return self.message_type == 'question'
    
    def is_answer(self) -> bool:
        """Check if this message is an answer from AI"""
        return self.message_type == 'answer'
    
    def get_content_preview(self, max_length: int = 100) -> str:
        """Get a preview of the message content"""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length] + "..."
    
    def is_related_to_slide(self, slide_number: int) -> bool:
        """Check if this message is related to a specific slide"""
        return self.slide_number == slide_number
    
    def get_message_info(self) -> dict:
        """Get basic message information"""
        return {
            "id": str(self.id),
            "type": self.message_type,
            "content": self.content,
            "slide_number": self.slide_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "learner_session_id": str(self.learner_session_id)
        }