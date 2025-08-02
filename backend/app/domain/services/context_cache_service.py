"""
FIA v3.0 - Context Cache Service
Service for managing Gemini Context Caching for training materials
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime, timedelta
import hashlib

import google.generativeai as genai

from app.domain.ports.settings_port import SettingsPort
from app.domain.ports.ai_adapter_port import AIAdapterPort, AIError

# Configure logging
logger = logging.getLogger(__name__)


class ContextCacheError(Exception):
    """Custom exception for context cache errors"""
    pass


class ContextCacheService:
    """Service for managing Gemini Context Caching for training documents"""
    
    def __init__(self, settings_port: SettingsPort, ai_adapter: AIAdapterPort):
        """Initialize the context cache service"""
        self.settings = settings_port
        self.ai_adapter = ai_adapter
        self.client = self._initialize_gemini_client()
        self.model_name = self.settings.get_gemini_model_name()
        self.default_ttl_hours = self.settings.get_context_cache_ttl_hours()
        
    def _initialize_gemini_client(self):
        """Initialize Gemini client with API key configuration"""
        try:
            if not settings.gemini_api_key:
                raise ContextCacheError("Gemini API key not configured")
            
            # Configure Gemini with API key
            genai.configure(api_key=settings.gemini_api_key)
            
            # Create model instance
            model = genai.GenerativeModel(settings.gemini_model_name)
            
            logger.info(f"✅ Gemini model initialized: {settings.gemini_model_name}")
            return model
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini model: {e}")
            raise ContextCacheError(f"Failed to initialize Gemini model: {e}")
    
    def _generate_cache_key(self, file_path: str, mime_type: str) -> str:
        """
        Generate a unique cache key for a document
        
        Args:
            file_path: Path to the document
            mime_type: MIME type of the document
            
        Returns:
            Unique cache key string
        """
        # Use file path, mime type, and file modification time for uniqueness
        file_stat = Path(file_path).stat()
        key_input = f"{file_path}:{mime_type}:{file_stat.st_mtime}:{file_stat.st_size}"
        
        # Generate SHA256 hash for consistent key
        cache_key = hashlib.sha256(key_input.encode()).hexdigest()[:16]
        
        return f"training-doc-{cache_key}"
    
    async def create_document_cache(
        self,
        file_path: str,
        mime_type: str,
        display_name: Optional[str] = None,
        ttl_hours: Optional[int] = None,
        system_instruction: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a context cache for a training document
        
        Args:
            file_path: Path to the document file
            mime_type: MIME type of the document
            display_name: Optional display name for the cache
            ttl_hours: TTL in hours (default from settings)
            system_instruction: Optional system instruction for the cache
            
        Returns:
            Dictionary with cache information
            
        Raises:
            ContextCacheError: If cache creation fails
        """
        try:
            logger.info(f"Creating context cache for document: {file_path}")
            
            # Validate file exists and size
            if not Path(file_path).exists():
                raise ContextCacheError(f"File not found: {file_path}")
            
            file_size = Path(file_path).stat().st_size
            if file_size > 50 * 1024 * 1024:  # 50MB limit
                raise ContextCacheError(f"File too large for caching: {file_size} bytes (max 50MB)")
            
            # Generate cache key and display name
            cache_key = self._generate_cache_key(file_path, mime_type)
            if not display_name:
                display_name = f"Training Document Cache - {Path(file_path).name}"
            
            # Read file content
            file_content = await self._read_file_content(file_path)
            
            # Create content for caching
            contents = [
                Content(
                    role="user",
                    parts=[
                        Part.from_bytes(
                            data=file_content,
                            mime_type=mime_type
                        )
                    ]
                )
            ]
            
            # Default system instruction for training documents
            default_system_instruction = """
            You are an expert educational content analyzer specialized in creating personalized training plans.
            You analyze training documents to extract structure, learning objectives, and content organization
            that will be used to generate personalized learning experiences for learners with different profiles.
            Always maintain focus on pedagogical value and learning outcomes.
            """
            
            final_system_instruction = system_instruction or default_system_instruction
            
            # Set TTL
            ttl_hours = ttl_hours or self.default_ttl_hours
            ttl_seconds = ttl_hours * 3600
            
            # Create cache configuration
            config = CreateCachedContentConfig(
                contents=contents,
                system_instruction=Content(
                    parts=[Part.from_text(final_system_instruction)]
                ),
                display_name=display_name,
                ttl=f"{ttl_seconds}s"
            )
            
            # Create the cache
            def create_cache():
                return self.client.caches.create(
                    model=self.model_name,
                    config=config
                )
            
            loop = asyncio.get_event_loop()
            cached_content = await loop.run_in_executor(None, create_cache)
            
            # Process cache response
            cache_info = {
                'success': True,
                'cache_id': cached_content.name,
                'cache_key': cache_key,
                'display_name': display_name,
                'model': self.model_name,
                'created_at': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(hours=ttl_hours)).isoformat(),
                'ttl_hours': ttl_hours,
                'file_info': {
                    'path': file_path,
                    'name': Path(file_path).name,
                    'mime_type': mime_type,
                    'size_bytes': file_size
                },
                'usage_metadata': {
                    'cached_content_token_count': getattr(cached_content.usage_metadata, 'total_token_count', 0)
                }
            }
            
            logger.info(f"Context cache created successfully: {cached_content.name}")
            logger.info(f"Cache tokens: {cache_info['usage_metadata']['cached_content_token_count']}")
            
            return cache_info
            
        except Exception as e:
            logger.error(f"Failed to create context cache: {e}")
            raise ContextCacheError(f"Context cache creation failed: {e}")
    
    async def get_cache_info(self, cache_id: str) -> Dict[str, Any]:
        """
        Get information about a context cache
        
        Args:
            cache_id: The cache ID to retrieve
            
        Returns:
            Cache information dictionary
        """
        try:
            def get_cache():
                return self.client.caches.get(cache_id)
            
            loop = asyncio.get_event_loop()
            cached_content = await loop.run_in_executor(None, get_cache)
            
            return {
                'cache_id': cached_content.name,
                'display_name': cached_content.display_name,
                'model': cached_content.model,
                'created_at': cached_content.create_time.isoformat() if cached_content.create_time else None,
                'updated_at': cached_content.update_time.isoformat() if cached_content.update_time else None,
                'expires_at': cached_content.expire_time.isoformat() if cached_content.expire_time else None,
                'usage_metadata': {
                    'cached_content_token_count': getattr(cached_content.usage_metadata, 'total_token_count', 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache info: {e}")
            raise ContextCacheError(f"Failed to get cache info: {e}")
    
    async def list_caches(self) -> List[Dict[str, Any]]:
        """
        List all context caches for the project
        
        Returns:
            List of cache information dictionaries
        """
        try:
            def list_all_caches():
                return self.client.caches.list()
            
            loop = asyncio.get_event_loop()
            caches = await loop.run_in_executor(None, list_all_caches)
            
            cache_list = []
            for cache in caches:
                cache_info = {
                    'cache_id': cache.name,
                    'display_name': cache.display_name,
                    'model': cache.model,
                    'created_at': cache.create_time.isoformat() if cache.create_time else None,
                    'expires_at': cache.expire_time.isoformat() if cache.expire_time else None,
                    'usage_metadata': {
                        'cached_content_token_count': getattr(cache.usage_metadata, 'total_token_count', 0)
                    }
                }
                cache_list.append(cache_info)
            
            logger.info(f"Retrieved {len(cache_list)} context caches")
            return cache_list
            
        except Exception as e:
            logger.error(f"Failed to list caches: {e}")
            raise ContextCacheError(f"Failed to list caches: {e}")
    
    async def update_cache_expiration(
        self,
        cache_id: str,
        ttl_hours: int
    ) -> Dict[str, Any]:
        """
        Update the expiration time of a context cache
        
        Args:
            cache_id: The cache ID to update
            ttl_hours: New TTL in hours
            
        Returns:
            Updated cache information
        """
        try:
            ttl_seconds = ttl_hours * 3600
            
            def update_cache():
                return self.client.caches.update(
                    cache_id,
                    ttl=f"{ttl_seconds}s"
                )
            
            loop = asyncio.get_event_loop()
            updated_cache = await loop.run_in_executor(None, update_cache)
            
            logger.info(f"Cache TTL updated to {ttl_hours} hours: {cache_id}")
            
            return {
                'cache_id': updated_cache.name,
                'updated_at': datetime.utcnow().isoformat(),
                'new_expires_at': updated_cache.expire_time.isoformat() if updated_cache.expire_time else None,
                'ttl_hours': ttl_hours
            }
            
        except Exception as e:
            logger.error(f"Failed to update cache expiration: {e}")
            raise ContextCacheError(f"Failed to update cache expiration: {e}")
    
    async def delete_cache(self, cache_id: str) -> bool:
        """
        Delete a context cache
        
        Args:
            cache_id: The cache ID to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            def delete_cache_item():
                self.client.caches.delete(cache_id)
                return True
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, delete_cache_item)
            
            logger.info(f"Context cache deleted: {cache_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to delete cache: {e}")
            raise ContextCacheError(f"Failed to delete cache: {e}")
    
    async def use_cached_content(
        self,
        cache_id: str,
        prompt: str,
        **generation_config
    ) -> Dict[str, Any]:
        """
        Generate content using a cached context
        
        Args:
            cache_id: The cache ID to use
            prompt: The prompt to send with the cached content
            **generation_config: Additional generation configuration
            
        Returns:
            Generated content response
        """
        try:
            default_config = {
                'max_output_tokens': 8192,
                'temperature': 0.1,
                'top_p': 0.95
            }
            default_config.update(generation_config)
            
            def generate_with_cache():
                return self.client.models.generate_content(
                    model=self.model_name,
                    contents=[prompt],
                    cached_content=cache_id,
                    config=genai.GenerateContentConfig(**default_config)
                )
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, generate_with_cache)
            
            return {
                'success': True,
                'content': response.text,
                'cache_id': cache_id,
                'usage_metadata': {
                    'prompt_token_count': getattr(response.usage_metadata, 'prompt_token_count', 0),
                    'candidates_token_count': getattr(response.usage_metadata, 'candidates_token_count', 0),
                    'cached_content_token_count': getattr(response.usage_metadata, 'cached_content_token_count', 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to use cached content: {e}")
            raise ContextCacheError(f"Failed to use cached content: {e}")
    
    async def _read_file_content(self, file_path: str) -> bytes:
        """
        Read file content asynchronously
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content as bytes
        """
        try:
            def read_file():
                with open(file_path, 'rb') as file:
                    return file.read()
            
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(None, read_file)
            
            if not content:
                raise ContextCacheError("File is empty")
                
            logger.debug(f"Read {len(content)} bytes from {file_path}")
            return content
            
        except FileNotFoundError:
            raise ContextCacheError(f"File not found: {file_path}")
        except PermissionError:
            raise ContextCacheError(f"Permission denied reading file: {file_path}")
        except Exception as e:
            raise ContextCacheError(f"Failed to read file {file_path}: {e}")
    
    async def find_cache_by_document(
        self,
        file_path: str,
        mime_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find existing cache for a document
        
        Args:
            file_path: Path to the document
            mime_type: MIME type of the document
            
        Returns:
            Cache information if found, None otherwise
        """
        try:
            cache_key = self._generate_cache_key(file_path, mime_type)
            caches = await self.list_caches()
            
            # Look for cache with matching display name pattern
            for cache in caches:
                if cache_key in cache.get('display_name', ''):
                    logger.info(f"Found existing cache for document: {cache['cache_id']}")
                    return cache
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding cache for document: {e}")
            return None