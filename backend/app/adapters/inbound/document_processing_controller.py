"""
FIA v3.0 - Document Processing Controller
API endpoints for document processing functionality
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from pathlib import Path

from app.domain.services.document_processing_service import (
    DocumentProcessingService, 
    DocumentProcessingError
)
from app.domain.schemas.document_processing import (
    DocumentProcessingRequest,
    DocumentProcessingResponse,
    DocumentSummaryResponse,
    DocumentStructureResponse,
    DocumentValidationResponse
)
from app.infrastructure.auth import get_current_trainer


# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/document-processing", tags=["Document Processing"])


def get_document_processing_service() -> DocumentProcessingService:
    """Dependency to get document processing service"""
    return DocumentProcessingService()


@router.post(
    "/parse",
    response_model=DocumentProcessingResponse,
    summary="Parse document content",
    description="Parse PDF or PowerPoint document using Gemini Document Understanding"
)
async def parse_document(
    request: DocumentProcessingRequest,
    current_trainer = Depends(get_current_trainer),
    doc_service: DocumentProcessingService = Depends(get_document_processing_service)
) -> DocumentProcessingResponse:
    """
    Parse document content using Gemini Document Understanding API
    
    Args:
        request: Document processing request
        current_trainer: Current authenticated trainer
        doc_service: Document processing service
        
    Returns:
        Parsed document content and metadata
    """
    try:
        logger.info(f"Parsing document: {request.file_path} for trainer: {current_trainer.id}")
        
        # Validate file exists
        if not Path(request.file_path).exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {request.file_path}"
            )
        
        # Parse document
        result = await doc_service.parse_document_content(
            file_path=request.file_path,
            mime_type=request.mime_type,
            custom_prompt=request.custom_prompt
        )
        
        return DocumentProcessingResponse(**result)
        
    except DocumentProcessingError as e:
        logger.error(f"Document processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error parsing document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document parsing failed"
        )


@router.post(
    "/summary",
    response_model=DocumentSummaryResponse,
    summary="Get document summary",
    description="Extract a concise summary of the document content"
)
async def get_document_summary(
    request: DocumentProcessingRequest,
    current_trainer = Depends(get_current_trainer),
    doc_service: DocumentProcessingService = Depends(get_document_processing_service)
) -> DocumentSummaryResponse:
    """
    Get a concise summary of the document
    
    Args:
        request: Document processing request
        current_trainer: Current authenticated trainer
        doc_service: Document processing service
        
    Returns:
        Document summary
    """
    try:
        logger.info(f"Generating summary for: {request.file_path}")
        
        # Validate file exists
        if not Path(request.file_path).exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {request.file_path}"
            )
        
        # Get summary
        summary = await doc_service.extract_document_summary(
            file_path=request.file_path,
            mime_type=request.mime_type
        )
        
        return DocumentSummaryResponse(
            summary=summary,
            file_name=Path(request.file_path).name
        )
        
    except DocumentProcessingError as e:
        logger.error(f"Document summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error generating summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Summary generation failed"
        )


@router.post(
    "/structure",
    response_model=DocumentStructureResponse,
    summary="Analyze document structure",
    description="Analyze document structure for training plan generation"
)
async def analyze_document_structure(
    request: DocumentProcessingRequest,
    current_trainer = Depends(get_current_trainer),
    doc_service: DocumentProcessingService = Depends(get_document_processing_service)
) -> DocumentStructureResponse:
    """
    Analyze document structure for training purposes
    
    Args:
        request: Document processing request
        current_trainer: Current authenticated trainer
        doc_service: Document processing service
        
    Returns:
        Document structure analysis
    """
    try:
        logger.info(f"Analyzing structure for: {request.file_path}")
        
        # Validate file exists
        if not Path(request.file_path).exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {request.file_path}"
            )
        
        # Analyze structure
        result = await doc_service.analyze_document_structure(
            file_path=request.file_path,
            mime_type=request.mime_type
        )
        
        # Validate if suitable for training
        is_valid, _ = await doc_service.validate_document_for_training(
            file_path=request.file_path,
            mime_type=request.mime_type
        )
        
        return DocumentStructureResponse(
            structure_analysis=result.get('content', ''),
            file_name=Path(request.file_path).name,
            suitable_for_training=is_valid,
            processing_metadata=result.get('processing_metadata')
        )
        
    except DocumentProcessingError as e:
        logger.error(f"Document structure analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error analyzing structure: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Structure analysis failed"
        )


@router.post(
    "/validate",
    response_model=DocumentValidationResponse,
    summary="Validate document for training",
    description="Validate if document is suitable for creating training content"
)
async def validate_document_for_training(
    request: DocumentProcessingRequest,
    current_trainer = Depends(get_current_trainer),
    doc_service: DocumentProcessingService = Depends(get_document_processing_service)
) -> DocumentValidationResponse:
    """
    Validate if document is suitable for training purposes
    
    Args:
        request: Document processing request
        current_trainer: Current authenticated trainer
        doc_service: Document processing service
        
    Returns:
        Document validation result
    """
    try:
        logger.info(f"Validating document: {request.file_path}")
        
        # Validate file exists
        if not Path(request.file_path).exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {request.file_path}"
            )
        
        # Validate document
        is_valid, message = await doc_service.validate_document_for_training(
            file_path=request.file_path,
            mime_type=request.mime_type
        )
        
        return DocumentValidationResponse(
            is_valid=is_valid,
            validation_message=message,
            file_name=Path(request.file_path).name
        )
        
    except DocumentProcessingError as e:
        logger.error(f"Document validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error validating document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document validation failed"
        )


@router.get(
    "/health",
    summary="Check document processing service health",
    description="Health check for Gemini Document Processing service"
)
async def health_check(
    doc_service: DocumentProcessingService = Depends(get_document_processing_service)
) -> Dict[str, Any]:
    """
    Health check for document processing service
    
    Returns:
        Service health status
    """
    try:
        return {
            "status": "healthy",
            "service": "Document Processing",
            "gemini_model": doc_service.model_name,
            "message": "Service is operational"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Document processing service is unavailable"
        )