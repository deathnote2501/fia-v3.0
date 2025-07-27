"""
FIA v3.0 - Plan Generation Service Tests
Comprehensive tests for personalized training plan generation
"""

import pytest
import tempfile
import os
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from app.services.plan_generation_service import PlanGenerationService, PlanGenerationError
from app.domain.entities.learner_session import LearnerSession
from app.domain.entities.training import Training


class TestPlanGenerationService:
    """Test suite for Plan Generation Service"""
    
    @pytest.fixture
    def plan_service(self):
        """Create a mock plan generation service for testing"""
        with patch('app.services.plan_generation_service.settings') as mock_settings:
            mock_settings.google_cloud_project = "test-project"
            mock_settings.google_cloud_region = "us-central1"
            mock_settings.gemini_model_name = "gemini-1.5-flash-002"
            
            with patch('app.services.plan_generation_service.vertexai'):
                with patch('app.domain.services.context_cache_service.genai'):
                    service = PlanGenerationService()
                    service.client = Mock()
                    service.cache_service = Mock()
                    return service
    
    @pytest.fixture
    def mock_learner_session(self):
        """Create a mock learner session"""
        session = Mock(spec=LearnerSession)
        session.id = "test-session-id"
        session.email = "learner@test.com"
        session.experience_level = "intermediate"
        session.learning_style = "visual"
        session.job_position = "Développeur Web"
        session.activity_sector = "Technologies"
        session.country = "France"
        session.language = "fr"
        session.personalized_plan = None
        return session
    
    @pytest.fixture
    def mock_training(self):
        """Create a mock training"""
        training = Mock(spec=Training)
        training.id = "test-training-id"
        training.name = "Formation JavaScript Avancé"
        training.file_path = "/test/path/training.pdf"
        training.mime_type = "application/pdf"
        training.trainer_id = "test-trainer-id"
        return training
    
    @pytest.fixture
    def mock_pdf_file(self):
        """Create a temporary PDF file for testing"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(b'%PDF-1.4\nTest training content\n%%EOF')
            temp_file.flush()
            yield temp_file.name
        os.unlink(temp_file.name)
    
    def test_build_learner_profile(self, plan_service, mock_learner_session):
        """Test learner profile building"""
        profile = plan_service._build_learner_profile(mock_learner_session)
        
        assert profile["email"] == "learner@test.com"
        assert profile["experience_level"] == "intermediate"
        assert profile["learning_style"] == "visual"
        assert profile["job_position"] == "Développeur Web"
        assert profile["activity_sector"] == "Technologies"
        assert profile["country"] == "France"
    
    def test_get_stage_names(self, plan_service):
        """Test stage names retrieval"""
        stage_names = plan_service.get_stage_names()
        
        assert len(stage_names) == 5
        assert "Mise en contexte" in stage_names
        assert "Acquisition des fondamentaux" in stage_names
        assert "Construction progressive" in stage_names
        assert "Maîtrise" in stage_names
        assert "Validation" in stage_names
    
    @pytest.mark.asyncio
    async def test_generate_personalized_plan_with_cache(self, plan_service, mock_learner_session, mock_training):
        """Test personalized plan generation with cache"""
        # Mock cache service
        mock_cache_info = {'cache_id': 'existing-cache-id'}
        plan_service.cache_service.find_cache_by_document = AsyncMock(return_value=mock_cache_info)
        
        # Mock cache response
        mock_plan_data = {
            "stages": [
                {
                    "stage_number": 1,
                    "title": "Découverte et Introduction",
                    "description": "Introduction aux concepts fondamentaux",
                    "modules": [
                        {
                            "title": "Bases JavaScript",
                            "description": "Les fondamentaux du langage",
                            "submodules": [
                                {
                                    "title": "Syntaxe de base",
                                    "description": "Syntaxe et concepts de base",
                                    "slides": [
                                        {"title": "Variables et types"},
                                        {"title": "Fonctions de base"},
                                        {"title": "Structures de contrôle"}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ] * 5  # 5 stages
        }
        
        plan_service.cache_service.use_cached_content = AsyncMock(return_value={
            'success': True,
            'content': json.dumps(mock_plan_data),
            'usage_metadata': {
                'prompt_token_count': 100,
                'candidates_token_count': 500,
                'cached_content_token_count': 2000
            }
        })
        
        # Update training with valid file path
        mock_training.file_path = "/test/path/training.pdf"
        
        result = await plan_service.generate_personalized_plan(
            learner_session=mock_learner_session,
            training=mock_training,
            use_cache=True
        )
        
        assert result['success'] is True
        assert 'plan_data' in result
        assert 'generation_metadata' in result
        assert result['generation_metadata']['learner_email'] == "learner@test.com"
        assert result['generation_metadata']['total_stages'] == 5
    
    @pytest.mark.asyncio
    async def test_generate_personalized_plan_new_cache(self, plan_service, mock_learner_session, mock_training, mock_pdf_file):
        """Test personalized plan generation with new cache creation"""
        # Update training with valid file path
        mock_training.file_path = mock_pdf_file
        
        # Mock no existing cache
        plan_service.cache_service.find_cache_by_document = AsyncMock(return_value=None)
        
        # Mock cache creation
        plan_service.cache_service.create_document_cache = AsyncMock(return_value={
            'success': True,
            'cache_id': 'new-cache-id'
        })
        
        # Mock plan generation response
        mock_plan_data = {
            "stages": [
                {
                    "stage_number": i,
                    "title": f"Étape {i}",
                    "description": f"Description étape {i}",
                    "modules": [
                        {
                            "title": f"Module {i}.1",
                            "description": f"Description module {i}.1",
                            "submodules": [
                                {
                                    "title": f"Sous-module {i}.1.1",
                                    "description": f"Description sous-module {i}.1.1",
                                    "slides": [
                                        {"title": f"Slide {i}.1.1.1"},
                                        {"title": f"Slide {i}.1.1.2"}
                                    ]
                                }
                            ]
                        }
                    ]
                }
                for i in range(1, 6)
            ]
        }
        
        plan_service.cache_service.use_cached_content = AsyncMock(return_value={
            'success': True,
            'content': json.dumps(mock_plan_data),
            'usage_metadata': {
                'prompt_token_count': 150,
                'candidates_token_count': 800,
                'cached_content_token_count': 1800
            }
        })
        
        result = await plan_service.generate_personalized_plan(
            learner_session=mock_learner_session,
            training=mock_training,
            use_cache=True
        )
        
        assert result['success'] is True
        assert result['generation_metadata']['total_stages'] == 5
        
        # Verify cache creation was called
        plan_service.cache_service.create_document_cache.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_personalized_plan_cache_error(self, plan_service, mock_learner_session, mock_training, mock_pdf_file):
        """Test that cache service failure raises proper error message"""
        # Update training with valid file path
        mock_training.file_path = mock_pdf_file
        
        # Mock cache service failure
        plan_service.cache_service.find_cache_by_document = AsyncMock(side_effect=Exception("Cache error"))
        
        # Expect PlanGenerationError with learner-friendly message
        with pytest.raises(PlanGenerationError) as exc_info:
            await plan_service.generate_personalized_plan(
                learner_session=mock_learner_session,
                training=mock_training,
                use_cache=True
            )
        
        # Verify error message is learner-friendly
        assert "temporairement indisponible" in str(exc_info.value)
        assert "réessayer plus tard" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_regenerate_plan_section(self, plan_service, mock_learner_session, mock_training):
        """Test plan section regeneration"""
        # Mock cache service for regeneration
        mock_cache_info = {'cache_id': 'test-cache-id'}
        plan_service.cache_service.find_cache_by_document = AsyncMock(return_value=mock_cache_info)
        
        plan_service.cache_service.use_cached_content = AsyncMock(return_value={
            'success': True,
            'content': json.dumps({
                "title": "Regenerated Module",
                "description": "This module has been regenerated",
                "submodules": [
                    {
                        "title": "New Submodule",
                        "description": "Regenerated submodule",
                        "slides": [
                            {"title": "New Slide 1"},
                            {"title": "New Slide 2"}
                        ]
                    }
                ]
            })
        })
        
        result = await plan_service.regenerate_plan_section(
            learner_session=mock_learner_session,
            training=mock_training,
            section_type="module",
            section_identifier="module-1.1",
            custom_instructions="Make it more practical"
        )
        
        assert result['success'] is True
        assert result['section_type'] == "module"
        assert result['section_identifier'] == "module-1.1"
        assert 'regenerated_content' in result
        assert 'regenerated_at' in result
    
    def test_process_plan_response_valid(self, plan_service, mock_learner_session, mock_training):
        """Test processing of valid plan response"""
        valid_plan_content = json.dumps({
            "stages": [
                {
                    "stage_number": i,
                    "title": f"Stage {i}",
                    "description": f"Stage {i} description",
                    "modules": [
                        {
                            "title": f"Module {i}.1",
                            "description": f"Module {i}.1 description",
                            "submodules": [
                                {
                                    "title": f"Submodule {i}.1.1",
                                    "description": f"Submodule {i}.1.1 description",
                                    "slides": [
                                        {"title": f"Slide {i}.1.1.1"},
                                        {"title": f"Slide {i}.1.1.2"}
                                    ]
                                }
                            ]
                        }
                    ]
                }
                for i in range(1, 6)
            ]
        })
        
        result = plan_service._process_plan_response(
            valid_plan_content,
            mock_learner_session,
            mock_training
        )
        
        assert result['success'] is True
        assert 'plan_data' in result
        assert 'generation_metadata' in result
        assert result['generation_metadata']['total_stages'] == 5
        assert result['generation_metadata']['total_modules'] == 5
        assert result['generation_metadata']['total_submodules'] == 5
        assert result['generation_metadata']['total_slides'] == 10
    
    def test_process_plan_response_invalid_json(self, plan_service, mock_learner_session, mock_training):
        """Test processing of invalid JSON response"""
        invalid_json_content = "Invalid JSON content"
        
        with pytest.raises(PlanGenerationError) as exc_info:
            plan_service._process_plan_response(
                invalid_json_content,
                mock_learner_session,
                mock_training
            )
        
        assert "Invalid JSON response" in str(exc_info.value)
    
    def test_process_plan_response_missing_stages(self, plan_service, mock_learner_session, mock_training):
        """Test processing of response missing stages"""
        invalid_plan_content = json.dumps({
            "not_stages": []
        })
        
        with pytest.raises(PlanGenerationError) as exc_info:
            plan_service._process_plan_response(
                invalid_plan_content,
                mock_learner_session,
                mock_training
            )
        
        assert "missing stages" in str(exc_info.value)
    
    def test_process_plan_response_wrong_stage_count(self, plan_service, mock_learner_session, mock_training):
        """Test processing of response with wrong number of stages"""
        invalid_plan_content = json.dumps({
            "stages": [
                {"stage_number": 1, "title": "Only Stage"}
            ]  # Only 1 stage instead of 5
        })
        
        with pytest.raises(PlanGenerationError) as exc_info:
            plan_service._process_plan_response(
                invalid_plan_content,
                mock_learner_session,
                mock_training
            )
        
        assert "Invalid number of stages: 1 (expected 5)" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_read_file_content_success(self, plan_service, mock_pdf_file):
        """Test successful file content reading"""
        content = await plan_service._read_file_content(mock_pdf_file)
        
        assert content is not None
        assert isinstance(content, bytes)
        assert b'Test training content' in content
    
    @pytest.mark.asyncio
    async def test_read_file_content_not_found(self, plan_service):
        """Test file content reading with non-existent file"""
        with pytest.raises(PlanGenerationError) as exc_info:
            await plan_service._read_file_content("/nonexistent/file.pdf")
        
        assert "File not found" in str(exc_info.value)
    
    def test_error_handling(self, plan_service):
        """Test custom error classes"""
        with pytest.raises(PlanGenerationError):
            raise PlanGenerationError("Test error message")


class TestPlanGenerationIntegration:
    """Integration tests for Plan Generation Service"""
    
    def test_service_initialization(self):
        """Test that Plan Generation Service can be initialized"""
        with patch('app.services.plan_generation_service.settings') as mock_settings:
            mock_settings.google_cloud_project = "test-project"
            mock_settings.google_cloud_region = "us-central1"
            mock_settings.gemini_model_name = "gemini-1.5-flash-002"
            
            with patch('app.services.plan_generation_service.vertexai'):
                with patch('app.domain.services.context_cache_service.genai'):
                    service = PlanGenerationService()
                    
                    assert service is not None
                    assert hasattr(service, 'client')
                    assert hasattr(service, 'model_name')
                    assert hasattr(service, 'cache_service')
    
    def test_schema_imports(self):
        """Test that Plan Generation schemas can be imported"""
        try:
            from app.domain.schemas.plan_generation import (
                PlanGenerationRequest, PlanGenerationResponse,
                SectionRegenerationRequest, PlanValidationRequest
            )
            
            assert PlanGenerationRequest is not None
            assert PlanGenerationResponse is not None
            assert SectionRegenerationRequest is not None
            assert PlanValidationRequest is not None
            
        except ImportError as e:
            pytest.fail(f"Failed to import Plan Generation schemas: {e}")
    
    def test_controller_imports(self):
        """Test that Plan Generation Controller can be imported"""
        try:
            from app.adapters.inbound.plan_generation_controller import router
            
            assert router is not None
            assert hasattr(router, 'routes')
            
            # Check that multiple endpoints exist
            routes = router.routes
            assert len(routes) > 0
            
        except ImportError as e:
            pytest.fail(f"Failed to import Plan Generation Controller: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])