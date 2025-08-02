#!/usr/bin/env python3
"""
Test du service GeminiCallLogger
Script de test pour vérifier le bon fonctionnement du logger centralisé
"""

import sys
import json
from pathlib import Path

# Ajouter le chemin du projet pour les imports
sys.path.append(str(Path(__file__).parent))

from app.infrastructure.gemini_call_logger import gemini_call_logger
from uuid import uuid4

def test_basic_logging():
    """Test basique du logging input/output"""
    print("🧪 Test 1: Logging basique")
    
    # Test d'un appel simple
    call_id = gemini_call_logger.log_input(
        service_name="test_service",
        prompt="Ceci est un prompt de test pour vérifier le logging",
        session_id="test_session_123",
        learner_session_id=str(uuid4()),
        additional_context={"test": True, "environment": "development"}
    )
    
    print(f"✅ Call ID généré: {call_id}")
    
    # Test de la réponse
    test_response = {
        "response": "Ceci est une réponse de test",
        "metadata": {"tokens": 150, "model": "gemini-2.0-flash"}
    }
    
    gemini_call_logger.log_output(
        call_id=call_id,
        service_name="test_service",
        response=test_response,
        session_id="test_session_123",
        learner_session_id=str(uuid4()),
        processing_time=1.234,
        additional_metadata={"test_mode": True}
    )
    
    print("✅ Test 1 terminé\n")

def test_string_response():
    """Test avec une réponse string"""
    print("🧪 Test 2: Réponse string")
    
    call_id = gemini_call_logger.log_input(
        service_name="conversation",
        prompt="Tu es un assistant. Réponds brièvement à la question suivante: Comment ça va ?",
        learner_session_id=str(uuid4())
    )
    
    gemini_call_logger.log_output(
        call_id=call_id,
        service_name="conversation",
        response="Ça va bien, merci ! Comment puis-je vous aider aujourd'hui ?",
        processing_time=0.856
    )
    
    print("✅ Test 2 terminé\n")

def test_error_logging():
    """Test du logging d'erreurs"""
    print("🧪 Test 3: Logging d'erreurs")
    
    call_id = gemini_call_logger.log_input(
        service_name="plan_generation",
        prompt="Génère un plan de formation sur l'intelligence artificielle",
        session_id="error_test_session"
    )
    
    # Simuler une erreur
    try:
        raise ValueError("Erreur de test - prompt trop long")
    except ValueError as e:
        gemini_call_logger.log_error(
            call_id=call_id,
            service_name="plan_generation",
            error=e,
            session_id="error_test_session",
            processing_time=2.1
        )
    
    print("✅ Test 3 terminé\n")

def test_json_response():
    """Test avec une réponse JSON complexe"""
    print("🧪 Test 4: Réponse JSON complexe")
    
    call_id = gemini_call_logger.log_input(
        service_name="chart_generation",
        prompt="Génère des graphiques pour les données de vente",
        additional_context={
            "max_charts": 2,
            "chart_types": ["line", "pie"],
            "data_source": "sales_report_2024"
        }
    )
    
    complex_response = {
        "recommended_charts": [
            {
                "type": "line",
                "title": "Évolution des ventes 2024",
                "data": [100, 150, 200, 180, 220],
                "labels": ["Jan", "Fév", "Mar", "Avr", "Mai"],
                "sources": [{"title": "Rapport interne", "url": ""}]
            },
            {
                "type": "pie", 
                "title": "Répartition par secteur",
                "data": [35, 25, 40],
                "labels": ["Tech", "Services", "Retail"]
            }
        ],
        "metadata": {
            "generation_time": "2024-01-28T15:30:00Z",
            "model_version": "gemini-2.0-flash",
            "grounding_sources": 3
        }
    }
    
    gemini_call_logger.log_output(
        call_id=call_id,
        service_name="chart_generation",
        response=complex_response,
        processing_time=3.456,
        additional_metadata={"charts_generated": 2, "grounding_enabled": True}
    )
    
    print("✅ Test 4 terminé\n")

def test_stats():
    """Test des statistiques"""
    print("🧪 Test 5: Statistiques du logger")
    
    stats = gemini_call_logger.get_stats()
    print(f"📊 Statistiques: {json.dumps(stats, indent=2)}")
    
    print("✅ Test 5 terminé\n")

def main():
    """Fonction principale de test"""
    print("🚀 Début des tests du GeminiCallLogger")
    print("=" * 60)
    
    try:
        test_basic_logging()
        test_string_response()
        test_error_logging()
        test_json_response()
        test_stats()
        
        print("🎉 Tous les tests sont terminés avec succès !")
        print("🔍 Vérifiez les logs ci-dessus pour confirmer le bon formatage")
        
    except Exception as e:
        print(f"❌ Erreur durant les tests: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())