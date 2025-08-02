# 🔧 PLAN DE REFACTORISATION SMART KISS
## FIA v3.0 - Architecture Hexagonale Compliance

### 📊 ÉTAT ACTUEL (Analyse Hooks)
```
Score Refactorisation: 37/100
• 3 Violations Critiques (30 points) 🔴
• 1 Violation Importante (5 points) 🟡  
• 2 Violations Mineures (2 points) 🟢

Stratégie: URGENT - Refactorisation nécessaire
```

---

## 🎯 STRATÉGIE GLOBALE : DÉVELOPPEMENT PARALLÈLE

### **Principe KISS** : **K**eep **I**t **S**imple, **S**tupid
1. **Isoler** les composants indépendants
2. **Tester** chaque composant individuellement  
3. **Migrer** progressivement sans casser l'existant
4. **Valider** avec hooks à chaque étape

### **Approche Zero-Downtime**
- ✅ Application continue de fonctionner
- ✅ Tests intermédiaires à chaque phase
- ✅ Rollback possible à tout moment
- ✅ Validation hooks automatique

---

## 📅 PLAN EN 4 PHASES (8-12 semaines)

### **PHASE 1: SAFE CHANGES (Semaine 1-2) - Risque 0%**
*Corrections sans impact fonctionnel*

#### 1.1 Naming Conventions (3 jours)
```bash
Hook: ./.claude/hooks/naming_conventions.sh
Cible: 16 fichiers avec termes français
Risque: 0% (cosmétique)
```

**Actions:**
- [ ] Remplacer variables `formateur` → `trainer` dans comments
- [ ] Logs français → anglais (messages utilisateur)
- [ ] Documentation interne → anglais
- [ ] Tests variables françaises → anglaises

**Validation:**
```bash
# Before
./.claude/hooks/naming_conventions.sh
# Expected: ❌ 16 fichiers French terms

# After  
./.claude/hooks/naming_conventions.sh
# Expected: ✅ 0-3 fichiers French terms (acceptable)
```

#### 1.2 Database Performance (5 jours)
```bash
Hook: ./.claude/hooks/performance_validation.sh
Cible: Pagination + Index manquants
Risque: 5% (ajouts uniquement)
```

**Actions:**
- [ ] Ajouter `.limit()` `.offset()` dans repositories (8 fichiers)
- [ ] Créer migration index database (10 index critiques)
- [ ] Tests performance avant/après

**Tests Intermédiaires:**
```bash
# Test pagination
curl "/api/trainings?limit=10&offset=0"
# Test performance requêtes
EXPLAIN ANALYZE SELECT * FROM training_sessions WHERE trainer_id = ?
```

---

### **PHASE 2: MODERATE CHANGES (Semaine 3-5) - Risque 15%**
*Corrections avec tests requis*

#### 2.1 Domain Layer Cleanup (7 jours)
```bash
Hook: ./.claude/hooks/architecture_validation.sh  
Cible: 5 domain services avec imports infrastructure
Risque: 15% (refactoring imports)
```

**Approche Incremental:**
1. **Créer ports manquants** (2 jours)
   ```python
   # Nouveau: app/domain/ports/settings_port.py
   class SettingsPort:
       def get_setting(self, key: str) -> str
   
   # Nouveau: app/adapters/outbound/settings_adapter.py  
   class SettingsAdapter(SettingsPort):
       def get_setting(self, key: str) -> str:
           return settings.get(key)
   ```

2. **Refactorer service par service** (5 jours)
   ```python
   # AVANT: domain/services/ai_training_generation_service.py
   from app.infrastructure.settings import settings
   
   # APRÈS: domain/services/ai_training_generation_service.py
   def __init__(self, settings_port: SettingsPort):
       self.settings = settings_port
   ```

**Tests Continus:**
```bash
# Après chaque service refactoré
python -m pytest tests/test_domain/ -v
./.claude/hooks/test_hooks_quick.sh
```

#### 2.2 FastAPI Dependencies Isolation (3 jours)
```bash
Cible: app/domain/schemas/user.py
Risque: 20% (authentification)
```

**Actions:**
- [ ] Créer schemas domain purs (sans FastAPI-Users)
- [ ] Adapter schemas existants dans infrastructure
- [ ] Tests authentification complets

---

### **PHASE 3: RISKY CHANGES (Semaine 6-9) - Risque 40%**
*Développement parallèle requis*

#### 3.1 Services Duplication Resolution (14 jours)
```bash
Cible: backend/app/services/ vs backend/app/domain/services/
Risque: 95% (imports conflicts)
Approche: Développement parallèle OBLIGATOIRE
```

**Étapes Critiques:**

1. **Analyse Dépendances** (3 jours)
   ```bash
   # Script analyse imports
   grep -r "from app.services" backend/app/
   grep -r "from app.controllers" backend/app/
   # Mapping complet dépendances
   ```

2. **Développement Parallèle** (8 jours)
   ```bash
   # Créer branche dédiée
   git checkout -b refactor/services-consolidation
   
   # Nouvelle structure unifiée
   backend/app/domain/services/ (SEULE source vérité)
   backend/app/adapters/inbound/ (SEULS controllers)
   ```

3. **Migration Progressive** (3 jours)
   ```bash
   # Migrer imports un par un
   # Tests après chaque migration
   # Rollback si échec
   ```

**Tests Régression Intensive:**
```bash
# Full app tests
poetry run python -c "from app.main import app; print('✅ App starts')"
curl -f http://localhost:8000/docs || echo "❌ API broken"
```

#### 3.2 Controllers Unification (7 jours)
```bash
Cible: backend/app/controllers/ → backend/app/adapters/inbound/
Risque: 60% (routes conflicts)
```

**Actions:**
- [ ] Migrer `plan_generation_controller.py` → `adapters/inbound/`
- [ ] Tester routes `/api/plan-generation/*`
- [ ] Supprimer dossier `controllers/` legacy

---

### **PHASE 4: VALIDATION & CLEANUP (Semaine 10-12) - Risque 5%**
*Finalisation et optimisation*

#### 4.1 Architecture Compliance (7 jours)
```bash
Objectif: Domain Purity 90%+
Hook: ./.claude/hooks/architecture_validation.sh
```

**Validation Finale:**
```bash
# Score avant refactorisation
./.claude/hooks/refactoring_priority.sh
# Score: 37/100 (3 critiques, 1 important, 2 mineurs)

# Score après refactorisation (objectif)
./.claude/hooks/refactoring_priority.sh  
# Score: 5/100 (0 critiques, 0 importants, 5 mineurs)
```

#### 4.2 Performance & Security (7 jours)
- [ ] Tests performance complets
- [ ] Audit sécurité hooks
- [ ] Documentation refactorisation

---

## 🛠️ OUTILS DE VALIDATION

### **Hooks Spécialisés**
```bash
# Quick check pendant développement (5s)
./.claude/hooks/test_hooks_quick.sh

# Analyse refactorisation priorités
./.claude/hooks/refactoring_priority.sh

# Validation complète avant commit
./.claude/hooks/validate_best_practices.sh
```

### **Tests Intermédiaires Automatisés**
```bash
# Test app startup
make test-startup

# Test API health  
make test-api

# Test domain purity
make test-architecture

# Test performance
make test-performance
```

---

## 📈 MÉTRIQUES DE SUCCÈS

### **Avant Refactorisation**
```
Domain Purity: 0%
Services Dupliqués: 2 directories  
Controllers Mixtes: 2 structures
Imports Infrastructure: 5 violations
Score Refactorisation: 37/100
```

### **Après Refactorisation (Objectif)**
```
Domain Purity: 90%+
Services Dupliqués: 0 directories
Controllers Unifiés: 1 structure hexagonale
Imports Infrastructure: 0 violations  
Score Refactorisation: <10/100
```

### **KPIs Fonctionnels**
- ✅ Application démarre sans erreur
- ✅ Toutes les routes répondent
- ✅ Authentification fonctionnelle
- ✅ Génération IA opérationnelle
- ✅ Base de données accessible
- ✅ Tests passent à 100%

---

## 🚨 PLAN DE CONTINGENCE

### **Si Phase 3 Échoue (Services/Controllers)**
1. **Rollback complet** vers structure actuelle
2. **Tolérer violations** temporairement
3. **Focus Phase 1+2** uniquement
4. **Reporter Phase 3** à version ultérieure

### **Détection Problème**
```bash
# Si hooks détectent régression
./.claude/hooks/test_hooks_quick.sh
# Exit code != 0 → STOP refactorisation

# Si app plante
curl -f http://localhost:8000/health || ROLLBACK
```

### **Critères STOP Immédiat**
- Application ne démarre plus
- Routes critiques cassées (`/api/auth/*`, `/api/sessions/*`)
- Base de données inaccessible  
- Tests tombent < 80% passage

---

## 💡 RECOMMANDATION FINALE

**Commencer par PHASE 1 immédiatement** : Risque 0%, bénéfice immédiat

Les hooks identifient précisément les problèmes et guident la refactorisation. Approche incrémentale avec validation continue garantit succès sans casser l'existant.

**Next Steps:**
```bash
# 1. Lancer analyse actuelle
./.claude/hooks/refactoring_priority.sh

# 2. Commencer Phase 1.1 Naming
git checkout -b refactor/phase1-naming

# 3. Valider hooks après chaque change
./.claude/hooks/test_hooks_quick.sh
```