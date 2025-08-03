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
 * Safe translation function with intelligent fallbacks
 * @param {string} key - Translation key
 * @param {string} customFallback - Custom fallback text
 * @returns {string} Translated text or smart fallback
 */
export function safeT(key, customFallback = null) {
    // If i18n is ready, try to get translation
    if (window.i18n && window.i18n.translations && window.i18n.translations[window.i18n.currentLanguage]) {
        const translation = window.i18n.t(key);
        // If translation exists and is not the key itself, return it
        if (translation && translation !== key) {
            return translation;
        }
    }
    
    // Use custom fallback if provided
    if (customFallback) {
        return customFallback;
    }
    
    // Smart fallbacks for common keys to avoid technical display
    const smartFallbacks = {
        'status.validatingSession': 'Validating Session',
        'status.validatingSessionMessage': 'Please wait while we verify your session...',
        'status.generatingPlan': 'Generating Your Training Plan',
        'status.generatingPlanMessage': 'This may take a few moments...',
        'status.loadingSession': 'Loading Your Session',
        'status.loadingSessionMessage': 'Loading your training content...',
        'status.loading': 'Loading...',
        'status.loadingGeneric': 'Loading...',
        'status.loadingTrainings': 'Loading trainings...',
        'status.loadingSlideContent': 'Loading slide content...',
        'status.loadingData': 'Loading data...',
        'error.generic': 'An error occurred',
        'error.loadingTrainings': 'Error loading trainings',
        'error.loadingSessions': 'Error loading sessions',
        'error.loadingData': 'Error loading data'
    };
    
    return smartFallbacks[key] || 'Loading...';
}

/**
 * Format date according to current locale
 * @param {string|Date} dateInput - Date string or Date object
 * @param {Object} options - Formatting options
 * @returns {string} Formatted date
 */
export function formatLocalizedDate(dateInput, options = {}) {
    const date = dateInput instanceof Date ? dateInput : new Date(dateInput);
    
    // Get current language from i18n service, fallback to 'en'
    const currentLanguage = (window.i18n && window.i18n.currentLanguage) || 'en';
    
    // Map language codes to locale codes
    const localeMap = {
        'fr': 'fr-FR',
        'en': 'en-US',
        'es': 'es-ES',
        'de': 'de-DE'
    };
    
    const locale = localeMap[currentLanguage] || 'en-US';
    
    // Default options for short date format
    const defaultOptions = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        ...options
    };
    
    try {
        return date.toLocaleDateString(locale, defaultOptions);
    } catch (error) {
        console.warn('Date formatting error:', error);
        return date.toLocaleDateString('en-US', defaultOptions);
    }
}

/**
 * Format date with time according to current locale
 * @param {string|Date} dateInput - Date string or Date object
 * @returns {string} Formatted date with time
 */
export function formatLocalizedDateTime(dateInput) {
    return formatLocalizedDate(dateInput, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Fonction raccourci pour traduire (disponible globalement)
 */
export function setupGlobalTranslation() {
    window.t = function(key) {
        return window.i18n ? window.i18n.t(key) : key;
    };
    
    // Add safeT globally
    window.safeT = safeT;
    
    // Add date formatting functions globally
    window.formatLocalizedDate = formatLocalizedDate;
    window.formatLocalizedDateTime = formatLocalizedDateTime;
    
    console.log('🔧 [i18n-helper] Fonctions t(), safeT() et formatage de dates disponibles globalement');
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