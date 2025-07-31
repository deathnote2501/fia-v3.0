/**
 * FIA v3.0 - Profile Form Component
 * Handles learner profile form generation, validation and submission
 */

export class ProfileForm {
    constructor(token, sessionData) {
        this.token = token;
        this.sessionData = sessionData;
        this.onSubmitSuccess = null; // Callback for successful submission
        this.onSubmitError = null; // Callback for submission error
        
        console.log('📝 [PROFILE-FORM] ProfileForm initialized');
    }
    
    /**
     * Generate profile form HTML
     * @returns {string} Complete profile form HTML
     */
    generateFormHTML() {
        return `
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <!-- Session Info Card -->
                    <div class="card border-0 shadow-sm mb-4">
                        <div class="card-body">
                            <div class="d-flex align-items-center">
                                <div class="bg-success rounded-circle p-2 me-3">
                                    <i class="bi bi-check-circle text-white"></i>
                                </div>
                                <div>
                                    <h5 class="card-title mb-1">Welcome to Training Session</h5>
                                    <h6 class="card-subtitle text-muted">${this.sessionData.session_name}</h6>
                                </div>
                            </div>
                            ${this.sessionData.session_description ? 
                                `<p class="card-text mt-3 mb-0">${this.sessionData.session_description}</p>` : 
                                ''
                            }
                        </div>
                    </div>

                    <!-- Profile Form Card -->
                    <div class="card border-0 shadow-sm">
                        <div class="card-header bg-primary text-white">
                            <h5 class="mb-0">
                                <i class="bi bi-person-plus me-2"></i>
                                Complete Your Learner Profile
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="alert alert-info">
                                <i class="bi bi-info-circle me-2"></i>
                                Please provide your information to personalize your learning experience.
                            </div>

                            <form id="profile-form">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="email" class="form-label">Email Address *</label>
                                            <input type="email" class="form-control" id="email" name="email" required 
                                                   placeholder="your.email@example.com">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="experience_level" class="form-label">Experience Level *</label>
                                            <select class="form-select" id="experience_level" name="experience_level" required>
                                                <option value="">Choose your level...</option>
                                                <option value="beginner">Beginner</option>
                                                <option value="intermediate">Intermediate</option>
                                                <option value="advanced">Advanced</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>

                                <div class="mb-3">
                                    <label for="job_and_sector" class="form-label">Job Position & Sector *</label>
                                    <input type="text" class="form-control" id="job_and_sector" name="job_and_sector" required 
                                           placeholder="e.g., Software Developer in Information Technology">
                                    <div class="form-text">Your current job position and the sector you work in</div>
                                </div>

                                <div class="mb-3">
                                    <label for="objectives" class="form-label">Training Objectives *</label>
                                    <textarea class="form-control" id="objectives" name="objectives" rows="3" required 
                                              minlength="5" maxlength="1000"
                                              placeholder="What do you hope to achieve with this training? What specific skills or knowledge are you looking to gain?"></textarea>
                                    <div class="form-text">Help us personalize your learning experience (minimum 5 characters)</div>
                                </div>

                                <div class="mb-3">
                                    <label for="training_duration" class="form-label">Preferred Training Duration *</label>
                                    <select class="form-select" id="training_duration" name="training_duration" required>
                                        <option value="">Choose your preferred duration...</option>
                                        <option value="2h">2 hours</option>
                                        <option value="4h">4 hours</option>
                                        <option value="6h">6 hours</option>
                                        <option value="1 jour">1 day</option>
                                        <option value="1.5 jour">1.5 days</option>
                                        <option value="2 jours">2 days</option>
                                        <option value="3 jours">3 days</option>
                                    </select>
                                    <div class="form-text">This will help us structure the appropriate number of modules and slides</div>
                                </div>

                                <div class="mb-4">
                                    <label for="language" class="form-label">Preferred Language</label>
                                    <select class="form-select" id="language" name="language">
                                        <option value="fr">French</option>
                                        <option value="en">English</option>
                                        <option value="es">Español</option>
                                        <option value="de">Deutsch</option>
                                    </select>
                                    <div class="form-text">Language for the training content and AI interactions</div>
                                </div>

                                <div class="d-grid">
                                    <button type="submit" class="btn btn-success btn-lg" id="submit-profile-btn">
                                        <i class="bi bi-arrow-right me-2"></i>
                                        Start My Personalized Training
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Setup form event listeners and validation
     */
    setupFormEventListeners() {
        const form = document.getElementById('profile-form');
        const submitBtn = document.getElementById('submit-profile-btn');

        if (!form || !submitBtn) {
            console.error('❌ [PROFILE-FORM] Form elements not found');
            return;
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleFormSubmission(form, submitBtn);
        });
        
        console.log('✅ [PROFILE-FORM] Form event listeners setup complete');
    }
    
    /**
     * Handle form submission
     * @param {HTMLFormElement} form - The form element
     * @param {HTMLButtonElement} submitBtn - The submit button element
     */
    async handleFormSubmission(form, submitBtn) {
        try {
            console.log('📤 [PROFILE-FORM] Processing form submission...');
            
            // Disable submit button and show loading state
            this.setSubmitButtonState(submitBtn, true, 'Saving Profile...');
            
            // Extract and validate form data
            const profileData = this.extractFormData(form);
            this.validateFormData(profileData);
            
            // Submit to API
            await this.submitProfileData(profileData);
            
            // Call success callback
            if (this.onSubmitSuccess) {
                this.onSubmitSuccess();
            }
            
        } catch (error) {
            console.error('❌ [PROFILE-FORM] Form submission error:', error);
            
            // Show error in form
            this.showFormError(form, error.message);
            
            // Call error callback
            if (this.onSubmitError) {
                this.onSubmitError(error);
            }
            
            // Re-enable submit button
            this.setSubmitButtonState(submitBtn, false, 'Start My Personalized Training');
        }
    }
    
    /**
     * Extract form data into a structured object
     * @param {HTMLFormElement} form - The form element
     * @returns {Object} Structured profile data
     */
    extractFormData(form) {
        const formData = new FormData(form);
        const profileData = {
            email: formData.get('email'),
            experience_level: formData.get('experience_level'),
            job_and_sector: formData.get('job_and_sector'),
            objectives: formData.get('objectives'),
            training_duration: formData.get('training_duration'),
            language: formData.get('language') || 'fr'
        };
        
        console.log('📋 [PROFILE-FORM] Form data extracted:', profileData);
        return profileData;
    }
    
    /**
     * Validate form data
     * @param {Object} profileData - Profile data to validate
     * @throws {Error} If validation fails
     */
    validateFormData(profileData) {
        // Validate objectives length
        if (!profileData.objectives || profileData.objectives.trim().length < 5) {
            throw new Error('Training objectives must be at least 5 characters long');
        }
        
        // Validate required fields
        const requiredFields = ['email', 'experience_level', 'job_and_sector', 'training_duration'];
        for (const field of requiredFields) {
            if (!profileData[field] || profileData[field].trim() === '') {
                throw new Error(`${field.replace('_', ' ')} is required`);
            }
        }
        
        console.log('✅ [PROFILE-FORM] Form data validation passed');
    }
    
    /**
     * Submit profile data to API
     * @param {Object} profileData - Profile data to submit
     * @throws {Error} If API request fails
     */
    async submitProfileData(profileData) {
        console.log('🌐 [PROFILE-FORM] Submitting to API...');
        
        const response = await fetch(`/api/session/${this.token}/profile`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(profileData)
        });
        
        console.log('📥 [PROFILE-FORM] API response status:', response.status);
        
        if (!response.ok) {
            const errorMessage = await this.parseAPIError(response);
            throw new Error(errorMessage);
        }
        
        console.log('✅ [PROFILE-FORM] Profile submitted successfully');
    }
    
    /**
     * Parse API error response
     * @param {Response} response - Failed API response
     * @returns {Promise<string>} Error message
     */
    async parseAPIError(response) {
        let errorMessage = 'Failed to save profile';
        
        try {
            const errorData = await response.json();
            console.error('🔍 [PROFILE-FORM] Server error data:', errorData);
            
            if (errorData.detail) {
                if (typeof errorData.detail === 'string') {
                    errorMessage = errorData.detail;
                } else if (Array.isArray(errorData.detail)) {
                    // Pydantic validation errors
                    errorMessage = errorData.detail.map(err => 
                        `${err.loc?.join?.('.')} (${err.type}): ${err.msg}`
                    ).join('; ');
                } else {
                    errorMessage = JSON.stringify(errorData.detail);
                }
            } else {
                errorMessage = JSON.stringify(errorData);
            }
        } catch (parseError) {
            errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        }
        
        return errorMessage;
    }
    
    /**
     * Set submit button state
     * @param {HTMLButtonElement} submitBtn - Submit button element
     * @param {boolean} disabled - Whether button should be disabled
     * @param {string} text - Button text
     */
    setSubmitButtonState(submitBtn, disabled, text) {
        submitBtn.disabled = disabled;
        const icon = disabled ? 'bi-hourglass-split' : 'bi-arrow-right';
        submitBtn.innerHTML = `<i class="bi ${icon} me-2"></i>${text}`;
    }
    
    /**
     * Show error message in the form
     * @param {HTMLFormElement} form - Form element
     * @param {string} errorMessage - Error message to display
     */
    showFormError(form, errorMessage) {
        // Remove existing error alerts
        const existingAlerts = form.querySelectorAll('.alert-danger');
        existingAlerts.forEach(alert => alert.remove());
        
        // Create error alert
        const alertContainer = document.createElement('div');
        alertContainer.className = 'alert alert-danger alert-dismissible';
        alertContainer.innerHTML = `
            <i class="bi bi-exclamation-triangle me-2"></i>
            <strong>Error:</strong> ${errorMessage}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at beginning of form
        form.insertBefore(alertContainer, form.firstChild);
        
        console.log('⚠️ [PROFILE-FORM] Error displayed in form');
    }
    
    /**
     * Set callback for successful form submission
     * @param {Function} callback - Success callback function
     */
    setOnSubmitSuccess(callback) {
        this.onSubmitSuccess = callback;
        console.log('✅ [PROFILE-FORM] Success callback set');
    }
    
    /**
     * Set callback for form submission error
     * @param {Function} callback - Error callback function
     */
    setOnSubmitError(callback) {
        this.onSubmitError = callback;
        console.log('✅ [PROFILE-FORM] Error callback set');
    }
}