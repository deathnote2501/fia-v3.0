/**
 * Trainer Dashboard Initialization Module
 * Handles i18n setup, language selector, and DOM initialization for the trainer dashboard
 */

import { initializeI18n, setupGlobalTranslation, addLanguageSelector } from '../i18n/i18n-helper.js';

/**
 * Setup language selector functionality
 */
function setupLanguageSelector() {
    document.querySelectorAll('.language-option').forEach(option => {
        option.addEventListener('click', async (e) => {
            e.preventDefault();
            const lang = e.target.closest('.language-option').getAttribute('data-lang');
            
            if (window.i18n) {
                await window.i18n.setLanguage(lang);
                updateLanguageDisplay();
            }
        });
    });
    
    // Listen for language changes
    window.addEventListener('languageChanged', updateLanguageDisplay);
}

/**
 * Update language display in the UI
 */
function updateLanguageDisplay() {
    if (!window.i18n) return;
    
    const currentLang = window.i18n.getCurrentLanguage();
    const langDisplay = document.getElementById('current-language');
    const langOptions = document.querySelectorAll('.language-option');
    
    // Update language display
    if (langDisplay) {
        langDisplay.textContent = currentLang.toUpperCase();
    }
    
    // Update check marks
    langOptions.forEach(option => {
        const icon = option.querySelector('i');
        const optionLang = option.getAttribute('data-lang');
        
        if (optionLang === currentLang) {
            icon.classList.remove('d-none');
        } else {
            icon.classList.add('d-none');
        }
    });
}

/**
 * Initialize the trainer dashboard
 */
async function initializeTrainer() {
    console.log('🌐 [trainer] Initializing i18n service...');
    
    // Initialize i18n FIRST
    await initializeI18n();
    setupGlobalTranslation();
    
    // Setup language selector functionality
    setupLanguageSelector();
    
    // Initial translation of the page
    if (window.i18n) {
        window.i18n.updateDOM();
        updateLanguageDisplay();
    }
    
    console.log('✅ [trainer] i18n service initialized');
    
    // Signal that i18n is ready for other scripts
    window.dispatchEvent(new CustomEvent('i18nReady'));
}

// Initialize when DOM is loaded
window.addEventListener('DOMContentLoaded', initializeTrainer);