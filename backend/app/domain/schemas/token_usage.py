"""
FIA v3.0 - Token Usage Schemas
Pydantic schemas for token usage tracking API endpoints
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime


class TokenUsageTimeRange(BaseModel):
    """Time range filter for token usage queries"""
    start_time: Optional[str] = Field(None, description="Start time in ISO format (YYYY-MM-DDTHH:MM:SSZ)")
    end_time: Optional[str] = Field(None, description="End time in ISO format (YYYY-MM-DDTHH:MM:SSZ)")


class TokenUsageSummary(BaseModel):
    """Summary of token usage statistics"""
    total_tokens: int = Field(..., description="Total tokens consumed")
    input_tokens: int = Field(..., description="Total input tokens")
    output_tokens: int = Field(..., description="Total output tokens")
    total_calls: int = Field(..., description="Total number of AI calls")
    session_duration_seconds: Optional[float] = Field(None, description="Session duration in seconds")


class ServiceTypeUsage(BaseModel):
    """Token usage statistics for a specific service type"""
    input_tokens: int = Field(..., description="Input tokens for this service type")
    output_tokens: int = Field(..., description="Output tokens for this service type")
    calls: int = Field(..., description="Number of calls for this service type")
    service_names: List[str] = Field(..., description="List of service names in this category")


class CostEstimation(BaseModel):
    """Cost estimation based on token usage"""
    currency: str = Field(..., description="Currency code (e.g., USD)")
    input_cost: float = Field(..., description="Cost for input tokens")
    output_cost: float = Field(..., description="Cost for output tokens")
    total_cost: float = Field(..., description="Total estimated cost")
    cost_breakdown: Dict[str, Any] = Field(..., description="Detailed cost breakdown")
    note: str = Field(..., description="Information about cost estimation")


class RecentCall(BaseModel):
    """Information about a recent AI call"""
    call_id: str = Field(..., description="Unique call identifier")
    service_name: str = Field(..., description="Name of the service that made the call")
    service_type: str = Field(..., description="Type of service (plan, conversation, etc.)")
    timestamp: str = Field(..., description="Timestamp of the call in ISO format")
    input_tokens: int = Field(..., description="Input tokens used")
    output_tokens: int = Field(..., description="Output tokens generated")
    processing_time: float = Field(..., description="Processing time in seconds")


class TokenUsageMetadata(BaseModel):
    """Metadata about token usage data"""
    data_source: str = Field(..., description="Source of the data (e.g., application_logs)")
    estimation_accuracy: str = Field(..., description="Accuracy level (high/estimated)")


class TokenUsageResponse(BaseModel):
    """Complete token usage response"""
    learner_session_id: str = Field(..., description="ID of the learner session")
    query_time: str = Field(..., description="Time when the query was executed")
    time_range: TokenUsageTimeRange = Field(..., description="Time range for the query")
    summary: TokenUsageSummary = Field(..., description="Summary statistics")
    by_service_type: Dict[str, ServiceTypeUsage] = Field(..., description="Breakdown by service type")
    recent_calls: List[RecentCall] = Field(..., description="Recent AI calls")
    cost_estimation: CostEstimation = Field(..., description="Cost estimation")
    metadata: TokenUsageMetadata = Field(..., description="Metadata about the data")
    error: Optional[Dict[str, str]] = Field(None, description="Error information if query failed")


class TokenUsageErrorResponse(BaseModel):
    """Error response for token usage endpoints"""
    learner_session_id: str = Field(..., description="ID of the learner session")
    query_time: str = Field(..., description="Time when the query was executed")
    error: Dict[str, str] = Field(..., description="Error details")
    summary: TokenUsageSummary = Field(..., description="Empty summary")
    by_service_type: Dict[str, ServiceTypeUsage] = Field(default_factory=dict, description="Empty breakdown")
    recent_calls: List[RecentCall] = Field(default_factory=list, description="Empty calls list")
    cost_estimation: Dict[str, str] = Field(..., description="Error cost estimation")


class ServiceTypeAnalyticsResponse(BaseModel):
    """Response for service type analytics"""
    learner_session_id: str = Field(..., description="ID of the learner session")
    service_types: Dict[str, ServiceTypeUsage] = Field(..., description="Service type breakdown")
    insights: List[str] = Field(..., description="Usage insights and patterns")
    recommendations: List[str] = Field(..., description="Optimization recommendations")
    error: Optional[str] = Field(None, description="Error message if analysis failed")


class TokenUsageHealthResponse(BaseModel):
    """Health check response for token usage service"""
    status: str = Field(..., description="Service status (healthy/degraded/unhealthy)")
    logger_adapter_available: bool = Field(..., description="Whether logger adapter is available")
    service: str = Field(default="token_usage", description="Service name")
    version: str = Field(default="3.0", description="Service version")
    error: Optional[str] = Field(None, description="Error message if unhealthy")