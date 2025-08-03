/**
 * Index Page i18n Initialization Module
 * 
 * This module handles the specific i18n initialization for the landing page (index.html).
 * Externalized from inline script for better maintainability and SPEC.md compliance.
 */

import I18n from '/frontend/src/i18n/i18n.js';
import { initializeI18n, setupGlobalTranslation } from '/frontend/src/i18n/i18n-helper.js';

/**
 * Initialize i18n system for the landing page
 * This function sets up the complete i18n infrastructure
 */
export async function initializeIndexI18n() {
    try {
        console.log('🌐 [INDEX-I18N] Starting i18n initialization...');
        
        // Create i18n instance globally
        window.i18n = new I18n();
        
        // Wait for translations to load
        await window.i18n.loadTranslations();
        
        // Setup global translation functions
        setupGlobalTranslation();
        
        // Apply translations to DOM
        window.i18n.updateDOM();
        
        console.log('✅ [INDEX-I18N] i18n initialized successfully');
        return true;
        
    } catch (error) {
        console.error('❌ [INDEX-I18N] Failed to initialize i18n:', error);
        
        // Set fallback global functions to prevent errors
        if (!window.safeT) {
            window.safeT = (key, fallback) => fallback || key;
        }
        if (!window.t) {
            window.t = (key) => key;
        }
        
        return false;
    }
}

/**
 * Setup i18n initialization on DOM ready
 * This is the main entry point for index.html
 */
export function setupIndexI18nInitialization() {
    console.log('🌐 [INDEX-I18N] Setting up index page i18n...');
    
    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', async () => {
        await initializeIndexI18n();
    });
}

// Auto-setup when module loads
setupIndexI18nInitialization();