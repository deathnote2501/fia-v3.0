# Document Processing Service

Service pour analyser les supports de formation (PDF/PowerPoint) à l'aide de l'API Gemini Document Understanding.

## Fonctionnalités

### 🔍 Analyse complète de documents
- Parsing intelligent des PDF et PowerPoint
- Extraction de la structure et de l'organisation
- Identification des objectifs pédagogiques
- Analyse de la complexité du contenu

### 📋 Fonctions principales

#### `parse_document_content()`
Analyse complète du document avec prompt personnalisable
```python
result = await service.parse_document_content(
    file_path="/path/to/document.pdf",
    mime_type="application/pdf",
    custom_prompt="Analyze learning objectives"
)
```

#### `extract_document_summary()`
Extraction d'un résumé concis (2-3 paragraphes)
```python
summary = await service.extract_document_summary(
    file_path="/path/to/document.pdf",
    mime_type="application/pdf"
)
```

#### `analyze_document_structure()`
Analyse structurelle pour création de plans de formation
```python
structure = await service.analyze_document_structure(
    file_path="/path/to/document.pdf",
    mime_type="application/pdf"
)
```

#### `validate_document_for_training()`
Validation de l'adéquation pour la formation
```python
is_valid, message = await service.validate_document_for_training(
    file_path="/path/to/document.pdf",
    mime_type="application/pdf"
)
```

## Configuration requise

### Variables d'environnement
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_REGION=europe-west1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GEMINI_MODEL_NAME=gemini-2.0-flash-001
```

### Types MIME supportés
- `application/pdf` - Documents PDF
- `application/vnd.ms-powerpoint` - PowerPoint (.ppt)
- `application/vnd.openxmlformats-officedocument.presentationml.presentation` - PowerPoint (.pptx)

## Limitations Gemini

- **Taille maximale** : 1000 pages par document
- **Résolution** : Pages redimensionnées à 3072x3072 max
- **Token minimum** : 1024 tokens (Flash) / 2048 tokens (Pro)
- **Formats** : PDF uniquement pour vision, autres formats en texte pur

## Gestion d'erreurs

### `DocumentProcessingError`
Exception personnalisée pour les erreurs de traitement
- Problèmes de credentials Gemini
- Fichiers non trouvés ou corrompus
- Réponses vides de l'API
- Erreurs de parsing

### Codes d'erreur API
- `422` : Erreur de traitement (fichier invalide, etc.)
- `404` : Fichier non trouvé
- `500` : Erreur serveur (problème Gemini, etc.)

## Intégration avec l'architecture existante

### Utilisation avec les entités Training
```python
from app.domain.entities import Training
from app.domain.services.document_processing_service import DocumentProcessingService

# Analyser un support de formation existant
training = session.get(Training, training_id)
doc_service = DocumentProcessingService()

result = await doc_service.parse_document_content(
    file_path=training.file_path,
    mime_type=training.mime_type
)
```

### API Endpoints disponibles
- `POST /api/document-processing/parse` - Analyse complète
- `POST /api/document-processing/summary` - Résumé
- `POST /api/document-processing/structure` - Structure
- `POST /api/document-processing/validate` - Validation
- `GET /api/document-processing/health` - Health check

## Performance et optimisation

### Context Caching
Le service est conçu pour travailler avec Context Caching :
- TTL par défaut : 12 heures
- Réduction de coût : 75% sur tokens en cache
- Stockage régional sécurisé

### Rate Limiting
- Limite par défaut : 60 requêtes/minute
- Configurable via `GEMINI_RATE_LIMIT_PER_MINUTE`

## Exemples d'utilisation

### Analyse basique
```python
service = DocumentProcessingService()
result = await service.parse_document_content(
    file_path="/uploads/training.pdf",
    mime_type="application/pdf"
)

if result['success']:
    content = result['content']
    metadata = result['processing_metadata']
    print(f"Analysé avec {metadata['model_used']}")
```

### Validation pour formation
```python
is_valid, message = await service.validate_document_for_training(
    file_path="/uploads/document.pdf",
    mime_type="application/pdf"
)

if is_valid:
    print(f"✅ Document valide: {message}")
else:
    print(f"❌ Document invalide: {message}")
```

## Prochaines étapes

Ce service sera utilisé dans les phases suivantes pour :
1. **Context Caching** : Mise en cache des supports analysés
2. **Plan Generation** : Utilisation de l'analyse pour créer les plans personnalisés
3. **Structured Output** : Génération de plans JSON structurés