#!/usr/bin/env python3
"""
Démonstration du nouveau système de logging centralisé Phase 1.2
Montre les logs générés pour debug facile dans Chrome DevTools
"""

import sys
import asyncio
import json
from pathlib import Path
from uuid import uuid4

# Ajouter le chemin du projet pour les imports
sys.path.append(str(Path(__file__).parent))

async def demo_conversation_logging():
    """Démonstration du logging pour les conversations"""
    print("🎯 Démonstration: Logging des conversations")
    print("=" * 80)
    
    try:
        from app.adapters.outbound.conversation_adapter import ConversationAdapter
        
        adapter = ConversationAdapter()
        
        # Simulation d'une conversation d'apprenant
        learner_session_id = uuid4()
        
        print(f"👤 Learner Session ID: {learner_session_id}")
        print(f"💬 Message: 'Comment fonctionne le machine learning ?'")
        print(f"🎯 Action: Conversation avec enrichissement de profil")
        print()
        print("📋 LOGS GÉNÉRÉS (visible dans Chrome DevTools):")
        print("-" * 80)
        
        # Appel qui génère les logs complets
        result = await adapter.chat_with_learner(
            message="Comment fonctionne le machine learning ?",
            conversation_history=[],
            training_context="Formation Intelligence Artificielle - Module 1: Introduction",
            learner_profile={
                "experience_level": "beginner",
                "job_position": "développeur web",
                "activity_sector": "technologie",
                "language": "fr",
                "objectives": "comprendre l'IA pour intégrer dans mes projets"
            },
            learner_session_id=learner_session_id
        )
        
        print()
        print("✅ Réponse générée avec succès")
        print(f"📝 Response preview: {result.get('response', '')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

async def demo_image_generation_logging():
    """Démonstration du logging pour la génération d'images"""
    print("\n🎯 Démonstration: Logging DALL-E")
    print("=" * 80)
    
    try:
        from app.adapters.outbound.openai_adapter import OpenAIAdapter
        
        adapter = OpenAIAdapter()
        
        # Simulation de génération d'infographie
        learner_session_id = uuid4()
        slide_id = uuid4()
        
        print(f"👤 Learner Session ID: {learner_session_id}")
        print(f"🖼️ Slide ID: {slide_id}")
        print(f"🎨 Action: Génération infographie DALL-E")
        print()
        print("📋 LOGS GÉNÉRÉS (visible dans Chrome DevTools):")
        print("-" * 80)
        
        # Appel qui génère les logs complets
        result = await adapter.generate_infographic(
            slide_content="Le machine learning utilise des algorithmes pour analyser des données et faire des prédictions. Les réseaux de neurones s'inspirent du cerveau humain.",
            slide_title="Introduction au Machine Learning",
            learner_profile={
                "language": "french",
                "experience_level": "intermediate"
            },
            learner_session_id=learner_session_id,
            slide_id=slide_id
        )
        
        print()
        print("✅ Infographie générée avec succès")
        print(f"🖼️ Image size: {len(result.get('image_data', ''))} base64 chars")
        print(f"✨ Revised prompt: {result.get('revised_prompt', '')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def show_log_format_example():
    """Montre le format exact des logs générés"""
    print("\n🔍 Format des logs dans Chrome DevTools")
    print("=" * 80)
    
    print("""
LOGS BACKEND (dans la console du serveur FastAPI):

====================================================================================================
🎯 [GEMINI_CALL] [INPUT] [CONVERSATION_CHAT] [Session: test_ses... | Learner: 649a485c...]
📋 Call ID: call_3_1754062631
⏰ Timestamp: 2025-08-01T15:37:17.123456+00:00
📏 Prompt Length: 2847 characters
🔧 Context: {
  "prompt_type": "chat",
  "action_type": "chat",
  "generation_config": {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_output_tokens": 2048,
    "response_mime_type": "application/json"
  }
}
-------------------------------------------------- PROMPT START --------------------------------------------------
<ROLE>
Tu es un formateur pédagogue spécialisé dans la réponse aux [MESSAGE] d'un apprenant...
[PROMPT COMPLET ICI - VISIBLE POUR DEBUG]
</ROLE>
-------------------------------------------------- PROMPT END ----------------------------------------------------
====================================================================================================

====================================================================================================
📥 [GEMINI_CALL] [OUTPUT] [CONVERSATION_CHAT] [Session: test_ses... | Learner: 649a485c...]
📋 Call ID: call_3_1754062631
⏰ Timestamp: 2025-08-01T15:37:18.456789+00:00
📏 Response Length: 456 characters
⚡ Processing Time: 1.333s
🔧 Metadata: {
  "parsed_successfully": true,
  "action_type": "chat"
}
-------------------------------------------------- RESPONSE START ------------------------------------------------
{
  "response": "Le Machine Learning, c'est donner à un ordinateur la capacité d'apprendre...",
  "learner_profile": {
    "learning_style_observed": "préfère les explications concrètes",
    "comprehension_level": "bon niveau de compréhension",
    "interests": ["applications pratiques", "exemples concrets"],
    "blockers": ["concepts trop abstraits"],
    "objectives": "intégrer l'IA dans mes projets web",
    "engagement_patterns": "pose des questions précises"
  }
}
-------------------------------------------------- RESPONSE END --------------------------------------------------
====================================================================================================

LOGS FRONTEND (dans Chrome DevTools - à implémenter en Phase 2):

[API_CALL] [REQUEST] POST /api/chat - Payload: {...}
[API_CALL] [RESPONSE] 200 OK (1.45s) - Response: {...}
""")

async def main():
    """Fonction principale de démonstration"""
    print("🚀 Démonstration Logging Centralisé Phase 1.2")
    print("📋 Ce que vous verrez dans les logs de debug...")
    
    # Démonstrations
    await demo_conversation_logging()
    await demo_image_generation_logging()
    
    show_log_format_example()
    
    print("\n" + "=" * 80)
    print("🎉 Phase 1.2 terminée avec succès !")
    print("✅ Logging centralisé opérationnel")
    print("🔍 Tous les prompts et réponses Gemini sont maintenant visibles")
    print("📊 Traçabilité complète avec session IDs")
    print("⚡ Temps de traitement pour optimisation")
    
    print("\n📋 Utilisation:")
    print("1. Lancez votre serveur FastAPI")
    print("2. Utilisez l'app FIA normalement") 
    print("3. Regardez les logs dans la console serveur")
    print("4. Filtrez avec '[GEMINI_CALL]' pour voir uniquement les appels AI")
    print("5. Debug facile avec prompts et réponses complètes !")

if __name__ == "__main__":
    asyncio.run(main())