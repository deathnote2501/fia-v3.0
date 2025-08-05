"""
Settings Adapter - Infrastructure Implementation of Settings Port
"""

from typing import Optional
from app.domain.ports.settings_port import SettingsPort
from app.infrastructure.settings import settings


class SettingsAdapter(SettingsPort):
    """Adapter that implements SettingsPort using infrastructure settings"""
    
    def get_gemini_model_name(self) -> str:
        """Get the Gemini model name"""
        return settings.gemini_model_name
    
    def get_gemini_api_key(self) -> str:
        """Get the Gemini API key"""
        return settings.gemini_api_key
    
    def get_google_cloud_project(self) -> str:
        """Get the Google Cloud project ID"""
        return settings.google_cloud_project
    
    def get_google_cloud_region(self) -> str:
        """Get the Google Cloud region"""
        return settings.google_cloud_region
    
    def get_storage_path(self) -> str:
        """Get the file storage path"""
        return settings.storage_path
    
    def get_context_cache_ttl_hours(self) -> int:
        """Get the context cache TTL in hours"""
        return settings.gemini_context_cache_ttl_hours
    
    def get_rate_limit_per_minute(self) -> int:
        """Get the rate limit per minute for Gemini API"""
        return settings.gemini_rate_limit_per_minute
    
    def get_frontend_url(self) -> str:
        """Get the frontend base URL"""
        return settings.frontend_url
    
    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get any setting by key with optional default"""
        return getattr(settings, key, default)
    
    # Cloudflare R2 Storage methods
    def get_storage_type(self) -> str:
        """Get the storage type (local or r2)"""
        return settings.storage_type
    
    def get_r2_bucket_name(self) -> str:
        """Get the Cloudflare R2 bucket name"""
        return settings.r2_bucket_name
    
    def get_r2_endpoint_url(self) -> str:
        """Get the Cloudflare R2 endpoint URL"""
        return settings.r2_endpoint_url
    
    def get_r2_access_key(self) -> str:
        """Get the Cloudflare R2 access key"""
        return settings.r2_access_key
    
    def get_r2_secret_key(self) -> str:
        """Get the Cloudflare R2 secret key"""
        return settings.r2_secret_key