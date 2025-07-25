/**
 * FIA v3.0 - Validation Utilities
 * Client-side validation helpers using Bootstrap styling
 */

class FormValidator {
    constructor(form) {
        this.form = form;
        this.rules = {};
    }

    /**
     * Add validation rule for a field
     * @param {string} fieldName 
     * @param {object} rule 
     */
    addRule(fieldName, rule) {
        this.rules[fieldName] = rule;
        return this;
    }

    /**
     * Validate email format
     * @param {string} email 
     * @returns {boolean}
     */
    static isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    /**
     * Validate password strength
     * @param {string} password 
     * @returns {object}
     */
    static validatePassword(password) {
        const result = {
            isValid: false,
            errors: []
        };

        if (password.length < 8) {
            result.errors.push('Password must be at least 8 characters long');
        }

        if (!/[A-Z]/.test(password)) {
            result.errors.push('Password must contain at least one uppercase letter');
        }

        if (!/[a-z]/.test(password)) {
            result.errors.push('Password must contain at least one lowercase letter');
        }

        if (!/\d/.test(password)) {
            result.errors.push('Password must contain at least one number');
        }

        result.isValid = result.errors.length === 0;
        return result;
    }

    /**
     * Show field validation error
     * @param {HTMLElement} field 
     * @param {string} message 
     */
    static showFieldError(field, message) {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');
        
        const feedbackElement = document.getElementById(`${field.id}-feedback`);
        if (feedbackElement) {
            feedbackElement.textContent = message;
        }
    }

    /**
     * Show field validation success
     * @param {HTMLElement} field 
     */
    static showFieldSuccess(field) {
        field.classList.add('is-valid');
        field.classList.remove('is-invalid');
        
        const feedbackElement = document.getElementById(`${field.id}-feedback`);
        if (feedbackElement) {
            feedbackElement.textContent = '';
        }
    }

    /**
     * Clear field validation state
     * @param {HTMLElement} field 
     */
    static clearFieldValidation(field) {
        field.classList.remove('is-valid', 'is-invalid');
        
        const feedbackElement = document.getElementById(`${field.id}-feedback`);
        if (feedbackElement) {
            feedbackElement.textContent = '';
        }
    }

    /**
     * Validate single field
     * @param {HTMLElement} field 
     * @returns {boolean}
     */
    validateField(field) {
        const fieldName = field.name || field.id;
        const rule = this.rules[fieldName];
        
        if (!rule) return true;

        const value = field.value.trim();

        // Required validation
        if (rule.required && !value) {
            FormValidator.showFieldError(field, rule.requiredMessage || 'This field is required');
            return false;
        }

        // Email validation
        if (rule.email && value && !FormValidator.isValidEmail(value)) {
            FormValidator.showFieldError(field, 'Please enter a valid email address');
            return false;
        }

        // Password validation
        if (rule.password && value) {
            const passwordValidation = FormValidator.validatePassword(value);
            if (!passwordValidation.isValid) {
                FormValidator.showFieldError(field, passwordValidation.errors[0]);
                return false;
            }
        }

        // Custom validation
        if (rule.custom && value) {
            const customResult = rule.custom(value);
            if (!customResult.isValid) {
                FormValidator.showFieldError(field, customResult.message);
                return false;
            }
        }

        FormValidator.showFieldSuccess(field);
        return true;
    }

    /**
     * Validate entire form
     * @returns {boolean}
     */
    validateForm() {
        let isValid = true;
        const fields = this.form.querySelectorAll('input, select, textarea');
        
        fields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });

        return isValid;
    }

    /**
     * Setup real-time validation
     */
    setupRealTimeValidation() {
        const fields = this.form.querySelectorAll('input, select, textarea');
        
        fields.forEach(field => {
            // Validate on blur
            field.addEventListener('blur', () => {
                this.validateField(field);
            });

            // Clear validation on input (except for password confirmation)
            field.addEventListener('input', () => {
                if (!field.id.includes('confirm')) {
                    FormValidator.clearFieldValidation(field);
                }
            });
        });
    }
}

/**
 * Show alert message
 * @param {string} message 
 * @param {string} type - success, error, warning, info
 * @param {string} containerId 
 */
function showAlert(message, type = 'info', containerId = 'alert-container') {
    const container = document.getElementById(containerId);
    if (!container) return;

    const alertTypes = {
        success: 'alert-success',
        error: 'alert-danger',
        warning: 'alert-warning',
        info: 'alert-info'
    };

    const alertClass = alertTypes[type] || 'alert-info';
    
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    container.innerHTML = alertHtml;
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        const alert = container.querySelector('.alert');
        if (alert) {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }
    }, 5000);
}

/**
 * Toggle password visibility
 * @param {string} passwordFieldId 
 * @param {string} toggleButtonId 
 */
function setupPasswordToggle(passwordFieldId, toggleButtonId) {
    const passwordField = document.getElementById(passwordFieldId);
    const toggleButton = document.getElementById(toggleButtonId);
    
    if (!passwordField || !toggleButton) return;

    toggleButton.addEventListener('click', () => {
        const isPassword = passwordField.type === 'password';
        passwordField.type = isPassword ? 'text' : 'password';
        
        const icon = toggleButton.querySelector('i');
        icon.className = isPassword ? 'bi bi-eye-slash' : 'bi bi-eye';
    });
}

// Export for use in other modules
window.FormValidator = FormValidator;
window.showAlert = showAlert;
window.setupPasswordToggle = setupPasswordToggle;