"""
AI Adapter Port - Domain Interface for AI Services
Pure domain interface without infrastructure dependencies
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from uuid import UUID


class AIAdapterPort(ABC):
    """Port for AI adapter operations from domain layer"""
    
    @abstractmethod
    async def generate_content(
        self, 
        prompt: str, 
        model_name: Optional[str] = None,
        context_cache_id: Optional[str] = None,
        temperature: float = 0.7,
        session_id: Optional[str] = None,
        learner_session_id: Optional[str] = None
    ) -> str:
        """Generate content using AI model"""
        pass
    
    @abstractmethod
    async def process_document(
        self, 
        file_path: str, 
        analysis_prompt: str
    ) -> Dict[str, Any]:
        """Process document with AI analysis"""
        pass
    
    @abstractmethod
    async def create_context_cache(
        self, 
        content: str, 
        ttl_hours: int = 12
    ) -> str:
        """Create context cache and return cache ID"""
        pass
    
    @abstractmethod
    async def delete_context_cache(self, cache_id: str) -> bool:
        """Delete context cache by ID"""
        pass


class AIError(Exception):
    """Domain exception for AI-related errors"""
    pass


class RateLimitExceededException(AIError):
    """Domain exception for rate limit exceeded"""
    pass