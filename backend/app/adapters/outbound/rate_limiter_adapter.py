"""
Rate Limiter Adapter - Infrastructure Implementation of Rate Limiter Port
"""

from typing import Optional

from app.domain.ports.rate_limiter_port import RateLimiterPort, RateLimitExceededException
from app.infrastructure.rate_limiter import gemini_rate_limiter, RateLimitExceeded


class RateLimiterAdapter(RateLimiterPort):
    """Adapter that implements RateLimiterPort using infrastructure rate limiter"""
    
    async def check_rate_limit(self, key: str, limit_per_minute: int) -> bool:
        """Check if operation is within rate limit"""
        try:
            return await gemini_rate_limiter.check_rate_limit(key, limit_per_minute)
        except RateLimitExceeded as e:
            raise RateLimitExceededException(str(e), retry_after=e.retry_after) from e
    
    async def get_remaining_requests(self, key: str) -> Optional[int]:
        """Get remaining requests for the current window"""
        return await gemini_rate_limiter.get_remaining_requests(key)
    
    async def reset_rate_limit(self, key: str) -> bool:
        """Reset rate limit for a specific key"""
        return await gemini_rate_limiter.reset_rate_limit(key)