#!/usr/bin/env python3
"""
Test script pour valider tous les endpoints de conversation
Usage: python test_conversation_endpoints.py
"""

import asyncio
import requests
import json
import sys
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def print_test_header(test_name: str):
    """Afficher l'en-tête d'un test"""
    print(f"\n{'='*60}")
    print(f"🧪 TEST: {test_name}")
    print('='*60)

def print_success(message: str):
    """Afficher un message de succès"""
    print(f"✅ {message}")

def print_error(message: str):
    """Afficher un message d'erreur"""
    print(f"❌ {message}")

def print_info(message: str):
    """Afficher une information"""
    print(f"ℹ️  {message}")

def test_endpoint(method: str, url: str, data: Dict[Any, Any] = None, expected_status: int = 200) -> Dict[Any, Any]:
    """Tester un endpoint et retourner la réponse"""
    try:
        print_info(f"Calling {method} {url}")
        
        if method.upper() == "GET":
            response = requests.get(url, timeout=TIMEOUT)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=TIMEOUT)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print_info(f"Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print_success(f"✅ Status code correct: {response.status_code}")
        else:
            print_error(f"Status code incorrect: {response.status_code} (expected: {expected_status})")
            
        try:
            response_data = response.json()
            print_info(f"Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Not a dict'}")
            return response_data
        except:
            print_info(f"Response text: {response.text[:200]}...")
            return {"text": response.text}
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        return {"error": str(e)}

def main():
    """Fonction principale de test"""
    print("🚀 Starting conversation endpoints testing...")
    
    # Test 1: Health check
    print_test_header("Health Check")
    health_response = test_endpoint("GET", f"{BASE_URL}/api/chat/health")
    
    if "status" in health_response:
        if health_response["status"] == "healthy":
            print_success("Service is healthy")
        else:
            print_error(f"Service not healthy: {health_response['status']}")
    
    # Test 2: General API health
    print_test_header("General API Health")
    api_health = test_endpoint("GET", f"{BASE_URL}/api/health")
    
    # Test 3: Chat endpoint with minimal data
    print_test_header("Chat Endpoint - Minimal Request")
    
    chat_request_minimal = {
        "message": "Bonjour, comment ça va ?",
        "context": {
            "training_id": "833a9b61-5444-421b-aa9b-57f6717d9fa6",
            "learner_session_id": "aac104a4-dd4e-45de-98bf-e361dae11625",
            "current_slide_id": None,
            "training_content": "Introduction à l'IA générative",
            "learner_profile": {
                "experience_level": "expert",
                "learning_style": "visual",
                "job_position": "développeur test",
                "activity_sector": "informatique",
                "country": "France",
                "language": "fr"
            },
            "conversation_history": []
        },
        "conversation_type": "general"
    }
    
    chat_response = test_endpoint("POST", f"{BASE_URL}/api/chat", chat_request_minimal)
    
    if "response" in chat_response:
        print_success(f"Chat response received: '{chat_response['response'][:100]}...'")
        if "confidence_score" in chat_response:
            print_info(f"Confidence score: {chat_response['confidence_score']}")
        if "suggested_actions" in chat_response:
            print_info(f"Suggested actions: {chat_response['suggested_actions']}")
    else:
        print_error("No response field in chat response")
    
    # Test 4: Chat endpoint with conversation history
    print_test_header("Chat Endpoint - With History")
    
    chat_request_with_history = {
        "message": "Peux-tu me donner un exemple concret ?",
        "context": {
            "training_id": "833a9b61-5444-421b-aa9b-57f6717d9fa6",
            "learner_session_id": "aac104a4-dd4e-45de-98bf-e361dae11625",
            "current_slide_id": None,
            "training_content": "Introduction à l'IA générative - concepts, applications",
            "learner_profile": {
                "experience_level": "expert",
                "learning_style": "visual", 
                "job_position": "développeur test",
                "activity_sector": "informatique",
                "country": "France",
                "language": "fr"
            },
            "conversation_history": [
                {
                    "role": "assistant",
                    "content": "Bonjour ! Je suis là pour vous aider avec cette formation sur l'IA générative.",
                    "timestamp": "12:00:00",
                    "metadata": {}
                },
                {
                    "role": "user", 
                    "content": "Bonjour, comment ça va ?",
                    "timestamp": "12:01:00",
                    "metadata": {}
                }
            ]
        },
        "conversation_type": "general"
    }
    
    chat_response_history = test_endpoint("POST", f"{BASE_URL}/api/chat", chat_request_with_history)
    
    # Test 5: Hint endpoint  
    print_test_header("Hint Endpoint")
    
    hint_request = {
        "current_slide": {
            "title": "Introduction à l'IA générative",
            "content": "L'IA générative permet de créer du nouveau contenu..."
        },
        "learner_question": "Je ne comprends pas la différence avec l'IA classique",
        "learner_profile": {
            "experience_level": "expert",
            "learning_style": "visual"
        }
    }
    
    hint_response = test_endpoint(
        "POST", 
        f"{BASE_URL}/api/chat/hint?learner_session_id=aac104a4-dd4e-45de-98bf-e361dae11625", 
        hint_request
    )
    
    # Test 6: Explain endpoint
    print_test_header("Explain Endpoint")
    
    explain_request = {
        "concept": "IA générative",
        "training_context": "Formation sur l'intelligence artificielle générative",
        "learner_profile": {
            "experience_level": "expert",
            "learning_style": "visual",
            "job_position": "développeur test"
        }
    }
    
    explain_response = test_endpoint(
        "POST",
        f"{BASE_URL}/api/chat/explain?learner_session_id=aac104a4-dd4e-45de-98bf-e361dae11625",
        explain_request
    )
    
    # Test 7: Metrics endpoint
    print_test_header("Metrics Endpoint")
    
    metrics_response = test_endpoint(
        "GET",
        f"{BASE_URL}/api/chat/metrics/aac104a4-dd4e-45de-98bf-e361dae11625"
    )
    
    # Résumé des tests
    print_test_header("RÉSUMÉ DES TESTS")
    
    tests_results = {
        "Health Check": "status" in health_response,
        "API Health": "status" in api_health,
        "Chat Minimal": "response" in chat_response,
        "Chat with History": "response" in chat_response_history, 
        "Hint": isinstance(hint_response, (str, dict)),
        "Explain": isinstance(explain_response, (str, dict)),
        "Metrics": "total_messages" in metrics_response if isinstance(metrics_response, dict) else False
    }
    
    passed = sum(tests_results.values())
    total = len(tests_results)
    
    print(f"\n🎯 RÉSULTATS: {passed}/{total} tests passés")
    
    for test_name, passed in tests_results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {test_name}")
    
    if passed == total:
        print("\n🎉 Tous les tests sont réussis ! Les endpoints de conversation fonctionnent correctement.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) échoué(s). Vérifiez les logs ci-dessus.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erreur inattendue: {str(e)}")
        sys.exit(1)