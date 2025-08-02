"""
Settings Port - Domain Interface for Configuration Access
Pure domain interface without infrastructure dependencies
"""

from abc import ABC, abstractmethod
from typing import Optional


class SettingsPort(ABC):
    """Port for accessing application settings from domain layer"""
    
    @abstractmethod
    def get_gemini_model_name(self) -> str:
        """Get the Gemini model name"""
        pass
    
    @abstractmethod 
    def get_gemini_api_key(self) -> str:
        """Get the Gemini API key"""
        pass
    
    @abstractmethod
    def get_google_cloud_project(self) -> str:
        """Get the Google Cloud project ID"""
        pass
    
    @abstractmethod
    def get_google_cloud_region(self) -> str:
        """Get the Google Cloud region"""
        pass
    
    @abstractmethod
    def get_storage_path(self) -> str:
        """Get the file storage path"""
        pass
    
    @abstractmethod
    def get_context_cache_ttl_hours(self) -> int:
        """Get the context cache TTL in hours"""
        pass
    
    @abstractmethod
    def get_rate_limit_per_minute(self) -> int:
        """Get the rate limit per minute for Gemini API"""
        pass
    
    @abstractmethod
    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get any setting by key with optional default"""
        pass