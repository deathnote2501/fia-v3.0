"""
Rate Limiter Port - Domain Interface for Rate Limiting
Pure domain interface without infrastructure dependencies
"""

from abc import ABC, abstractmethod
from typing import Optional


class RateLimiterPort(ABC):
    """Port for rate limiting operations from domain layer"""
    
    @abstractmethod
    async def check_rate_limit(self, key: str, limit_per_minute: int) -> bool:
        """Check if operation is within rate limit"""
        pass
    
    @abstractmethod
    async def get_remaining_requests(self, key: str) -> Optional[int]:
        """Get remaining requests for the current window"""
        pass
    
    @abstractmethod
    async def reset_rate_limit(self, key: str) -> bool:
        """Reset rate limit for a specific key"""
        pass


class RateLimitExceededException(Exception):
    """Domain exception for rate limit exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after