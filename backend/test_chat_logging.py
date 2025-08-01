#!/usr/bin/env python3
"""
Test pour vérifier que les logs centralisés apparaissent maintenant pour /api/chat
"""

import sys
import asyncio
from pathlib import Path
from uuid import uuid4

# Ajouter le chemin du projet pour les imports
sys.path.append(str(Path(__file__).parent))

async def test_chat_logging():
    """Test que les logs de conversation apparaissent bien"""
    print("🧪 Test: Logging de conversation via /api/chat")
    print("=" * 60)
    
    try:
        # Configuration du logging pour voir tous les niveaux
        import logging
        logging.basicConfig(level=logging.DEBUG)
        
        from app.domain.services.conversation_service import ConversationService
        from app.adapters.outbound.conversation_adapter import ConversationAdapter
        from app.domain.schemas.conversation import ChatRequest, ConversationContext, ConversationMessage
        
        # Créer le service de conversation
        adapter = ConversationAdapter()
        service = ConversationService(adapter)
        
        # Créer une requête de chat comme celle du frontend
        learner_session_id = uuid4()
        
        chat_request = ChatRequest(
            message="Salut ! Comment ça va ?",
            conversation_type="general",
            context=ConversationContext(
                training_id=uuid4(),  # Ajout du training_id requis
                learner_session_id=learner_session_id,
                training_content="Formation TikTok et web-marketing",
                learner_profile={
                    "experience_level": "beginner",
                    "job_position": "marketing",
                    "language": "fr"
                },
                conversation_history=[]
            )
        )
        
        print(f"👤 Learner Session ID: {learner_session_id}")
        print(f"💬 Message: '{chat_request.message}'")
        print()
        print("📋 LOGS ATTENDUS (doivent maintenant apparaître):")
        print("-" * 60)
        
        # Appel qui devrait maintenant générer les logs centralisés
        response = await service.handle_learner_chat(chat_request)
        
        print()
        print("✅ Response générée avec succès")
        print(f"📝 Response: {response.response[:100]}...")
        print(f"🎯 Confidence: {response.confidence_score}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Fonction principale de test"""
    print("🔍 Test correction du logging /api/chat")
    
    success = await test_chat_logging()
    
    if success:
        print("\n🎉 Fix appliqué avec succès !")
        print("✅ Les logs centralisés devraient maintenant apparaître")
        print("🔍 Regarde dans la console serveur pour voir les logs [GEMINI_CALL]")
    else:
        print("\n❌ Le test a échoué")
        print("🔧 Vérifiez les erreurs ci-dessus")

if __name__ == "__main__":
    asyncio.run(main())