"""
FIA v3.0 - Document Processing Service
Service for parsing PDF/PowerPoint files using Gemini Document Understanding API
"""

import asyncio
import logging
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
import io

import google.generativeai as genai

from app.infrastructure.settings import settings
from app.domain.services.context_cache_service import ContextCacheService, ContextCacheError


# Configure logging
logger = logging.getLogger(__name__)


class DocumentProcessingError(Exception):
    """Custom exception for document processing errors"""
    pass


class DocumentProcessingService:
    """Service for processing PDF/PowerPoint documents using Gemini API"""
    
    def __init__(self):
        """Initialize the document processing service"""
        self.model_name = settings.gemini_model_name
        self.client = self._initialize_gemini_client()
        self.cache_service = ContextCacheService()
        
    def _initialize_gemini_client(self) -> genai.Client:
        """Initialize Gemini client with Vertex AI configuration"""
        try:
            # Check if we have the required settings
            if not settings.google_cloud_project:
                raise DocumentProcessingError("Google Cloud Project not configured")
            
            # Configure for Vertex AI
            client = genai.Client(
                vertexai=True,
                project=settings.google_cloud_project,
                location=settings.google_cloud_region,
                http_options=HttpOptions(api_version="v1")
            )
            
            logger.info(f"Gemini client initialized for project: {settings.google_cloud_project}")
            logger.info(f"Using model: {self.model_name} in region: {settings.google_cloud_region}")
            return client
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise DocumentProcessingError(f"Failed to initialize Gemini client: {e}")
    
    async def parse_document_content(
        self, 
        file_path: str, 
        mime_type: str,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Parse document content using Gemini Document Understanding
        
        Args:
            file_path: Path to the document file
            mime_type: MIME type of the document
            custom_prompt: Optional custom prompt for parsing
            
        Returns:
            Dictionary containing parsed document information
            
        Raises:
            DocumentProcessingError: If parsing fails
        """
        try:
            # Default prompt for training material analysis
            default_prompt = """
            Analyze this training document and extract the following information:
            
            1. Document structure and organization
            2. Main topics and concepts covered
            3. Learning objectives (if mentioned)
            4. Key chapters, sections, or modules
            5. Important diagrams, charts, or visual elements
            6. Total estimated content complexity (beginner/intermediate/advanced)
            7. Approximate reading time or duration
            8. Any prerequisites mentioned
            9. Summary of the overall content
            
            Please provide a comprehensive analysis that will help create personalized learning paths.
            """
            
            prompt = custom_prompt or default_prompt
            
            # Read file content
            file_content = await self._read_file_content(file_path)
            
            # Create content parts for Gemini
            content_parts = [
                types.Part.from_bytes(
                    data=file_content,
                    mime_type=mime_type
                ),
                prompt
            ]
            
            # Generate content using Gemini
            response = await self._call_gemini_api(content_parts)
            
            # Process and structure the response
            processed_result = self._process_gemini_response(response, file_path, mime_type)
            
            logger.info(f"Successfully parsed document: {file_path}")
            return processed_result
            
        except Exception as e:
            logger.error(f"Failed to parse document {file_path}: {e}")
            raise DocumentProcessingError(f"Document parsing failed: {e}")
    
    async def extract_document_summary(
        self, 
        file_path: str, 
        mime_type: str
    ) -> str:
        """
        Extract a concise summary of the document
        
        Args:
            file_path: Path to the document file
            mime_type: MIME type of the document
            
        Returns:
            Summary text
        """
        summary_prompt = """
        Provide a concise summary (2-3 paragraphs) of this training document.
        Focus on:
        - What the document teaches
        - Main learning outcomes
        - Target audience level
        - Key topics covered
        """
        
        result = await self.parse_document_content(file_path, mime_type, summary_prompt)
        return result.get('content', '')
    
    async def analyze_document_structure(
        self, 
        file_path: str, 
        mime_type: str
    ) -> Dict[str, Any]:
        """
        Analyze document structure for training plan generation
        
        Args:
            file_path: Path to the document file
            mime_type: MIME type of the document
            
        Returns:
            Structured analysis of the document
        """
        structure_prompt = """
        Analyze the structure of this training document and provide:
        
        1. Main chapters/sections with their titles
        2. Sub-sections under each main section
        3. Learning objectives for each section (if identifiable)
        4. Difficulty progression (does it go from basic to advanced?)
        5. Key concepts introduced in each section
        6. Practical exercises or examples mentioned
        7. Assessment opportunities identified
        
        Structure your response to help create a personalized learning plan.
        """
        
        return await self.parse_document_content(file_path, mime_type, structure_prompt)
    
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
            
            # Run file reading in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(None, read_file)
            
            if not content:
                raise DocumentProcessingError("File is empty")
                
            logger.debug(f"Read {len(content)} bytes from {file_path}")
            return content
            
        except FileNotFoundError:
            raise DocumentProcessingError(f"File not found: {file_path}")
        except PermissionError:
            raise DocumentProcessingError(f"Permission denied reading file: {file_path}")
        except Exception as e:
            raise DocumentProcessingError(f"Failed to read file {file_path}: {e}")
    
    async def _call_gemini_api(self, content_parts: list) -> Any:
        """
        Call Gemini API with content parts
        
        Args:
            content_parts: List of content parts for Gemini
            
        Returns:
            Gemini API response
        """
        try:
            def make_request():
                return self.client.models.generate_content(
                    model=self.model_name,
                    contents=content_parts,
                    config=GenerateContentConfig(
                        max_output_tokens=8192,
                        temperature=0.1,  # Low temperature for consistent analysis
                        top_p=0.95
                    )
                )
            
            # Run API call in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, make_request)
            
            if not response or not response.text:
                raise DocumentProcessingError("Empty response from Gemini API")
                
            logger.debug(f"Received response from Gemini API: {len(response.text)} characters")
            return response
            
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise DocumentProcessingError(f"Gemini API error: {e}")
    
    def _process_gemini_response(
        self, 
        response: Any, 
        file_path: str, 
        mime_type: str
    ) -> Dict[str, Any]:
        """
        Process and structure Gemini API response
        
        Args:
            response: Raw Gemini API response
            file_path: Original file path
            mime_type: Document MIME type
            
        Returns:
            Structured response dictionary
        """
        try:
            return {
                'success': True,
                'content': response.text,
                'file_info': {
                    'path': file_path,
                    'name': Path(file_path).name,
                    'mime_type': mime_type
                },
                'processing_metadata': {
                    'model_used': self.model_name,
                    'content_length': len(response.text),
                    'timestamp': asyncio.get_event_loop().time()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to process Gemini response: {e}")
            return {
                'success': False,
                'error': f"Response processing failed: {e}",
                'content': '',
                'file_info': {
                    'path': file_path,
                    'name': Path(file_path).name,
                    'mime_type': mime_type
                }
            }
    
    async def validate_document_for_training(
        self, 
        file_path: str, 
        mime_type: str
    ) -> Tuple[bool, str]:
        """
        Validate if document is suitable for training purposes
        
        Args:
            file_path: Path to the document file
            mime_type: MIME type of the document
            
        Returns:
            Tuple of (is_valid, validation_message)
        """
        validation_prompt = """
        Analyze this document and determine if it's suitable for creating training content.
        
        Consider:
        1. Does it contain educational/training material?
        2. Is the content structured and organized?
        3. Are there clear learning concepts?
        4. Is it appropriate for professional training?
        5. Does it have sufficient content depth?
        
        Respond with:
        - VALID: [reason] if suitable for training
        - INVALID: [reason] if not suitable for training
        """
        
        try:
            result = await self.parse_document_content(file_path, mime_type, validation_prompt)
            content = result.get('content', '').strip()
            
            if content.startswith('VALID:'):
                return True, content[6:].strip()
            elif content.startswith('INVALID:'):
                return False, content[8:].strip()
            else:
                # Fallback: if response format is unexpected, assume valid
                return True, "Document validation completed"
                
        except Exception as e:
            logger.error(f"Document validation failed: {e}")
            return False, f"Validation error: {e}"
    
    async def parse_document_with_cache(
        self,
        file_path: str,
        mime_type: str,
        custom_prompt: Optional[str] = None,
        force_refresh: bool = False,
        ttl_hours: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Parse document using context caching for optimization
        
        Args:
            file_path: Path to the document file
            mime_type: MIME type of the document
            custom_prompt: Optional custom prompt for parsing
            force_refresh: Force cache refresh even if exists
            ttl_hours: Custom TTL for cache
            
        Returns:
            Dictionary containing parsed document information
        """
        try:
            # Check for existing cache unless force refresh
            cache_info = None
            if not force_refresh:
                cache_info = await self.cache_service.find_cache_by_document(file_path, mime_type)
            
            # Create cache if not exists or force refresh
            if not cache_info or force_refresh:
                logger.info(f"Creating new cache for document: {file_path}")
                
                cache_result = await self.cache_service.create_document_cache(
                    file_path=file_path,
                    mime_type=mime_type,
                    ttl_hours=ttl_hours
                )
                
                if not cache_result['success']:
                    # Fallback to direct processing
                    logger.warning("Cache creation failed, using direct processing")
                    return await self.parse_document_content(file_path, mime_type, custom_prompt)
                
                cache_id = cache_result['cache_id']
                logger.info(f"Cache created: {cache_id}")
            else:
                cache_id = cache_info['cache_id']
                logger.info(f"Using existing cache: {cache_id}")
            
            # Use cached content for processing
            prompt = custom_prompt or """
            Analyze this training document and extract the following information:
            
            1. Document structure and organization
            2. Main topics and concepts covered
            3. Learning objectives (if mentioned)
            4. Key chapters, sections, or modules
            5. Important diagrams, charts, or visual elements
            6. Total estimated content complexity (beginner/intermediate/advanced)
            7. Approximate reading time or duration
            8. Any prerequisites mentioned
            9. Summary of the overall content
            
            Please provide a comprehensive analysis that will help create personalized learning paths.
            """
            
            cached_response = await self.cache_service.use_cached_content(
                cache_id=cache_id,
                prompt=prompt,
                temperature=0.1,
                top_p=0.95
            )
            
            if cached_response['success']:
                return {
                    'success': True,
                    'content': cached_response['content'],
                    'file_info': {
                        'path': file_path,
                        'name': Path(file_path).name,
                        'mime_type': mime_type
                    },
                    'processing_metadata': {
                        'model_used': self.model_name,
                        'content_length': len(cached_response['content']),
                        'timestamp': asyncio.get_event_loop().time(),
                        'cache_used': True,
                        'cache_id': cache_id
                    },
                    'cache_info': {
                        'cache_id': cache_id,
                        'was_cached': cache_info is not None,
                        'usage_metadata': cached_response['usage_metadata']
                    }
                }
            else:
                # Fallback to direct processing
                logger.warning("Cached content generation failed, using direct processing")
                return await self.parse_document_content(file_path, mime_type, custom_prompt)
                
        except ContextCacheError as e:
            logger.warning(f"Cache error, falling back to direct processing: {e}")
            return await self.parse_document_content(file_path, mime_type, custom_prompt)
        except Exception as e:
            logger.error(f"Failed to parse document with cache: {e}")
            raise DocumentProcessingError(f"Document parsing with cache failed: {e}")
    
    async def get_cache_for_document(
        self,
        file_path: str,
        mime_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cache information for a document
        
        Args:
            file_path: Path to the document file
            mime_type: MIME type of the document
            
        Returns:
            Cache information if found, None otherwise
        """
        try:
            return await self.cache_service.find_cache_by_document(file_path, mime_type)
        except Exception as e:
            logger.error(f"Error getting cache for document: {e}")
            return None
    
    async def create_cache_for_document(
        self,
        file_path: str,
        mime_type: str,
        display_name: Optional[str] = None,
        ttl_hours: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a context cache for a document
        
        Args:
            file_path: Path to the document file
            mime_type: MIME type of the document
            display_name: Optional display name for the cache
            ttl_hours: TTL in hours
            
        Returns:
            Cache creation result
        """
        try:
            return await self.cache_service.create_document_cache(
                file_path=file_path,
                mime_type=mime_type,
                display_name=display_name,
                ttl_hours=ttl_hours
            )
        except Exception as e:
            logger.error(f"Error creating cache for document: {e}")
            raise DocumentProcessingError(f"Cache creation failed: {e}")
    
    async def delete_cache_for_document(
        self,
        file_path: str,
        mime_type: str
    ) -> bool:
        """
        Delete cache for a document
        
        Args:
            file_path: Path to the document file
            mime_type: MIME type of the document
            
        Returns:
            True if deletion was successful
        """
        try:
            cache_info = await self.cache_service.find_cache_by_document(file_path, mime_type)
            if cache_info:
                return await self.cache_service.delete_cache(cache_info['cache_id'])
            return True  # No cache to delete
            
        except Exception as e:
            logger.error(f"Error deleting cache for document: {e}")
            return False