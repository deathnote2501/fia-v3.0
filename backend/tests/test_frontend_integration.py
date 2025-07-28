#!/usr/bin/env python3
"""
Test script pour vérifier que le frontend peut appeler les deux endpoints
Usage: python test_frontend_integration.py
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

def test_both_endpoints():
    """Tester les deux endpoints simplify et more-details"""
    print_test_header("Frontend Integration Test - Both Endpoints")
    
    # Test data - contenu markdown simple
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
    
    results = {}
    
    # Test 1: Simplify endpoint
    try:
        print_info("Testing SIMPLIFY endpoint...")
        
        response = requests.post(
            f"{BASE_URL}/api/slides/simplify/{test_learner_session_id}",
            json=request_data,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("data", {}).get("simplified_content"):
                simplified = data["data"]["simplified_content"]
                results["simplify"] = {
                    "success": True,
                    "length": len(simplified),
                    "preview": simplified[:100] + "..."
                }
                print_success(f"Simplify OK - {len(test_content)} → {len(simplified)} chars")
            else:
                results["simplify"] = {"success": False, "error": "Invalid response structure"}
                print_error("Simplify failed - Invalid response")
        else:
            results["simplify"] = {"success": False, "error": f"HTTP {response.status_code}"}
            print_error(f"Simplify failed - HTTP {response.status_code}")
    
    except Exception as e:
        results["simplify"] = {"success": False, "error": str(e)}
        print_error(f"Simplify failed - {str(e)}")
    
    # Test 2: More Details endpoint
    try:
        print_info("Testing MORE DETAILS endpoint...")
        
        response = requests.post(
            f"{BASE_URL}/api/slides/more-details/{test_learner_session_id}",
            json=request_data,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("data", {}).get("detailed_content"):
                detailed = data["data"]["detailed_content"]
                results["more_details"] = {
                    "success": True,
                    "length": len(detailed),
                    "preview": detailed[:100] + "..."
                }
                print_success(f"More Details OK - {len(test_content)} → {len(detailed)} chars")
            else:
                results["more_details"] = {"success": False, "error": "Invalid response structure"}
                print_error("More Details failed - Invalid response")
        else:
            results["more_details"] = {"success": False, "error": f"HTTP {response.status_code}"}
            print_error(f"More Details failed - HTTP {response.status_code}")
    
    except Exception as e:
        results["more_details"] = {"success": False, "error": str(e)}
        print_error(f"More Details failed - {str(e)}")
    
    return results

def main():
    """Fonction principale de test"""
    print("🚀 Starting frontend integration testing...")
    
    # Test des deux endpoints
    results = test_both_endpoints()
    
    # Résumé
    print_test_header("RÉSUMÉ DES TESTS FRONTEND")
    
    simplify_ok = results.get("simplify", {}).get("success", False)
    more_details_ok = results.get("more_details", {}).get("success", False)
    
    print(f"\n🎯 RÉSULTATS:")
    print(f"✅ Simplify Endpoint: {'OK' if simplify_ok else 'FAILED'}")
    print(f"✅ More Details Endpoint: {'OK' if more_details_ok else 'FAILED'}")
    
    if simplify_ok and more_details_ok:
        print("\n🎉 Les deux endpoints sont fonctionnels ! Le frontend peut utiliser les deux boutons.")
        
        # Afficher les comparaisons
        if results["simplify"]["success"] and results["more_details"]["success"]:
            orig_len = len("""# Introduction à l'IA Générative

## Qu'est-ce que l'IA Générative ?

L'IA Générative crée du nouveau contenu automatiquement.
Elle utilise des algorithmes pour apprendre et générer du texte, des images, du code.

## Applications pratiques

- Génération de code
- Création de contenu  
- Assistance automatisée

## Pourquoi c'est important ?

L'IA Générative révolutionne le développement logiciel en automatisant des tâches créatives.""")
            
            print(f"\n📊 COMPARAISON DES RÉSULTATS:")
            print(f"📝 Original: {orig_len} characters")
            print(f"📉 Simplified: {results['simplify']['length']} characters ({((results['simplify']['length'] - orig_len) / orig_len * 100):+.1f}%)")
            print(f"📈 More Details: {results['more_details']['length']} characters ({((results['more_details']['length'] - orig_len) / orig_len * 100):+.1f}%)")
        
        return 0
    else:
        print(f"\n⚠️ Certains endpoints ont échoué. Vérifiez les logs ci-dessus.")
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