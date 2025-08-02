"""
FIA v3.0 - File Storage Service
Implementation of file storage operations for training materials
"""

import os
from datetime import datetime
from pathlib import Path
from typing import BinaryIO, Tuple
from uuid import UUID

from app.domain.ports.file_storage import FileStoragePort
from app.domain.ports.settings_port import SettingsPort


class FileStorageService(FileStoragePort):
    """Local file system implementation of file storage"""
    
    def __init__(self, settings_port: SettingsPort):
        self.settings = settings_port
        # Base upload directory from settings
        storage_path = self.settings.get_storage_path()
        self.uploads_dir = Path(storage_path) / "trainings"
        # Ensure directory exists
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
    
    async def store_training_file(
        self,
        trainer_id: UUID,
        training_id: UUID,
        file_content: BinaryIO,
        original_filename: str,
        mime_type: str
    ) -> Tuple[str, int]:
        """Store training file with organized naming convention"""
        
        # Extract file extension
        file_extension = Path(original_filename).suffix.lower()
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create filename: {training_id}_{timestamp}.{extension}
        filename = f"{training_id}_{timestamp}{file_extension}"
        
        # Create trainer directory if it doesn't exist
        trainer_dir = self.uploads_dir / str(trainer_id)
        trainer_dir.mkdir(exist_ok=True)
        
        # Full file path
        file_path = trainer_dir / filename
        
        # Read content and get size
        file_content.seek(0)  # Ensure we're at the beginning
        content = file_content.read()
        file_size = len(content)
        
        # Write file synchronously (content is already in memory)
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Return relative path for database storage
        relative_path = f"{trainer_id}/{filename}"
        
        return relative_path, file_size
    
    async def get_training_file_path(self, file_path: str) -> Path:
        """Get full system path for stored file"""
        return self.uploads_dir / file_path
    
    async def delete_training_file(self, file_path: str) -> bool:
        """Delete training file from storage"""
        full_path = await self.get_training_file_path(file_path)
        
        if full_path.exists():
            full_path.unlink()
            
            # Remove trainer directory if empty
            trainer_dir = full_path.parent
            if trainer_dir.is_dir() and not any(trainer_dir.iterdir()):
                trainer_dir.rmdir()
            
            return True
        
        return False
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in storage"""
        full_path = await self.get_training_file_path(file_path)
        return full_path.exists() and full_path.is_file()
    
    def get_file_info(self, file_path: str) -> dict:
        """Get file information (size, modified date, etc.)"""
        full_path = self.uploads_dir / file_path
        
        if not full_path.exists():
            return {}
        
        stat = full_path.stat()
        return {
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'exists': True
        }