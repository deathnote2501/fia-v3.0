/**
 * Index Page Main Orchestrator
 * 
 * This module orchestrates all the functionality for the landing page (index.html).
 * It replaces the inline JavaScript and provides a clean, maintainable structure.
 */

import { autoInitializeBasicPage } from '/frontend/src/components/page-init.js';
import '/frontend/src/components/landing-page.js';
import '/frontend/src/components/index-init.js';

/**
 * Main initialization function for the index page
 * This function coordinates all the page components
 */
function initializeIndexPage() {
    console.log('🏠 [INDEX-PAGE] Starting index page initialization...');
    
    try {
        // Initialize basic page functionality
        autoInitializeBasicPage();
        
        // Note: index-init.js auto-initializes i18n
        // Note: landing-page.js auto-initializes landing functionality
        
        console.log('✅ [INDEX-PAGE] Index page initialized successfully');
        
        // Set global flag for debugging
        window.indexPageReady = true;
        
    } catch (error) {
        console.error('❌ [INDEX-PAGE] Error initializing index page:', error);
        window.indexPageReady = false;
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeIndexPage);
} else {
    initializeIndexPage();
}

console.log('🏠 [INDEX-PAGE] Index page orchestrator loaded');