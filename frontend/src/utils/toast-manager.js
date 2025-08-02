/**
 * FIA v3.0 - Toast Notification Manager
 * Modern toast notifications in top-right corner with i18n support
 */

class ToastManager {
    constructor() {
        this.toastContainer = null;
        this.toastCounter = 0;
        this.activeToasts = new Map();
        this.i18n = null;
        
        this.init();
    }

    /**
     * Initialize toast container and i18n
     */
    init() {
        this.createToastContainer();
        this.loadI18n();
    }

    /**
     * Create toast container in top-right corner
     */
    createToastContainer() {
        // Remove existing container if present
        const existing = document.getElementById('toast-container');
        if (existing) {
            existing.remove();
        }

        // Create new toast container
        this.toastContainer = document.createElement('div');
        this.toastContainer.id = 'toast-container';
        this.toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        this.toastContainer.style.cssText = `
            z-index: 9999;
            max-width: 400px;
            pointer-events: none;
        `;

        // Append to body
        document.body.appendChild(this.toastContainer);
    }

    /**
     * Load i18n instance if available
     */
    loadI18n() {
        // Try to get global i18n instance
        if (window.i18n) {
            this.i18n = window.i18n;
        } else if (window.I18n) {
            // Try to create instance if class is available
            try {
                this.i18n = new window.I18n();
            } catch (e) {
                console.warn('[ToastManager] Could not initialize i18n:', e);
            }
        }
    }

    /**
     * Translate text using i18n or fallback to key
     * @param {string} key - Translation key
     * @returns {string} Translated text or original key
     */
    translate(key) {
        if (this.i18n && typeof this.i18n.t === 'function') {
            return this.i18n.t(key);
        }
        return key; // Fallback to original key
    }

    /**
     * Check if error is critical and needs contact info
     * @param {string} type - Toast type
     * @param {string} messageKey - Message key
     * @returns {boolean}
     */
    isCriticalError(type, messageKey) {
        const criticalTypes = ['error', 'danger'];
        const criticalKeys = [
            'error.server',
            'error.database',
            'error.auth.system',
            'error.api.critical',
            'error.unexpected',
            'error.system'
        ];

        return criticalTypes.includes(type) && 
               (criticalKeys.includes(messageKey) || messageKey.includes('critical') || messageKey.includes('system'));
    }

    /**
     * Add contact information for critical errors
     * @param {string} message - Base message
     * @param {string} type - Toast type
     * @param {string} messageKey - Original message key
     * @returns {string} Message with contact info if needed
     */
    addContactInfo(message, type, messageKey) {
        if (this.isCriticalError(type, messageKey)) {
            const contactText = this.translate('contact.support') || 'Contact support: jerome.iavarone@gmail.com';
            return `${message}<br><small class="text-muted">${contactText}</small>`;
        }
        return message;
    }

    /**
     * Show toast notification
     * @param {string} messageKey - i18n key or direct message
     * @param {string} type - Toast type: success, error, warning, info
     * @param {object} options - Additional options
     */
    show(messageKey, type = 'info', options = {}) {
        const {
            duration = this.getDefaultDuration(type),
            allowHtml = true,
            showClose = true,
            autoDismiss = true
        } = options;

        // Ensure container exists
        if (!this.toastContainer) {
            this.createToastContainer();
        }

        // Translate message
        let message = this.translate(messageKey);
        
        // Add contact info for critical errors
        message = this.addContactInfo(message, type, messageKey);

        // Create toast element
        const toastId = `toast-${++this.toastCounter}`;
        const toast = this.createToastElement(toastId, message, type, showClose, allowHtml);

        // Add to container
        this.toastContainer.appendChild(toast);

        // Enable pointer events on this toast
        toast.style.pointerEvents = 'auto';

        // Initialize Bootstrap toast
        const bsToast = new bootstrap.Toast(toast, {
            autohide: autoDismiss,
            delay: duration
        });

        // Store reference
        this.activeToasts.set(toastId, {
            element: toast,
            bsToast: bsToast,
            type: type
        });

        // Show toast
        bsToast.show();

        // Clean up when hidden
        toast.addEventListener('hidden.bs.toast', () => {
            this.removeToast(toastId);
        });

        return toastId;
    }

    /**
     * Get default duration based on type
     * @param {string} type - Toast type
     * @returns {number} Duration in milliseconds
     */
    getDefaultDuration(type) {
        const durations = {
            success: 4000,
            info: 5000,
            warning: 6000,
            error: 8000,
            danger: 8000
        };
        return durations[type] || 5000;
    }

    /**
     * Create toast HTML element
     * @param {string} id - Toast ID
     * @param {string} message - Message content
     * @param {string} type - Toast type
     * @param {boolean} showClose - Show close button
     * @param {boolean} allowHtml - Allow HTML content
     * @returns {HTMLElement} Toast element
     */
    createToastElement(id, message, type, showClose, allowHtml) {
        const toast = document.createElement('div');
        toast.id = id;
        toast.className = 'toast align-items-center mb-2';
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        // Set toast styling based on type
        const typeClasses = {
            success: 'text-bg-success',
            error: 'text-bg-danger',
            danger: 'text-bg-danger',
            warning: 'text-bg-warning',
            info: 'text-bg-info'
        };
        toast.classList.add(typeClasses[type] || 'text-bg-info');

        // Get icon for type
        const icons = {
            success: 'bi-check-circle-fill',
            error: 'bi-exclamation-triangle-fill',
            danger: 'bi-exclamation-triangle-fill',
            warning: 'bi-exclamation-triangle-fill',
            info: 'bi-info-circle-fill'
        };
        const icon = icons[type] || 'bi-info-circle-fill';

        // Create toast content
        const closeButton = showClose ? `
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        ` : '';

        if (allowHtml) {
            toast.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body d-flex align-items-center">
                        <i class="bi ${icon} me-2"></i>
                        <div class="flex-grow-1">${message}</div>
                    </div>
                    ${closeButton}
                </div>
            `;
        } else {
            toast.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body d-flex align-items-center">
                        <i class="bi ${icon} me-2"></i>
                        <div class="flex-grow-1"></div>
                    </div>
                    ${closeButton}
                </div>
            `;
            // Set text content safely (no HTML)
            toast.querySelector('.flex-grow-1').textContent = message;
        }

        return toast;
    }

    /**
     * Remove toast from container and memory
     * @param {string} toastId - Toast ID to remove
     */
    removeToast(toastId) {
        const toastData = this.activeToasts.get(toastId);
        if (toastData) {
            toastData.element.remove();
            this.activeToasts.delete(toastId);
        }
    }

    /**
     * Clear all active toasts
     */
    clearAll() {
        this.activeToasts.forEach((toastData, toastId) => {
            toastData.bsToast.hide();
        });
        this.activeToasts.clear();
    }

    /**
     * Show success toast
     * @param {string} messageKey - i18n key or message
     * @param {object} options - Additional options
     */
    success(messageKey, options = {}) {
        return this.show(messageKey, 'success', options);
    }

    /**
     * Show error toast
     * @param {string} messageKey - i18n key or message
     * @param {object} options - Additional options
     */
    error(messageKey, options = {}) {
        return this.show(messageKey, 'error', options);
    }

    /**
     * Show warning toast
     * @param {string} messageKey - i18n key or message
     * @param {object} options - Additional options
     */
    warning(messageKey, options = {}) {
        return this.show(messageKey, 'warning', options);
    }

    /**
     * Show info toast
     * @param {string} messageKey - i18n key or message
     * @param {object} options - Additional options
     */
    info(messageKey, options = {}) {
        return this.show(messageKey, 'info', options);
    }
}

// Create global instance
const toastManager = new ToastManager();

/**
 * Global toast function - compatible with existing showAlert pattern
 * @param {string} message - Message or i18n key
 * @param {string} type - Toast type
 * @param {object} options - Additional options
 */
function showToast(message, type = 'info', options = {}) {
    return toastManager.show(message, type, options);
}

// Export for use in other modules
window.toastManager = toastManager;
window.showToast = showToast;

// Also export for ES6 modules
export { ToastManager, toastManager, showToast };
export default toastManager;