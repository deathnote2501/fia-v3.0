#!/usr/bin/env python3
"""
Test script pour valider le service more_details_slide_content
Usage: python test_more_details_service.py
"""

import asyncio
import sys
import os
import logging

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.slide_generation_service import SlideGenerationService

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

async def test_more_details_service():
    """Tester le service more_details_slide_content"""
    print_test_header("SlideGenerationService - More Details")
    
    # Contenu de test - slide simple à approfondir
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

    try:
        print_info(f"Testing more_details_slide_content for session: {test_learner_session_id}")
        print_info(f"Original content length: {len(test_content)} characters")
        print_info(f"Original content preview: {test_content[:100]}...")
        
        # Initialiser le service
        slide_service = SlideGenerationService()
        print_success("SlideGenerationService initialized")
        
        # Tester la méthode more_details_slide_content
        result = await slide_service.more_details_slide_content(
            learner_session_id=test_learner_session_id,
            current_slide_content=test_content
        )
        
        print_success("more_details_slide_content completed!")
        
        # Vérifier la structure du résultat
        expected_keys = ["detailed_content", "original_length", "detailed_length", "processing_time", "learner_session_id"]
        result_keys = list(result.keys())
        
        if all(key in result_keys for key in expected_keys):
            print_success("Result structure is correct")
            
            detailed_content = result["detailed_content"]
            original_length = result["original_length"]
            detailed_length = result["detailed_length"]
            processing_time = result["processing_time"]
            
            print_info(f"Original length: {original_length}")
            print_info(f"Detailed length: {detailed_length}")
            print_info(f"Processing time: {processing_time}s")
            print_info(f"Length increase: {detailed_length - original_length} chars (+{((detailed_length - original_length) / original_length * 100):.1f}%)")
            print_info(f"Detailed content preview: {detailed_content[:150]}...")
            
            # Vérifier que le contenu a été approfondi
            if detailed_length > original_length:
                print_success("Content was successfully enhanced with more details")
            else:
                print_error("Content was not expanded")
                
            # Vérifier que c'est du markdown valide
            if detailed_content.startswith('#') and '##' in detailed_content:
                print_success("Content appears to be valid markdown")
            else:
                print_error("Content doesn't appear to be valid markdown")
                
            return True
            
        else:
            print_error(f"Missing keys in result. Expected: {expected_keys}, Got: {result_keys}")
            return False
            
    except Exception as e:
        print_error(f"Test failed with exception: {str(e)}")
        logger.exception("Full exception details:")
        return False

async def main():
    """Fonction principale de test"""
    print("🚀 Starting SlideGenerationService more_details tests...")
    
    # Test du service more_details
    more_details_ok = await test_more_details_service()
    
    # Résumé
    print_test_header("RÉSUMÉ DES TESTS")
    
    tests_results = {
        "More Details Service": more_details_ok
    }
    
    passed = sum(tests_results.values())
    total = len(tests_results)
    
    print(f"\n🎯 RÉSULTATS: {passed}/{total} tests passés")
    
    for test_name, passed in tests_results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {test_name}")
    
    if passed == total:
        print("\n🎉 Tous les tests sont réussis ! Le service more_details fonctionne correctement.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) échoué(s). Vérifiez les logs ci-dessus.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erreur inattendue: {str(e)}")
        sys.exit(1)