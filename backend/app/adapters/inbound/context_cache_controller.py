"""
FIA v3.0 - Context Cache Controller
API endpoints for context cache management
"""

import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pathlib import Path

from app.domain.services.context_cache_service import (
    ContextCacheService,
    ContextCacheError
)
from app.domain.services.document_processing_service import DocumentProcessingService
from app.domain.schemas.context_cache import (
    ContextCacheCreateRequest,
    ContextCacheResponse,
    ContextCacheInfo,
    ContextCacheListResponse,
    CacheExpirationUpdateRequest,
    CacheExpirationUpdateResponse,
    CacheContentGenerationRequest,
    CacheContentGenerationResponse,
    CacheDeleteResponse,
    CacheHealthResponse,
    CacheStatistics,
    TrainingDocumentCacheRequest,
    TrainingDocumentCacheResponse,
    CacheFindRequest,
    CacheFindResponse
)
from app.infrastructure.auth import get_current_trainer
from app.domain.entities import Training
from app.infrastructure.database import AsyncSessionLocal

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/context-cache", tags=["Context Cache"])


def get_context_cache_service() -> ContextCacheService:
    """Dependency to get context cache service"""
    return ContextCacheService()


def get_document_processing_service() -> DocumentProcessingService:
    """Dependency to get document processing service"""
    return DocumentProcessingService()


@router.post(
    "/create",
    response_model=ContextCacheResponse,
    summary="Create context cache",
    description="Create a new context cache for a training document"
)
async def create_context_cache(
    request: ContextCacheCreateRequest,
    current_trainer = Depends(get_current_trainer),
    cache_service: ContextCacheService = Depends(get_context_cache_service)
) -> ContextCacheResponse:
    """
    Create a context cache for a document
    
    Args:
        request: Cache creation request
        current_trainer: Current authenticated trainer
        cache_service: Context cache service
        
    Returns:
        Cache creation response
    """
    try:
        logger.info(f"Creating context cache for: {request.file_path}")
        
        # Validate file exists
        if not Path(request.file_path).exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {request.file_path}"
            )
        
        # Create cache
        cache_result = await cache_service.create_document_cache(
            file_path=request.file_path,
            mime_type=request.mime_type,
            display_name=request.display_name,
            ttl_hours=request.ttl_hours,
            system_instruction=request.system_instruction
        )
        
        return ContextCacheResponse(**cache_result)
        
    except ContextCacheError as e:
        logger.error(f"Context cache error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cache creation failed"
        )


@router.get(
    "/list",
    response_model=ContextCacheListResponse,
    summary="List context caches",
    description="List all context caches for the project"
)
async def list_context_caches(
    current_trainer = Depends(get_current_trainer),
    cache_service: ContextCacheService = Depends(get_context_cache_service)
) -> ContextCacheListResponse:
    """
    List all context caches
    
    Args:
        current_trainer: Current authenticated trainer
        cache_service: Context cache service
        
    Returns:
        List of context caches
    """
    try:
        caches = await cache_service.list_caches()
        
        return ContextCacheListResponse(
            caches=[ContextCacheInfo(**cache) for cache in caches],
            total_count=len(caches)
        )
        
    except ContextCacheError as e:
        logger.error(f"Context cache error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error listing caches: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cache listing failed"
        )


@router.get(
    "/{cache_id}",
    response_model=ContextCacheInfo,
    summary="Get cache information",
    description="Get detailed information about a specific cache"
)
async def get_cache_info(
    cache_id: str,
    current_trainer = Depends(get_current_trainer),
    cache_service: ContextCacheService = Depends(get_context_cache_service)
) -> ContextCacheInfo:
    """
    Get information about a specific cache
    
    Args:
        cache_id: Cache ID to retrieve
        current_trainer: Current authenticated trainer
        cache_service: Context cache service
        
    Returns:
        Cache information
    """
    try:
        cache_info = await cache_service.get_cache_info(cache_id)
        return ContextCacheInfo(**cache_info)
        
    except ContextCacheError as e:
        logger.error(f"Context cache error: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error getting cache info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cache info retrieval failed"
        )


@router.patch(
    "/update-expiration",
    response_model=CacheExpirationUpdateResponse,
    summary="Update cache expiration",
    description="Update the expiration time (TTL) of a context cache"
)
async def update_cache_expiration(
    request: CacheExpirationUpdateRequest,
    current_trainer = Depends(get_current_trainer),
    cache_service: ContextCacheService = Depends(get_context_cache_service)
) -> CacheExpirationUpdateResponse:
    """
    Update cache expiration time
    
    Args:
        request: Expiration update request
        current_trainer: Current authenticated trainer
        cache_service: Context cache service
        
    Returns:
        Update response
    """
    try:
        result = await cache_service.update_cache_expiration(
            cache_id=request.cache_id,
            ttl_hours=request.ttl_hours
        )
        
        return CacheExpirationUpdateResponse(**result)
        
    except ContextCacheError as e:
        logger.error(f"Context cache error: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error updating cache expiration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cache expiration update failed"
        )


@router.post(
    "/generate",
    response_model=CacheContentGenerationResponse,
    summary="Generate content with cache",
    description="Generate content using a cached context"
)
async def generate_content_with_cache(
    request: CacheContentGenerationRequest,
    current_trainer = Depends(get_current_trainer),
    cache_service: ContextCacheService = Depends(get_context_cache_service)
) -> CacheContentGenerationResponse:
    """
    Generate content using cached context
    
    Args:
        request: Content generation request
        current_trainer: Current authenticated trainer
        cache_service: Context cache service
        
    Returns:
        Generated content response
    """
    try:
        result = await cache_service.use_cached_content(
            cache_id=request.cache_id,
            prompt=request.prompt,
            max_output_tokens=request.max_output_tokens,
            temperature=request.temperature,
            top_p=request.top_p
        )
        
        return CacheContentGenerationResponse(**result)
        
    except ContextCacheError as e:
        logger.error(f"Context cache error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error generating content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content generation failed"
        )


@router.delete(
    "/{cache_id}",
    response_model=CacheDeleteResponse,
    summary="Delete context cache",
    description="Delete a context cache"
)
async def delete_context_cache(
    cache_id: str,
    current_trainer = Depends(get_current_trainer),
    cache_service: ContextCacheService = Depends(get_context_cache_service)
) -> CacheDeleteResponse:
    """
    Delete a context cache
    
    Args:
        cache_id: Cache ID to delete
        current_trainer: Current authenticated trainer
        cache_service: Context cache service
        
    Returns:
        Deletion response
    """
    try:
        success = await cache_service.delete_cache(cache_id)
        
        if success:
            return CacheDeleteResponse(
                success=True,
                cache_id=cache_id,
                deleted_at=str(status.HTTP_200_OK)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cache not found or already deleted"
            )
        
    except ContextCacheError as e:
        logger.error(f"Context cache error: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error deleting cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cache deletion failed"
        )


@router.post(
    "/training/{training_id}",
    response_model=TrainingDocumentCacheResponse,
    summary="Cache training document",
    description="Create or get cache for a specific training document"
)
async def cache_training_document(
    training_id: str,
    request: TrainingDocumentCacheRequest,
    current_trainer = Depends(get_current_trainer),
    doc_service: DocumentProcessingService = Depends(get_document_processing_service)
) -> TrainingDocumentCacheResponse:
    """
    Create or get cache for a training document
    
    Args:
        training_id: Training ID
        request: Training cache request
        current_trainer: Current authenticated trainer
        doc_service: Document processing service
        
    Returns:
        Training document cache response
    """
    try:
        # Get training from database
        async with AsyncSessionLocal() as session:
            training = await session.get(Training, training_id)
            if not training:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Training not found"
                )
            
            # Check if trainer owns this training
            if training.trainer_id != current_trainer.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this training"
                )
        
        # Check for existing cache
        cache_info = None
        if not request.force_refresh:
            cache_info = await doc_service.get_cache_for_document(
                file_path=training.file_path,
                mime_type=training.mime_type
            )
        
        was_existing = cache_info is not None
        
        # Create cache if needed
        if not cache_info or request.force_refresh:
            cache_result = await doc_service.create_cache_for_document(
                file_path=training.file_path,
                mime_type=training.mime_type,
                display_name=f"Training: {training.name}",
                ttl_hours=request.ttl_hours
            )
            cache_response = ContextCacheResponse(**cache_result)
        else:
            # Convert existing cache info to response format
            cache_response = ContextCacheResponse(
                success=True,
                cache_id=cache_info['cache_id'],
                cache_key='existing',
                display_name=cache_info['display_name'],
                model=cache_info['model'],
                created_at=cache_info['created_at'],
                expires_at=cache_info['expires_at'],
                ttl_hours=24,  # Default fallback
                file_info={
                    'path': training.file_path,
                    'name': training.file_name,
                    'mime_type': training.mime_type,
                    'size_bytes': training.file_size or 0
                },
                usage_metadata=cache_info['usage_metadata']
            )
        
        return TrainingDocumentCacheResponse(
            training_id=request.training_id,
            cache_info=cache_response,
            was_existing=was_existing,
            cached_at=cache_response.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error caching training document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Training document caching failed"
        )


@router.post(
    "/find",
    response_model=CacheFindResponse,
    summary="Find cache by document",
    description="Find existing cache for a document"
)
async def find_cache_by_document(
    request: CacheFindRequest,
    current_trainer = Depends(get_current_trainer),
    cache_service: ContextCacheService = Depends(get_context_cache_service)
) -> CacheFindResponse:
    """
    Find cache for a document
    
    Args:
        request: Cache find request
        current_trainer: Current authenticated trainer
        cache_service: Context cache service
        
    Returns:
        Cache find response
    """
    try:
        cache_info = await cache_service.find_cache_by_document(
            file_path=request.file_path,
            mime_type=request.mime_type
        )
        
        if cache_info:
            return CacheFindResponse(
                found=True,
                cache_info=ContextCacheInfo(**cache_info),
                message="Cache found for document"
            )
        else:
            return CacheFindResponse(
                found=False,
                cache_info=None,
                message="No cache found for document"
            )
        
    except Exception as e:
        logger.error(f"Error finding cache: {e}")
        return CacheFindResponse(
            found=False,
            cache_info=None,
            message=f"Error searching for cache: {str(e)}"
        )


@router.get(
    "/health",
    response_model=CacheHealthResponse,
    summary="Cache service health check",
    description="Health check for context cache service"
)
async def cache_health_check(
    cache_service: ContextCacheService = Depends(get_context_cache_service)
) -> CacheHealthResponse:
    """
    Health check for context cache service
    
    Returns:
        Service health status
    """
    try:
        # Get cache count for health check
        caches = await cache_service.list_caches()
        
        return CacheHealthResponse(
            status="healthy",
            service="Context Cache",
            total_caches=len(caches),
            available_operations=[
                "create", "list", "get", "update_expiration", 
                "generate", "delete", "find"
            ]
        )
        
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Context cache service is unavailable"
        )


@router.get(
    "/statistics",
    response_model=CacheStatistics,
    summary="Get cache statistics",
    description="Get detailed statistics about context caches"
)
async def get_cache_statistics(
    current_trainer = Depends(get_current_trainer),
    cache_service: ContextCacheService = Depends(get_context_cache_service)
) -> CacheStatistics:
    """
    Get cache statistics
    
    Args:
        current_trainer: Current authenticated trainer
        cache_service: Context cache service
        
    Returns:
        Cache statistics
    """
    try:
        caches = await cache_service.list_caches()
        
        total_caches = len(caches)
        active_caches = len([c for c in caches if c.get('expires_at')])
        total_tokens = sum(c.get('usage_metadata', {}).get('cached_content_token_count', 0) for c in caches)
        
        # Calculate average TTL (simplified)
        avg_ttl = 12.0  # Default fallback
        
        return CacheStatistics(
            total_caches=total_caches,
            active_caches=active_caches,
            total_cached_tokens=total_tokens,
            average_ttl_hours=avg_ttl
        )
        
    except Exception as e:
        logger.error(f"Error getting cache statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get cache statistics"
        )