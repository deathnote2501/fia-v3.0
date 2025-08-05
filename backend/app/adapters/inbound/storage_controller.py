"""
FIA v3.0 - Storage Controller
API endpoints for storage status and management
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from app.infrastructure.dependencies import get_file_storage_service, get_storage_info
from app.domain.ports.file_storage import FileStoragePort
from app.adapters.outbound.cloudflare_r2_storage_adapter import CloudflareR2StorageAdapter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/storage", tags=["Storage Management"])


@router.get("/status", summary="Get storage system status")
async def get_storage_status(
    storage_service: FileStoragePort = Depends(get_file_storage_service)
) -> Dict[str, Any]:
    """
    Get comprehensive storage system status
    
    Returns information about:
    - Storage type (local/R2)
    - Configuration
    - Health status
    - Warnings for Railway deployment
    """
    
    try:
        # Get basic storage info
        storage_info = get_storage_info()
        
        # Perform health check if R2
        health_status = {}
        if isinstance(storage_service, CloudflareR2StorageAdapter):
            health_status = await storage_service.health_check()
        
        # Railway deployment warnings
        warnings = []
        if storage_info["type"] == "local_filesystem":
            warnings.extend([
                "⚠️ Local storage is not persistent on Railway",
                "⚠️ Uploaded files will be lost on container restart",
                "⚠️ Consider migrating to Cloudflare R2 for production"
            ])
        
        return {
            "storage_configuration": storage_info,
            "health_check": health_status,
            "warnings": warnings,
            "recommendation": (
                "✅ Using persistent R2 storage" 
                if storage_info["type"] == "cloudflare_r2" 
                else "❌ Migrate to R2 for persistent storage"
            )
        }
        
    except Exception as e:
        logger.error(f"❌ Storage status check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Storage status check failed: {str(e)}"
        )


@router.get("/health", summary="Storage health check")
async def storage_health_check(
    storage_service: FileStoragePort = Depends(get_file_storage_service)
) -> Dict[str, Any]:
    """
    Simple health check endpoint for storage system
    """
    
    try:
        if isinstance(storage_service, CloudflareR2StorageAdapter):
            return await storage_service.health_check()
        else:
            # Local storage always "healthy" but not persistent
            return {
                "status": "healthy",
                "type": "local_filesystem",
                "warning": "Not persistent on Railway - files lost on restart"
            }
            
    except Exception as e:
        logger.error(f"❌ Storage health check failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


@router.get("/migration-guide", summary="Get R2 migration guide")
async def get_migration_guide() -> Dict[str, Any]:
    """
    Get step-by-step guide for migrating to Cloudflare R2
    """
    
    return {
        "title": "Migration to Cloudflare R2 Storage",
        "current_issue": {
            "problem": "Railway containers are ephemeral - uploaded files are lost on restart",
            "impact": "Training materials disappear when application restarts"
        },
        "solution": {
            "name": "Cloudflare R2",
            "benefits": [
                "Persistent storage survives container restarts",
                "S3-compatible API",
                "No egress fees",
                "Scalable across multiple Railway instances",
                "Cost-effective ($0.015/GB/month)"
            ]
        },
        "setup_steps": [
            "1. Create Cloudflare R2 bucket",
            "2. Generate R2 API tokens",
            "3. Set Railway environment variables",
            "4. Test storage configuration",
            "5. Deploy and verify"
        ],
        "environment_variables": {
            "STORAGE_TYPE": "r2",
            "R2_BUCKET_NAME": "your-bucket-name",
            "R2_ENDPOINT_URL": "https://your-account-id.r2.cloudflarestorage.com",
            "R2_ACCESS_KEY": "your-r2-access-key",
            "R2_SECRET_KEY": "your-r2-secret-key"
        },
        "testing": {
            "endpoints": [
                "GET /api/storage/status - Check configuration",
                "GET /api/storage/health - Verify connectivity"
            ]
        }
    }