/**
 * FIA v3.0 - Registration Form Component
 * Handles trainer registration with validation
 */

class RegistrationForm {
    constructor() {
        this.form = document.getElementById('registration-form');
        this.submitButton = document.getElementById('register-btn');
        this.validator = new FormValidator(this.form);
        
        this.init();
    }

    init() {
        if (!this.form) return;

        // Redirect if already authenticated
        authManager.redirectIfAuthenticated();

        this.setupValidation();
        this.setupPasswordToggle();
        this.setupFormSubmission();
    }

    setupValidation() {
        // Setup validation rules
        this.validator
            .addRule('email', {
                required: true,
                email: true,
                requiredMessage: 'Email address is required'
            })
            .addRule('first_name', {
                required: true,
                requiredMessage: 'First name is required'
            })
            .addRule('last_name', {
                required: true,
                requiredMessage: 'Last name is required'
            })
            .addRule('password', {
                required: true,
                password: true,
                requiredMessage: 'Password is required'
            })
            .addRule('confirm_password', {
                required: true,
                custom: (value) => {
                    const password = document.getElementById('password').value;
                    if (value !== password) {
                        return {
                            isValid: false,
                            message: 'Passwords do not match'
                        };
                    }
                    return { isValid: true };
                },
                requiredMessage: 'Please confirm your password'
            });

        // Setup real-time validation
        this.validator.setupRealTimeValidation();

        // Special handling for password confirmation
        const confirmPasswordField = document.getElementById('confirm-password');
        const passwordField = document.getElementById('password');
        
        if (confirmPasswordField && passwordField) {
            passwordField.addEventListener('input', () => {
                if (confirmPasswordField.value) {
                    this.validator.validateField(confirmPasswordField);
                }
            });
        }
    }

    setupPasswordToggle() {
        setupPasswordToggle('password', 'toggle-password');
    }

    setupFormSubmission() {
        this.form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleSubmission();
        });
    }

    async handleSubmission() {
        // Validate form
        if (!this.validator.validateForm()) {
            showAlert('Please correct the errors above', 'error');
            return;
        }

        const formData = new FormData(this.form);
        const userData = {
            email: formData.get('email'),
            first_name: formData.get('first_name'),
            last_name: formData.get('last_name'),
            password: formData.get('password')
        };

        this.setLoading(true);

        try {
            const result = await authManager.register(userData);

            if (result.success) {
                showAlert('Account created successfully! Redirecting to dashboard...', 'success');
                
                // Redirect to trainer dashboard after short delay
                setTimeout(() => {
                    window.location.href = '/frontend/public/trainer.html';
                }, 2000);
            } else {
                showAlert(result.message || 'Registration failed. Please try again.', 'error');
            }
        } catch (error) {
            console.error('Registration error:', error);
            showAlert('An unexpected error occurred. Please try again.', 'error');
        } finally {
            this.setLoading(false);
        }
    }

    setLoading(isLoading) {
        const btnText = this.submitButton.querySelector('.btn-text');
        const btnSpinner = this.submitButton.querySelector('.btn-spinner');
        
        if (isLoading) {
            btnText.classList.add('d-none');
            btnSpinner.classList.remove('d-none');
            this.submitButton.disabled = true;
        } else {
            btnText.classList.remove('d-none');
            btnSpinner.classList.add('d-none');
            this.submitButton.disabled = false;
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new RegistrationForm();
});