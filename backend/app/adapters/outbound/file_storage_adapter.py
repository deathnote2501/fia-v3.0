"""
FIA v3.0 - File Storage Outbound Adapter
Implementation of file storage service interactions
"""

import os
import logging
import aiofiles
from pathlib import Path
from typing import Optional, Dict, Any
from uuid import UUID

from app.domain.ports.outbound_ports import FileStorageServicePort
from app.infrastructure.settings import settings


logger = logging.getLogger(__name__)


class FileStorageAdapter(FileStorageServicePort):
    """Outbound adapter for file storage service"""
    
    def __init__(self):
        self.storage_path = Path(settings.file_storage_path)
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        
        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
    async def store_training_file(
        self,
        file_content: bytes,
        file_name: str,
        trainer_id: UUID
    ) -> str:
        """Store training file and return path"""
        try:
            # Validate file size
            if len(file_content) > self.max_file_size:
                raise ValueError(f"File size exceeds maximum allowed size of {self.max_file_size // (1024*1024)}MB")
            
            # Create trainer-specific directory
            trainer_dir = self.storage_path / str(trainer_id)
            trainer_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate safe file name
            safe_file_name = self._sanitize_filename(file_name)
            file_path = trainer_dir / safe_file_name
            
            # Handle file name conflicts
            counter = 1
            original_path = file_path
            while file_path.exists():
                name_parts = safe_file_name.rsplit('.', 1)
                if len(name_parts) == 2:
                    new_name = f"{name_parts[0]}_{counter}.{name_parts[1]}"
                else:
                    new_name = f"{safe_file_name}_{counter}"
                file_path = trainer_dir / new_name
                counter += 1
            
            # Write file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            # Return relative path from storage root
            relative_path = str(file_path.relative_to(self.storage_path))
            
            logger.info(f"File stored successfully: {relative_path}")
            return relative_path
            
        except Exception as e:
            logger.error(f"Error storing file {file_name}: {str(e)}")
            raise
    
    async def retrieve_training_file(
        self,
        file_path: str
    ) -> Optional[bytes]:
        """Retrieve training file content"""
        try:
            full_path = self.storage_path / file_path
            
            # Security check: ensure path is within storage directory
            if not self._is_safe_path(full_path):
                logger.error(f"Unsafe file path access attempt: {file_path}")
                return None
            
            if not full_path.exists():
                logger.warning(f"File not found: {file_path}")
                return None
            
            async with aiofiles.open(full_path, 'rb') as f:
                content = await f.read()
            
            logger.info(f"File retrieved successfully: {file_path}")
            return content
            
        except Exception as e:
            logger.error(f"Error retrieving file {file_path}: {str(e)}")
            return None
    
    async def delete_training_file(
        self,
        file_path: str
    ) -> bool:
        """Delete training file"""
        try:
            full_path = self.storage_path / file_path
            
            # Security check: ensure path is within storage directory
            if not self._is_safe_path(full_path):
                logger.error(f"Unsafe file path deletion attempt: {file_path}")
                return False
            
            if not full_path.exists():
                logger.warning(f"File not found for deletion: {file_path}")
                return False
            
            full_path.unlink()
            
            # Clean up empty directories
            try:
                parent_dir = full_path.parent
                if parent_dir != self.storage_path and not any(parent_dir.iterdir()):
                    parent_dir.rmdir()
            except OSError:
                pass  # Directory not empty, ignore
            
            logger.info(f"File deleted successfully: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            return False
    
    async def get_file_info(
        self,
        file_path: str
    ) -> Optional[Dict[str, Any]]:
        """Get file metadata"""
        try:
            full_path = self.storage_path / file_path
            
            # Security check: ensure path is within storage directory
            if not self._is_safe_path(full_path):
                logger.error(f"Unsafe file path access attempt: {file_path}")
                return None
            
            if not full_path.exists():
                logger.warning(f"File not found: {file_path}")
                return None
            
            stat = full_path.stat()
            
            file_info = {
                "file_name": full_path.name,
                "file_size": stat.st_size,
                "file_size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created_at": stat.st_ctime,
                "modified_at": stat.st_mtime,
                "file_extension": full_path.suffix.lower(),
                "mime_type": self._get_mime_type(full_path.suffix.lower()),
                "relative_path": file_path
            }
            
            return file_info
            
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {str(e)}")
            return None
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent security issues"""
        # Remove path separators and other potentially dangerous characters
        unsafe_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*', '\0']
        safe_name = filename
        
        for char in unsafe_chars:
            safe_name = safe_name.replace(char, '_')
        
        # Limit filename length
        if len(safe_name) > 255:
            name_parts = safe_name.rsplit('.', 1)
            if len(name_parts) == 2:
                safe_name = name_parts[0][:250] + '.' + name_parts[1]
            else:
                safe_name = safe_name[:255]
        
        return safe_name
    
    def _is_safe_path(self, file_path: Path) -> bool:
        """Check if file path is safe (within storage directory)"""
        try:
            # Resolve absolute paths and check if file_path is within storage_path
            resolved_file_path = file_path.resolve()
            resolved_storage_path = self.storage_path.resolve()
            
            return str(resolved_file_path).startswith(str(resolved_storage_path))
        except Exception:
            return False
    
    def _get_mime_type(self, file_extension: str) -> str:
        """Get MIME type based on file extension"""
        mime_types = {
            '.pdf': 'application/pdf',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif'
        }
        
        return mime_types.get(file_extension.lower(), 'application/octet-stream')
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            total_size = 0
            file_count = 0
            
            for file_path in self.storage_path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    file_count += 1
            
            return {
                "total_files": file_count,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "storage_path": str(self.storage_path)
            }
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {str(e)}")
            return {
                "total_files": 0,
                "total_size_bytes": 0,
                "total_size_mb": 0,
                "storage_path": str(self.storage_path),
                "error": str(e)
            }
    
    async def cleanup_orphaned_files(self, trainer_ids: list[UUID]) -> int:
        """Clean up files for deleted trainers"""
        try:
            cleanup_count = 0
            valid_trainer_dirs = {str(trainer_id) for trainer_id in trainer_ids}
            
            for trainer_dir in self.storage_path.iterdir():
                if trainer_dir.is_dir() and trainer_dir.name not in valid_trainer_dirs:
                    # This trainer directory is orphaned
                    for file_path in trainer_dir.rglob('*'):
                        if file_path.is_file():
                            file_path.unlink()
                            cleanup_count += 1
                    
                    # Remove empty directory
                    try:
                        trainer_dir.rmdir()
                    except OSError:
                        pass  # Directory not empty, ignore
            
            logger.info(f"Cleaned up {cleanup_count} orphaned files")
            return cleanup_count
            
        except Exception as e:
            logger.error(f"Error during orphaned files cleanup: {str(e)}")
            return 0