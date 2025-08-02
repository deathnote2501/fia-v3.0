"""
AI Adapter - Infrastructure Implementation of AI Adapter Port
"""

from typing import Dict, Any, Optional
from uuid import UUID

from app.domain.ports.ai_adapter_port import AIAdapterPort, AIError, RateLimitExceededException
from app.infrastructure.adapters.vertex_ai_adapter import VertexAIAdapter, VertexAIError


class AIAdapter(AIAdapterPort):
    """Adapter that implements AIAdapterPort using VertexAI infrastructure"""
    
    def __init__(self):
        self.vertex_ai = VertexAIAdapter()
    
    async def generate_content(
        self, 
        prompt: str, 
        model_name: str,
        context_cache_id: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate content using AI model"""
        try:
            return await self.vertex_ai.generate_content(
                prompt=prompt,
                model_name=model_name,
                context_cache_id=context_cache_id,
                temperature=temperature
            )
        except VertexAIError as e:
            raise AIError(str(e)) from e
    
    async def process_document(
        self, 
        file_path: str, 
        analysis_prompt: str
    ) -> Dict[str, Any]:
        """Process document with AI analysis"""
        try:
            return await self.vertex_ai.process_document(
                file_path=file_path,
                analysis_prompt=analysis_prompt
            )
        except VertexAIError as e:
            raise AIError(str(e)) from e
    
    async def create_context_cache(
        self, 
        content: str, 
        ttl_hours: int = 12
    ) -> str:
        """Create context cache and return cache ID"""
        try:
            return await self.vertex_ai.create_context_cache(
                content=content,
                ttl_hours=ttl_hours
            )
        except VertexAIError as e:
            raise AIError(str(e)) from e
    
    async def delete_context_cache(self, cache_id: str) -> bool:
        """Delete context cache by ID"""
        try:
            return await self.vertex_ai.delete_context_cache(cache_id)
        except VertexAIError as e:
            raise AIError(str(e)) from e