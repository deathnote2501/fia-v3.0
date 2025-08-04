/**
 * FIA v3.0 - Unified Training Page Initialization
 * Handles complete learner journey: token validation → profile → plan → training
 * Now with i18n support for learners
 */

import { initializeFIAApp } from '../main.js';

// Safe translation function with user-friendly fallbacks
function t(key) {
    if (window.t) {
        return window.t(key);
    }
    
    // User-friendly fallbacks for common keys
    const fallbacks = {
        'status.validatingSession': 'Validating Session',
        'status.validatingSessionMessage': 'Please wait while we verify your session...',
        'status.generatingPlan': 'Generating Your Training Plan',
        'status.generatingPlanMessage': 'This may take a few moments...',
        'status.loadingSession': 'Loading Your Session',
        'status.loadingSessionMessage': 'Loading your training content...',
        'status.loading': 'Loading...',
        'status.loadingGeneric': 'Loading...',
        'status.loadingTrainings': 'Loading trainings...',
        'status.loadingSlideContent': 'Loading slide content...',
        'status.loadingData': 'Loading data...',
        'error.generic': 'An error occurred',
        'error.loadingTrainings': 'Error loading trainings',
        'error.loadingSessions': 'Error loading sessions',
        'error.loadingData': 'Error loading data'
    };
    
    return fallbacks[key] || 'Loading...';
}

// Application States
const APP_STATES = {
    VALIDATING: 'validating',
    PROFILE_FORM: 'profile_form',
    GENERATING_PLAN: 'generating_plan',
    LOADING_SLIDE: 'loading_slide',
    TRAINING_ACTIVE: 'training_active',
    ERROR: 'error'
};

/**
 * Unified Training Application
 * Manages all states: validation, profile, plan generation, and training
 */
class UnifiedTrainingApp {
    constructor() {
        this.currentState = APP_STATES.VALIDATING;
        this.token = null;
        this.sessionData = null;
        this.learnerSession = null;
        this.progressAnimationInterval = null;
        
        console.log('🚀 [UNIFIED-APP] UnifiedTrainingApp initialized');
    }
    
    /**
     * Initialize the complete application workflow
     */
    async init() {
        try {
            console.log('🌟 [UNIFIED-APP] Starting unified training application...');
            
            // Initialize i18n first to avoid showing keys
            await this.initializeI18n();
            
            await this.validateToken();
            await this.checkProfileAndPlan();
            
        } catch (error) {
            console.error('❌ [UNIFIED-APP] Application initialization failed:', error);
            this.showErrorState('Application Error', error.message);
        }
    }
    
    /**
     * Initialize i18n service
     */
    async initializeI18n() {
        try {
            const { initializeI18n, setupGlobalTranslation } = await import('./i18n/i18n-helper.js');
            await initializeI18n();
            setupGlobalTranslation();
            
            // Re-translate any existing content after i18n is ready
            this.refreshTranslations();
            
            console.log('✅ [UNIFIED-APP] i18n initialized successfully');
        } catch (error) {
            console.warn('⚠️ [UNIFIED-APP] Failed to initialize i18n:', error);
            // Continue with fallback behavior
        }
        
        // 🔥 FORCE REFRESH TRANSLATIONS ALWAYS (even on error/fallback)
        this.forceRefreshTranslations();
    }
    
    /**
     * Refresh all translations in the current view
     */
    refreshTranslations() {
        // Update all elements with data-i18n attributes
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            if (window.t) {
                element.textContent = window.t(key);
            }
        });
        
        // 🔥 CORRECTION TOOLTIPS: Update all tooltips with data-i18n-title attributes
        document.querySelectorAll('[data-i18n-title]').forEach(element => {
            const key = element.getAttribute('data-i18n-title');
            if (window.t) {
                element.title = window.t(key);
            }
        });
        
        // 🔥 CORRECTION PLACEHOLDER: Update all placeholders with data-i18n-placeholder attributes
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            if (window.t) {
                element.placeholder = window.t(key);
            }
        });
        
        // Re-render current state with proper translations
        if (this.currentState === APP_STATES.VALIDATING) {
            this.showValidatingState();
        }
    }
    
    /**
     * 🔥 FORCE REFRESH ALL TRANSLATIONS (tooltips, placeholders, text) - ALWAYS
     */
    forceRefreshTranslations() {
        console.log('🔥 [UNIFIED-APP] Force refreshing all i18n translations...');
        
        // Wait a bit to ensure i18n is fully loaded
        setTimeout(() => {
            // Update all text elements with data-i18n attributes
            document.querySelectorAll('[data-i18n]').forEach(element => {
                const key = element.getAttribute('data-i18n');
                if (window.t) {
                    element.textContent = window.t(key);
                } else if (window.safeT) {
                    element.textContent = window.safeT(key);
                }
            });
            
            // 🔥 CORRECTION TOOLTIPS: Update all tooltips with data-i18n-title attributes
            document.querySelectorAll('[data-i18n-title]').forEach(element => {
                const key = element.getAttribute('data-i18n-title');
                if (window.t) {
                    element.title = window.t(key);
                } else if (window.safeT) {
                    element.title = window.safeT(key);
                }
            });
            
            // 🔥 CORRECTION PLACEHOLDER: Update all placeholders with data-i18n-placeholder attributes
            document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
                const key = element.getAttribute('data-i18n-placeholder');
                if (window.t) {
                    element.placeholder = window.t(key);
                } else if (window.safeT) {
                    element.placeholder = window.safeT(key);
                }
            });
            
            console.log('🔥 [UNIFIED-APP] All i18n translations force refreshed completed');
        }, 200); // Small delay to ensure i18n is fully loaded
    }
    
    /**
     * Validate session token
     */
    async validateToken() {
        console.log('🔑 [UNIFIED-APP] State: VALIDATING');
        this.currentState = APP_STATES.VALIDATING;
        this.showValidatingState();
        
        // Get token from URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        this.token = urlParams.get('token');
        
        if (!this.token) {
            throw new Error('No session token found in URL. Please access via proper session link.');
        }
        
        // Validate token with API
        console.log('🔄 [UNIFIED-APP] Validating token with API...');
        const sessionUrl = window.buildSecureApiUrl ? window.buildSecureApiUrl(`/api/session/${this.token}`) : `/api/session/${this.token}`;
        console.log('🔧 [DEBUG] Session validation URL:', sessionUrl);
        const response = await fetch(sessionUrl);
        
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Invalid or expired session token');
            }
            throw new Error('Unable to validate session. Please try again.');
        }
        
        this.sessionData = await response.json();
        this.learnerSession = this.sessionData.learner_session || {
            id: this.sessionData.id,
            language: this.sessionData.language || 'fr'
        };
        
        console.log('✅ [UNIFIED-APP] Token validation successful');
    }
    
    /**
     * Check profile and plan status, decide next state
     */
    async checkProfileAndPlan() {
        console.log('🔍 [UNIFIED-APP] Checking profile and plan status...');
        
        // Check if learner session exists (which means profile exists)
        const profileExists = this.learnerSession && this.learnerSession.id;
        
        if (!profileExists) {
            console.log('📝 [UNIFIED-APP] No profile found - State: PROFILE_FORM');
            this.currentState = APP_STATES.PROFILE_FORM;
            this.showProfileForm();
            return;
        }
        
        console.log('✅ [UNIFIED-APP] Profile exists, checking plan/slides...');
        
        // Profile exists, check if slides exist
        const slideExists = await this.checkIfSlideExists();
        
        if (!slideExists) {
            console.log('🎯 [UNIFIED-APP] No slide found - State: GENERATING_PLAN');
            this.currentState = APP_STATES.GENERATING_PLAN;
            await this.generateTrainingPlan();
            return;
        }
        
        // Profile and slides exist, load training
        console.log('🎓 [UNIFIED-APP] Profile and slides exist - State: LOADING_SLIDE');
        this.currentState = APP_STATES.LOADING_SLIDE;
        await this.loadTrainingContent();
    }
    
    
    /**
     * Check if slides exist by trying to get current slide
     */
    async checkIfSlideExists() {
        try {
            if (!this.learnerSession || !this.learnerSession.id) return false;
            
            const currentSlideUrl = window.buildSecureApiUrl ? window.buildSecureApiUrl(`/api/slides/session/${this.learnerSession.id}/current`) : `/api/slides/session/${this.learnerSession.id}/current`;
            console.log('🔧 [DEBUG] Current slide check URL:', currentSlideUrl);
            const response = await fetch(currentSlideUrl);
            const exists = response.ok;
            console.log(`🔍 [UNIFIED-APP] Slide exists check: ${exists}`);
            return exists;
        } catch (error) {
            console.error('⚠️ [UNIFIED-APP] Error checking slide existence:', error);
            return false;
        }
    }
    
    // ========================================
    // PROGRESS BAR ANIMATION METHODS
    // ========================================
    
    /**
     * Start progress bar animation (0% to 100% in 60 seconds)
     */
    startProgressAnimation() {
        const progressBar = document.getElementById('loading-progress-bar');
        if (!progressBar) return;
        
        const duration = 60000; // 60 seconds
        const intervalTime = 100; // Update every 100ms
        const totalSteps = duration / intervalTime;
        let currentStep = 0;
        
        // Clear any existing animation
        this.stopProgressAnimation();
        
        console.log('🎬 [UNIFIED-APP] Starting progress animation (60s)');
        
        this.progressAnimationInterval = setInterval(() => {
            currentStep++;
            const progress = Math.min((currentStep / totalSteps) * 100, 100);
            
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress.toString());
            
            // Stop when reaching 100%
            if (progress >= 100) {
                this.stopProgressAnimation();
            }
        }, intervalTime);
    }
    
    /**
     * Stop progress bar animation
     */
    stopProgressAnimation() {
        if (this.progressAnimationInterval) {
            clearInterval(this.progressAnimationInterval);
            this.progressAnimationInterval = null;
            console.log('⏹️ [UNIFIED-APP] Progress animation stopped');
        }
    }
    
    // ========================================
    // STATE DISPLAY METHODS
    // ========================================
    
    /**
     * Show validating state
     */
    showValidatingState() {
        document.getElementById('main-content').innerHTML = `
            <div class="text-center p-5">
                <div class="spinner-border text-primary mb-3" role="status" style="width: 3rem; height: 3rem;">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <h4>${t('status.validatingSession')}</h4>
                <p class="mt-3 text-muted">${t('status.validatingSessionMessage')}</p>
            </div>
        `;
    }
    
    /**
     * Show profile form adapted for 16:9 layout
     */
    showProfileForm() {
        console.log('📝 [UNIFIED-APP] Displaying profile form');
        
        document.getElementById('main-content').innerHTML = `
            <div class="container-fluid h-100 py-4">
                <div class="row justify-content-center h-100">
                    <div class="col-12">
                        <!-- Session Info -->
                        ${this.sessionData.session_description ? 
                            `<div class="alert alert-info mb-4">
                                <i class="bi bi-info-circle me-2"></i>
                                ${this.sessionData.session_description}
                            </div>` : 
                            ''
                        }
                        
                        <!-- Profile Form -->
                        <div class="card border-0 shadow-sm">
                            <h1 class="mb-0">
                                <i class="bi bi-person-plus me-2"></i>
                                Complete Your Learner Profile
                            </h1>
                            <div class="card-body p-4">
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

                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="mb-3">
                                                <label for="job_and_sector" class="form-label">Job Position & Sector *</label>
                                                <input type="text" class="form-control" id="job_and_sector" name="job_and_sector" required>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="mb-3">
                                                <label for="objectives" class="form-label">Training Objectives *</label>
                                                <input type="text" class="form-control" id="objectives" name="objectives" required>                                            
                                            </div>
                                        </div>
                                    </div>

                                    <div class="row">
                                        <div class="col-md-6">
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
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="mb-4">
                                                <label for="language" class="form-label">Preferred Language</label>
                                                <select class="form-select" id="language" name="language">
                                                    <option value="fr">French</option>
                                                    <option value="en">English</option>
                                                    <option value="es">Español</option>
                                                    <option value="de">Deutsch</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="d-grid">
                                        <button type="submit" class="btn btn-success btn-lg" id="submit-profile-btn">
                                            <i class="bi bi-mortarboard me-2"></i>
                                            Start My Personalized Training
                                        </button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Setup form event listeners
        this.setupProfileFormEventListeners();
    }
    
    /**
     * Setup profile form event listeners and validation
     */
    setupProfileFormEventListeners() {
        const form = document.getElementById('profile-form');
        const submitBtn = document.getElementById('submit-profile-btn');

        if (!form || !submitBtn) {
            console.error('❌ [UNIFIED-APP] Profile form elements not found');
            return;
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleProfileSubmission(form, submitBtn);
        });
        
        console.log('✅ [UNIFIED-APP] Profile form event listeners setup complete');
    }
    
    /**
     * Handle profile form submission
     */
    async handleProfileSubmission(form, submitBtn) {
        try {
            console.log('📤 [UNIFIED-APP] Processing profile form submission...');
            
            // Disable submit button and show loading state
            this.setSubmitButtonState(submitBtn, true, 'Saving Profile...');
            
            // Extract and validate form data
            const profileData = this.extractFormData(form);
            this.validateFormData(profileData);
            
            // Submit to API
            await this.submitProfileData(profileData);
            
            // Store profile data for plan generation
            this.submittedProfileData = profileData;
            
            // Profile saved successfully, move to plan generation
            console.log('✅ [UNIFIED-APP] Profile saved, transitioning to plan generation');
            this.currentState = APP_STATES.GENERATING_PLAN;
            await this.generateTrainingPlan();
            
        } catch (error) {
            console.error('❌ [UNIFIED-APP] Profile form submission error:', error);
            
            // Show error in form
            this.showFormError(form, error.message);
            
            // Re-enable submit button
            this.setSubmitButtonState(submitBtn, false, 'Start My Personalized Training');
        }
    }
    
    // ========================================
    // PROFILE FORM UTILITY METHODS
    // ========================================
    
    /**
     * Extract form data into a structured object
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
        
        console.log('📋 [UNIFIED-APP] Form data extracted:', profileData);
        return profileData;
    }
    
    /**
     * Validate form data
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
        
        console.log('✅ [UNIFIED-APP] Form data validation passed');
    }
    
    /**
     * Submit profile data to API
     */
    async submitProfileData(profileData) {
        console.log('🌐 [UNIFIED-APP] Submitting profile to API...');
        
        const profileUrl = window.buildSecureApiUrl ? window.buildSecureApiUrl(`/api/session/${this.token}/profile`) : `/api/session/${this.token}/profile`;
        console.log('🔧 [DEBUG] Profile submission URL:', profileUrl);
        const response = await fetch(profileUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(profileData)
        });
        
        console.log('📥 [UNIFIED-APP] API response status:', response.status);
        
        if (!response.ok) {
            const errorMessage = await this.parseAPIError(response);
            throw new Error(errorMessage);
        }
        
        // Get the created learner session data including the ID
        const learnerSessionData = await response.json();
        console.log('👤 [UNIFIED-APP] Learner session created:', learnerSessionData);
        
        // Update our learnerSession with the new data including the ID
        this.learnerSession = {
            ...this.learnerSession,
            ...learnerSessionData
        };
        
        console.log('✅ [UNIFIED-APP] Profile submitted successfully, learner session ID:', this.learnerSession.id);
    }
    
    /**
     * Parse API error response
     */
    async parseAPIError(response) {
        let errorMessage = 'Failed to save profile';
        
        try {
            const errorData = await response.json();
            console.error('🔍 [UNIFIED-APP] Server error data:', errorData);
            
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
     */
    setSubmitButtonState(submitBtn, disabled, text) {
        submitBtn.disabled = disabled;
        const icon = disabled ? 'bi-hourglass-split' : 'bi-mortarboard';
        submitBtn.innerHTML = `<i class="bi ${icon} me-2"></i>${text}`;
    }
    
    /**
     * Show error message in the form
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
        
        console.log('⚠️ [UNIFIED-APP] Error displayed in form');
    }
    
    // ========================================
    // PLAN GENERATION AND TRAINING METHODS
    // ========================================
    
    /**
     * Generate training plan
     */
    async generateTrainingPlan() {
        console.log('🎯 [UNIFIED-APP] Starting training plan generation...');
        
        // Show plan generation state
        document.getElementById('main-content').innerHTML = `
            <div class="text-center p-5">
                <h3>${t('status.generatingPlan')}</h3>
                <div class="progress mt-3" style="height: 25px;">
                    <div id="loading-progress-bar" class="progress-bar progress-bar-striped progress-bar-animated" 
                         role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">
                    </div>
                </div>
                <p class="mt-3 text-muted">${t('status.generatingPlanMessage')}</p>
            </div>
        `;
        
        // Start progress bar animation (0% to 100% in 60 seconds)
        this.startProgressAnimation();
        
        try {
            if (!this.sessionData?.training_session?.training_id) {
                throw new Error('No training ID available in session data');
            }
            
            
            // Generate the training plan using submitted profile data or existing session data
            const profileData = this.submittedProfileData || this.learnerSession || {};
            const generatePlanRequest = {
                training_id: this.sessionData.training_session.training_id,
                learner_session_id: this.learnerSession.id,
                learner_profile: {
                    // Required fields from new schema
                    experience_level: profileData.experience_level || 'intermediate',
                    language: profileData.language || 'fr',
                    
                    // New fields from profile refactoring
                    job_and_sector: profileData.job_and_sector || profileData.job_position,
                    objectives: profileData.objectives,
                    training_duration: profileData.training_duration,
                    
                    // Legacy fields for backward compatibility
                    learning_style: 'visual', // Default since not collected in form
                    job_position: profileData.job_and_sector || profileData.job_position,
                    activity_sector: profileData.job_and_sector || profileData.activity_sector,
                    country: profileData.country || 'France'
                },
                force_regenerate: true
            };
            
            console.log('📝 [UNIFIED-APP] Plan generation request:', generatePlanRequest);
            const planApiUrl = window.buildSecureApiUrl ? window.buildSecureApiUrl('/api/generate-plan-integrated') : '/api/generate-plan-integrated';
            console.log('🔧 [DEBUG] Plan API URL:', planApiUrl);
            const planResponse = await fetch(planApiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(generatePlanRequest)
            });
            
            if (!planResponse.ok) {
                let errorMessage = 'Failed to generate training plan';
                try {
                    const errorData = await planResponse.json();
                    if (typeof errorData.detail === 'string') {
                        errorMessage = errorData.detail;
                    } else if (typeof errorData.message === 'string') {
                        errorMessage = errorData.message;
                    }
                } catch (parseError) {
                    errorMessage = `HTTP ${planResponse.status}: ${planResponse.statusText}`;
                }
                throw new Error(errorMessage);
            }
            
            const planData = await planResponse.json();
            console.log('✅ [UNIFIED-APP] Training plan generated successfully:', planData);
            
            // Plan generated, now send resume email to learner (non-blocking)
            await this.sendResumeEmailToLearner();
            
            // Plan generated, now load training content
            this.currentState = APP_STATES.LOADING_SLIDE;
            await this.loadTrainingContent();
            
        } catch (error) {
            console.error('❌ [UNIFIED-APP] Training plan generation failed:', error);
            this.showErrorState('Plan Generation Failed', `Unable to generate your training plan: ${error.message}`);
        } finally {
            // Stop progress animation
            this.stopProgressAnimation();
        }
    }
    
    /**
     * Send resume email to learner (non-blocking, silent errors)
     */
    async sendResumeEmailToLearner() {
        try {
            console.log('📧 [UNIFIED-APP] Sending resume email to learner...');
            
            // Check if we have the necessary data
            if (!this.learnerSession?.id || !this.submittedProfileData?.email) {
                console.warn('⚠️ [UNIFIED-APP] Missing session ID or email, skipping resume email');
                return;
            }
            
            const emailRequest = {
                email: this.submittedProfileData.email,
                language: this.submittedProfileData.language || 'fr'
            };
            
            console.log('📧 [UNIFIED-APP] Sending resume email with data:', emailRequest);
            
            const emailUrl = window.buildSecureApiUrl ? window.buildSecureApiUrl(`/api/sessions/${this.learnerSession.id}/send-resume-link`) : `/api/sessions/${this.learnerSession.id}/send-resume-link`;
            console.log('🔧 [DEBUG] Resume email URL:', emailUrl);
            const emailResponse = await fetch(emailUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(emailRequest)
            });
            
            if (emailResponse.ok) {
                const emailResult = await emailResponse.json();
                console.log('✅ [UNIFIED-APP] Resume email sent successfully:', emailResult);
            } else {
                // Log error but don't throw - this is non-blocking
                const errorText = await emailResponse.text().catch(() => 'Unknown error');
                console.warn(`⚠️ [UNIFIED-APP] Resume email failed (${emailResponse.status}): ${errorText}`);
            }
            
        } catch (error) {
            // Silent error handling - email is optional feature
            console.warn('⚠️ [UNIFIED-APP] Resume email error (non-critical):', error.message);
        }
    }
    
    /**
     * Load training content (slides)
     */
    async loadTrainingContent() {
        console.log('📄 [UNIFIED-APP] Loading training content...');
        
        // Show loading slide state
        document.getElementById('main-content').innerHTML = `
            <div class="text-center p-5">
                <div class="spinner-border text-primary mb-3" role="status" style="width: 3rem; height: 3rem;">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <h4>${t('status.loadingSession')}</h4>
                <p class="mt-3 text-muted">${t('status.loadingSessionMessage')}</p>
            </div>
        `;
        
        try {
            // Initialize the FIA application for training
            await initializeFIAApp(this.learnerSession, this.sessionData);
            
            // Try to load current slide
            const currentSlideUrl2 = window.buildSecureApiUrl ? window.buildSecureApiUrl(`/api/slides/session/${this.learnerSession.id}/current`) : `/api/slides/session/${this.learnerSession.id}/current`;
            console.log('🔧 [DEBUG] Current slide load URL:', currentSlideUrl2);
            const slideResponse = await fetch(currentSlideUrl2);
            
            if (slideResponse.ok) {
                const slideData = await slideResponse.json();
                console.log('✅ [UNIFIED-APP] Current slide loaded:', slideData);
                
                this.currentState = APP_STATES.TRAINING_ACTIVE;
                // Display the slide content
                window.fiaApp.displaySlideContent(slideData.data || slideData);
            } else {
                // No current slide, generate first one
                console.log('🎯 [UNIFIED-APP] Generating first slide...');
                const firstSlideUrl = window.buildSecureApiUrl ? window.buildSecureApiUrl(`/api/slides/generate-first/${this.learnerSession.id}`) : `/api/slides/generate-first/${this.learnerSession.id}`;
                console.log('🔧 [DEBUG] First slide generation URL:', firstSlideUrl);
                const firstSlideResponse = await fetch(firstSlideUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                if (firstSlideResponse.ok) {
                    const firstSlideData = await firstSlideResponse.json();
                    console.log('✅ [UNIFIED-APP] First slide generated:', firstSlideData);
                    
                    this.currentState = APP_STATES.TRAINING_ACTIVE;
                    window.fiaApp.displaySlideContent(firstSlideData.data || firstSlideData);
                } else {
                    throw new Error('Failed to generate first slide');
                }
            }
            
        } catch (error) {
            console.error('❌ [UNIFIED-APP] Error loading training content:', error);
            this.showErrorState('Training Load Failed', `Unable to load your training content: ${error.message}`);
        }
    }
    
    /**
     * Show error state
     */
    showErrorState(title, message) {
        this.currentState = APP_STATES.ERROR;
        
        document.getElementById('main-content').innerHTML = `
            <div class="text-center p-5">
                <div class="text-danger mb-3">
                    <i class="bi bi-exclamation-triangle display-1"></i>
                </div>
                <h4 class="text-danger">${title}</h4>
                <p class="text-muted mb-4">${message}</p>
                <button class="btn btn-primary" onclick="location.reload()">
                    <i class="bi bi-arrow-clockwise me-2"></i>
                    Try Again
                </button>
            </div>
        `;
    }
}

/**
 * Initialize the unified training application
 */
async function initializeTrainingPage() {
    try {
        console.log('🌟 [UNIFIED-APP] Training page loaded, starting unified application...');
        
        // Create and initialize the unified application
        const unifiedApp = new UnifiedTrainingApp();
        await unifiedApp.init();
        
        // Make app globally available for debugging
        window.unifiedApp = unifiedApp;
        
        console.log('✅ [UNIFIED-APP] Unified training application initialized successfully');
        
    } catch (error) {
        console.error('❌ [UNIFIED-APP] Failed to initialize unified training application:', error);
        
        // Fallback error display
        const container = document.getElementById('main-content');
        if (container) {
            container.innerHTML = `
                <div class="text-center p-5">
                    <div class="text-danger mb-3">
                        <i class="bi bi-exclamation-triangle display-1"></i>
                    </div>
                    <h4 class="text-danger">Application Error</h4>
                    <p class="text-muted mb-4">Failed to initialize the training application: ${error.message}</p>
                    <button class="btn btn-primary" onclick="location.reload()">
                        <i class="bi bi-arrow-clockwise me-2"></i>
                        Try Again
                    </button>
                </div>
            `;
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeTrainingPage);