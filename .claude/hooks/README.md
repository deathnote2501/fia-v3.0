# FIA v3.0 - Hooks de Validation des Bonnes Pratiques

Ce dossier contient les hooks de validation qui s'assurent du respect des bonnes pratiques définies dans `SPEC.md`.

## 🎯 Objectif

Garantir que le développement respecte les standards définis :
- Architecture hexagonale
- Conventions de nommage anglais-first
- Sécurité et validation des données
- Optimisations de performance
- Préparation à l'internationalisation

## 📋 Hooks Disponibles

### 1. `validate_best_practices.sh` (Hook Principal)
**Description** : Orchestre l'exécution de tous les hooks de validation  
**Usage** : `./validate_best_practices.sh`  
**Fonction** : Point d'entrée principal qui exécute tous les autres hooks

### 2. `architecture_validation.sh`
**Description** : Valide l'architecture hexagonale et la structure du projet  
**Vérifie** :
- Structure des dossiers (domain/, adapters/, infrastructure/)
- Séparation des couches
- Absence de logique métier dans les adapters
- Configuration Poetry correcte
- Stack technologique obligatoire (FastAPI, SQLAlchemy, etc.)

### 3. `naming_conventions.sh`  
**Description** : Contrôle les conventions de nommage anglais-first  
**Vérifie** :
- Noms de fichiers en anglais
- Classes en PascalCase anglais
- Variables en snake_case anglais
- Routes en kebab-case anglais
- Tables et colonnes en snake_case anglais
- Absence de mots français dans le code

### 4. `security_validation.sh`
**Description** : Valide les pratiques de sécurité et validation  
**Vérifie** :
- Absence de secrets hardcodés
- Utilisation de variables d'environnement
- Hashage des mots de passe
- Validation Pydantic sur tous les endpoints
- Protection contre l'injection SQL
- Gestion des erreurs sécurisée
- Authentification JWT

### 5. `performance_validation.sh`
**Description** : Contrôle les optimisations de performance  
**Vérifie** :
- Index de base de données appropriés
- Pagination des listes de données
- Absence de requêtes N+1
- Context Caching Gemini (obligatoire)
- Rate limiting sur les appels API
- Logging structuré pour monitoring
- Optimisations frontend (DOM, événements)

### 6. `i18n_validation.sh`
**Description** : Valide l'approche anglais-first et la préparation i18n  
**Vérifie** :
- Textes UI en anglais uniquement
- Messages d'erreur en anglais
- URLs en anglais
- Structure prête pour traductions futures
- Gestion des locales
- **Exception** : Les prompts IA peuvent être en langues cibles

## 🚀 Utilisation

### Validation Complète
```bash
# Depuis la racine du projet
./.claude/hooks/validate_best_practices.sh
```

### Validation Spécifique
```bash
# Architecture seulement
./.claude/hooks/architecture_validation.sh

# Sécurité seulement  
./.claude/hooks/security_validation.sh

# etc.
```

## 📊 Codes de Sortie

- **0** : Validation réussie ✅
- **1** : Validation échouée ❌

## 🔧 Intégration avec Claude Code

Ces hooks peuvent être intégrés dans votre workflow de développement :

1. **Avant commit** : Validation automatique
2. **CI/CD Pipeline** : Contrôle qualité
3. **Code Review** : Vérification des standards
4. **Development** : Validation continue pendant le développement

## 📝 Règles Principales (SPEC.md)

### Architecture
- ✅ Architecture hexagonale obligatoire
- ✅ Séparation domain / adapters / infrastructure
- ✅ FastAPI + PostgreSQL + SQLAlchemy + Poetry

### Nommage  
- ✅ Tout en anglais (variables, classes, tables, routes)
- ✅ Exception : prompts IA en langues cibles
- ✅ snake_case pour variables et colonnes
- ✅ PascalCase pour classes
- ✅ kebab-case pour routes

### Sécurité
- ✅ Pas de secrets hardcodés
- ✅ Variables d'environnement obligatoires
- ✅ Validation Pydantic sur tous les endpoints
- ✅ Authentification JWT

### Performance
- ✅ Context Caching Gemini (TTL 6-24h)
- ✅ Rate limiting API Gemini
- ✅ Pagination avec limit() et offset()
- ✅ Index de base de données

### UI/Frontend
- ✅ Bootstrap uniquement (composants, couleurs, animations)
- ✅ JavaScript ES6 vanilla
- ✅ Pas de frameworks CSS personnalisés

## 🔍 Dépannage

Si une validation échoue :

1. **Lisez le message d'erreur** : Il indique précisément le problème
2. **Consultez SPEC.md** : Section correspondante pour les détails
3. **Corrigez le code** : Respectez les conventions
4. **Re-exécutez** : `./validate_best_practices.sh`

## 📚 Référence

Pour plus de détails sur les bonnes pratiques, consultez :
- `SPEC.md` - Guide complet des bonnes pratiques
- `CLAUDE.md` - Guide pour les instances Claude Code

---

**Maintenu par** : Équipe FIA v3.0  
**Dernière mise à jour** : Compatible avec les exigences SPEC.md