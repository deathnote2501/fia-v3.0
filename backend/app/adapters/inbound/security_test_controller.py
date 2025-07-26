"""
FIA v3.0 - Security Test Controller
API endpoints for testing security error handling
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/security-test", tags=["Security Testing"])


@router.post("/error-disclosure-test")
async def test_error_disclosure() -> Dict[str, Any]:
    """
    Test endpoint to verify error disclosure is properly handled
    
    This endpoint intentionally raises an exception to test that:
    1. Detailed error messages are logged server-side
    2. Generic error messages are returned to clients
    3. No sensitive information is disclosed
    """
    try:
        # Simulate a database connection error with sensitive info
        sensitive_info = "database_password_123"
        database_host = "internal-db-server.company.com"
        
        # This would be a real error in production
        raise Exception(f"Database connection failed to {database_host} with password {sensitive_info}")
        
    except Exception as e:
        # ✅ CORRECT: Log detailed error server-side
        logger.error(f"Security test error with sensitive details: {str(e)}")
        
        # ✅ CORRECT: Return generic error to client
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred"
        )


@router.post("/file-operation-test") 
async def test_file_operation_error() -> Dict[str, Any]:
    """
    Test file operation error handling
    """
    try:
        # Simulate file operation error with path disclosure
        file_path = "/etc/passwd"
        api_key = "sk-1234567890abcdef"
        
        raise Exception(f"Failed to access file {file_path} with API key {api_key}")
        
    except Exception as e:
        # ✅ CORRECT: Log with context but hide from client
        logger.error(f"File operation test failed: {str(e)}")
        
        # ✅ CORRECT: Generic message to client
        raise HTTPException(
            status_code=500,
            detail="File operation failed"
        )


@router.get("/logging-verification")
async def verify_logging_configuration() -> Dict[str, Any]:
    """
    Verify that logging is properly configured
    """
    try:
        # Test different log levels
        logger.debug("Debug message test")
        logger.info("Info message test") 
        logger.warning("Warning message test")
        logger.error("Error message test")
        
        return {
            "success": True,
            "message": "Logging test completed",
            "logger_name": logger.name,
            "log_levels_tested": ["debug", "info", "warning", "error"]
        }
        
    except Exception as e:
        logger.error(f"Logging verification failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Logging verification failed"
        )


@router.post("/rate-limit-error-test")
async def test_rate_limit_error_handling() -> Dict[str, Any]:
    """
    Test rate limiting error handling
    """
    from app.infrastructure.rate_limiter import RateLimitExceeded
    
    try:
        # Simulate rate limit exceeded with internal details
        internal_key = "user_123_internal_id"
        remaining_time = 45.7
        
        raise RateLimitExceeded(f"Rate limit exceeded for key {internal_key}, reset in {remaining_time}s")
        
    except RateLimitExceeded as e:
        # ✅ CORRECT: Log rate limit details
        logger.warning(f"Rate limit test exceeded: {str(e)}")
        
        # ✅ CORRECT: Generic rate limit message
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )
    except Exception as e:
        logger.error(f"Rate limit test failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Rate limit test failed"
        )