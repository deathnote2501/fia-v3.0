"""
FIA v3.0 - Context Cache Integration Tests
Simple integration tests for Context Caching functionality
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch


def test_cache_key_generation():
    """Test cache key generation logic"""
    from app.domain.services.context_cache_service import ContextCacheService
    
    with patch('app.domain.services.context_cache_service.settings') as mock_settings:
        mock_settings.google_cloud_project = "test-project"
        mock_settings.google_cloud_region = "us-central1"
        mock_settings.gemini_model_name = "gemini-1.5-flash-002"
        mock_settings.gemini_context_cache_ttl_hours = 12
        
        with patch('app.domain.services.context_cache_service.genai.Client'):
            service = ContextCacheService()
            
            # Create a test file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(b'Test PDF content')
                temp_file.flush()
                
                try:
                    cache_key = service._generate_cache_key(temp_file.name, "application/pdf")
                    
                    # Verify cache key format
                    assert cache_key.startswith("training-doc-")
                    assert len(cache_key) == 29  # "training-doc-" + 16 char hash
                    
                    # Test consistency
                    cache_key2 = service._generate_cache_key(temp_file.name, "application/pdf")
                    assert cache_key == cache_key2
                    
                finally:
                    os.unlink(temp_file.name)


def test_context_cache_schemas():
    """Test Context Cache Pydantic schemas"""
    from app.domain.schemas.context_cache import (
        ContextCacheCreateRequest, ContextCacheResponse, CacheFileInfo, CacheUsageMetadata
    )
    
    # Test request schema
    request = ContextCacheCreateRequest(
        file_path="/path/to/document.pdf",
        mime_type="application/pdf",
        display_name="Test Cache",
        ttl_hours=12
    )
    assert request.file_path == "/path/to/document.pdf"
    assert request.ttl_hours == 12
    
    # Test file info schema
    file_info = CacheFileInfo(
        path="/path/to/document.pdf",
        name="document.pdf",
        mime_type="application/pdf",
        size_bytes=1024
    )
    assert file_info.size_bytes == 1024
    
    # Test usage metadata schema
    usage = CacheUsageMetadata(
        cached_content_token_count=1500,
        prompt_token_count=50,
        candidates_token_count=200
    )
    assert usage.cached_content_token_count == 1500
    
    # Test response schema
    response = ContextCacheResponse(
        success=True,
        cache_id="test-cache-id",
        cache_key="test-key",
        display_name="Test Cache",
        model="gemini-1.5-flash-002",
        created_at="2024-01-01T00:00:00",
        expires_at="2024-01-01T12:00:00",
        ttl_hours=12,
        file_info=file_info,
        usage_metadata=usage
    )
    assert response.success is True
    assert response.cache_id == "test-cache-id"


def test_document_processing_cache_integration():
    """Test Document Processing Service cache integration points"""
    from app.domain.services.document_processing_service import DocumentProcessingService
    
    with patch('app.domain.services.document_processing_service.settings') as mock_settings:
        mock_settings.google_cloud_project = "test-project"
        mock_settings.google_cloud_region = "us-central1"
        mock_settings.gemini_model_name = "gemini-1.5-flash-002"
        
        with patch('app.domain.services.document_processing_service.genai.Client'):
            with patch('app.domain.services.context_cache_service.genai.Client'):
                service = DocumentProcessingService()
                
                # Verify cache service is initialized
                assert hasattr(service, 'cache_service')
                assert service.cache_service is not None
                
                # Verify cache-related methods exist
                assert hasattr(service, 'parse_document_with_cache')
                assert hasattr(service, 'get_cache_for_document')
                assert hasattr(service, 'create_cache_for_document')
                assert hasattr(service, 'delete_cache_for_document')


def test_context_cache_controller_endpoints():
    """Test that Context Cache Controller has all required endpoints"""
    from app.adapters.inbound.context_cache_controller import router
    
    # Get all route paths from the router
    route_paths = [route.path for route in router.routes]
    
    # Verify all expected endpoints exist
    expected_endpoints = [
        "/create",
        "/list", 
        "/{cache_id}",
        "/update-expiration",
        "/generate",
        "/find",
        "/health",
        "/statistics",
        "/training/{training_id}"
    ]
    
    for endpoint in expected_endpoints:
        # Convert path parameters to match FastAPI format
        expected_path = f"/api/context-cache{endpoint}"
        if "{cache_id}" in endpoint:
            assert any(expected_path.replace("{cache_id}", "{path}") in path or 
                      "/api/context-cache/{cache_id}" in route_paths for path in route_paths)
        elif "{training_id}" in endpoint:
            assert any("/api/context-cache/training/{training_id}" in route_paths)
        else:
            full_path = f"/api/context-cache{endpoint}"
            assert any(full_path in path for path in route_paths)


def test_schemas_import_correctly():
    """Test that all Context Cache schemas can be imported"""
    try:
        from app.domain.schemas.context_cache import (
            ContextCacheCreateRequest, ContextCacheResponse, ContextCacheInfo,
            ContextCacheListResponse, CacheExpirationUpdateRequest, 
            CacheExpirationUpdateResponse, CacheContentGenerationRequest,
            CacheContentGenerationResponse, CacheDeleteResponse, CacheHealthResponse,
            CacheError, CacheStatistics, TrainingDocumentCacheRequest,
            TrainingDocumentCacheResponse, CacheFindRequest, CacheFindResponse,
            CacheFileInfo, CacheUsageMetadata
        )
        
        # If we get here, all imports worked
        assert True
        
    except ImportError as e:
        pytest.fail(f"Failed to import Context Cache schemas: {e}")


def test_services_can_be_instantiated():
    """Test that Context Cache services can be instantiated with mocks"""
    from app.domain.services.context_cache_service import ContextCacheService
    
    with patch('app.domain.services.context_cache_service.settings') as mock_settings:
        mock_settings.google_cloud_project = "test-project"
        mock_settings.google_cloud_region = "us-central1"
        mock_settings.gemini_model_name = "gemini-1.5-flash-002"
        mock_settings.gemini_context_cache_ttl_hours = 12
        
        with patch('app.domain.services.context_cache_service.genai.Client') as mock_client:
            mock_client.return_value = Mock()
            
            try:
                service = ContextCacheService()
                assert service is not None
                assert hasattr(service, 'client')
                assert hasattr(service, 'model_name')
                assert hasattr(service, 'default_ttl_hours')
                
            except Exception as e:
                pytest.fail(f"Failed to instantiate ContextCacheService: {e}")


def test_error_classes_defined():
    """Test that custom error classes are properly defined"""
    from app.domain.services.context_cache_service import ContextCacheError
    
    # Test error can be raised and caught
    try:
        raise ContextCacheError("Test error")
    except ContextCacheError as e:
        assert str(e) == "Test error"
    except Exception:
        pytest.fail("ContextCacheError should be catchable as ContextCacheError")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])