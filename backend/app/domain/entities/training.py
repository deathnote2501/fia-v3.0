"""
FIA v3.0 - Pure Domain Training Entity
Business logic representation of a training without infrastructure dependencies
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from enum import Enum


class FileType(Enum):
    """Supported training file types"""
    PDF = "pdf"
    PPT = "ppt"
    PPTX = "pptx"
    MARKDOWN = "md"


class Training:
    """Pure domain entity representing a training in the system"""
    
    SUPPORTED_MIME_TYPES = {
        FileType.PDF: "application/pdf",
        FileType.PPT: "application/vnd.ms-powerpoint",
        FileType.PPTX: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        FileType.MARKDOWN: "text/markdown"
    }
    
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    def __init__(
        self,
        trainer_id: UUID,
        name: str,
        description: Optional[str] = None,
        file_path: Optional[str] = None,
        file_name: Optional[str] = None,
        file_type: Optional[FileType] = None,
        file_size: Optional[int] = None,
        mime_type: Optional[str] = None,
        is_ai_generated: bool = False,
        training_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None
    ):
        self.id = training_id or uuid4()
        self.trainer_id = trainer_id
        self.name = name
        self.description = description
        self.file_path = file_path
        self.file_name = file_name
        self.file_type = file_type
        self.file_size = file_size
        self.mime_type = mime_type
        self.is_ai_generated = is_ai_generated
        self.created_at = created_at or datetime.utcnow()
        
        # Domain validation
        self._validate()
    
    def _validate(self) -> None:
        """Validate domain rules"""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Training name is required")
        
        if len(self.name) > 200:
            raise ValueError("Training name cannot exceed 200 characters")
        
        if self.description and len(self.description) > 2000:
            raise ValueError("Training description cannot exceed 2000 characters")
        
        # AI-generated trainings require description
        if self.is_ai_generated and (not self.description or len(self.description.strip()) == 0):
            raise ValueError("Description is required for AI-generated trainings")
        
        # Non-AI trainings require file information (skip validation during initial creation)
        # This validation will be handled at the controller level for non-AI trainings
        
        if self.file_size and self.file_size > self.MAX_FILE_SIZE:
            raise ValueError(f"File size cannot exceed {self.MAX_FILE_SIZE // (1024*1024)}MB")
        
        if self.file_type and self.mime_type:
            expected_mime = self.SUPPORTED_MIME_TYPES.get(self.file_type)
            if expected_mime and self.mime_type != expected_mime:
                raise ValueError(f"MIME type {self.mime_type} doesn't match file type {self.file_type.value}")
    
    def attach_file(
        self, 
        file_path: str, 
        file_name: str, 
        file_type: FileType, 
        file_size: int, 
        mime_type: str
    ) -> None:
        """Business logic: Attach a file to the training"""
        self.file_path = file_path
        self.file_name = file_name
        self.file_type = file_type
        self.file_size = file_size
        self.mime_type = mime_type
        self._validate()
    
    def update_details(self, name: Optional[str] = None, description: Optional[str] = None) -> None:
        """Business logic: Update training details"""
        if name:
            self.name = name
        if description is not None:
            self.description = description
        self._validate()
    
    def has_file(self) -> bool:
        """Business logic: Check if training has an attached file"""
        return bool(self.file_path and self.file_name and self.file_type)
    
    def is_file_supported(self, file_extension: str) -> bool:
        """Business logic: Check if file type is supported"""
        try:
            FileType(file_extension.lower().lstrip('.'))
            return True
        except ValueError:
            return False
    
    def get_file_info(self) -> dict:
        """Business logic: Get file information"""
        if not self.has_file():
            return {}
        
        return {
            "file_name": self.file_name,
            "file_type": self.file_type.value if self.file_type else None,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "file_size_mb": round(self.file_size / (1024 * 1024), 2) if self.file_size else None
        }
    
    def __str__(self) -> str:
        return f"Training({self.name})"
    
    def __repr__(self) -> str:
        return f"Training(id={self.id}, name='{self.name}', trainer_id={self.trainer_id})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Training):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)