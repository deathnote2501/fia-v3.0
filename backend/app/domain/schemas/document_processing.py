"""
FIA v3.0 - Document Processing Schemas
Pydantic schemas for document processing responses
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class DocumentProcessingRequest(BaseModel):
    """Schema for document processing request"""
    file_path: str = Field(..., description="Path to the document file")
    mime_type: str = Field(..., description="MIME type of the document")
    custom_prompt: Optional[str] = Field(None, description="Custom prompt for processing")


class DocumentFileInfo(BaseModel):
    """Schema for document file information"""
    path: str = Field(..., description="File path")
    name: str = Field(..., description="File name")
    mime_type: str = Field(..., description="MIME type")


class ProcessingMetadata(BaseModel):
    """Schema for processing metadata"""
    model_used: str = Field(..., description="Gemini model used")
    content_length: int = Field(..., description="Length of processed content")
    timestamp: float = Field(..., description="Processing timestamp")


class DocumentProcessingResponse(BaseModel):
    """Schema for document processing response"""
    success: bool = Field(..., description="Whether processing was successful")
    content: str = Field(..., description="Processed document content")
    file_info: DocumentFileInfo = Field(..., description="File information")
    processing_metadata: Optional[ProcessingMetadata] = Field(None, description="Processing metadata")
    error: Optional[str] = Field(None, description="Error message if processing failed")


class DocumentSummaryResponse(BaseModel):
    """Schema for document summary response"""
    summary: str = Field(..., description="Document summary")
    file_name: str = Field(..., description="Source file name")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")


class DocumentStructureResponse(BaseModel):
    """Schema for document structure analysis response"""
    structure_analysis: str = Field(..., description="Structured analysis of the document")
    file_name: str = Field(..., description="Source file name")
    suitable_for_training: bool = Field(..., description="Whether document is suitable for training")
    processing_metadata: Optional[ProcessingMetadata] = Field(None, description="Processing metadata")


class DocumentValidationResponse(BaseModel):
    """Schema for document validation response"""
    is_valid: bool = Field(..., description="Whether document is valid for training")
    validation_message: str = Field(..., description="Validation result message")
    file_name: str = Field(..., description="Source file name")


class DocumentProcessingError(BaseModel):
    """Schema for document processing errors"""
    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Error message")
    file_path: Optional[str] = Field(None, description="File path that caused error")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")