"""
FIA v3.0 - Context Cache Service Tests
Comprehensive tests for Context Caching functionality
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from app.domain.services.context_cache_service import ContextCacheService, ContextCacheError
from app.domain.services.document_processing_service import DocumentProcessingService


class TestContextCacheService:
    """Test suite for Context Cache Service"""
    
    @pytest.fixture
    def cache_service(self):
        """Create a mock cache service for testing"""
        with patch('app.domain.services.context_cache_service.settings') as mock_settings:
            mock_settings.google_cloud_project = "test-project"
            mock_settings.google_cloud_region = "us-central1"
            mock_settings.gemini_model_name = "gemini-1.5-flash-002"
            mock_settings.gemini_context_cache_ttl_hours = 12
            
            with patch('app.domain.services.context_cache_service.genai.Client') as mock_client:
                service = ContextCacheService()
                service.client = Mock()
                return service
    
    @pytest.fixture
    def mock_pdf_file(self):
        """Create a temporary PDF file for testing"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            # Create a small PDF-like content
            temp_file.write(b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<<\n/Size 1\n/Root 1 0 R\n>>\nstartxref\n50\n%%EOF')
            temp_file.flush()
            yield temp_file.name
        os.unlink(temp_file.name)
    
    def test_generate_cache_key(self, cache_service, mock_pdf_file):
        """Test cache key generation"""
        cache_key = cache_service._generate_cache_key(mock_pdf_file, "application/pdf")
        
        assert cache_key.startswith("training-doc-")
        assert len(cache_key) == 29  # "training-doc-" + 16 character hash
        
        # Test consistency - same file should generate same key
        cache_key2 = cache_service._generate_cache_key(mock_pdf_file, "application/pdf")
        assert cache_key == cache_key2
    
    @pytest.mark.asyncio
    async def test_create_document_cache_success(self, cache_service, mock_pdf_file):
        """Test successful document cache creation"""
        # Mock the Gemini client response
        mock_cached_content = Mock()
        mock_cached_content.name = "projects/test-project/locations/us-central1/cachedContents/test-cache-id"
        mock_cached_content.usage_metadata.total_token_count = 1500
        
        cache_service.client.caches.create.return_value = mock_cached_content
        
        result = await cache_service.create_document_cache(
            file_path=mock_pdf_file,
            mime_type="application/pdf",
            display_name="Test Document Cache",
            ttl_hours=6
        )
        
        assert result['success'] is True
        assert result['cache_id'] == mock_cached_content.name
        assert result['display_name'] == "Test Document Cache"
        assert result['ttl_hours'] == 6
        assert result['file_info']['mime_type'] == "application/pdf"
        assert result['usage_metadata']['cached_content_token_count'] == 1500
    
    @pytest.mark.asyncio
    async def test_create_document_cache_file_not_found(self, cache_service):
        """Test cache creation with non-existent file"""
        with pytest.raises(ContextCacheError) as exc_info:
            await cache_service.create_document_cache(
                file_path="/path/to/nonexistent/file.pdf",
                mime_type="application/pdf"
            )
        
        assert "File not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_document_cache_file_too_large(self, cache_service):
        """Test cache creation with oversized file"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Create a file larger than 50MB
            temp_file.write(b'x' * (51 * 1024 * 1024))
            temp_file.flush()
            
            try:
                with pytest.raises(ContextCacheError) as exc_info:
                    await cache_service.create_document_cache(
                        file_path=temp_file.name,
                        mime_type="application/pdf"
                    )
                
                assert "File too large for caching" in str(exc_info.value)
            finally:
                os.unlink(temp_file.name)
    
    @pytest.mark.asyncio
    async def test_get_cache_info_success(self, cache_service):
        """Test successful cache info retrieval"""
        mock_cached_content = Mock()
        mock_cached_content.name = "test-cache-id"
        mock_cached_content.display_name = "Test Cache"
        mock_cached_content.model = "gemini-1.5-flash-002"
        mock_cached_content.create_time = datetime.utcnow()
        mock_cached_content.update_time = datetime.utcnow()
        mock_cached_content.expire_time = datetime.utcnow() + timedelta(hours=12)
        mock_cached_content.usage_metadata.total_token_count = 1200
        
        cache_service.client.caches.get.return_value = mock_cached_content
        
        result = await cache_service.get_cache_info("test-cache-id")
        
        assert result['cache_id'] == "test-cache-id"
        assert result['display_name'] == "Test Cache"
        assert result['model'] == "gemini-1.5-flash-002"
        assert result['usage_metadata']['cached_content_token_count'] == 1200
    
    @pytest.mark.asyncio
    async def test_list_caches_success(self, cache_service):
        """Test successful cache listing"""
        mock_cache1 = Mock()
        mock_cache1.name = "cache-1"
        mock_cache1.display_name = "Cache 1"
        mock_cache1.model = "gemini-1.5-flash-002"
        mock_cache1.create_time = datetime.utcnow()
        mock_cache1.expire_time = datetime.utcnow() + timedelta(hours=12)
        mock_cache1.usage_metadata.total_token_count = 1000
        
        mock_cache2 = Mock()
        mock_cache2.name = "cache-2"
        mock_cache2.display_name = "Cache 2"
        mock_cache2.model = "gemini-1.5-flash-002"
        mock_cache2.create_time = datetime.utcnow()
        mock_cache2.expire_time = datetime.utcnow() + timedelta(hours=24)
        mock_cache2.usage_metadata.total_token_count = 1500
        
        cache_service.client.caches.list.return_value = [mock_cache1, mock_cache2]
        
        result = await cache_service.list_caches()
        
        assert len(result) == 2
        assert result[0]['cache_id'] == "cache-1"
        assert result[1]['cache_id'] == "cache-2"
        assert result[0]['usage_metadata']['cached_content_token_count'] == 1000
        assert result[1]['usage_metadata']['cached_content_token_count'] == 1500
    
    @pytest.mark.asyncio
    async def test_update_cache_expiration_success(self, cache_service):
        """Test successful cache expiration update"""
        mock_updated_cache = Mock()
        mock_updated_cache.name = "test-cache-id"
        mock_updated_cache.expire_time = datetime.utcnow() + timedelta(hours=24)
        
        cache_service.client.caches.update.return_value = mock_updated_cache
        
        result = await cache_service.update_cache_expiration("test-cache-id", 24)
        
        assert result['cache_id'] == "test-cache-id"
        assert result['ttl_hours'] == 24
        assert 'updated_at' in result
        assert 'new_expires_at' in result
    
    @pytest.mark.asyncio
    async def test_delete_cache_success(self, cache_service):
        """Test successful cache deletion"""
        cache_service.client.caches.delete.return_value = None
        
        result = await cache_service.delete_cache("test-cache-id")
        
        assert result is True
        cache_service.client.caches.delete.assert_called_once_with("test-cache-id")
    
    @pytest.mark.asyncio
    async def test_use_cached_content_success(self, cache_service):
        """Test successful content generation with cache"""
        mock_response = Mock()
        mock_response.text = "Generated content based on cached document"
        mock_response.usage_metadata.prompt_token_count = 50
        mock_response.usage_metadata.candidates_token_count = 100
        mock_response.usage_metadata.cached_content_token_count = 1500
        
        cache_service.client.models.generate_content.return_value = mock_response
        
        result = await cache_service.use_cached_content(
            cache_id="test-cache-id",
            prompt="Analyze this document",
            temperature=0.2,
            max_output_tokens=4096
        )
        
        assert result['success'] is True
        assert result['content'] == "Generated content based on cached document"
        assert result['cache_id'] == "test-cache-id"
        assert result['usage_metadata']['prompt_token_count'] == 50
        assert result['usage_metadata']['candidates_token_count'] == 100
        assert result['usage_metadata']['cached_content_token_count'] == 1500
    
    @pytest.mark.asyncio
    async def test_find_cache_by_document_found(self, cache_service, mock_pdf_file):
        """Test finding existing cache for document"""
        # Mock list_caches to return a cache with matching pattern
        cache_key = cache_service._generate_cache_key(mock_pdf_file, "application/pdf")
        mock_cache = {
            'cache_id': 'found-cache-id',
            'display_name': f'Training Document Cache - {cache_key}',
            'model': 'gemini-1.5-flash-002'
        }
        
        cache_service.list_caches = AsyncMock(return_value=[mock_cache])
        
        result = await cache_service.find_cache_by_document(mock_pdf_file, "application/pdf")
        
        assert result is not None
        assert result['cache_id'] == 'found-cache-id'
    
    @pytest.mark.asyncio
    async def test_find_cache_by_document_not_found(self, cache_service, mock_pdf_file):
        """Test finding cache when none exists"""
        cache_service.list_caches = AsyncMock(return_value=[])
        
        result = await cache_service.find_cache_by_document(mock_pdf_file, "application/pdf")
        
        assert result is None


class TestDocumentProcessingServiceWithCache:
    """Test suite for Document Processing Service with caching integration"""
    
    @pytest.fixture
    def doc_service(self):
        """Create a mock document processing service"""
        with patch('app.domain.services.document_processing_service.settings') as mock_settings:
            mock_settings.google_cloud_project = "test-project"
            mock_settings.google_cloud_region = "us-central1"
            mock_settings.gemini_model_name = "gemini-1.5-flash-002"
            
            with patch('app.domain.services.document_processing_service.genai.Client'):
                service = DocumentProcessingService()
                service.client = Mock()
                service.cache_service = Mock()
                return service
    
    @pytest.fixture
    def mock_pdf_file(self):
        """Create a temporary PDF file for testing"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(b'%PDF-1.4\nTest PDF content for caching\n%%EOF')
            temp_file.flush()
            yield temp_file.name
        os.unlink(temp_file.name)
    
    @pytest.mark.asyncio
    async def test_parse_document_with_cache_existing_cache(self, doc_service, mock_pdf_file):
        """Test parsing document with existing cache"""
        # Mock cache service to return existing cache
        mock_cache_info = {
            'cache_id': 'existing-cache-id',
            'display_name': 'Existing Cache'
        }
        doc_service.cache_service.find_cache_by_document = AsyncMock(return_value=mock_cache_info)
        
        # Mock cache usage response
        mock_cache_response = {
            'success': True,
            'content': 'Document analysis from cache',
            'usage_metadata': {
                'prompt_token_count': 50,
                'candidates_token_count': 200,
                'cached_content_token_count': 1500
            }
        }
        doc_service.cache_service.use_cached_content = AsyncMock(return_value=mock_cache_response)
        
        result = await doc_service.parse_document_with_cache(
            file_path=mock_pdf_file,
            mime_type="application/pdf"
        )
        
        assert result['success'] is True
        assert result['content'] == 'Document analysis from cache'
        assert result['processing_metadata']['cache_used'] is True
        assert result['cache_info']['was_cached'] is True
        assert result['cache_info']['cache_id'] == 'existing-cache-id'
    
    @pytest.mark.asyncio
    async def test_parse_document_with_cache_new_cache(self, doc_service, mock_pdf_file):
        """Test parsing document with new cache creation"""
        # Mock cache service to return no existing cache
        doc_service.cache_service.find_cache_by_document = AsyncMock(return_value=None)
        
        # Mock cache creation
        mock_cache_creation = {
            'success': True,
            'cache_id': 'new-cache-id'
        }
        doc_service.cache_service.create_document_cache = AsyncMock(return_value=mock_cache_creation)
        
        # Mock cache usage response
        mock_cache_response = {
            'success': True,
            'content': 'Document analysis from new cache',
            'usage_metadata': {
                'prompt_token_count': 50,
                'candidates_token_count': 200,
                'cached_content_token_count': 1500
            }
        }
        doc_service.cache_service.use_cached_content = AsyncMock(return_value=mock_cache_response)
        
        result = await doc_service.parse_document_with_cache(
            file_path=mock_pdf_file,
            mime_type="application/pdf"
        )
        
        assert result['success'] is True
        assert result['content'] == 'Document analysis from new cache'
        assert result['processing_metadata']['cache_used'] is True
        assert result['cache_info']['was_cached'] is False
        assert result['cache_info']['cache_id'] == 'new-cache-id'
    
    @pytest.mark.asyncio
    async def test_parse_document_with_cache_force_refresh(self, doc_service, mock_pdf_file):
        """Test parsing document with forced cache refresh"""
        # Mock cache creation for force refresh
        mock_cache_creation = {
            'success': True,
            'cache_id': 'refreshed-cache-id'
        }
        doc_service.cache_service.create_document_cache = AsyncMock(return_value=mock_cache_creation)
        
        # Mock cache usage response
        mock_cache_response = {
            'success': True,
            'content': 'Document analysis from refreshed cache',
            'usage_metadata': {
                'prompt_token_count': 50,
                'candidates_token_count': 200,
                'cached_content_token_count': 1500
            }
        }
        doc_service.cache_service.use_cached_content = AsyncMock(return_value=mock_cache_response)
        
        result = await doc_service.parse_document_with_cache(
            file_path=mock_pdf_file,
            mime_type="application/pdf",
            force_refresh=True
        )
        
        assert result['success'] is True
        assert result['content'] == 'Document analysis from refreshed cache'
        assert result['processing_metadata']['cache_used'] is True
        # find_cache_by_document should not be called with force_refresh=True
        doc_service.cache_service.find_cache_by_document.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_parse_document_with_cache_fallback_on_cache_failure(self, doc_service, mock_pdf_file):
        """Test fallback to direct processing when cache fails"""
        # Mock cache service to raise error
        doc_service.cache_service.find_cache_by_document = AsyncMock(side_effect=Exception("Cache error"))
        
        # Mock direct processing fallback
        doc_service.parse_document_content = AsyncMock(return_value={
            'success': True,
            'content': 'Direct processing result',
            'file_info': {'path': mock_pdf_file}
        })
        
        result = await doc_service.parse_document_with_cache(
            file_path=mock_pdf_file,
            mime_type="application/pdf"
        )
        
        assert result['success'] is True
        assert result['content'] == 'Direct processing result'
        # Verify fallback was called
        doc_service.parse_document_content.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_cache_for_document(self, doc_service, mock_pdf_file):
        """Test getting cache information for a document"""
        mock_cache_info = {
            'cache_id': 'test-cache-id',
            'display_name': 'Test Cache'
        }
        doc_service.cache_service.find_cache_by_document = AsyncMock(return_value=mock_cache_info)
        
        result = await doc_service.get_cache_for_document(mock_pdf_file, "application/pdf")
        
        assert result == mock_cache_info
        doc_service.cache_service.find_cache_by_document.assert_called_once_with(mock_pdf_file, "application/pdf")
    
    @pytest.mark.asyncio
    async def test_create_cache_for_document(self, doc_service, mock_pdf_file):
        """Test creating cache for a document"""
        mock_cache_result = {
            'success': True,
            'cache_id': 'new-cache-id'
        }
        doc_service.cache_service.create_document_cache = AsyncMock(return_value=mock_cache_result)
        
        result = await doc_service.create_cache_for_document(
            file_path=mock_pdf_file,
            mime_type="application/pdf",
            display_name="Test Cache",
            ttl_hours=12
        )
        
        assert result == mock_cache_result
        doc_service.cache_service.create_document_cache.assert_called_once_with(
            file_path=mock_pdf_file,
            mime_type="application/pdf",
            display_name="Test Cache",
            ttl_hours=12
        )
    
    @pytest.mark.asyncio
    async def test_delete_cache_for_document(self, doc_service, mock_pdf_file):
        """Test deleting cache for a document"""
        # Mock finding existing cache
        mock_cache_info = {'cache_id': 'cache-to-delete'}
        doc_service.cache_service.find_cache_by_document = AsyncMock(return_value=mock_cache_info)
        doc_service.cache_service.delete_cache = AsyncMock(return_value=True)
        
        result = await doc_service.delete_cache_for_document(mock_pdf_file, "application/pdf")
        
        assert result is True
        doc_service.cache_service.delete_cache.assert_called_once_with('cache-to-delete')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])