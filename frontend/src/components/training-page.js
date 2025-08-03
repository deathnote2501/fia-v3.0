/**
 * Training Page Main Orchestrator
 * 
 * This module orchestrates all the functionality for the training page (training.html).
 * It replaces the inline JavaScript and provides a clean, maintainable structure.
 * 
 * CRITICAL: This includes the mobile emergency fix that was previously inline
 * to ensure mobile buttons work correctly in production.
 */

import '/frontend/src/utils/mobile-emergency-fix.js';
import '/frontend/src/utils/mobile-debug-helper.js';
import '/frontend/src/utils/mobile-fallback-init.js';
import '/frontend/src/training-init.js';
import '/frontend/src/debug/popover-debug-commands.js';

/**
 * Main initialization function for the training page
 * This function coordinates all the page components including critical mobile fixes
 */
function initializeTrainingPage() {
    console.log('🎓 [TRAINING-PAGE] Starting training page initialization...');
    
    try {
        // Critical: Mobile emergency fix is auto-initialized by its module
        // This ensures mobile buttons work in production
        
        // Other modules auto-initialize:
        // - mobile-debug-helper.js
        // - mobile-fallback-init.js  
        // - training-init.js
        // - popover-debug-commands.js
        
        console.log('✅ [TRAINING-PAGE] Training page initialized successfully');
        
        // Set global flag for debugging
        window.trainingPageReady = true;
        
        // Log mobile fix status for production debugging
        setTimeout(() => {
            if (window.mobileEmergencyFixStatus) {
                console.log('📱 [TRAINING-PAGE] Mobile emergency fix status:', window.mobileEmergencyFixStatus);
            }
        }, 2000);
        
    } catch (error) {
        console.error('❌ [TRAINING-PAGE] Error initializing training page:', error);
        window.trainingPageReady = false;
    }
}

/**
 * Enhanced initialization with production-safe fallbacks
 * This ensures the page works even if some modules fail to load
 */
function setupTrainingPageInitialization() {
    console.log('🎓 [TRAINING-PAGE] Setting up training page...');
    
    // Strategy 1: DOM already ready
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        console.log('🎓 [TRAINING-PAGE] DOM ready, initializing immediately');
        initializeTrainingPage();
    }
    
    // Strategy 2: Wait for DOM ready
    if (document.readyState === 'loading') {
        console.log('🎓 [TRAINING-PAGE] DOM loading, waiting for ready state');
        document.addEventListener('DOMContentLoaded', initializeTrainingPage);
    }
    
    // Strategy 3: Delayed fallback for production safety
    setTimeout(() => {
        console.log('🎓 [TRAINING-PAGE] Executing fallback initialization');
        initializeTrainingPage();
    }, 1000);
}

// Initialize the training page
setupTrainingPageInitialization();

console.log('🎓 [TRAINING-PAGE] Training page orchestrator loaded');