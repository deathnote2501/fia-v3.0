/**
 * FIA v3.0 - Error Message Manager
 * Centralized error handling with i18n support and automatic contact info
 */

class ErrorManager {
    constructor() {
        this.toastManager = null;
        this.i18n = null;
        this.init();
    }

    /**
     * Initialize ErrorManager with dependencies
     */
    init() {
        this.loadDependencies();
        console.log('🚨 [ErrorManager] Initialized with i18n and toast support');
    }

    /**
     * Load required dependencies (ToastManager and i18n)
     */
    loadDependencies() {
        // Load ToastManager
        if (window.toastManager) {
            this.toastManager = window.toastManager;
        } else {
            console.warn('⚠️ [ErrorManager] ToastManager not available, falling back to showAlert');
        }

        // Load i18n
        if (window.i18n) {
            this.i18n = window.i18n;
        } else if (window.I18n) {
            try {
                this.i18n = new window.I18n();
            } catch (e) {
                console.warn('⚠️ [ErrorManager] Could not initialize i18n:', e);
            }
        }
    }

    /**
     * Translate error key with fallback
     * @param {string} errorKey - i18n key or direct message
     * @returns {string} Translated message
     */
    translate(errorKey) {
        if (this.i18n && typeof this.i18n.t === 'function') {
            return this.i18n.t(errorKey);
        }
        return errorKey; // Fallback to original key
    }

    /**
     * Check if error is critical and needs contact info
     * @param {string} errorKey - Error key
     * @returns {boolean}
     */
    isCriticalError(errorKey) {
        const criticalPatterns = [
            'error.server',
            'error.database', 
            'error.auth.system',
            'error.api.critical',
            'error.unexpected',
            'error.system',
            'critical',
            'system'
        ];
        
        return criticalPatterns.some(pattern => errorKey.includes(pattern));
    }

    /**
     * Add contact information for critical errors
     * @param {string} message - Base error message
     * @param {string} errorKey - Original error key
     * @returns {string} Message with contact info if needed
     */
    addContactInfo(message, errorKey) {
        if (this.isCriticalError(errorKey)) {
            const contactText = this.translate('contact.support') || 'Contact support: jerome.iavarone@gmail.com';
            return `${message}<br><small class="text-muted mt-1">${contactText}</small>`;
        }
        return message;
    }

    /**
     * Show error message using best available method
     * @param {string} errorKey - i18n key or direct message
     * @param {object} options - Display options
     */
    showError(errorKey, options = {}) {
        const {
            type = 'error',
            duration = 8000,
            context = {},
            fallbackMethod = 'alert'
        } = options;

        // Translate message
        let message = this.translate(errorKey);
        
        // Add context if provided
        if (context && Object.keys(context).length > 0) {
            // Simple context interpolation
            Object.entries(context).forEach(([key, value]) => {
                message = message.replace(`{{${key}}}`, value);
            });
        }

        // Add contact info for critical errors
        message = this.addContactInfo(message, errorKey);

        // Try ToastManager first
        if (this.toastManager) {
            return this.toastManager.show(message, type, { 
                duration, 
                allowHtml: true 
            });
        }

        // Fallback to showAlert if available
        if (typeof showAlert === 'function') {
            return showAlert(message, type, duration);
        }

        // Last resort fallback
        if (fallbackMethod === 'alert') {
            alert(`Error: ${message.replace(/<[^>]*>/g, '')}`); // Strip HTML for alert
        } else if (fallbackMethod === 'console') {
            console.error(`[ErrorManager] ${errorKey}:`, message);
        }

        return null;
    }

    /**
     * Show success message
     * @param {string} messageKey - i18n key or message
     * @param {object} options - Display options
     */
    showSuccess(messageKey, options = {}) {
        return this.showMessage(messageKey, 'success', { duration: 4000, ...options });
    }

    /**
     * Show warning message
     * @param {string} messageKey - i18n key or message
     * @param {object} options - Display options
     */
    showWarning(messageKey, options = {}) {
        return this.showMessage(messageKey, 'warning', { duration: 6000, ...options });
    }

    /**
     * Show info message
     * @param {string} messageKey - i18n key or message
     * @param {object} options - Display options
     */
    showInfo(messageKey, options = {}) {
        return this.showMessage(messageKey, 'info', { duration: 5000, ...options });
    }

    /**
     * Generic message display method
     * @param {string} messageKey - i18n key or message
     * @param {string} type - Message type
     * @param {object} options - Display options
     */
    showMessage(messageKey, type, options = {}) {
        const {
            duration = 5000,
            context = {},
            fallbackMethod = 'console'
        } = options;

        // Translate message
        let message = this.translate(messageKey);
        
        // Add context if provided
        if (context && Object.keys(context).length > 0) {
            Object.entries(context).forEach(([key, value]) => {
                message = message.replace(`{{${key}}}`, value);
            });
        }

        // Try ToastManager first
        if (this.toastManager) {
            return this.toastManager.show(message, type, { duration });
        }

        // Fallback to showAlert if available
        if (typeof showAlert === 'function') {
            return showAlert(message, type, duration);
        }

        // Last resort fallback
        if (fallbackMethod === 'console') {
            console.log(`[ErrorManager] ${type.toUpperCase()}: ${message}`);
        }

        return null;
    }

    /**
     * Handle API errors automatically
     * @param {Response|Error} error - API response or error object
     * @param {object} options - Display options
     */
    handleApiError(error, options = {}) {
        let errorKey = 'error.unexpected';

        if (error instanceof Response) {
            // HTTP Response error
            switch (error.status) {
                case 400:
                    errorKey = 'error.validation';
                    break;
                case 401:
                    errorKey = 'error.auth.failed';
                    break;
                case 403:
                    errorKey = 'error.forbidden';
                    break;
                case 404:
                    errorKey = 'error.notfound';
                    break;
                case 408:
                    errorKey = 'error.timeout';
                    break;
                case 500:
                    errorKey = 'error.server';
                    break;
                case 503:
                    errorKey = 'error.server';
                    break;
                default:
                    errorKey = 'error.api.critical';
            }
        } else if (error instanceof Error) {
            // JavaScript Error object
            if (error.name === 'NetworkError' || error.message.includes('fetch')) {
                errorKey = 'error.network';
            } else if (error.name === 'TypeError') {
                errorKey = 'error.validation';
            } else {
                errorKey = 'error.unexpected';
            }
        }

        return this.showError(errorKey, options);
    }

    /**
     * Handle validation errors
     * @param {object|string} validationData - Validation error data
     * @param {object} options - Display options
     */
    handleValidationError(validationData, options = {}) {
        if (typeof validationData === 'string') {
            return this.showError(validationData, options);
        }

        if (validationData && validationData.detail) {
            // FastAPI validation error format
            if (Array.isArray(validationData.detail)) {
                const firstError = validationData.detail[0];
                const context = {
                    field: firstError.loc ? firstError.loc.join('.') : 'unknown',
                    message: firstError.msg || 'validation error'
                };
                return this.showError('error.validation', { context, ...options });
            }
        }

        return this.showError('error.validation', options);
    }
}

// Create global instance
const errorManager = new ErrorManager();

/**
 * Global error function - enhanced showAlert replacement
 * @param {string} messageKey - Message or i18n key
 * @param {string} type - Message type
 * @param {object} options - Additional options
 */
function showAlert(messageKey, type = 'info', options = {}) {
    // Backwards compatibility: if third param is number, treat as duration
    if (typeof options === 'number') {
        options = { duration: options };
    }

    if (type === 'error') {
        return errorManager.showError(messageKey, options);
    } else {
        return errorManager.showMessage(messageKey, type, options);
    }
}

/**
 * Global error handling function
 * @param {string} errorKey - Error key
 * @param {object} options - Display options
 */
function showError(errorKey, options = {}) {
    return errorManager.showError(errorKey, options);
}

/**
 * Global success function
 * @param {string} messageKey - Message key
 * @param {object} options - Display options
 */
function showSuccess(messageKey, options = {}) {
    return errorManager.showSuccess(messageKey, options);
}

/**
 * Global warning function
 * @param {string} messageKey - Message key
 * @param {object} options - Display options
 */
function showWarning(messageKey, options = {}) {
    return errorManager.showWarning(messageKey, options);
}

/**
 * Global info function
 * @param {string} messageKey - Message key
 * @param {object} options - Display options
 */
function showInfo(messageKey, options = {}) {
    return errorManager.showInfo(messageKey, options);
}

// Export for global access
window.errorManager = errorManager;
window.showAlert = showAlert;
window.showError = showError;
window.showSuccess = showSuccess;
window.showWarning = showWarning;
window.showInfo = showInfo;

// Export for ES6 modules
export { ErrorManager, errorManager, showAlert, showError, showSuccess, showWarning, showInfo };
export default errorManager;