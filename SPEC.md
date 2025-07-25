# Voici le fonctionnement actuel de l'app du point de vue utilisateur

## La vue du côté formateur
- Un formateur peut creer un compte sur /register.html (email, mot de passe, nomet prenom) puis se logguer sur /login.html
- Il peut accéder à son dashboard via l'url trainer.html
- Sur trainer.html 
    - Il a un onglet pour créer des formations : nom, description et charger un supprt pdf ou powerpoint qui sera insere dans la base de données au  format brute
    - Il a un onglet pour créer des sessions pour les apprenants qui génère un lien qu'il enverra par email aux apprenants
    - Il peut mettre à jour son profil via l'onglet "Profile"

## La vue du côté de l'apprenant
- Quand une session est créée par le formateur, un lien de session est généré et est envoyé à l'apprenant par email
- L'apprenant clique sur le lien est arrive sur une page ou on lui pose des questions pour créer son profil que l'on enregister en BD (email, niveau, style d'apprentissage, poste occupé, secteur d'activité, pays de résidence et langue (par defaut la langue du navigateur))
- Une fois répondu à ces questions, on appelle l'api gemini flash 2.0 pour generer un plan de formation personnalisé au profil de l'apprenant basé sur le format brute du support de formation
- Une fois le plan de formation créé, les 2 premieres slides sont creees
- L'apprenant est alors redirigé sur la premiere slide
- L'apprenant visualise alors le premier slide (le 2e etant deja genere pour eviter les latences quand on passe d'un slide à l'autre)
- Quand l'utilisateur avance sur le slide suivant, on genere le slide n + 1
- L'interface desktop de l'apprenant est la suivante : au centre le contenu du slide (75% de la largeur) et à droite un chat pour poser des questions au formateur IA gemini (25% de la largeur)
- Il peut avancer et reculer dans les slides (tous les slides générés etant enregistré dans la base de données)
- Il peut poser des quesions au formateur ia via le chat qui repond à la question en se basant sur le contenu du slide et le profil de l'apprenant
- Pour chaque session on doit pouvoir enregistrer le nombre de slide vue par l'apprenant, le temps passé et les messages envoyés au formateur ia gemini

## La vue côté administrateur
- Les logs affichent tous les appels et les réponses à l'api gemini de tel manière à ce qu'ils soient facile à lire dans le reste des logs 

---------------------------------------------------------------------------------------------------------------

# Guide des Bonnes Pratiques à respecter pour le développement

## 🏗️ Architecture et Organisation
### Principes Fondamentaux
- **Principe KISS** : Toujours choisir la solution la plus simple et directe
- **Boy Scout Rule** : Toujours laisser le code plus propre qu'on ne l'a trouvé
- **Responsabilité unique** : Un module = une responsabilité
- **Architecture modulaire** : Organiser le code FastAPI en modules distincts (routes, modèles, services, configuration)
- **Architecture hexagonale** : Séparation claire entre logique métier, adapters et infrastructure

### Stack Technologique Obligatoire
- **Backend** : FastAPI + PostgreSQL + SQLAlchemy + Alembic + Poetry
- **Architecture** : Architecture hexagonale avec séparation des couches
- **Serveur** : FastAPI server
- **Authentification & Sessions** : FastAPI-Users pour la gestion des sessions formateurs et apprenants + JWT
- **IA** : Google Gemini Flash 2.0 avec Context Caching et Structured Output
- **Frontend** : HTML5/CSS3/JavaScript ES6 vanilla
- **UI** : Bootstrap + Bootstrap Icons uniquement
- **Infrastructure** : Railway (déploiement) + GitHub (versioning)

## 🌐 Internationalisation (i18n)
### Langue par Défaut : Anglais First
- OBLIGATION : Toute l'application développée en anglais par défaut
- Libellés UI : Tous les textes d'interface en anglais
- Variables : Noms de variables en anglais uniquement
- URLs : Toutes les routes en anglais (ex: /api/trainers, /api/sessions)
- Tables : Noms de tables en anglais (ex: trainers, training_sessions, learner_sessions)
- Champs BDD : Noms de colonnes en anglais (ex: first_name, created_at, session_type)
- Endpoints : Noms d'endpoints en anglais (ex: /create-session, /capture-email)
- Constantes : Toutes les constantes en anglais (ex: SESSION_TYPE_B2B, ENGAGEMENT_LEVEL_HIGH)
- Prompt : Les prompts font exception à la règle : ils sont dans les langues cibles de l'app (français, anglais, etc.)

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
### Gemini Flash 2.0
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

**Objectif** : Code maintenable, évolutif et performant



# 🚀 Stratégie de Développement - Étapes avec Interface pour Tests

## 📋 **Phase 1: Setup & Infrastructure (Jour 1)**

### Étapes Backend
- Créer repository GitHub avec .gitignore
- Initialiser Poetry dans backend/
- Créer structure dossiers architecture hexagonale
- Configurer variables d'environnement
- Setup Railway de base

### Étapes Frontend
- Créer structure frontend/ avec dossiers
- Setup page index.html basique avec Bootstrap
- Créer fichier CSS/JS de base

### Tests Phase 1 (Manuel Interface)
- Accéder à index.html → page s'affiche
- Bootstrap CSS/JS chargés → styles appliqués
- Variables d'environnement → affichage status dans page test

---

## 🗄️ **Phase 2: Base de Données & Modèles (Jour 1-2)**

### Étapes Backend
- Configurer connexion PostgreSQL
- Créer modèles SQLAlchemy
- Définir schemas Pydantic
- Créer migration Alembic initiale
- Implémenter repositories

### Étapes Frontend
- Créer pages register.html et login.html
- Formulaires Bootstrap basiques
- Scripts JS pour validation frontend

### Tests Phase 2 (Manuel Interface)
- Pages register/login → formulaires s'affichent
- Validation JS → messages d'erreur frontend
- Migration BDD → vérifier tables créées
- Test connexion → page status BDD

---

## 🔌 **Phase 3: Auth & Endpoints Core (Jour 2-3)**

### Étapes Backend
- Configurer FastAPI-Users
- Endpoints authentification (/register, /login)
- Middleware authentification
- Endpoints upload training

### Étapes Frontend
- Intégrer appels API dans register/login
- Page trainer.html avec onglets Bootstrap
- Formulaire upload PDF/PPT
- Messages success/error

### Tests Phase 3 (Manuel Interface)
- **register.html** → créer compte formateur
- **login.html** → connexion formateur
- **trainer.html** → accès après login
- **Upload PDF** → via interface, voir fichier en BDD
- **Déconnexion** → redirection vers login

---

## 🎯 **Phase 4: Sessions & Interface Apprenant (Jour 3-4)**

### Étapes Backend
- Endpoint création session training
- Endpoint accès session par token
- Endpoint sauvegarde profil apprenant

### Étapes Frontend
- **trainer.html** → onglet "Créer Session" fonctionnel
- **session/{token}/profile.html** → formulaire profil apprenant
- Navigation entre pages
- Affichage liens sessions générés

### Tests Phase 4 (Manuel Interface)
- **Créer session** → lien généré dans trainer.html
- **Cliquer lien** → accès page profil apprenant
- **Remplir profil** → données sauvegardées
- **Test token invalide** → page erreur

---

## 🤖 **Phase 5: Intégration Gemini (Jour 4-5)**

### Étapes Backend
- Service Gemini avec Context Caching
- Rate limiting
- Génération plan personnalisé
- Génération slides background

### Étapes Frontend
- Page loading après profil
- Affichage plan généré
- Page slides avec navigation
- Interface basique chat (25% largeur)

### Tests Phase 5 (Manuel Interface)
- **Après profil** → loading puis plan affiché
- **Navigation slides** → avancer/reculer fonctionne
- **Chat basique** → envoyer message test
- **Performance** → mesurer temps génération
- **Erreur Gemini** → message d'erreur utilisateur

---

## 🎨 **Phase 6: Interface Slides Complète (Jour 5-6)**

### Étapes Frontend
- Interface slides 75% + chat 25%
- Chat temps réel avec formateur IA
- Progression visuelle
- Navigation clavier
- Responsive mobile

### Étapes Backend
- Endpoint chat avec contexte slide
- Tracking temps par slide
- Sauvegarde progression

### Tests Phase 6 (Manuel Interface)
- **Layout slides** → 75%/25% correct sur desktop
- **Chat IA** → réponses contextuelles au slide
- **Navigation** → flèches clavier fonctionnent  
- **Mobile** → interface utilisable sur téléphone
- **Progression** → barre progression mise à jour

---

## 📊 **Phase 7: Analytics & Dashboard (Jour 6-7)**

### Étapes Backend
- Endpoints analytics détaillés
- Logging structuré
- Health checks

### Étapes Frontend
- **trainer.html** → onglet analytics avec graphiques
- Affichage stats par formation
- Dashboard temps réel
- Export données

### Tests Phase 7 (Manuel Interface)
- **Dashboard analytics** → stats s'affichent
- **Graphiques** → données temps réel
- **Export** → téléchargement CSV
- **Logs** → visibles côté admin
- **Performance** → métriques tableau de bord

---

## 🚀 **Phase 8: Production & Tests Finaux (Jour 7)**

### Étapes Déploiement
- Configuration production Railway
- HTTPS et domaine
- Monitoring logs

### Tests Production (Manuel Interface)
- **Parcours complet formateur** → création à analytics
- **Parcours complet apprenant** → profil à fin formation
- **Performance** → temps réponse acceptable
- **Sécurité** → tentatives accès non autorisé
- **Mobile** → tous écrans fonctionnels

---

## 🧪 **Plan de Tests par Phase**

### Tests Systématiques à Faire
**Phase 3** : Tester auth via interface uniquement
**Phase 4** : Tester création/accès sessions via interface
**Phase 5** : Tester génération contenu via interface  
**Phase 6** : Tester expérience learning complète
**Phase 7** : Tester dashboard formateur complet

### Scenarios Tests Manuels
- **Happy path** : Parcours sans erreur
- **Error path** : Tester erreurs utilisateur
- **Edge cases** : Fichiers volumineux, connexion lente
- **Security** : Tentatives accès non autorisé
- **Performance** : Mesurer temps réponse réels

### Validation avant Phase Suivante
- Interface fonctionnelle pour tester la phase
- Aucun bug bloquant utilisateur
- Performance acceptable via interface
- Messages d'erreur clairs pour utilisateur