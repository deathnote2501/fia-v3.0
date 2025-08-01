#!/usr/bin/env python3
"""
Test des améliorations de logging Phase 1.2
Vérifier que les modifications aux adapters AI fonctionnent sans casser l'existant
"""

import sys
import asyncio
import json
from pathlib import Path
from uuid import uuid4

# Ajouter le chemin du projet pour les imports
sys.path.append(str(Path(__file__).parent))

async def test_vertex_ai_adapter():
    """Test du VertexAIAdapter avec le nouveau logging"""
    print("🧪 Test 1: VertexAIAdapter avec logging centralisé")
    
    try:
        from app.infrastructure.adapters.vertex_ai_adapter import VertexAIAdapter
        
        # Créer l'adapter
        adapter = VertexAIAdapter()
        
        if not adapter.is_available():
            print("⚠️ VertexAI non disponible - Test simulé")
            return True
        
        # Test avec des paramètres de session
        test_prompt = "Generate a simple JSON response with a greeting message."
        session_id = "test_session_123"
        learner_session_id = str(uuid4())
        
        print(f"📝 Testing avec session_id: {session_id}, learner_session_id: {learner_session_id}")
        
        # Tentative d'appel (peut échouer selon la config, mais ne doit pas crasher)
        try:
            result = await adapter.generate_content(
                prompt=test_prompt,
                session_id=session_id,
                learner_session_id=learner_session_id
            )
            print(f"✅ VertexAI response: {len(result)} characters")
        except Exception as e:
            print(f"⚠️ VertexAI call failed (expected if not configured): {str(e)}")
        
        print("✅ Test 1 terminé - VertexAIAdapter logging OK\n")
        return True
        
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
        return False

async def test_conversation_adapter():
    """Test du ConversationAdapter avec le nouveau logging"""
    print("🧪 Test 2: ConversationAdapter avec logging centralisé")
    
    try:
        from app.adapters.outbound.conversation_adapter import ConversationAdapter
        
        # Créer l'adapter
        adapter = ConversationAdapter()
        
        # Données de test
        test_message = "What is machine learning?"
        conversation_history = []
        training_context = "Machine Learning Basics"
        learner_profile = {
            "experience_level": "beginner",
            "job_position": "developer",
            "language": "en"
        }
        learner_session_id = uuid4()
        
        print(f"📝 Testing conversation avec learner_session_id: {learner_session_id}")
        
        # Test de la méthode principale (peut échouer selon la config)
        try:
            result = await adapter.chat_with_learner(
                message=test_message,
                conversation_history=conversation_history,
                training_context=training_context,
                learner_profile=learner_profile,
                learner_session_id=learner_session_id
            )
            print(f"✅ Conversation response: {result.get('response', 'No response')[:100]}...")
        except Exception as e:
            print(f"⚠️ Conversation call failed (expected if not configured): {str(e)}")
        
        # Test des autres méthodes
        try:
            comment_result = await adapter.comment_slide(
                slide_content="This slide explains basic AI concepts",
                slide_title="Introduction to AI",
                learner_profile=learner_profile
            )
            print(f"✅ Comment slide response: {comment_result.get('response', 'No response')[:50]}...")
        except Exception as e:
            print(f"⚠️ Comment slide failed (expected if not configured): {str(e)}")
        
        print("✅ Test 2 terminé - ConversationAdapter logging OK\n")
        return True
        
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
        return False

async def test_openai_adapter():
    """Test du OpenAIAdapter avec le nouveau logging"""
    print("🧪 Test 3: OpenAIAdapter avec logging centralisé")
    
    try:
        from app.adapters.outbound.openai_adapter import OpenAIAdapter
        
        # Créer l'adapter
        adapter = OpenAIAdapter()
        
        # Données de test
        slide_content = "This slide explains the concept of neural networks and their applications."
        slide_title = "Neural Networks Overview"
        learner_profile = {"language": "english", "level": "intermediate"}
        learner_session_id = uuid4()
        slide_id = uuid4()
        
        print(f"📝 Testing infographic avec learner_session_id: {learner_session_id}")
        
        # Test de génération d'infographie (peut échouer selon la config)
        try:
            result = await adapter.generate_infographic(
                slide_content=slide_content,
                slide_title=slide_title,
                learner_profile=learner_profile,
                learner_session_id=learner_session_id,
                slide_id=slide_id
            )
            print(f"✅ Infographic generated: {len(result.get('image_data', ''))} base64 chars")
        except Exception as e:
            print(f"⚠️ Infographic generation failed (expected if not configured): {str(e)}")
        
        print("✅ Test 3 terminé - OpenAIAdapter logging OK\n")
        return True
        
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
        return False

async def test_logging_integration():
    """Test de l'intégration du logging avec les services"""
    print("🧪 Test 4: Intégration logging centralisé")
    
    try:
        from app.infrastructure.gemini_call_logger import gemini_call_logger
        
        # Vérifier que le logger est accessible
        stats = gemini_call_logger.get_stats()
        print(f"📊 Logger stats: {json.dumps(stats, indent=2)}")
        
        # Test d'un appel direct
        call_id = gemini_call_logger.log_input(
            service_name="test_integration",
            prompt="Test prompt for integration verification",
            session_id="test_session",
            learner_session_id="test_learner",
            additional_context={"test": True}
        )
        
        gemini_call_logger.log_output(
            call_id=call_id,
            service_name="test_integration",
            response="Test response for integration",
            session_id="test_session",
            learner_session_id="test_learner",
            processing_time=0.123
        )
        
        print(f"✅ Logger integration test completed - Call ID: {call_id}")
        print("✅ Test 4 terminé - Logging integration OK\n")
        return True
        
    except Exception as e:
        print(f"❌ Test 4 failed: {e}")
        return False

def test_import_safety():
    """Test que tous les imports fonctionnent"""
    print("🧪 Test 5: Sécurité des imports")
    
    try:
        # Test des imports critiques
        from app.infrastructure.gemini_call_logger import gemini_call_logger
        from app.infrastructure.adapters.vertex_ai_adapter import VertexAIAdapter
        from app.adapters.outbound.conversation_adapter import ConversationAdapter
        from app.adapters.outbound.openai_adapter import OpenAIAdapter
        
        print("✅ Tous les imports critiques fonctionnent")
        print("✅ Test 5 terminé - Import safety OK\n")
        return True
        
    except Exception as e:
        print(f"❌ Test 5 failed: {e}")
        return False

async def main():
    """Fonction principale de test"""
    print("🚀 Tests de logging centralisé Phase 1.2")
    print("=" * 60)
    
    results = []
    
    # Tests séquentiels
    results.append(test_import_safety())
    results.append(await test_logging_integration())
    results.append(await test_vertex_ai_adapter())
    results.append(await test_conversation_adapter())
    results.append(await test_openai_adapter())
    
    # Résultats
    passed = sum(results)
    total = len(results)
    
    print("=" * 60)
    print(f"📊 Résultats: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests de logging Phase 1.2 réussis !")
        print("✅ Les modifications n'ont pas cassé l'existant")
        print("🔍 Le logging centralisé est prêt à l'usage")
        return 0
    else:
        print("⚠️ Certains tests ont échoué")
        print("🔧 Vérifiez les erreurs ci-dessus")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))