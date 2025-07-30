"""
FIA v3.0 - Image Generation Schemas
Pydantic models for image generation requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime


class ImageGenerationRequest(BaseModel):
    """Schema for image generation request"""
    slide_content: str = Field(..., min_length=10, max_length=5000, description="Slide content to generate infographic from")
    learner_session_id: UUID = Field(..., description="Learner session ID for personalization")
    slide_id: Optional[UUID] = Field(None, description="Optional slide ID for tracking")


class ImageGenerationResponse(BaseModel):
    """Schema for image generation response"""
    success: bool = Field(..., description="Whether generation was successful")
    image_data: Optional[str] = Field(None, description="Base64 encoded image data")
    revised_prompt: Optional[str] = Field(None, description="The revised prompt used by OpenAI")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Image metadata (size, format, etc.)")
    generation_time_seconds: float = Field(..., description="Time taken to generate image")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    error_message: Optional[str] = Field(None, description="Error message if generation failed")


class ImageGenerationStatus(BaseModel):
    """Schema for image generation service status"""
    service_available: bool = Field(..., description="Whether OpenAI service is available")
    rate_limit_status: Dict[str, Any] = Field(..., description="Current rate limit status")
    total_images_generated: int = Field(default=0, description="Total images generated in current session")
    last_generation_at: Optional[datetime] = Field(None, description="Last successful generation timestamp")


class ImageGenerationMetrics(BaseModel):
    """Schema for image generation metrics"""
    total_requests: int = Field(default=0, description="Total generation requests")
    successful_generations: int = Field(default=0, description="Successful generations")
    failed_generations: int = Field(default=0, description="Failed generations")
    average_generation_time: float = Field(default=0.0, description="Average generation time in seconds")
    rate_limit_hits: int = Field(default=0, description="Number of rate limit hits")
    success_rate: float = Field(default=0.0, description="Success rate percentage")