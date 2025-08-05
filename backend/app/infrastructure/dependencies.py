"""
FIA v3.0 - Dependency Injection Utilities
Common dependency injection functions for FastAPI
"""

from app.domain.ports.file_storage import FileStoragePort
from app.adapters.outbound.settings_adapter import SettingsAdapter
from app.adapters.outbound.storage_factory import StorageFactory


def get_file_storage_service() -> FileStoragePort:
    """
    Dependency to get file storage service based on configuration
    
    Returns:
        FileStoragePort: Either local storage or Cloudflare R2 based on settings
    """
    settings_adapter = SettingsAdapter()
    return StorageFactory.create_storage_adapter(settings_adapter)


def get_storage_info() -> dict:
    """
    Get information about current storage configuration
    
    Returns:
        dict: Storage configuration details
    """
    settings_adapter = SettingsAdapter()
    return StorageFactory.get_storage_info(settings_adapter)