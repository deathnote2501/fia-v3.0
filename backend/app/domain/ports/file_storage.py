"""
FIA v3.0 - File Storage Port
Interface for file storage operations
"""

from abc import ABC, abstractmethod
from typing import BinaryIO, Tuple
from uuid import UUID
from pathlib import Path


class FileStoragePort(ABC):
    """Abstract interface for file storage operations"""
    
    @abstractmethod
    async def store_training_file(
        self,
        trainer_id: UUID,
        training_id: UUID,
        file_content: BinaryIO,
        original_filename: str,
        mime_type: str
    ) -> Tuple[str, int]:
        """
        Store a training file and return file path and size
        
        Args:
            trainer_id: ID of the trainer uploading the file
            training_id: ID of the training this file belongs to
            file_content: Binary file content
            original_filename: Original filename with extension
            mime_type: MIME type of the file
            
        Returns:
            Tuple of (file_path, file_size_in_bytes)
        """
        pass
    
    @abstractmethod
    async def get_training_file_path(self, file_path: str) -> Path:
        """
        Get full system path for a stored training file
        
        Args:
            file_path: Stored file path
            
        Returns:
            Full Path object to the file
        """
        pass
    
    @abstractmethod
    async def delete_training_file(self, file_path: str) -> bool:
        """
        Delete a training file
        
        Args:
            file_path: Stored file path
            
        Returns:
            True if file was deleted, False if file didn't exist
        """
        pass
    
    @abstractmethod
    async def file_exists(self, file_path: str) -> bool:
        """
        Check if a training file exists
        
        Args:
            file_path: Stored file path
            
        Returns:
            True if file exists, False otherwise
        """
        pass