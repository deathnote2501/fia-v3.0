/**
 * FIA v3.0 - Error System Initialization
 * Auto-loads ErrorManager with i18n and ToastManager integration
 */

/**
 * Initialize complete error handling system
 * Call this function after DOM is loaded
 */
async function initializeErrorSystem() {
    console.log('🚨 [ErrorInit] Initializing error handling system...');

    try {
        // 1. Load i18n system first
        if (!window.i18n) {
            console.log('🌐 [ErrorInit] Loading i18n system...');
            
            // Import i18n helper
            const { initializeI18n, setupGlobalTranslation } = await import('../i18n/i18n-helper.js');
            
            // Initialize i18n
            await initializeI18n();
            
            // Setup global translation function
            setupGlobalTranslation();
            
            console.log('✅ [ErrorInit] i18n system loaded');
        }

        // 2. Load ToastManager
        if (!window.toastManager) {
            console.log('🍞 [ErrorInit] Loading ToastManager...');
            
            // Import and initialize ToastManager
            const { default: toastManager } = await import('./toast-manager.js');
            window.toastManager = toastManager;
            
            console.log('✅ [ErrorInit] ToastManager loaded');
        }

        // 3. Load ErrorManager
        if (!window.errorManager) {
            console.log('🚨 [ErrorInit] Loading ErrorManager...');
            
            // Import and initialize ErrorManager
            const { default: errorManager } = await import('./error-manager.js');
            window.errorManager = errorManager;
            
            console.log('✅ [ErrorInit] ErrorManager loaded');
        }

        // 4. Wait a bit for all systems to be ready
        await new Promise(resolve => setTimeout(resolve, 100));

        // 5. Verify integration
        if (window.errorManager && window.i18n && window.toastManager) {
            console.log('✅ [ErrorInit] Complete error system initialized successfully');
            
            // Test the system with a success message
            window.errorManager.showSuccess('status.success', { duration: 2000 });
            
            return true;
        } else {
            console.warn('⚠️ [ErrorInit] Some components failed to load');
            return false;
        }

    } catch (error) {
        console.error('❌ [ErrorInit] Failed to initialize error system:', error);
        return false;
    }
}

/**
 * Auto-initialize when DOM is ready
 */
function autoInitialize() {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeErrorSystem);
    } else {
        // DOM already loaded
        initializeErrorSystem();
    }
}

/**
 * Initialize error system with fallback for older browsers
 */
function initializeWithFallback() {
    // Try modern initialization
    if (typeof import === 'function') {
        autoInitialize();
    } else {
        // Fallback for older browsers
        console.warn('⚠️ [ErrorInit] ES6 modules not supported, using fallback initialization');
        
        // Basic error handling without modules
        window.showError = function(message, options = {}) {
            console.error('[Error]', message);
            if (typeof alert !== 'undefined') {
                alert(`Error: ${message}`);
            }
        };
        
        window.showSuccess = function(message, options = {}) {
            console.log('[Success]', message);
        };
        
        window.showWarning = function(message, options = {}) {
            console.warn('[Warning]', message);
        };
        
        window.showInfo = function(message, options = {}) {
            console.info('[Info]', message);
        };
    }
}

// Export functions
window.initializeErrorSystem = initializeErrorSystem;
window.initializeWithFallback = initializeWithFallback;

// Auto-initialize by default
initializeWithFallback();

// Export for ES6 modules
export { initializeErrorSystem, autoInitialize, initializeWithFallback };
export default initializeErrorSystem;