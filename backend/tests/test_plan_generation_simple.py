"""
FIA v3.0 - Simple Plan Generation Tests
Basic validation tests for Plan Generation implementation
"""

import pytest
import json
from unittest.mock import Mock, patch


def test_plan_generation_service_imports():
    """Test that Plan Generation Service can be imported"""
    try:
        from app.domain.services.plan_generation_service import PlanGenerationService, PlanGenerationError
        assert PlanGenerationService is not None
        assert PlanGenerationError is not None
    except ImportError as e:
        pytest.fail(f"Failed to import Plan Generation Service: {e}")


def test_plan_generation_schemas_imports():
    """Test that Plan Generation schemas can be imported"""
    try:
        from app.domain.schemas.plan_generation import (
            PlanGenerationRequest, PlanGenerationResponse,
            LearnerProfileSummary, PlanGenerationMetadata
        )
        assert PlanGenerationRequest is not None
        assert PlanGenerationResponse is not None
        assert LearnerProfileSummary is not None
        assert PlanGenerationMetadata is not None
    except ImportError as e:
        pytest.fail(f"Failed to import Plan Generation schemas: {e}")


def test_service_initialization():
    """Test that Plan Generation Service can be initialized with mocks"""
    with patch('app.domain.services.plan_generation_service.settings') as mock_settings:
        mock_settings.google_cloud_project = "test-project"
        mock_settings.google_cloud_region = "us-central1"
        mock_settings.gemini_model_name = "gemini-1.5-flash-002"
        
        with patch('app.domain.services.plan_generation_service.genai.Client'):
            with patch('app.domain.services.context_cache_service.genai.Client'):
                from app.domain.services.plan_generation_service import PlanGenerationService
                
                service = PlanGenerationService()
                assert service is not None
                assert hasattr(service, 'client')
                assert hasattr(service, 'model_name')
                assert hasattr(service, 'cache_service')


def test_learner_profile_context_building():
    """Test learner profile context building logic"""
    with patch('app.domain.services.plan_generation_service.settings') as mock_settings:
        mock_settings.google_cloud_project = "test-project"
        mock_settings.google_cloud_region = "us-central1"
        mock_settings.gemini_model_name = "gemini-1.5-flash-002"
        
        with patch('app.domain.services.plan_generation_service.genai.Client'):
            with patch('app.domain.services.context_cache_service.genai.Client'):
                from app.domain.services.plan_generation_service import PlanGenerationService
                
                service = PlanGenerationService()
                
                # Create mock learner session
                mock_learner = Mock()
                mock_learner.email = "test@example.com"
                mock_learner.experience_level = "intermediate"
                mock_learner.learning_style = "visual"
                mock_learner.job_position = "Developer"
                mock_learner.activity_sector = "Technology"
                mock_learner.country = "France"
                mock_learner.language = "fr"
                
                context = service._build_learner_profile_context(mock_learner)
                
                # Verify context contains expected information
                assert "test@example.com" in context
                assert "Intermédiaire" in context
                assert "Visuel" in context
                assert "Developer" in context
                assert "Technology" in context
                assert "France" in context
                assert "PROFIL DE L'APPRENANT" in context


def test_optimized_prompt_building():
    """Test optimized prompt building"""
    with patch('app.domain.services.plan_generation_service.settings') as mock_settings:
        mock_settings.google_cloud_project = "test-project"
        mock_settings.google_cloud_region = "us-central1"
        mock_settings.gemini_model_name = "gemini-1.5-flash-002"
        
        with patch('app.domain.services.plan_generation_service.genai.Client'):
            with patch('app.domain.services.context_cache_service.genai.Client'):
                from app.domain.services.plan_generation_service import PlanGenerationService
                
                service = PlanGenerationService()
                
                profile_context = "TEST PROFILE CONTEXT"
                prompt = service._build_optimized_prompt(profile_context)
                
                # Verify prompt contains essential elements
                assert "TEST PROFILE CONTEXT" in prompt
                assert "5 ÉTAPES FIXES" in prompt
                assert "Découverte et Introduction" in prompt
                assert "Apprentissage Fondamental" in prompt
                assert "Application Pratique" in prompt
                assert "Approfondissement" in prompt
                assert "Maîtrise et Évaluation" in prompt
                assert "PERSONNALISATION SELON LE PROFIL" in prompt


def test_plan_response_processing():
    """Test plan response processing and validation"""
    with patch('app.domain.services.plan_generation_service.settings') as mock_settings:
        mock_settings.google_cloud_project = "test-project"
        mock_settings.google_cloud_region = "us-central1"
        mock_settings.gemini_model_name = "gemini-1.5-flash-002"
        
        with patch('app.domain.services.plan_generation_service.genai.Client'):
            with patch('app.domain.services.context_cache_service.genai.Client'):
                from app.domain.services.plan_generation_service import PlanGenerationService
                
                service = PlanGenerationService()
                
                # Create mock objects
                mock_learner = Mock()
                mock_learner.email = "test@example.com"
                mock_learner.experience_level = "intermediate"
                mock_learner.learning_style = "visual"
                mock_learner.job_position = "Developer"
                mock_learner.activity_sector = "Technology"
                
                mock_training = Mock()
                mock_training.name = "Test Training"
                mock_training.id = "test-training-id"
                
                # Create valid plan data
                valid_plan_data = {
                    "stages": [
                        {
                            "stage_number": i,
                            "title": f"Stage {i}",
                            "description": f"Stage {i} description",
                            "modules": [
                                {
                                    "title": f"Module {i}.1",
                                    "description": f"Module description",
                                    "submodules": [
                                        {
                                            "title": f"Submodule {i}.1.1",
                                            "description": f"Submodule description",
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
                
                plan_content = json.dumps(valid_plan_data)
                
                result = service._process_plan_response(
                    plan_content,
                    mock_learner,
                    mock_training
                )
                
                # Verify processing results
                assert result['success'] is True
                assert 'plan_data' in result
                assert 'generation_metadata' in result
                assert result['generation_metadata']['total_stages'] == 5
                assert result['generation_metadata']['total_modules'] == 5
                assert result['generation_metadata']['learner_email'] == "test@example.com"


def test_schema_validation():
    """Test Plan Generation schema validation"""
    from app.domain.schemas.plan_generation import (
        PlanGenerationRequest, LearnerProfileSummary, PlanGenerationMetadata
    )
    from uuid import uuid4
    from datetime import datetime
    
    # Test PlanGenerationRequest
    request = PlanGenerationRequest(
        learner_session_id=uuid4(),
        training_id=uuid4(),
        use_cache=True,
        force_regenerate=False
    )
    assert request.use_cache is True
    assert request.force_regenerate is False
    
    # Test LearnerProfileSummary
    profile = LearnerProfileSummary(
        email="test@example.com",
        experience_level="intermediate",
        learning_style="visual",
        job_position="Developer",
        activity_sector="Technology",
        country="France",
        language="fr"
    )
    assert profile.email == "test@example.com"
    assert profile.experience_level == "intermediate"
    
    # Test PlanGenerationMetadata
    metadata = PlanGenerationMetadata(
        learner_email="test@example.com",
        learner_level="intermediate",
        learner_style="visual",
        learner_job="Developer",
        learner_sector="Technology",
        training_name="Test Training",
        training_id="test-id",
        generated_at=datetime.utcnow().isoformat(),
        total_stages=5,
        total_modules=10,
        total_submodules=20,
        total_slides=40,
        generation_method="cached",
        cache_used=True
    )
    assert metadata.total_stages == 5
    assert metadata.cache_used is True


def test_error_handling():
    """Test custom error classes"""
    from app.domain.services.plan_generation_service import PlanGenerationError
    
    # Test error can be raised and caught
    with pytest.raises(PlanGenerationError):
        raise PlanGenerationError("Test error message")


def test_integration_with_context_cache():
    """Test integration with Context Cache Service"""
    with patch('app.domain.services.plan_generation_service.settings') as mock_settings:
        mock_settings.google_cloud_project = "test-project"
        mock_settings.google_cloud_region = "us-central1"
        mock_settings.gemini_model_name = "gemini-1.5-flash-002"
        
        with patch('app.domain.services.plan_generation_service.genai.Client'):
            with patch('app.domain.services.context_cache_service.genai.Client'):
                from app.domain.services.plan_generation_service import PlanGenerationService
                
                service = PlanGenerationService()
                
                # Verify cache service integration
                assert hasattr(service, 'cache_service')
                assert service.cache_service is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])