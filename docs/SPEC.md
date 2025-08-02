# Voici le fonctionnement actuel de l'app du point de vue utilisateur

## La vue du côté formateur
- Un formateur peut creer un compte sur /register.html (email, mot de passe, nom et prenom) puis se logguer sur /login.html
- Il peut accéder à son dashboard via l'url trainer.html
- Sur trainer.html 
    - Il a un onglet pour créer et visualiser ses formations (ou créer des formations full IA en .md) : nom, description et charger un supprt pdf ou powerpoint qui sera stocké dans son format natif pdf ou powerpoint dans la base de donnee
    - Il a un onglet pour créer des sessions pour les apprenants qui génère un lien qu'il enverra par email aux apprenants

## La vue du côté de l'apprenant
- Quand une session est créée par le formateur, un lien de session est généré et est envoyé à l'apprenant par email
- L'apprenant clique sur le lien est arrive sur une page ou on lui pose des questions pour créer son profil que l'on enregister en BD (email, niveau, poste occupé et secteur d'activité, objectifs/attentes, durée de la formation  et langue)

- Une fois répondu à ces questions, on utilise vertexAI pour generer un plan de formation personnalisé au profil de l'apprenant basé sur 5 étapes
- Chaque étape est structurée de la manière suivante : un ou plusiurs modules qui contient un ou plusieurs sous-modules qui contient un ou plusieurs slides : on ne genere que la structure du plan "Étapes → Modules → Sous-modules" pas les slides car ils sont génrés en temps reel en fonction du profil de l'apprenant.
Etape
├── Module 1
│   ├── Sous-module 2.1
│   │   ├── Slide 1
│   │   ├── Slide 2
│   │   └── Slide 3
│   └── Sous-module 2.2
│       ├── Slide 1
│       └── Slide 2
└── Titre 2
    └── Sous-titre 2.1
        ├── Slide 1
        └── Slide 2

- L'apprenant arrive sur le premier slide de la formation généré en markdown avec une mise en forme Marked.js.
- L'apprenant peut aller sur la slide suivante (cela génère la slide) ou revenir en arrière sur les slides deja generée. On ne regénère pas une slide existante dans la BD.
- L'apprenant peut poser des quesions au formateur ia via le chat en texte, via le micro ou avec Live API pour une discussion naturelle.
- Il peut utiliser des actions pré-définie via des boutons au dessus du champ de saisie.
L'IA repond aux questions ou message de l'apprenant en se basant sur le contenu du slide (training_slides) et le profil de l'apprenant (learner_sessions).
- IA analyse chaque conversation pour enrichir automatiquement le profil de l'apprenant et personnaliser les slides futurs.
- L'apprenant a les options suivantes pour agir sur les slides : simplifier,  approfondir, générer une image et générer des graphiques

## La vue côté administrateur
- Les logs affichent tous les appels et les réponses à l'api gemini via Vertex AI (important!) de tel manière à ce qu'ils soient facile à lire dans le reste des logs 

## Les principaux composants
- Authentification et Gestion des Comptes
- Gestion des Formations
- Gestion des Sessions d'Apprentissage
- Intelligence Artificielle - Génération de Contenu
- Structure Pédagogique Adaptative

---------------------------------------------------------------------------------------------------------------

# Guide des Bonnes Pratiques à respecter pour le développement
## 🏗️ Architecture et Organisation
### Principes Fondamentaux
- **Principe KISS** : Toujours choisir la solution la plus simple et directe
- **Boy Scout Rule** : Toujours laisser le code plus propre qu'on ne l'a trouvé
- **Responsabilité unique** : Un module = une responsabilité
- **Architecture modulaire** : Organiser le code FastAPI en modules distincts (routes, modèles, services, configuration)
- **Architecture hexagonale** : Séparation claire entre logique métier, adapters et infrastructure
- **HTML** : Interdiction d’inclure du JavaScript via <script> et du CSS via <style> dans les fichiers HTML : utiliser uniquement des fichiers externes

- **ArClaude 4 hooks** : Mise en place et activation des hooks claude 4 avant de demarrer le code

### Stack Technologique Obligatoire
- **Backend** : FastAPI + PostgreSQL + SQLAlchemy + Alembic + Poetry
- **Architecture** : Architecture hexagonale avec séparation des couches
- **Serveur** : FastAPI server
- **Authentification & Sessions** : FastAPI-Users pour la gestion des sessions formateurs et apprenants + JWT
- **IA** : VertexAI
- **Frontend** : HTML5/CSS3/JavaScript ES6 vanilla (pas de <script> ou <style> dans le HTML, uniquement des fichiers externes)
- **UI** : Bootstrap + Bootstrap Icons uniquement
- **Infrastructure** : Railway (déploiement) + GitHub (versioning)

## 🌐 Internationalisation (i18n) - Approche Pragmatique
### Langue par Défaut : Anglais First (avec Tolérance)
- **OBJECTIF** : Toute l'application développée en anglais par défaut
- **TOLÉRANCE** : Loupés occasionnels acceptables si fonctionnalité préservée
- **PRIORITÉ** : Fonctionnalité > Purisme linguistique

### Règles de Nommage Assouplies
#### 🟢 Termes Anglais Acceptés (Pas de flaggage)
- session, training, profile, module, user, learner, trainer
- Routes : /api/sessions, /api/training, /api/learners 
- Tables : training_sessions, learner_sessions, user_profiles
- Variables : session_id, training_plan, learner_profile

#### 🔴 Termes Français à Éviter (Hooks détectent)
- formateur, apprenant, formation, cours, utilisateur
- Routes : /api/formateurs, /api/formations
- Tables : formateurs, formations, apprenants
- Variables : formateur_id, plan_formation

### Exceptions Acceptées
- **Prompts IA** : Langues cibles (français pour tests, anglais prod)
- **Comments** : Français acceptable temporairement
- **Tests** : Variables françaises tolérées
- **Logs** : Messages français acceptables
- **Documentation** : SPEC.md peut rester en français

### Architecture i18n
- OBLIGATION : Prévoir l'architecture i18n dès le début pour traduction future
- Messages système : En anglais avec support i18n pour extension ultérieure
- Contenu formation : Reste dans la langue du PDF/PPT source (français pour les tests)
- Interface utilisateur : Labels et textes en anglais uniquement pour MVP
- Fichiers de traduction : Structure prête pour ajout de langues (fr, es, de, etc.)

### Conventions de Nommage Anglais
- Tables : snake_case anglais (ex: training_sessions, chat_messages, device_sessions)
- Colonnes : snake_case anglais (ex: email_captured_at, payment_completed_at, engagement_history)
- Classes : PascalCase anglais (ex: TrainingSession, LearnerSession, ChatMessage)
- Variables : snake_case anglais (ex: session_id, current_slide, engagement_level)
- Routes : kebab-case anglais (ex: /api/training-sessions, /capture-email, /create-payment)

## 📁 Structure du Projet
### Organisation Backend - Architecture Hexagonale
```
backend/
├── app/
│   ├── main.py
│   ├── domain/            # Logique métier pure
│   │   ├── entities/      # Entités métier
│   │   ├── ports/         # Interfaces (repositories, services)
│   │   └── services/      # Services métier
│   ├── adapters/          # Couche d'adaptation
│   │   ├── inbound/       # API, controllers
│   │   ├── outbound/      # Database, Gemini, external APIs
│   │   └── repositories/  # Implémentations repositories
│   ├── infrastructure/    # Configuration, database, sécurité
│   └── utils/             # Utilitaires
├── alembic/               # Migrations
└── pyproject.toml         # Configuration Poetry
```

### Organisation Frontend
```
frontend/
├── public/            # Pages HTML
├── src/
│   ├── components/    # Composants réutilisables
│   ├── styles/        # CSS modulaire
│   └── utils/         # Utilitaires JS
```

## 🔧 Configuration et Sécurité
### Variables d'Environnement
- **INTERDICTION ABSOLUE** : Jamais de valeurs hardcodées dans le code
- **OBLIGATION** : Centraliser toute la configuration avec des variables d'environnement
- **JAMAIS** stocker les mots de passe en clair
- **TOUJOURS** utiliser le hashage pour les mots de passe

### Gestion des Erreurs
- **JAMAIS** exposer d'informations sensibles dans les messages d'erreur
- **TOUJOURS** logger les erreurs détaillées côté serveur uniquement
- Messages d'erreur génériques pour l'utilisateur final

## 🗄️ Gestion des Données
### Modèles et Base de Données
- **OBLIGATION** : Définir des modèles cohérents entre Pydantic et PostgreSQL
- **OBLIGATION** : Utiliser des conventions de nommage claires et uniformes
- **OBLIGATION** : Valider toutes les données entrantes avec Pydantic
- **OBLIGATION** : Gérer les migrations avec Alembic
- **OBLIGATION** : Créer des schémas précis pour les requêtes et réponses API

### Conventions de Nommage
- **Tables** : snake_case anglais
- **Colonnes** : snake_case anglais
- **Classes** : PascalCase anglais
- **Variables** : snake_case anglais
- **Routes** : kebab-case anglais 

## ⚡ Performance et Scalabilité
### Optimisation Obligatoire
- **OBLIGATION** : Utiliser des index appropriés en base de données
- **OBLIGATION** : Optimiser les requêtes SQL et éviter les requêtes N+1
- **OBLIGATION** : Paginer toutes les listes de données avec `limit()` et `offset()`
- **OBLIGATION** : Utiliser le Context Caching de Gemini (TTL 6-24 heures)
- **OBLIGATION** : Surveiller les performances et l'utilisation des ressources
- **OBLIGATION** : Implémenter le rate limiting sur les appels API Gemini

### Cache et Performance
- Implémenter une stratégie de cache pour les données fréquentes
- Utiliser le Context Caching de Gemini pour les formations
- Pas de Redis nécessaire (uniquement Context Cache Gemini)

## 🤖 Intégration IA
### Gemini Flash 2.5 via Vertex AI ou SDK si besoin
- **OBLIGATION** : Utiliser Context Caching avec TTL 6-24 heures
- **OBLIGATION** : Utiliser Structured Output JSON
- **OBLIGATION** : Appels API séparés (conversation vs analyse d'engagement)
- **OBLIGATION** : Rate limiting sur les appels API Gemini

## 🎨 Frontend et Interface
### Standards UI
- **OBLIGATION** : Utiliser uniquement les composants, couleurs, effets et animations standard de Bootstrap
- **OBLIGATION** : Utiliser Bootstrap Icons
- **OBLIGATION** : Architecture composants réutilisables en JavaScript ES6

## 🛠️ Développement et Maintenance
### Workflow Poetry
- **OBLIGATION** : Toutes les commandes Poetry depuis le dossier `backend/`
- **OBLIGATION** : Utiliser Poetry pour la gestion des dépendances et environnement

### Documentation
- **OBLIGATION** : Documenter l'API avec les outils intégrés FastAPI
- **OBLIGATION** : Maintenir une documentation claire pour l'équipe
- **OBLIGATION** : Implémenter un système de logging structuré

### Versioning et Déploiement
- **OBLIGATION** : Planifier le versioning de l'API dès le début
- **OBLIGATION** : Utiliser Claude Dev Hook pour formatage automatique et imports
- **OBLIGATION** : Déploiement exclusivement sur Railway
- **OBLIGATION** : Versioning sur GitHub

## 🔒 Sécurité et Validation
### Authentification
- **OBLIGATION** : Implémenter une authentification robuste avec JWT
- **OBLIGATION** : Valider et sanitiser toutes les données utilisateur côté backend
- **OBLIGATION** : Ne jamais faire confiance aux données frontend

### Validation des Données
- **OBLIGATION** : Validation Pydantic pour tous les endpoints POST/PUT/PATCH
- **OBLIGATION** : Schémas précis pour toutes les requêtes et réponses
- **OBLIGATION** : Gestion centralisée des erreurs

## 🔧 Claude Code Hooks - Validation Automatique
### Configuration et Activation
- **OBLIGATION** : Hooks Claude Code actifs pour validation temps réel
- **AUTORISATION** : Mode non-bloquant pour développement itératif
- **EXCEPTION** : Hooks peuvent être contournés temporairement si nécessaire

### Scripts de Validation Disponibles
```bash
# Validation complète (2 minutes) - avant commits importants
./.claude/hooks/validate_best_practices.sh

# Test rapide (5 secondes) - pendant développement itératif  
./.claude/hooks/test_hooks_quick.sh

# Tests modulaires par domaine
./.claude/hooks/architecture_validation.sh
./.claude/hooks/naming_conventions.sh
./.claude/hooks/performance_validation.sh
./.claude/hooks/security_validation.sh
./.claude/hooks/i18n_validation.sh
```

### Niveaux de Sévérité des Violations
#### 🔴 Violations Critiques (À corriger prioritairement)
- Imports infrastructure dans domain layer
- Services/controllers dupliqués (confusion imports)
- Secrets hardcodés dans le code
- Authentification cassée

#### 🟡 Violations Importantes (À planifier)
- Absence pagination (limit/offset)
- Absence index database
- Imports FastAPI dans domain
- Architecture hexagonale non respectée

#### 🟢 Violations Mineures (Tolérables temporairement)
- Termes français dans commentaires/prompts
- Variables non-anglaises dans tests
- Logs en français (acceptable selon SPEC)

### Workflow Développement avec Hooks
#### Phase Développement Itératif
1. **Codage** : Hooks non-bloquants actifs automatiquement
2. **Test rapide** : `test_hooks_quick.sh` à chaque étape
3. **Validation** : Corriger violations critiques immédiatement
4. **Tolérance** : Violations mineures acceptables temporairement

#### Phase Pré-Production
1. **Validation complète** : `validate_best_practices.sh`
2. **Correction prioritaire** : Violations critiques et importantes
3. **Documentation** : Justification violations mineures acceptées
4. **Tests** : Vérification fonctionnelle après corrections

### Philosophie : Pragmatisme vs Perfectionnisme
- **PRIORITÉ 1** : Fonctionnalité et stabilité
- **PRIORITÉ 2** : Architecture et bonnes pratiques
- **PRIORITÉ 3** : Purisme linguistique et cosmétique
- **PRINCIPE** : "Mieux vaut du code qui marche en français que du code qui plante en anglais"

**Objectif** : Code maintenable, évolutif et performant avec validation continue
