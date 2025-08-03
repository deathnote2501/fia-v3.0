/**
 * Common Page Initialization Module
 * Shared i18n setup and DOM initialization for all pages
 * 
 * This module provides the base initialization that's common across pages.
 * Pages with specific needs can import and extend this functionality.
 */

/**
 * Initialize basic i18n functionality for any page
 * This handles the common i18n setup that most pages need
 */
export function initializeBasicPage() {
    // Initialize i18n when available
    if (window.i18n) {
        // Update all elements with data-i18n attributes
        window.i18n.updateDOM();
        
        // Update title specifically
        const titleElement = document.querySelector('title[data-i18n]');
        if (titleElement) {
            const key = titleElement.getAttribute('data-i18n');
            const translation = window.i18n.t(key);
            if (translation && translation !== key) {
                titleElement.textContent = translation;
            }
        }
    }
}

/**
 * Auto-initialize basic pages when DOM is loaded
 * This is the default behavior for simple pages
 */
export function autoInitializeBasicPage() {
    document.addEventListener('DOMContentLoaded', initializeBasicPage);
}