/**
 * Training Page Main Orchestrator
 * 
 * This module orchestrates all the functionality for the training page (training.html).
 * It replaces the inline JavaScript and provides a clean, maintainable structure.
 * 
 * The mobile interface is handled by the main mobile-interface-handler.js component
 * loaded through training-init.js → main.js orchestration.
 */

import './training-init.js';
import '../debug/popover-debug-commands.js';

/**
 * Main initialization function for the training page
 * This function coordinates all the page components
 */
function initializeTrainingPage() {
    console.log('🎓 [TRAINING-PAGE] Starting training page initialization...');
    
    try {
        // Modules auto-initialize:
        // - training-init.js (main training logic)
        // - popover-debug-commands.js (debug functionality)
        // 
        // Mobile interface is handled by mobile-interface-handler.js
        // which is loaded through the main.js orchestration
        
        console.log('✅ [TRAINING-PAGE] Training page initialized successfully');
        
        // Set global flag for debugging
        window.trainingPageReady = true;
        
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