/**
 * FIA v3.0 - Service i18n Minimaliste KISS
 * Service ultra-simple pour l'internationalisation (50 lignes max)
 */

class I18n {
    constructor() {
        this.currentLanguage = this.detectLanguage();
        this.translations = {};
        this.loadTranslations();
        
        console.log(`🌐 [i18n] Initialized with language: ${this.currentLanguage}`);
    }
    
    /**
     * Détecter la langue à utiliser
     * Priorité: 1. URL param, 2. localStorage, 3. navigator.language, 4. default 'fr'
     */
    detectLanguage() {
        // 1. Paramètre URL ?lang=
        const urlParams = new URLSearchParams(window.location.search);
        const urlLang = urlParams.get('lang');
        if (urlLang && this.isValidLanguage(urlLang)) {
            return urlLang;
        }
        
        // 2. localStorage
        const storedLang = localStorage.getItem('fia-language');
        if (storedLang && this.isValidLanguage(storedLang)) {
            return storedLang;
        }
        
        // 3. Langue du navigateur
        const browserLang = navigator.language.split('-')[0]; // 'fr-FR' -> 'fr'
        if (this.isValidLanguage(browserLang)) {
            return browserLang;
        }
        
        // 4. Défaut
        return 'fr';
    }
    
    /**
     * Vérifier si la langue est supportée
     */
    isValidLanguage(lang) {
        return ['fr', 'en', 'es', 'de'].includes(lang);
    }
    
    /**
     * Charger les traductions de manière dynamique
     */
    async loadTranslations() {
        try {
            const module = await import(`./translations/${this.currentLanguage}.js`);
            this.translations[this.currentLanguage] = module.default || module[this.currentLanguage];
            console.log(`✅ [i18n] Translations loaded for ${this.currentLanguage}`);
        } catch (error) {
            console.warn(`⚠️ [i18n] Failed to load translations for ${this.currentLanguage}, falling back to keys`);
            this.translations[this.currentLanguage] = {};
        }
    }
    
    /**
     * Traduire une clé
     */
    t(key) {
        const translation = this.translations[this.currentLanguage]?.[key];
        return translation || key; // Fallback: retourner la clé si pas de traduction
    }
    
    /**
     * Changer de langue
     */
    async setLanguage(lang) {
        if (!this.isValidLanguage(lang)) {
            console.warn(`⚠️ [i18n] Invalid language: ${lang}`);
            return;
        }
        
        this.currentLanguage = lang;
        this.saveLanguage(lang);
        await this.loadTranslations();
        this.updateDOM();
        
        console.log(`🌐 [i18n] Language changed to: ${lang}`);
    }
    
    /**
     * Sauvegarder la langue en localStorage
     */
    saveLanguage(lang) {
        localStorage.setItem('fia-language', lang);
    }
    
    /**
     * Mettre à jour le DOM avec les nouvelles traductions
     */
    updateDOM() {
        // Mettre à jour tous les éléments avec data-i18n
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            element.textContent = this.t(key);
        });
        
        // Mettre à jour l'attribut lang du document
        document.documentElement.lang = this.currentLanguage;
        
        // Déclencher un événement pour que les composants puissent réagir
        window.dispatchEvent(new CustomEvent('languageChanged', { 
            detail: { language: this.currentLanguage } 
        }));
    }
    
    /**
     * Obtenir la langue actuelle
     */
    getCurrentLanguage() {
        return this.currentLanguage;
    }
}

// Export global pour utilisation dans d'autres scripts
window.I18n = I18n;

// Export pour modules ES6
export default I18n;