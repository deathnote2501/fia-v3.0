#!/usr/bin/env python3
"""
Test script pour valider l'endpoint de more details des slides
Usage: python test_more_details_endpoint.py
"""

import requests
import json
import sys

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

def test_more_details_endpoint():
    """Tester l'endpoint de more details"""
    print_test_header("Slide More Details Endpoint Test")
    
    # Test data - contenu markdown simple à approfondir
    test_learner_session_id = "aac104a4-dd4e-45de-98bf-e361dae11625"
    test_content = """# Introduction à l'IA Générative

## Qu'est-ce que l'IA Générative ?

L'IA Générative crée du nouveau contenu automatiquement.
Elle utilise des algorithmes pour apprendre et générer du texte, des images, du code.

## Applications pratiques

- Génération de code
- Création de contenu  
- Assistance automatisée

## Pourquoi c'est important ?

L'IA Générative révolutionne le développement logiciel en automatisant des tâches créatives."""

    request_data = {
        "current_content": test_content
    }
    
    try:
        print_info(f"Calling POST /api/slides/more-details/{test_learner_session_id}")
        print_info(f"Content length: {len(test_content)} characters")
        print_info(f"Content preview: {test_content[:100]}...")
        
        response = requests.post(
            f"{BASE_URL}/api/slides/more-details/{test_learner_session_id}",
            json=request_data,
            timeout=TIMEOUT
        )
        
        print_info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print_success("✅ Status code correct: 200")
            
            try:
                response_data = response.json()
                print_info(f"Response keys: {list(response_data.keys())}")
                
                if response_data.get("success"):
                    print_success("API returned success=true")
                    
                    data = response_data.get("data", {})
                    detailed_content = data.get("detailed_content")
                    
                    if detailed_content:
                        print_success("Enhanced content received!")
                        print_info(f"Original length: {data.get('original_length', 'N/A')}")
                        print_info(f"Enhanced length: {data.get('detailed_length', 'N/A')}")
                        print_info(f"Processing time: {data.get('processing_time', 'N/A')}s")
                        print_info(f"Enhanced preview: {detailed_content[:200]}...")
                        
                        # Vérifier que le contenu a été approfondi
                        original_len = data.get('original_length', 0)
                        enhanced_len = data.get('detailed_length', 0)
                        
                        if enhanced_len > original_len:
                            increase_pct = ((enhanced_len - original_len) / original_len * 100)
                            print_success(f"Content was successfully enhanced (+{increase_pct:.1f}%)")
                        else:
                            print_error("Content was not expanded")
                            
                        # Vérifier que c'est du markdown valide
                        if detailed_content.startswith('#') and '##' in detailed_content:
                            print_success("Content appears to be valid markdown")
                        else:
                            print_error("Content doesn't appear to be valid markdown")
                            
                        return True
                    else:
                        print_error("No detailed_content in response")
                        return False
                else:
                    print_error(f"API returned success=false: {response_data.get('message', 'No message')}")
                    return False
                    
            except json.JSONDecodeError as e:
                print_error(f"Invalid JSON response: {str(e)}")
                print_info(f"Response text: {response.text[:200]}...")
                return False
                
        else:
            print_error(f"Status code incorrect: {response.status_code}")
            print_info(f"Response text: {response.text[:200]}...")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        return False

def test_health_check():
    """Tester le health check des slides"""
    print_test_header("Slide Service Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/api/slides/health", timeout=TIMEOUT)
        print_info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Health check passed")
            print_info(f"Service status: {data.get('status', 'unknown')}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False

def test_validation_error():
    """Tester la validation des erreurs"""
    print_test_header("Validation Error Test")
    
    test_learner_session_id = "aac104a4-dd4e-45de-98bf-e361dae11625"
    
    # Test avec contenu trop court
    request_data = {
        "current_content": "short"  # Moins de 10 caractères
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/slides/more-details/{test_learner_session_id}",
            json=request_data,
            timeout=TIMEOUT
        )
        
        print_info(f"Status: {response.status_code}")
        
        if response.status_code == 400:
            print_success("Validation error correctly returned 400")
            return True
        else:
            print_error(f"Expected 400, got {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Validation test error: {str(e)}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Starting slide more-details endpoint testing...")
    
    # Test 1: Health check
    health_ok = test_health_check()
    
    # Test 2: More Details endpoint
    more_details_ok = test_more_details_endpoint()
    
    # Test 3: Validation
    validation_ok = test_validation_error()
    
    # Résumé
    print_test_header("RÉSUMÉ DES TESTS")
    
    tests_results = {
        "Health Check": health_ok,
        "More Details Endpoint": more_details_ok,
        "Validation Error": validation_ok
    }
    
    passed = sum(tests_results.values())
    total = len(tests_results)
    
    print(f"\n🎯 RÉSULTATS: {passed}/{total} tests passés")
    
    for test_name, passed in tests_results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {test_name}")
    
    if passed == total:
        print("\n🎉 Tous les tests sont réussis ! L'endpoint more-details fonctionne correctement.")
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