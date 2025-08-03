# 🛠️ Debug Interface Introduction Popovers - FIA v3.0

Ce guide vous aide à tester et déboguer le système de popovers d'introduction d'interface.

## 🚀 Méthodes de Test Disponibles

### 1. Page de Debug Dédiée (`debug-popovers.html`)

Ouvrez dans votre navigateur : `http://localhost/fia-v3.0/frontend/debug-popovers.html`

**Fonctionnalités :**
- Interface de test complète avec tous les éléments de training.html
- Boutons de test pour chaque fonction
- Console de debug intégrée
- Tests Bootstrap, import composant, storage

### 2. Commandes Console (training.html)

Ouvrez `training.html` et utilisez la console du navigateur (F12) :

```javascript
// Tester Bootstrap
window.debugPopovers.testBootstrap()

// Vérifier tous les éléments d'interface
window.debugPopovers.checkElements()

// Forcer l'affichage des popovers
window.debugPopovers.forceShow()

// Masquer tous les popovers
window.debugPopovers.hideAll()

// Reset complet de l'état
window.debugPopovers.reset()

// Simuler un slide "plan"
window.debugPopovers.simulatePlanSlide()

// Inspecter l'état du système
window.debugPopovers.inspect()

// Test complet automatique
window.debugPopovers.fullTest()
```

## 🔍 Diagnostic des Problèmes Courants

### Problème 1: Popovers ne s'affichent pas

**Étapes de diagnostic :**

1. **Vérifier Bootstrap :**
   ```javascript
   window.debugPopovers.testBootstrap()
   ```
   ✅ Doit retourner `true` et afficher les infos Bootstrap

2. **Vérifier les éléments DOM :**
   ```javascript
   window.debugPopovers.checkElements()
   ```
   ✅ Tous les éléments doivent être trouvés (9/9)

3. **Vérifier LocalStorage :**
   ```javascript
   localStorage.getItem('fia_interface_intro_completed')
   ```
   ❌ Si `"true"`, reset avec `window.debugPopovers.reset()`

4. **Forcer l'affichage :**
   ```javascript
   window.debugPopovers.forceShow()
   ```

### Problème 2: slide_type="plan" non détecté

**Test de simulation :**
```javascript
window.debugPopovers.simulatePlanSlide()
```

**Vérifier dans les logs :**
- `🎯 [INTERFACE-INTRO] SLIDE TYPE "PLAN" DÉTECTÉ !`
- `🚀 [INTERFACE-INTRO] Démarrage import du composant...`

### Problème 3: Import du composant échoue

**Vérifier les chemins :**
- Le fichier existe : `frontend/src/components/interface-introduction-popovers.js`
- Le chemin d'import est correct dans `slide-content-manager.js`

**Test d'import manuel :**
```javascript
import('./src/components/interface-introduction-popovers.js')
  .then(module => console.log('✅ Import OK:', module))
  .catch(error => console.error('❌ Import failed:', error))
```

## 📊 Points de Contrôle Système

### 1. Bootstrap Configuration
- ✅ Bootstrap 5.3.2 chargé
- ✅ `bootstrap.Popover` disponible
- ✅ Popovers manuels fonctionnels

### 2. Éléments DOM Requis
- ✅ `chat-input` (Zone de saisie)
- ✅ `voice-chat-btn` (Bouton vocal)  
- ✅ `tts-toggle` (Toggle audio)
- ✅ `live-api-btn` (Bouton conversation)
- ✅ `new-next-btn` / `new-previous-btn` (Navigation)
- ✅ `new-simplify-btn` / `new-more-details-btn` (Actions)
- ✅ `generate-chart-btn` (Graphique)

### 3. Système i18n
- ✅ Traductions FR/EN chargées
- ✅ Fallbacks configurés
- ✅ `window.i18n.t()` ou `window.safeT()` disponible

### 4. LocalStorage
- ✅ Clé `fia_interface_intro_completed` gérée
- ✅ Reset possible pour tests

## 🎯 Workflow de Test Recommandé

### Test Initial Complet
```javascript
// 1. Test complet automatique
await window.debugPopovers.fullTest()

// 2. Si échec, diagnostic étape par étape
window.debugPopovers.inspect()
```

### Test Simulation Slide Plan
```javascript
// 1. Reset état
window.debugPopovers.reset()

// 2. Simuler slide plan
window.debugPopovers.simulatePlanSlide()

// 3. Vérifier affichage après 1 seconde
```

### Test Forçage Manuel
```javascript
// 1. Forcer affichage direct
await window.debugPopovers.forceShow()

// 2. Vérifier popovers visibles
// 3. Tester fermeture individuelle
```

## 🚨 Messages d'Erreur Fréquents

### `Bootstrap is not defined`
**Solution :** Vérifier que Bootstrap 5.3.2 est chargé avant les scripts

### `Cannot read property 'Popover' of undefined`
**Solution :** Bootstrap chargé mais Popover non disponible, vérifier la version

### `Failed to resolve module specifier`
**Solution :** Chemin d'import incorrect, vérifier le path relatif

### `localStorage is not defined`
**Solution :** Contexte non-browser, utiliser un serveur local

## 📝 Logs de Debug à Surveiller

**Logs Normaux (Succès) :**
```
🎯 [INTERFACE-INTRO] SLIDE TYPE "PLAN" DÉTECTÉ !
🚀 [INTERFACE-INTRO] Démarrage import du composant...
✅ [INTERFACE-INTRO] Composant importé avec succès
🎯 [INTERFACE-INTRO] Instance créée, vérification...
📢 [INTERFACE-INTRO] DÉMARRAGE INTRODUCTION INTERFACE !
✨ [INTERFACE-INTRO] Popovers d'introduction lancés avec succès
```

**Logs Problématiques :**
```
❌ [INTERFACE-INTRO] Erreur lors du chargement des popovers...
⚠️ [INTERFACE-INTRO] Element not found: chat-input
ℹ️ [INTERFACE-INTRO] Introduction déjà terminée, pas d'affichage
```

## 🔧 Débogage Avancé

### Inspection ManuellePopovers Bootstrap
```javascript
// Trouver tous les popovers actifs
document.querySelectorAll('[data-bs-toggle="popover"]')

// Créer un popover de test manuel
const testEl = document.querySelector('#chat-input')
const testPopover = new bootstrap.Popover(testEl, {
    title: 'Test',
    content: 'Popover de test',
    trigger: 'manual'
})
testPopover.show()
```

### Vérification État des Modules
```javascript
// Vérifier disponibilité du module
import('./src/components/interface-introduction-popovers.js')
  .then(module => {
    const instance = new module.InterfaceIntroductionPopovers()
    console.log('Module OK:', instance)
  })
```

Avec ces outils, vous devriez pouvoir identifier et résoudre rapidement tout problème avec les popovers d'introduction !