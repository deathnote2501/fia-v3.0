"""
FIA v3.0 - Storage Factory
Factory to create appropriate storage adapter based on configuration
"""

import logging
from app.domain.ports.file_storage import FileStoragePort
from app.domain.ports.settings_port import SettingsPort
from app.domain.services.file_storage_service import FileStorageService
from app.adapters.outbound.cloudflare_r2_storage_adapter import CloudflareR2StorageAdapter

logger = logging.getLogger(__name__)


class StorageFactory:
    """Factory to create storage adapters based on configuration"""
    
    @staticmethod
    def create_storage_adapter(settings_port: SettingsPort) -> FileStoragePort:
        """
        Create appropriate storage adapter based on settings
        
        Args:
            settings_port: Settings port implementation
            
        Returns:
            FileStoragePort implementation (local or R2)
        """
        storage_type = settings_port.get_storage_type().lower()
        
        if storage_type == "r2":
            logger.info("🌐 Creating Cloudflare R2 storage adapter")
            
            # Validate R2 configuration
            if not all([
                settings_port.get_r2_bucket_name(),
                settings_port.get_r2_endpoint_url(),
                settings_port.get_r2_access_key(),
                settings_port.get_r2_secret_key()
            ]):
                logger.warning("⚠️ R2 configuration incomplete, falling back to local storage")
                return FileStorageService(settings_port)
            
            try:
                r2_adapter = CloudflareR2StorageAdapter(settings_port)
                if r2_adapter.is_available():
                    logger.info("✅ Cloudflare R2 storage adapter created successfully")
                    return r2_adapter
                else:
                    logger.warning("⚠️ R2 storage not available, falling back to local storage")
                    return FileStorageService(settings_port)
            except Exception as e:
                logger.error(f"❌ Failed to create R2 adapter: {e}")
                return FileStorageService(settings_port)
        
        else:
            logger.info("📁 Creating local file storage adapter")
            return FileStorageService(settings_port)
    
    @staticmethod
    def get_storage_info(settings_port: SettingsPort) -> dict:
        """Get information about current storage configuration"""
        storage_type = settings_port.get_storage_type().lower()
        
        if storage_type == "r2":
            return {
                "type": "cloudflare_r2",
                "bucket": settings_port.get_r2_bucket_name(),
                "endpoint": settings_port.get_r2_endpoint_url(),
                "persistent": True,
                "scalable": True
            }
        else:
            return {
                "type": "local_filesystem",
                "path": settings_port.get_storage_path(),
                "persistent": False,  # ⚠️ Not persistent on Railway
                "scalable": False     # ⚠️ Not scalable across instances
            }