"""
Rate Limiter Adapter - Infrastructure Implementation of Rate Limiter Port
"""

from typing import Optional

from app.domain.ports.rate_limiter_port import RateLimiterPort, RateLimitExceededException
from app.infrastructure.rate_limiter import gemini_rate_limiter, RateLimitExceeded


class RateLimiterAdapter(RateLimiterPort):
    """Adapter that implements RateLimiterPort using infrastructure rate limiter"""
    
    async def acquire(self, wait: bool = True, max_wait_seconds: int = 60) -> bool:
        """
        Acquire a rate limit slot using the gemini rate limiter
        
        Args:
            wait: Whether to wait if rate limit is exceeded
            max_wait_seconds: Maximum time to wait in seconds
            
        Returns:
            True if slot acquired successfully
            
        Raises:
            RateLimitExceededException: If rate limit exceeded and wait=False
        """
        try:
            # Use the gemini rate limiter to acquire a slot
            await gemini_rate_limiter.acquire(wait=wait)
            return True
        except RateLimitExceeded as e:
            # Extract retry time if available
            status = gemini_rate_limiter.get_status()
            retry_after = int(status.get('reset_in_seconds', 60))
            raise RateLimitExceededException(str(e), retry_after=retry_after) from e
    
    async def check_rate_limit(self, key: str, limit_per_minute: int) -> bool:
        """Check if operation is within rate limit"""
        try:
            # Use the gemini rate limiter to check if requests are allowed
            await gemini_rate_limiter.acquire(wait=False)
            return True
        except RateLimitExceeded as e:
            # Extract retry time if available
            status = gemini_rate_limiter.get_status()
            retry_after = int(status.get('reset_in_seconds', 60))
            raise RateLimitExceededException(str(e), retry_after=retry_after) from e
    
    async def get_remaining_requests(self, key: str) -> Optional[int]:
        """Get remaining requests for the current window"""
        status = gemini_rate_limiter.get_status()
        return status.get('remaining_requests')
    
    async def reset_rate_limit(self, key: str) -> bool:
        """Reset rate limit for a specific key"""
        # Clear the rate limiter for the given key
        gemini_rate_limiter.rate_limiter.clear_key(key)
        return True