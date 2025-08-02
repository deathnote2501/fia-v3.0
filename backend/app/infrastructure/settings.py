"""
FIA v3.0 - Application Settings
Configuration management using Pydantic Settings
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra environment variables
    )
    
    # Security
    secret_key: str = Field(default="dev-secret-key-change-in-production", description="Secret key for JWT and sessions")
    jwt_secret_key: str = Field(default="dev-jwt-secret-change-in-production", description="JWT signing key")
    
    # Database
    database_url: str = Field(default="sqlite:///./test.db", description="PostgreSQL database URL")
    
    # Google Gemini AI
    gemini_api_key: str = Field(default="", description="Google Gemini API key")
    google_application_credentials: str = Field(default="", description="Path to GCP credentials JSON")
    google_credentials_json: str = Field(default="", description="GCP credentials as JSON string")
    google_cloud_project: str = Field(default="", description="GCP project ID") 
    google_cloud_region: str = Field(default="europe-west1", description="GCP region")
    gemini_model_name: str = Field(default="gemini-2.0-flash-001", description="Gemini 2.0 Flash model name")
    
    # OpenAI
    openai_api_key: str = Field(default="", description="OpenAI API key for image generation")
    
    # Application
    environment: str = Field(default="development", description="Environment (development/production)")
    debug: bool = Field(default=False, description="Debug mode")
    port: int = Field(default=8000, description="Server port")
    frontend_url: str = Field(default="http://localhost:8000", description="Frontend base URL")
    
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Rate Limiting
    gemini_rate_limit_per_minute: int = Field(default=60, description="Gemini API rate limit")
    gemini_context_cache_ttl_hours: int = Field(default=12, description="Context cache TTL in hours")
    
    # Email (Brevo)
    brevo_api_key: str = Field(default="", description="Brevo API key")
    brevo_sender_email: str = Field(default="noreply@example.com", description="Brevo sender email")
    brevo_sender_name: str = Field(default="FIA v3.0 Team", description="Brevo sender name")


# Global settings instance
settings = Settings()