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
        return settings.GEMINI_MODEL_NAME
    
    def get_gemini_api_key(self) -> str:
        """Get the Gemini API key"""
        return settings.GEMINI_API_KEY
    
    def get_google_cloud_project(self) -> str:
        """Get the Google Cloud project ID"""
        return settings.GOOGLE_CLOUD_PROJECT
    
    def get_google_cloud_region(self) -> str:
        """Get the Google Cloud region"""
        return settings.GOOGLE_CLOUD_REGION
    
    def get_storage_path(self) -> str:
        """Get the file storage path"""
        return settings.STORAGE_PATH
    
    def get_context_cache_ttl_hours(self) -> int:
        """Get the context cache TTL in hours"""
        return settings.GEMINI_CONTEXT_CACHE_TTL_HOURS
    
    def get_rate_limit_per_minute(self) -> int:
        """Get the rate limit per minute for Gemini API"""
        return settings.GEMINI_RATE_LIMIT_PER_MINUTE
    
    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get any setting by key with optional default"""
        return getattr(settings, key, default)