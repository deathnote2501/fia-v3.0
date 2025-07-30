"""
FIA v3.0 - Rate Limiter Infrastructure
Rate limiting for API calls with sliding window algorithm
"""

import asyncio
import time
import logging
from typing import Dict, Optional
from collections import defaultdict, deque

from app.infrastructure.settings import settings

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""
    pass


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter implementation
    Tracks requests in a time window and enforces limits
    """
    
    def __init__(self, requests_per_minute: int = 60, window_size_seconds: int = 60):
        self.requests_per_minute = requests_per_minute
        self.window_size_seconds = window_size_seconds
        self.requests: Dict[str, deque] = defaultdict(deque)
        self._lock = asyncio.Lock()
        
    async def is_allowed(self, key: str) -> bool:
        """
        Check if request is allowed for the given key
        
        Args:
            key: Identifier for the rate limit (e.g., 'gemini_api', 'user_123')
            
        Returns:
            True if request is allowed, False otherwise
        """
        async with self._lock:
            current_time = time.time()
            request_times = self.requests[key]
            
            # Remove old requests outside the time window
            cutoff_time = current_time - self.window_size_seconds
            while request_times and request_times[0] <= cutoff_time:
                request_times.popleft()
            
            # Check if we can make a new request
            if len(request_times) < self.requests_per_minute:
                request_times.append(current_time)
                return True
            
            return False
    
    async def wait_until_allowed(self, key: str, max_wait_seconds: int = 300) -> None:
        """
        Wait until a request is allowed or timeout
        
        Args:
            key: Identifier for the rate limit
            max_wait_seconds: Maximum time to wait in seconds
            
        Raises:
            RateLimitExceeded: If max wait time exceeded
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_seconds:
            if await self.is_allowed(key):
                return
            
            # Calculate wait time until next slot is available
            async with self._lock:
                request_times = self.requests[key]
                if request_times:
                    oldest_request = request_times[0]
                    wait_time = max(0.1, oldest_request + self.window_size_seconds - time.time())
                    wait_time = min(wait_time, 5.0)  # Maximum 5 seconds between checks
                else:
                    wait_time = 0.1
            
            await asyncio.sleep(wait_time)
        
        raise RateLimitExceeded(f"Rate limit exceeded for key '{key}' after {max_wait_seconds}s")
    
    def get_remaining_requests(self, key: str) -> int:
        """Get number of remaining requests in current window"""
        current_time = time.time()
        request_times = self.requests[key]
        
        # Count requests in current window
        cutoff_time = current_time - self.window_size_seconds
        current_requests = sum(1 for req_time in request_times if req_time > cutoff_time)
        
        return max(0, self.requests_per_minute - current_requests)
    
    def get_reset_time(self, key: str) -> Optional[float]:
        """Get timestamp when rate limit will reset"""
        request_times = self.requests[key]
        if not request_times:
            return None
        
        oldest_request = request_times[0]
        return oldest_request + self.window_size_seconds
    
    def clear_key(self, key: str) -> None:
        """Clear rate limit data for a specific key"""
        if key in self.requests:
            del self.requests[key]
    
    def clear_all(self) -> None:
        """Clear all rate limit data"""
        self.requests.clear()


class GeminiRateLimiter:
    """
    Specialized rate limiter for Gemini API calls
    Implements rate limiting per SPEC.md requirements
    """
    
    def __init__(self):
        self.rate_limiter = SlidingWindowRateLimiter(
            requests_per_minute=settings.gemini_rate_limit_per_minute,
            window_size_seconds=60
        )
        self.api_key = "gemini_api"
        
    async def acquire(self, wait: bool = True, max_wait_seconds: int = 300) -> None:
        """
        Acquire a rate limit slot for Gemini API
        
        Args:
            wait: Whether to wait if rate limit is exceeded
            max_wait_seconds: Maximum time to wait
            
        Raises:
            RateLimitExceeded: If rate limit exceeded and wait=False or timeout
        """
        if wait:
            await self.rate_limiter.wait_until_allowed(self.api_key, max_wait_seconds)
        else:
            if not await self.rate_limiter.is_allowed(self.api_key):
                remaining = self.rate_limiter.get_remaining_requests(self.api_key)
                reset_time = self.rate_limiter.get_reset_time(self.api_key)
                raise RateLimitExceeded(
                    f"Gemini API rate limit exceeded. "
                    f"Remaining requests: {remaining}. "
                    f"Reset time: {reset_time}"
                )
    
    def get_status(self) -> Dict[str, any]:
        """Get current rate limit status"""
        remaining = self.rate_limiter.get_remaining_requests(self.api_key)
        reset_time = self.rate_limiter.get_reset_time(self.api_key)
        
        return {
            "requests_per_minute": settings.gemini_rate_limit_per_minute,
            "remaining_requests": remaining,
            "reset_time": reset_time,
            "reset_in_seconds": max(0, reset_time - time.time()) if reset_time else 0
        }


# Global rate limiter instances
gemini_rate_limiter = GeminiRateLimiter()


class OpenAIRateLimiter:
    """
    Specialized rate limiter for OpenAI API calls
    Similar pattern to GeminiRateLimiter but with lower limits for cost control
    """
    
    def __init__(self):
        # Lower rate limit for image generation to control costs (10 images/minute)
        self.rate_limiter = SlidingWindowRateLimiter(
            requests_per_minute=10,
            window_size_seconds=60
        )
        self.api_key = "openai_api"
        
    async def acquire(self, wait: bool = True, max_wait_seconds: int = 300) -> None:
        """
        Acquire a rate limit slot for OpenAI API
        
        Args:
            wait: Whether to wait if rate limit is exceeded
            max_wait_seconds: Maximum time to wait
            
        Raises:
            RateLimitExceeded: If rate limit exceeded and wait=False or timeout
        """
        if wait:
            await self.rate_limiter.wait_until_allowed(self.api_key, max_wait_seconds)
        else:
            if not await self.rate_limiter.is_allowed(self.api_key):
                remaining = self.rate_limiter.get_remaining_requests(self.api_key)
                reset_time = self.rate_limiter.get_reset_time(self.api_key)
                raise RateLimitExceeded(
                    f"OpenAI API rate limit exceeded. "
                    f"Remaining requests: {remaining}. "
                    f"Reset time: {reset_time}"
                )
    
    def get_status(self) -> Dict[str, any]:
        """Get current rate limit status"""
        remaining = self.rate_limiter.get_remaining_requests(self.api_key)
        reset_time = self.rate_limiter.get_reset_time(self.api_key)
        
        return {
            "requests_per_minute": 10,
            "remaining_requests": remaining,
            "reset_time": reset_time,
            "reset_in_seconds": max(0, reset_time - time.time()) if reset_time else 0
        }


# Global rate limiter instances
openai_rate_limiter = OpenAIRateLimiter()


async def with_gemini_rate_limit(func, *args, **kwargs):
    """
    Decorator-like function to apply rate limiting to Gemini API calls
    
    Usage:
        result = await with_gemini_rate_limit(some_async_function, arg1, arg2)
    """
    await gemini_rate_limiter.acquire()
    
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in rate-limited function: {str(e)}")
        raise


class RateLimitMiddleware:
    """
    Rate limiting middleware for FastAPI
    Can be used to add rate limiting to specific endpoints
    """
    
    def __init__(self, requests_per_minute: int = 60):
        self.rate_limiter = SlidingWindowRateLimiter(requests_per_minute)
    
    async def __call__(self, request, call_next):
        """Middleware implementation for FastAPI"""
        # Extract client identifier (IP address)
        client_ip = request.client.host if request.client else "unknown"
        key = f"client_{client_ip}"
        
        if not await self.rate_limiter.is_allowed(key):
            from fastapi import HTTPException
            remaining = self.rate_limiter.get_remaining_requests(key)
            reset_time = self.rate_limiter.get_reset_time(key)
            
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "remaining_requests": remaining,
                    "reset_time": reset_time
                }
            )
        
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.rate_limiter.get_remaining_requests(key)
        reset_time = self.rate_limiter.get_reset_time(key)
        
        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        if reset_time:
            response.headers["X-RateLimit-Reset"] = str(int(reset_time))
        
        return response