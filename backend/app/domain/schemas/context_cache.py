"""
FIA v3.0 - Context Cache Schemas
Pydantic schemas for context cache data validation
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID


class CacheFileInfo(BaseModel):
    """Schema for cached file information"""
    path: str = Field(..., description="File path")
    name: str = Field(..., description="File name")
    mime_type: str = Field(..., description="MIME type")
    size_bytes: int = Field(..., description="File size in bytes")


class CacheUsageMetadata(BaseModel):
    """Schema for cache usage metadata"""
    cached_content_token_count: int = Field(0, description="Number of tokens in cached content")
    prompt_token_count: Optional[int] = Field(None, description="Number of prompt tokens")
    candidates_token_count: Optional[int] = Field(None, description="Number of response tokens")


class ContextCacheCreateRequest(BaseModel):
    """Schema for context cache creation request"""
    file_path: str = Field(..., description="Path to the document file")
    mime_type: str = Field(..., description="MIME type of the document")
    display_name: Optional[str] = Field(None, description="Display name for the cache")
    ttl_hours: Optional[int] = Field(None, ge=1, description="TTL in hours (minimum 1 hour)")
    system_instruction: Optional[str] = Field(None, description="Custom system instruction")


class ContextCacheResponse(BaseModel):
    """Schema for context cache response"""
    success: bool = Field(..., description="Whether cache creation was successful")
    cache_id: str = Field(..., description="Unique cache identifier")
    cache_key: str = Field(..., description="Generated cache key")
    display_name: str = Field(..., description="Cache display name")
    model: str = Field(..., description="Gemini model used")
    created_at: str = Field(..., description="Cache creation timestamp")
    expires_at: str = Field(..., description="Cache expiration timestamp")
    ttl_hours: int = Field(..., description="TTL in hours")
    file_info: CacheFileInfo = Field(..., description="Cached file information")
    usage_metadata: CacheUsageMetadata = Field(..., description="Cache usage metadata")


class ContextCacheInfo(BaseModel):
    """Schema for context cache information"""
    cache_id: str = Field(..., description="Cache identifier")
    display_name: str = Field(..., description="Cache display name")
    model: str = Field(..., description="Gemini model")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    expires_at: Optional[str] = Field(None, description="Expiration timestamp")
    usage_metadata: CacheUsageMetadata = Field(..., description="Usage metadata")


class ContextCacheListResponse(BaseModel):
    """Schema for context cache list response"""
    caches: List[ContextCacheInfo] = Field(..., description="List of context caches")
    total_count: int = Field(..., description="Total number of caches")


class CacheExpirationUpdateRequest(BaseModel):
    """Schema for cache expiration update request"""
    cache_id: str = Field(..., description="Cache ID to update")
    ttl_hours: int = Field(..., ge=1, description="New TTL in hours")


class CacheExpirationUpdateResponse(BaseModel):
    """Schema for cache expiration update response"""
    cache_id: str = Field(..., description="Updated cache ID")
    updated_at: str = Field(..., description="Update timestamp")
    new_expires_at: Optional[str] = Field(None, description="New expiration timestamp")
    ttl_hours: int = Field(..., description="New TTL in hours")


class CacheContentGenerationRequest(BaseModel):
    """Schema for generating content with cached context"""
    cache_id: str = Field(..., description="Cache ID to use")
    prompt: str = Field(..., min_length=1, description="Prompt for content generation")
    max_output_tokens: Optional[int] = Field(8192, ge=1, le=32768, description="Maximum output tokens")
    temperature: Optional[float] = Field(0.1, ge=0.0, le=2.0, description="Temperature for generation")
    top_p: Optional[float] = Field(0.95, ge=0.0, le=1.0, description="Top-p for generation")


class CacheContentGenerationResponse(BaseModel):
    """Schema for cache content generation response"""
    success: bool = Field(..., description="Whether generation was successful")
    content: str = Field(..., description="Generated content")
    cache_id: str = Field(..., description="Cache ID used")
    usage_metadata: CacheUsageMetadata = Field(..., description="Token usage metadata")


class CacheDeleteResponse(BaseModel):
    """Schema for cache deletion response"""
    success: bool = Field(..., description="Whether deletion was successful")
    cache_id: str = Field(..., description="Deleted cache ID")
    deleted_at: str = Field(..., description="Deletion timestamp")


class CacheHealthResponse(BaseModel):
    """Schema for cache service health response"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    total_caches: int = Field(..., description="Total number of active caches")
    available_operations: List[str] = Field(..., description="Available cache operations")


class CacheError(BaseModel):
    """Schema for cache error responses"""
    error_type: str = Field(..., description="Type of cache error")
    error_message: str = Field(..., description="Error message")
    cache_id: Optional[str] = Field(None, description="Cache ID related to error")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class CacheStatistics(BaseModel):
    """Schema for cache statistics"""
    total_caches: int = Field(..., description="Total number of caches")
    active_caches: int = Field(..., description="Number of active (non-expired) caches")
    total_cached_tokens: int = Field(..., description="Total tokens across all caches")
    average_ttl_hours: float = Field(..., description="Average TTL in hours")
    cache_hit_rate: Optional[float] = Field(None, description="Cache hit rate percentage")


class TrainingDocumentCacheRequest(BaseModel):
    """Schema for caching a training document"""
    training_id: UUID = Field(..., description="Training ID from database")
    force_refresh: bool = Field(False, description="Force cache refresh even if exists")
    custom_system_instruction: Optional[str] = Field(None, description="Custom system instruction")
    ttl_hours: Optional[int] = Field(None, description="Custom TTL in hours")


class TrainingDocumentCacheResponse(BaseModel):
    """Schema for training document cache response"""
    training_id: UUID = Field(..., description="Training ID")
    cache_info: ContextCacheResponse = Field(..., description="Cache information")
    was_existing: bool = Field(..., description="Whether cache already existed")
    cached_at: str = Field(..., description="When caching was completed")


class CacheFindRequest(BaseModel):
    """Schema for finding cache by document"""
    file_path: str = Field(..., description="Document file path")
    mime_type: str = Field(..., description="Document MIME type")


class CacheFindResponse(BaseModel):
    """Schema for cache find response"""
    found: bool = Field(..., description="Whether cache was found")
    cache_info: Optional[ContextCacheInfo] = Field(None, description="Cache information if found")
    message: str = Field(..., description="Result message")