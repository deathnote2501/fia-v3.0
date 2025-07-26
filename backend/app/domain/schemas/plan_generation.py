"""
FIA v3.0 - Plan Generation Schemas
Pydantic schemas for personalized training plan generation
"""

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any, List, Literal


class LearnerProfileSummary(BaseModel):
    """Schema for learner profile summary used in plan generation"""
    email: EmailStr
    experience_level: Literal["beginner", "intermediate", "advanced"]
    learning_style: Literal["visual", "auditory", "kinesthetic", "reading"]
    job_position: str
    activity_sector: str
    country: str
    language: str = "fr"


class TrainingSummary(BaseModel):
    """Schema for training summary used in plan generation"""
    id: UUID
    name: str
    file_path: str
    mime_type: str
    file_name: str


class PlanGenerationRequest(BaseModel):
    """Schema for plan generation request"""
    learner_session_id: UUID = Field(..., description="Learner session ID")
    training_id: UUID = Field(..., description="Training ID")
    use_cache: bool = Field(True, description="Whether to use context caching")
    custom_instructions: Optional[str] = Field(None, max_length=1000, description="Custom generation instructions")
    force_regenerate: bool = Field(False, description="Force regeneration even if plan exists")


class PlanGenerationMetadata(BaseModel):
    """Schema for plan generation metadata"""
    learner_email: EmailStr
    learner_level: str
    learner_style: str
    learner_job: str
    learner_sector: str
    training_name: str
    training_id: str
    generated_at: str
    total_stages: int
    total_modules: int
    total_submodules: int
    total_slides: int
    generation_method: str = Field(..., description="'cached' or 'direct'")
    cache_used: bool = Field(..., description="Whether cache was used")
    tokens_used: Optional[Dict[str, int]] = Field(None, description="Token usage information")


class PlanGenerationResponse(BaseModel):
    """Schema for plan generation response"""
    success: bool = Field(..., description="Whether generation was successful")
    learner_session_id: UUID = Field(..., description="Learner session ID")
    plan_data: Dict[str, Any] = Field(..., description="Generated plan structure")
    generation_metadata: PlanGenerationMetadata = Field(..., description="Generation metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    errors: Optional[List[str]] = Field(None, description="Any errors encountered")


class SectionRegenerationRequest(BaseModel):
    """Schema for regenerating specific plan sections"""
    learner_session_id: UUID = Field(..., description="Learner session ID")
    training_id: UUID = Field(..., description="Training ID")
    section_type: Literal["stage", "module", "submodule"] = Field(..., description="Type of section to regenerate")
    section_identifier: str = Field(..., description="Identifier for the section")
    custom_instructions: Optional[str] = Field(None, max_length=1000, description="Specific instructions for regeneration")
    regeneration_reason: Optional[str] = Field(None, max_length=500, description="Reason for regeneration")


class SectionRegenerationResponse(BaseModel):
    """Schema for section regeneration response"""
    success: bool = Field(..., description="Whether regeneration was successful")
    section_type: str = Field(..., description="Type of regenerated section")
    section_identifier: str = Field(..., description="Section identifier")
    regenerated_content: str = Field(..., description="Regenerated content")
    regenerated_at: str = Field(..., description="Regeneration timestamp")
    original_reason: Optional[str] = Field(None, description="Reason for regeneration")


class PlanValidationRequest(BaseModel):
    """Schema for validating generated plans"""
    plan_data: Dict[str, Any] = Field(..., description="Plan data to validate")
    learner_profile: LearnerProfileSummary = Field(..., description="Learner profile for validation")
    validation_criteria: Optional[List[str]] = Field(None, description="Specific validation criteria")


class PlanValidationResult(BaseModel):
    """Schema for plan validation results"""
    is_valid: bool = Field(..., description="Whether the plan is valid")
    validation_score: float = Field(..., ge=0, le=1, description="Validation score (0-1)")
    validation_details: Dict[str, Any] = Field(..., description="Detailed validation results")
    recommendations: Optional[List[str]] = Field(None, description="Improvement recommendations")
    validated_at: datetime = Field(default_factory=datetime.utcnow, description="Validation timestamp")


class PlanOptimizationRequest(BaseModel):
    """Schema for plan optimization request"""
    current_plan: Dict[str, Any] = Field(..., description="Current plan data")
    learner_progress: Dict[str, Any] = Field(..., description="Learner progress data")
    optimization_goals: List[str] = Field(..., description="Optimization objectives")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Optimization constraints")


class PlanOptimizationResponse(BaseModel):
    """Schema for plan optimization response"""
    success: bool = Field(..., description="Whether optimization was successful")
    optimized_plan: Dict[str, Any] = Field(..., description="Optimized plan data")
    optimization_summary: Dict[str, Any] = Field(..., description="Summary of optimizations made")
    improvement_metrics: Dict[str, float] = Field(..., description="Improvement metrics")
    optimized_at: datetime = Field(default_factory=datetime.utcnow, description="Optimization timestamp")


class PersonalizedContentRequest(BaseModel):
    """Schema for generating personalized content for specific slides"""
    learner_session_id: UUID = Field(..., description="Learner session ID")
    slide_id: UUID = Field(..., description="Slide ID to generate content for")
    content_type: Literal["text", "visual", "interactive", "assessment"] = Field(..., description="Type of content to generate")
    personalization_level: Literal["basic", "moderate", "deep"] = Field("moderate", description="Level of personalization")
    additional_context: Optional[str] = Field(None, max_length=500, description="Additional context for content generation")


class PersonalizedContentResponse(BaseModel):
    """Schema for personalized content response"""
    success: bool = Field(..., description="Whether content generation was successful")
    slide_id: UUID = Field(..., description="Slide ID")
    content_type: str = Field(..., description="Type of generated content")
    generated_content: str = Field(..., description="Generated personalized content")
    personalization_factors: List[str] = Field(..., description="Factors used for personalization")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    content_metadata: Dict[str, Any] = Field(..., description="Content metadata and suggestions")


class PlanGenerationStatistics(BaseModel):
    """Schema for plan generation statistics"""
    total_plans_generated: int = Field(..., description="Total number of plans generated")
    cache_hit_rate: float = Field(..., ge=0, le=1, description="Cache hit rate for plan generation")
    average_generation_time: float = Field(..., description="Average generation time in seconds")
    plans_by_level: Dict[str, int] = Field(..., description="Plans count by experience level")
    plans_by_style: Dict[str, int] = Field(..., description="Plans count by learning style")
    plans_by_sector: Dict[str, int] = Field(..., description="Plans count by activity sector")
    token_usage_stats: Dict[str, int] = Field(..., description="Token usage statistics")
    cost_savings: Dict[str, float] = Field(..., description="Cost savings from caching")


class PlanGenerationHealth(BaseModel):
    """Schema for plan generation service health"""
    status: str = Field(..., description="Service status")
    service: str = Field("Plan Generation", description="Service name")
    cache_service_available: bool = Field(..., description="Whether cache service is available")
    gemini_api_available: bool = Field(..., description="Whether Gemini API is available")
    last_successful_generation: Optional[datetime] = Field(None, description="Last successful plan generation")
    current_load: int = Field(..., description="Current number of active generations")
    available_operations: List[str] = Field(..., description="Available operations")


class PlanTemplateRequest(BaseModel):
    """Schema for creating plan templates"""
    template_name: str = Field(..., min_length=1, max_length=100, description="Template name")
    target_level: Literal["beginner", "intermediate", "advanced"] = Field(..., description="Target experience level")
    target_style: Literal["visual", "auditory", "kinesthetic", "reading"] = Field(..., description="Target learning style")
    sector_focus: Optional[str] = Field(None, max_length=100, description="Sector focus")
    template_structure: Dict[str, Any] = Field(..., description="Template structure definition")
    description: Optional[str] = Field(None, max_length=500, description="Template description")


class PlanTemplateResponse(BaseModel):
    """Schema for plan template response"""
    id: UUID = Field(..., description="Template ID")
    template_name: str = Field(..., description="Template name")
    target_level: str = Field(..., description="Target experience level")
    target_style: str = Field(..., description="Target learning style")
    sector_focus: Optional[str] = Field(None, description="Sector focus")
    template_structure: Dict[str, Any] = Field(..., description="Template structure")
    description: Optional[str] = Field(None, description="Template description")
    created_at: datetime = Field(..., description="Creation timestamp")
    usage_count: int = Field(0, description="Number of times template was used")
    success_rate: float = Field(0.0, ge=0, le=1, description="Template success rate")


class PlanGenerationError(BaseModel):
    """Schema for plan generation errors"""
    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Error message")
    learner_session_id: Optional[UUID] = Field(None, description="Learner session ID if applicable")
    training_id: Optional[UUID] = Field(None, description="Training ID if applicable")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    stack_trace: Optional[str] = Field(None, description="Stack trace if available")
    suggested_actions: Optional[List[str]] = Field(None, description="Suggested actions to resolve error")