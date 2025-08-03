/**
 * Training Page Initialization Module
 * Handles advanced i18n setup with learner language detection for the training interface
 */

import { initializeI18n, setupGlobalTranslation } from '../i18n/i18n-helper.js';

/**
 * Initialize i18n with learner language detection
 */
async function initializeLearnerI18n() {
    try {
        // Try to detect learner language from session
        const learnerLanguage = await detectLearnerLanguage();
        
        // Initialize i18n service
        await initializeI18n();
        
        // Set detected language if different from default
        if (learnerLanguage && window.i18n && learnerLanguage !== window.i18n.getCurrentLanguage()) {
            await window.i18n.setLanguage(learnerLanguage);
            console.log(`🌐 [training] Learner language set to: ${learnerLanguage}`);
        }
        
        // Apply initial translations
        if (window.i18n) {
            window.i18n.updateDOM();
        }
        
    } catch (error) {
        console.warn('⚠️ [training] Error initializing learner i18n:', error);
        // Fallback to default initialization
        await initializeI18n();
        setupGlobalTranslation();
    }
}

/**
 * Detect learner language from session API
 */
async function detectLearnerLanguage() {
    try {
        // Get token from URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token');
        
        if (!token) {
            console.log('🔍 [training] No session token found, using browser language');
            return null;
        }
        
        // Get session data including learner language
        const response = await fetch(`/api/session/${token}`);
        if (response.ok) {
            const sessionData = await response.json();
            const learnerLanguage = sessionData.learner_session?.language;
            
            if (learnerLanguage) {
                console.log(`🎯 [training] Detected learner language from session: ${learnerLanguage}`);
                return learnerLanguage;
            }
        }
    } catch (error) {
        console.warn('⚠️ [training] Error detecting learner language from API:', error);
    }
    
    return null;
}

/**
 * Update learner interface with custom translations (simplified, no duplication)
 */
function updateLearnerInterface() {
    // i18n.updateDOM() now handles all standard attributes
    // This function is kept for future learner-specific customizations
    console.log('🔄 [training] Learner interface updated with translations');
}

/**
 * Initialize the training page
 */
async function initializeTraining() {
    console.log('🌐 [training] Initializing i18n service for learner...');
    
    // Initialize i18n with learner language detection
    await initializeLearnerI18n();
    setupGlobalTranslation();
    
    console.log('✅ [training] i18n service initialized for learner');
}

// Make updateLearnerInterface available globally for dynamic updates
window.updateLearnerInterface = updateLearnerInterface;

// Initialize when DOM is loaded
window.addEventListener('DOMContentLoaded', initializeTraining);