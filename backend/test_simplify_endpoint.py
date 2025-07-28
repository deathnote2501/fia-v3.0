#!/usr/bin/env python3
"""
Test script pour valider l'endpoint de simplification des slides
Usage: python test_simplify_endpoint.py
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

def test_simplify_endpoint():
    """Tester l'endpoint de simplification"""
    print_test_header("Slide Simplify Endpoint Test")
    
    # Test data - contenu markdown complexe à simplifier
    test_learner_session_id = "aac104a4-dd4e-45de-98bf-e361dae11625"
    test_content = """# Introduction à l'Intelligence Artificielle Générative

## Définition et Concepts Fondamentaux

L'intelligence artificielle générative représente une révolution technologique majeure qui transforme fondamentalement la manière dont nous créons, interagissons et conceptualisons le contenu numérique. Cette technologie sophistiquée utilise des algorithmes d'apprentissage automatique avancés, notamment les réseaux de neurones profonds, pour analyser d'immenses corpus de données textuelles, visuelles ou multimodales afin de générer du nouveau contenu original et cohérent.

### Caractéristiques Techniques Principales

- **Apprentissage profond (Deep Learning)** : Utilisation de réseaux de neurones multicouches
- **Modèles transformateurs** : Architecture révolutionnaire pour le traitement du langage naturel
- **Entraînement sur données massives** : Billions de paramètres optimisés sur des téraoctets de données
- **Capacités multimodales** : Génération simultanée de texte, images, audio et vidéo

## Applications Industrielles et Sectorielles

### Secteur Financier et Bancaire
- Automatisation de la rédaction de rapports d'analyse financière
- Génération de synthèses économiques personnalisées
- Création de contenu marketing adapté aux différents segments clientèle
- Analyse prédictive et modélisation de scénarios économiques complexes

### Domaine Médical et de la Santé
- Assistance à la rédaction de dossiers médicaux
- Génération de recommandations thérapeutiques personnalisées
- Création de contenu éducatif pour la formation continue des professionnels

> **Citation d'expert** : "L'IA générative n'est pas seulement un outil, c'est un partenaire créatif qui augmente nos capacités humaines tout en préservant notre unicité créative." - Dr. Sarah Chen, Directrice de Recherche en IA

## Défis Éthiques et Considérations Stratégiques

L'implémentation de l'IA générative soulève des questions fondamentales concernant l'authenticité, la propriété intellectuelle, et l'impact sociétal. Les organisations doivent développer des frameworks éthiques robustes pour naviguer ces nouveaux territoires technologiques."""

    request_data = {
        "current_content": test_content
    }
    
    try:
        print_info(f"Calling POST /api/slides/simplify/{test_learner_session_id}")
        print_info(f"Content length: {len(test_content)} characters")
        print_info(f"Content preview: {test_content[:100]}...")
        
        response = requests.post(
            f"{BASE_URL}/api/slides/simplify/{test_learner_session_id}",
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
                    simplified_content = data.get("simplified_content")
                    
                    if simplified_content:
                        print_success("Simplified content received!")
                        print_info(f"Original length: {data.get('original_length', 'N/A')}")
                        print_info(f"Simplified length: {data.get('simplified_length', 'N/A')}")
                        print_info(f"Processing time: {data.get('processing_time', 'N/A')}s")
                        print_info(f"Simplified preview: {simplified_content[:200]}...")
                        
                        # Vérifier que le contenu est effectivement simplifié
                        if len(simplified_content) < len(test_content):
                            print_success("Content was successfully reduced in size")
                        else:
                            print_error("Content was not reduced in size")
                            
                        return True
                    else:
                        print_error("No simplified_content in response")
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

def main():
    """Fonction principale de test"""
    print("🚀 Starting slide simplify endpoint testing...")
    
    # Test 1: Health check
    health_ok = test_health_check()
    
    # Test 2: Simplify endpoint
    simplify_ok = test_simplify_endpoint()
    
    # Résumé
    print_test_header("RÉSUMÉ DES TESTS")
    
    tests_results = {
        "Health Check": health_ok,
        "Simplify Endpoint": simplify_ok
    }
    
    passed = sum(tests_results.values())
    total = len(tests_results)
    
    print(f"\n🎯 RÉSULTATS: {passed}/{total} tests passés")
    
    for test_name, passed in tests_results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {test_name}")
    
    if passed == total:
        print("\n🎉 Tous les tests sont réussis ! L'endpoint de simplification fonctionne correctement.")
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