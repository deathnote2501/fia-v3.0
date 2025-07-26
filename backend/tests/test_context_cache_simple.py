"""
FIA v3.0 - Simple Context Cache Tests
Basic validation tests for Context Caching implementation
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch


def test_context_cache_service_imports():
    """Test that Context Cache Service can be imported"""
    try:
        from app.domain.services.context_cache_service import ContextCacheService, ContextCacheError
        assert ContextCacheService is not None
        assert ContextCacheError is not None
    except ImportError as e:
        pytest.fail(f"Failed to import Context Cache Service: {e}")


def test_context_cache_schemas_imports():
    """Test that Context Cache schemas can be imported"""
    try:
        from app.domain.schemas.context_cache import (
            ContextCacheCreateRequest, ContextCacheResponse, 
            CacheFileInfo, CacheUsageMetadata
        )
        assert ContextCacheCreateRequest is not None
        assert ContextCacheResponse is not None
        assert CacheFileInfo is not None
        assert CacheUsageMetadata is not None
    except ImportError as e:
        pytest.fail(f"Failed to import Context Cache schemas: {e}")


def test_context_cache_controller_imports():
    """Test that Context Cache Controller can be imported"""
    try:
        from app.adapters.inbound.context_cache_controller import router
        assert router is not None
        assert hasattr(router, 'routes')
    except ImportError as e:
        pytest.fail(f"Failed to import Context Cache Controller: {e}")


def test_cache_key_generation_logic():
    """Test cache key generation without full service initialization"""
    from app.domain.services.context_cache_service import ContextCacheService
    
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
        temp_file.write(b'Test content')
        temp_file.flush()
        
        try:
            # Mock settings and client to avoid initialization issues
            with patch('app.domain.services.context_cache_service.settings') as mock_settings:
                mock_settings.google_cloud_project = "test-project"
                mock_settings.google_cloud_region = "us-central1"
                mock_settings.gemini_model_name = "gemini-1.5-flash-002"
                mock_settings.gemini_context_cache_ttl_hours = 12
                
                with patch('app.domain.services.context_cache_service.genai.Client'):
                    service = ContextCacheService()
                    
                    # Test cache key generation
                    cache_key = service._generate_cache_key(temp_file.name, "application/pdf")
                    
                    # Verify format
                    assert cache_key.startswith("training-doc-")
                    assert len(cache_key) == 29
                    
                    # Test consistency
                    cache_key2 = service._generate_cache_key(temp_file.name, "application/pdf")
                    assert cache_key == cache_key2
                    
        finally:
            os.unlink(temp_file.name)


def test_schema_validation():
    """Test basic schema validation"""
    from app.domain.schemas.context_cache import (
        ContextCacheCreateRequest, CacheFileInfo, CacheUsageMetadata
    )
    
    # Test request validation
    request = ContextCacheCreateRequest(
        file_path="/test/path.pdf",
        mime_type="application/pdf",
        ttl_hours=12
    )
    assert request.file_path == "/test/path.pdf"
    assert request.ttl_hours == 12
    
    # Test file info validation
    file_info = CacheFileInfo(
        path="/test/path.pdf",
        name="path.pdf",
        mime_type="application/pdf",
        size_bytes=1024
    )
    assert file_info.size_bytes == 1024
    
    # Test usage metadata validation
    usage = CacheUsageMetadata(
        cached_content_token_count=1500
    )
    assert usage.cached_content_token_count == 1500


def test_error_handling():
    """Test custom error classes"""
    from app.domain.services.context_cache_service import ContextCacheError
    
    # Test error can be raised and caught
    with pytest.raises(ContextCacheError):
        raise ContextCacheError("Test error message")


def test_document_processing_integration_points():
    """Test that Document Processing Service has cache integration"""
    with patch('app.domain.services.document_processing_service.settings') as mock_settings:
        mock_settings.google_cloud_project = "test-project"
        mock_settings.google_cloud_region = "us-central1" 
        mock_settings.gemini_model_name = "gemini-1.5-flash-002"
        
        with patch('app.domain.services.document_processing_service.genai.Client'):
            with patch('app.domain.services.context_cache_service.genai.Client'):
                from app.domain.services.document_processing_service import DocumentProcessingService
                
                service = DocumentProcessingService()
                
                # Verify cache-related methods exist
                assert hasattr(service, 'parse_document_with_cache')
                assert hasattr(service, 'get_cache_for_document')
                assert hasattr(service, 'create_cache_for_document')
                assert hasattr(service, 'delete_cache_for_document')
                assert hasattr(service, 'cache_service')


def test_api_endpoints_structure():
    """Test Context Cache API endpoints structure"""
    from app.adapters.inbound.context_cache_controller import router
    
    # Get route information
    routes = router.routes
    assert len(routes) > 0
    
    # Check that we have multiple endpoints
    route_methods = []
    for route in routes:
        if hasattr(route, 'methods'):
            route_methods.extend(route.methods)
    
    # Should have GET, POST, PATCH, DELETE methods
    assert 'GET' in route_methods
    assert 'POST' in route_methods
    assert 'PATCH' in route_methods
    assert 'DELETE' in route_methods


if __name__ == "__main__":
    pytest.main([__file__, "-v"])