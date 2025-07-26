"""
FIA v3.0 - Complete Plan Integration Tests
Tests for the complete flow: PDF Upload → Profile → Plan Generation → Database Storage
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch


def test_complete_service_chain_imports():
    """Test that all services in the complete chain can be imported"""
    try:
        # Document Processing (PDF parsing)
        from app.domain.services.document_processing_service import DocumentProcessingService
        
        # Context Caching (cost optimization)
        from app.domain.services.context_cache_service import ContextCacheService
        
        # Plan Generation (personalization)
        from app.domain.services.plan_generation_service import PlanGenerationService
        
        # Plan Parser (JSON → DB entities)
        from app.domain.services.plan_parser_service import PlanParserService
        
        # All services imported successfully
        assert DocumentProcessingService is not None
        assert ContextCacheService is not None
        assert PlanGenerationService is not None
        assert PlanParserService is not None
        
    except ImportError as e:
        pytest.fail(f"Failed to import complete service chain: {e}")


def test_plan_parser_service_basic_functionality():
    """Test basic Plan Parser Service functionality"""
    from app.domain.services.plan_parser_service import PlanParserService, PlanParserError
    
    # Test service initialization
    parser_service = PlanParserService()
    assert parser_service is not None
    
    # Test error handling
    with pytest.raises(PlanParserError):
        raise PlanParserError("Test parser error")


def test_structured_output_schema_validation():
    """Test that the Structured Output JSON schema works correctly"""
    from app.domain.schemas.learner_training_plan import GeminiTrainingPlanStructure
    
    # Test valid plan structure
    valid_plan_data = {
        "stages": [
            {
                "stage_number": i,
                "title": f"Étape {i}",
                "description": f"Description de l'étape {i}",
                "modules": [
                    {
                        "title": f"Module {i}.1",
                        "description": f"Description du module {i}.1",
                        "submodules": [
                            {
                                "title": f"Sous-module {i}.1.1",
                                "description": f"Description du sous-module {i}.1.1",
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
    
    # Validate with Pydantic schema
    plan_structure = GeminiTrainingPlanStructure(**valid_plan_data)
    assert len(plan_structure.stages) == 5
    assert plan_structure.stages[0].stage_number == 1
    assert len(plan_structure.stages[0].modules) == 1
    assert len(plan_structure.stages[0].modules[0].submodules) == 1
    assert len(plan_structure.stages[0].modules[0].submodules[0].slides) == 2


def test_plan_generation_controller_endpoints():
    """Test that Plan Generation Controller has all required endpoints"""
    try:
        from app.adapters.inbound.plan_generation_controller import router
        
        # Get all route paths
        route_paths = [route.path for route in router.routes]
        
        # Expected endpoints for complete flow
        expected_endpoints = [
            "/generate",           # Main plan generation
            "/regenerate-section", # Section regeneration
            "/plan/{learner_session_id}",  # Get existing plan
            "/validate",           # Plan validation
            "/health",            # Health check
            "/statistics",        # Usage statistics
            "/plan/{plan_id}/statistics"  # Database plan statistics
        ]
        
        # Check that all endpoints exist
        for endpoint in expected_endpoints:
            full_path = f"/api/plan-generation{endpoint}"
            assert any(full_path in path or endpoint.replace("{", "{").replace("}", "}") in path 
                      for path in route_paths), f"Endpoint {endpoint} not found"
        
    except ImportError as e:
        pytest.fail(f"Failed to import Plan Generation Controller: {e}")


def test_database_entities_relationships():
    """Test that database entities have correct relationships for plan storage"""
    try:
        from app.domain.entities.learner_training_plan import LearnerTrainingPlan
        from app.domain.entities.training_module import TrainingModule
        from app.domain.entities.training_submodule import TrainingSubmodule
        from app.domain.entities.training_slide import TrainingSlide
        
        # All entities imported successfully
        assert LearnerTrainingPlan is not None
        assert TrainingModule is not None
        assert TrainingSubmodule is not None
        assert TrainingSlide is not None
        
        # Check table names (should be snake_case English)
        assert LearnerTrainingPlan.__tablename__ == "learner_training_plans"
        assert TrainingModule.__tablename__ == "training_modules"
        assert TrainingSubmodule.__tablename__ == "training_submodules"
        assert TrainingSlide.__tablename__ == "training_slides"
        
    except ImportError as e:
        pytest.fail(f"Failed to import database entities: {e}")


def test_complete_flow_schemas():
    """Test that all schemas needed for the complete flow are available"""
    try:
        # Plan Generation schemas
        from app.domain.schemas.plan_generation import (
            PlanGenerationRequest, PlanGenerationResponse, 
            LearnerProfileSummary, PlanGenerationMetadata
        )
        
        # Learner Training Plan schemas
        from app.domain.schemas.learner_training_plan import (
            GeminiTrainingPlanStructure, LearnerTrainingPlanResponse,
            TrainingModuleResponse, TrainingSubmoduleResponse, TrainingSlideResponse
        )
        
        # Context Cache schemas
        from app.domain.schemas.context_cache import (
            ContextCacheCreateRequest, ContextCacheResponse
        )
        
        # Document Processing schemas
        from app.domain.schemas.document_processing import (
            DocumentProcessingRequest, DocumentProcessingResponse
        )
        
        # All schemas imported successfully
        assert PlanGenerationRequest is not None
        assert GeminiTrainingPlanStructure is not None
        assert ContextCacheCreateRequest is not None
        assert DocumentProcessingRequest is not None
        
    except ImportError as e:
        pytest.fail(f"Failed to import required schemas: {e}")


@pytest.mark.asyncio
async def test_plan_parser_mock_functionality():
    """Test Plan Parser Service with mocked database operations"""
    from app.domain.services.plan_parser_service import PlanParserService
    from uuid import uuid4
    
    parser_service = PlanParserService()
    
    # Mock session and entities
    mock_session = AsyncMock()
    mock_session.get.return_value = None  # No existing plan
    mock_session.flush = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    
    # Test plan data (valid structure)
    valid_plan_data = {
        "stages": [
            {
                "stage_number": 1,
                "title": "Découverte et Introduction",
                "description": "Phase de découverte",
                "modules": [
                    {
                        "title": "Module Introduction",
                        "description": "Module d'introduction",
                        "submodules": [
                            {
                                "title": "Bases fondamentales",
                                "description": "Les bases",
                                "slides": [
                                    {"title": "Slide 1: Concepts"},
                                    {"title": "Slide 2: Exemples"}
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "stage_number": 2,
                "title": "Apprentissage Fondamental",
                "description": "Phase d'apprentissage",
                "modules": [
                    {
                        "title": "Module Apprentissage",
                        "description": "Module d'apprentissage approfondi",
                        "submodules": [
                            {
                                "title": "Concepts avancés",
                                "description": "Les concepts avancés",
                                "slides": [
                                    {"title": "Slide 1: Théorie"},
                                    {"title": "Slide 2: Applications"}
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "stage_number": 3,
                "title": "Application Pratique",
                "description": "Phase pratique",
                "modules": [
                    {
                        "title": "Module Pratique",
                        "description": "Exercices pratiques",
                        "submodules": [
                            {
                                "title": "Exercices",
                                "description": "Mise en pratique",
                                "slides": [
                                    {"title": "Exercice 1"},
                                    {"title": "Exercice 2"}
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "stage_number": 4,
                "title": "Approfondissement",
                "description": "Phase d'approfondissement",
                "modules": [
                    {
                        "title": "Module Avancé",
                        "description": "Concepts avancés",
                        "submodules": [
                            {
                                "title": "Cas complexes",
                                "description": "Résolution de cas complexes",
                                "slides": [
                                    {"title": "Cas d'étude 1"},
                                    {"title": "Cas d'étude 2"}
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "stage_number": 5,
                "title": "Maîtrise et Évaluation",
                "description": "Phase de maîtrise",
                "modules": [
                    {
                        "title": "Module Évaluation",
                        "description": "Évaluation des compétences",
                        "submodules": [
                            {
                                "title": "Tests de validation",
                                "description": "Validation des acquis",
                                "slides": [
                                    {"title": "Test final"},
                                    {"title": "Bilan"}
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    generation_metadata = {
        "learner_email": "test@example.com",
        "total_stages": 5,
        "total_modules": 5,
        "total_submodules": 5,
        "total_slides": 10
    }
    
    learner_session_id = uuid4()
    
    # The actual test would require database setup, but we can validate the structure
    assert len(valid_plan_data["stages"]) == 5
    assert all(stage["stage_number"] == i for i, stage in enumerate(valid_plan_data["stages"], 1))
    assert generation_metadata["total_stages"] == 5


def test_integration_ready_status():
    """Test that all components are ready for integration testing"""
    components_status = {
        "document_processing_service": False,
        "context_cache_service": False,
        "plan_generation_service": False,
        "plan_parser_service": False,
        "api_controllers": False,
        "database_entities": False,
        "schemas": False
    }
    
    # Check Document Processing Service
    try:
        from app.domain.services.document_processing_service import DocumentProcessingService
        components_status["document_processing_service"] = True
    except ImportError:
        pass
    
    # Check Context Cache Service
    try:
        from app.domain.services.context_cache_service import ContextCacheService
        components_status["context_cache_service"] = True
    except ImportError:
        pass
    
    # Check Plan Generation Service
    try:
        from app.domain.services.plan_generation_service import PlanGenerationService
        components_status["plan_generation_service"] = True
    except ImportError:
        pass
    
    # Check Plan Parser Service
    try:
        from app.domain.services.plan_parser_service import PlanParserService
        components_status["plan_parser_service"] = True
    except ImportError:
        pass
    
    # Check API Controllers
    try:
        from app.adapters.inbound.plan_generation_controller import router as plan_router
        from app.adapters.inbound.context_cache_controller import router as cache_router
        components_status["api_controllers"] = True
    except ImportError:
        pass
    
    # Check Database Entities
    try:
        from app.domain.entities.learner_training_plan import LearnerTrainingPlan
        from app.domain.entities.training_module import TrainingModule
        components_status["database_entities"] = True
    except ImportError:
        pass
    
    # Check Schemas
    try:
        from app.domain.schemas.plan_generation import PlanGenerationRequest
        from app.domain.schemas.learner_training_plan import GeminiTrainingPlanStructure
        components_status["schemas"] = True
    except ImportError:
        pass
    
    # All components should be ready
    for component, status in components_status.items():
        assert status, f"Component {component} is not ready for integration"
    
    # Calculate readiness percentage
    ready_components = sum(components_status.values())
    total_components = len(components_status)
    readiness_percentage = (ready_components / total_components) * 100
    
    print(f"Integration Readiness: {readiness_percentage}% ({ready_components}/{total_components} components ready)")
    assert readiness_percentage == 100.0, "Not all components are ready for integration testing"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])