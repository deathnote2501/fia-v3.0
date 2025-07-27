#!/usr/bin/env python3
"""
Test simple pour vérifier que Vertex AI fonctionne
"""

import os
from pathlib import Path

# Configuration du chemin des credentials
project_root = Path(__file__).parent.parent
credentials_path = project_root / "animemate-ddb62-5161876d56bc.json"

print(f"🔍 Vérification du fichier credentials: {credentials_path}")
print(f"📁 Fichier existe: {credentials_path.exists()}")

if credentials_path.exists():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path)
    print(f"✅ Variable d'environnement définie: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
else:
    print("❌ Fichier credentials non trouvé")
    exit(1)

# Test des imports
print("\n🧪 Test des imports...")
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    print("✅ Imports Vertex AI réussis")
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    exit(1)

# Configuration Vertex AI
print("\n⚙️ Configuration Vertex AI...")
try:
    vertexai.init(
        project="animemate-ddb62",
        location="europe-west1"
    )
    print("✅ Vertex AI initialisé")
except Exception as e:
    print(f"❌ Erreur d'initialisation: {e}")
    exit(1)

# Création du modèle
print("\n🤖 Création du modèle...")
try:
    model = GenerativeModel(model_name="gemini-2.0-flash-001")
    print("✅ Modèle créé")
except Exception as e:
    print(f"❌ Erreur de création du modèle: {e}")
    exit(1)

# Test simple avec "Hello"
print("\n💬 Test avec un message simple...")
try:
    response = model.generate_content("Hello, please respond with a simple greeting.")
    
    if response and response.text:
        print(f"✅ Réponse reçue: {response.text}")
        print("🎉 Vertex AI fonctionne parfaitement !")
    else:
        print("❌ Réponse vide ou invalide")
        exit(1)
        
except Exception as e:
    print(f"❌ Erreur lors de la génération: {e}")
    exit(1)

print("\n✨ Tous les tests sont passés avec succès !")