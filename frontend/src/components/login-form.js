/**
 * FIA v3.0 - Login Form Component
 * Handles trainer login with validation
 */

class LoginForm {
    constructor() {
        this.form = document.getElementById('login-form');
        this.submitButton = document.getElementById('login-btn');
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
            .addRule('password', {
                required: true,
                requiredMessage: 'Password is required'
            });

        // Setup real-time validation
        this.validator.setupRealTimeValidation();
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
        const credentials = {
            email: formData.get('email'),
            password: formData.get('password')
        };

        this.setLoading(true);

        try {
            const result = await authManager.login(credentials.email, credentials.password);

            if (result.success) {
                // Get user info to determine redirect destination
                const user = authManager.getUser();
                console.log('🔥 LOGIN - User data after login:', user);
                
                // Determine redirect URL based on user role
                let redirectUrl = '/frontend/public/trainer.html'; // Default for trainers
                let dashboardType = 'trainer dashboard';
                
                if (user && user.is_superuser) {
                    redirectUrl = '/frontend/public/admin.html';
                    dashboardType = 'admin dashboard';
                    console.log('🔥 LOGIN - Admin user detected, redirecting to admin.html');
                } else {
                    console.log('🔥 LOGIN - Regular trainer, redirecting to trainer.html');
                }
                
                showAlert(`Login successful! Redirecting to ${dashboardType}...`, 'success');
                
                // Redirect after short delay
                setTimeout(() => {
                    window.location.href = redirectUrl;
                }, 1500);
            } else {
                showAlert(result.message || 'Invalid email or password.', 'error');
            }
        } catch (error) {
            console.error('Login error:', error);
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
    new LoginForm();
});