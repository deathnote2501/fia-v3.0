/**
 * FIA v3.0 - Helper i18n pour intégration facile
 * Fonctions utilitaires pour faciliter l'usage du service i18n
 */

/**
 * Initialiser le service i18n globalement
 */
export async function initializeI18n() {
    const { default: I18n } = await import('./i18n.js');
    window.i18n = new I18n();
    await window.i18n.loadTranslations();
    
    console.log('🌐 [i18n-helper] Service i18n initialisé globalement');
    return window.i18n;
}

/**
 * Fonction raccourci pour traduire (disponible globalement)
 */
export function setupGlobalTranslation() {
    window.t = function(key) {
        return window.i18n ? window.i18n.t(key) : key;
    };
    
    console.log('🔧 [i18n-helper] Fonction t() disponible globalement');
}

/**
 * Appliquer les traductions à un élément HTML et ses enfants
 */
export function translateElement(element) {
    if (!window.i18n) {
        console.warn('⚠️ [i18n-helper] Service i18n non initialisé');
        return;
    }
    
    // Traduire l'élément lui-même s'il a data-i18n
    const key = element.getAttribute('data-i18n');
    if (key) {
        element.textContent = window.i18n.t(key);
    }
    
    // Traduire les éléments enfants
    element.querySelectorAll('[data-i18n]').forEach(child => {
        const childKey = child.getAttribute('data-i18n');
        child.textContent = window.i18n.t(childKey);
    });
}

/**
 * Ajouter un sélecteur de langue à un élément
 */
export function addLanguageSelector(containerElement, options = {}) {
    const {
        languages = [
            { code: 'fr', name: 'Français' },
            { code: 'en', name: 'English' }
        ],
        className = 'language-selector',
        showFlag = false
    } = options;
    
    const selector = document.createElement('select');
    selector.className = className;
    
    languages.forEach(lang => {
        const option = document.createElement('option');
        option.value = lang.code;
        option.textContent = showFlag ? `${lang.flag || ''} ${lang.name}` : lang.name;
        
        if (window.i18n && window.i18n.getCurrentLanguage() === lang.code) {
            option.selected = true;
        }
        
        selector.appendChild(option);
    });
    
    selector.addEventListener('change', async (e) => {
        if (window.i18n) {
            await window.i18n.setLanguage(e.target.value);
        }
    });
    
    containerElement.appendChild(selector);
    
    // Écouter les changements de langue pour synchroniser le sélecteur
    window.addEventListener('languageChanged', (event) => {
        selector.value = event.detail.language;
    });
    
    return selector;
}

/**
 * Utilitaire pour remplacer du texte hardcodé par des clés de traduction
 */
export function replaceTextWithTranslations(mappings) {
    if (!window.i18n) {
        console.warn('⚠️ [i18n-helper] Service i18n non initialisé');
        return;
    }
    
    Object.entries(mappings).forEach(([selector, key]) => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            element.textContent = window.i18n.t(key);
            element.setAttribute('data-i18n', key); // Pour les futures mises à jour
        });
    });
}

/**
 * Détecter la langue préférée du formateur depuis l'API
 */
export async function detectTrainerLanguage() {
    try {
        // Vérifier si on est connecté en tant que formateur
        const token = localStorage.getItem('access_token');
        if (!token) {
            return null;
        }
        
        const response = await fetch('/api/trainers/me', {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const trainer = await response.json();
            return trainer.language || 'fr';
        }
    } catch (error) {
        console.warn('⚠️ [i18n-helper] Impossible de récupérer la langue du formateur:', error);
    }
    
    return null;
}

/**
 * Sauvegarder la langue du formateur via l'API
 */
export async function saveTrainerLanguage(language) {
    try {
        const token = localStorage.getItem('access_token');
        if (!token) {
            return false;
        }
        
        const response = await fetch('/api/trainers/me/language', {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ language })
        });
        
        return response.ok;
    } catch (error) {
        console.warn('⚠️ [i18n-helper] Impossible de sauvegarder la langue du formateur:', error);
        return false;
    }
}