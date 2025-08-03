/**
 * FIA v3.0 - Navigation Controls Component
 * Handles breadcrumb updates, progress bar, and navigation button states
 */

// Phase 3: Configuration for slide limitation (shared config)
const SLIDE_LIMIT_CONFIG = {
    MAX_FREE_SLIDES: 2,  // Change this number to modify the slide limit
    CONTACT_EMAIL: 'jerome.iavarone@gmail.com'
};

export class NavigationControls {
    constructor() {
        console.log('🧭 [NAVIGATION-CONTROLS] NavigationControls initialized');
        this.sessionLimits = null; // Cache for session limits
        this.currentToken = this.extractTokenFromURL();
        this.mobileHandler = null; // Will be set by main app
        
        // Check for existing unlimited access on initialization
        this.checkExistingUnlimitedAccess();
    }
    
    /**
     * Check for existing unlimited access on page load
     */
    checkExistingUnlimitedAccess() {
        if (this.hasUnlimitedAccess()) {
            console.log('🔓 [NAVIGATION-CONTROLS] Existing unlimited access detected on initialization');
        }
    }
    
    /**
     * Set the mobile interface handler for synchronization
     * @param {MobileInterfaceHandler} mobileHandler - Mobile interface handler instance
     */
    setMobileHandler(mobileHandler) {
        this.mobileHandler = mobileHandler;
        console.log('🧭 [NAVIGATION-CONTROLS] Mobile handler configured');
    }
    
    /**
     * Update breadcrumb navigation with slide data
     * @param {Object} slideData - Slide data containing breadcrumb information
     */
    updateBreadcrumb(slideData) {
        console.log('🧭 [NAVIGATION-CONTROLS] === MISE À JOUR BREADCRUMB ===');
        console.log('🧭 [NAVIGATION-CONTROLS] slideData:', slideData);
        
        const breadcrumbElement = document.getElementById('progress-breadcrumb');
        if (!breadcrumbElement) {
            console.log('⚠️ [NAVIGATION-CONTROLS] Élément progress-breadcrumb non trouvé');
            return;
        }
        
        // Extraire les informations de breadcrumb
        let breadcrumb = null;
        
        // Priorité: breadcrumb direct dans slideData
        if (slideData.breadcrumb) {
            console.log('🧭 [NAVIGATION-CONTROLS] BRANCHE 1: breadcrumb direct détecté');
            breadcrumb = slideData.breadcrumb;
        } else if (slideData.data && slideData.data.breadcrumb) {
            console.log('🧭 [NAVIGATION-CONTROLS] BRANCHE 2: breadcrumb dans data détecté');
            breadcrumb = slideData.data.breadcrumb;
        }
        
        console.log('🧭 [NAVIGATION-CONTROLS] Breadcrumb extrait:', breadcrumb);
        
        // Valeurs par défaut si pas de breadcrumb
        if (!breadcrumb) {
            console.log('🧭 [NAVIGATION-CONTROLS] Utilisation valeurs par défaut');
            breadcrumb = {
                stage_name: "Formation",
                module_name: "Module",
                submodule_name: "Contenu"
            };
        }
        
        // Construire le HTML du breadcrumb avec les styles appropriés
        const breadcrumbHtml = `
            <span class="progress-text">
                ${breadcrumb.stage_name} 
                <i class="bi bi-chevron-right text-muted mx-1"></i> 
                ${breadcrumb.module_name} 
                <i class="bi bi-chevron-right text-muted mx-1"></i> 
                <span class="current-module">${breadcrumb.submodule_name}</span>
            </span>
        `;
        
        console.log('🧭 [NAVIGATION-CONTROLS] HTML généré:', breadcrumbHtml);
        breadcrumbElement.innerHTML = breadcrumbHtml;
        
        console.log('✅ [NAVIGATION-CONTROLS] Breadcrumb mis à jour avec succès');
    }
    
    /**
     * Update navigation button states based on current position
     * @param {Object} currentSlide - Current slide data with position information
     */
    async updateNavigationButtonStates(currentSlide) {
        const newPreviousBtn = document.getElementById('new-previous-btn');
        const newNextBtn = document.getElementById('new-next-btn');
        
        if (!currentSlide || !currentSlide.position) {
            console.log('🔄 [NAVIGATION-CONTROLS] No position data available, keeping buttons enabled');
            return;
        }
        
        const position = currentSlide.position;
        console.log('🔄 [NAVIGATION-CONTROLS] Updating button states:', position);
        
        // Update Previous button
        if (newPreviousBtn) {
            if (position.has_previous === false) {
                newPreviousBtn.disabled = true;
                newPreviousBtn.classList.add('opacity-50');
                console.log('🔄 [NAVIGATION-CONTROLS] Previous button disabled - at beginning');
            } else {
                newPreviousBtn.disabled = false;
                newPreviousBtn.classList.remove('opacity-50');
                console.log('🔄 [NAVIGATION-CONTROLS] Previous button enabled');
            }
        }
        
        // Update Next button with B2C/B2B detection
        if (newNextBtn) {
            const currentPosition = position.current_position || 0;
            
            // Get session limits (B2C/B2B detection)
            const sessionLimits = await this.getSessionLimits();
            
            // Check B2C slide limitation
            if (sessionLimits.has_slide_limit && currentPosition >= sessionLimits.max_slides) {
                newNextBtn.disabled = true;
                newNextBtn.classList.add('opacity-50');
                newNextBtn.innerHTML = '<i class="bi bi-lock me-1"></i>Upgrade Required';
                console.log(`🚫 [NAVIGATION-CONTROLS] Next button disabled - B2C slide limit reached (${currentPosition}/${sessionLimits.max_slides})`);
                
                // Show B2C upgrade modal
                this.showB2CUpgradeModal(sessionLimits);
                
            } else if (position.has_next === false) {
                newNextBtn.disabled = true;
                newNextBtn.classList.add('opacity-50');
                newNextBtn.innerHTML = `<i class="bi bi-check-circle me-1"></i>${window.safeT ? window.safeT('learner.complete') : 'Complete'}`;
            } else {
                newNextBtn.disabled = false;
                newNextBtn.classList.remove('opacity-50');
                newNextBtn.innerHTML = `${window.safeT ? window.safeT('learner.next') : 'Next'}<i class="bi bi-chevron-right ms-1"></i>`;
                console.log('🔄 [NAVIGATION-CONTROLS] Next button enabled');
            }
        }
        
        // Show progress info and update progress bar
        if (position.current_position && position.total_slides) {
            const progressPercentage = Math.round((position.current_position / position.total_slides) * 100);
            console.log(`🔄 [NAVIGATION-CONTROLS] Progress: ${position.current_position}/${position.total_slides} slides (${progressPercentage}%)`);
            
            // Update progress bar
            this.updateProgressBar(progressPercentage);
        }
        
        // Sync mobile button states if mobile handler is available
        if (this.mobileHandler) {
            this.mobileHandler.updateMobileButtonStates();
        }
    }
    
    /**
     * Update the progress bar with the current percentage
     * @param {number} percentage - Progress percentage (0-100)
     */
    updateProgressBar(percentage) {
        const progressBar = document.getElementById('training-progress-bar');
        const progressContainer = progressBar?.parentElement;
        if (progressBar && progressContainer) {
            // Ensure minimum width for visibility
            const displayWidth = Math.max(percentage, 4); // Minimum 4% width for visibility
            
            progressBar.style.width = `${displayWidth}%`;
            progressBar.setAttribute('aria-valuenow', percentage);
            progressBar.textContent = `${percentage}%`;
            
            // Add data attribute for CSS targeting
            progressContainer.setAttribute('data-percentage', percentage);
            
            console.log(`📊 [NAVIGATION-CONTROLS] Progress bar updated to ${percentage}% (display width: ${displayWidth}%)`);
        }
    }
    
    /**
     * Enable navigation buttons
     */
    enableNavigationButtons() {
        const newPreviousBtn = document.getElementById('new-previous-btn');
        const newNextBtn = document.getElementById('new-next-btn');
        
        if (newPreviousBtn) {
            newPreviousBtn.disabled = false;
            newPreviousBtn.classList.remove('opacity-50');
        }
        
        if (newNextBtn) {
            newNextBtn.disabled = false;
            newNextBtn.classList.remove('opacity-50');
        }
        
        console.log('🔄 [NAVIGATION-CONTROLS] Navigation buttons enabled');
    }
    
    /**
     * Disable navigation buttons
     */
    disableNavigationButtons() {
        const newPreviousBtn = document.getElementById('new-previous-btn');
        const newNextBtn = document.getElementById('new-next-btn');
        
        if (newPreviousBtn) {
            newPreviousBtn.disabled = true;
            newPreviousBtn.classList.add('opacity-50');
        }
        
        if (newNextBtn) {
            newNextBtn.disabled = true;
            newNextBtn.classList.add('opacity-50');
        }
        
        console.log('🔄 [NAVIGATION-CONTROLS] Navigation buttons disabled');
    }
    
    /**
     * Set next button to complete state
     */
    setNextButtonComplete() {
        const newNextBtn = document.getElementById('new-next-btn');
        if (newNextBtn) {
            newNextBtn.disabled = true;
            newNextBtn.classList.add('opacity-50');
            newNextBtn.innerHTML = `<i class="bi bi-check-circle me-1"></i>${window.safeT ? window.safeT('learner.complete') : 'Complete'}`;
            console.log('🔄 [NAVIGATION-CONTROLS] Next button set to complete state');
        }
    }
    
    /**
     * Set previous button to beginning state
     */
    setPreviousButtonBeginning() {
        const newPreviousBtn = document.getElementById('new-previous-btn');
        if (newPreviousBtn) {
            newPreviousBtn.disabled = true;
            newPreviousBtn.classList.add('opacity-50');
            newPreviousBtn.innerHTML = `<i class="bi bi-stop-circle me-1"></i>${window.safeT ? window.safeT('learner.beginning') : 'Beginning'}`;
            console.log('🔄 [NAVIGATION-CONTROLS] Previous button set to beginning state');
        }
    }
    
    /**
     * Reset navigation buttons to default state
     */
    resetNavigationButtons() {
        const newPreviousBtn = document.getElementById('new-previous-btn');
        const newNextBtn = document.getElementById('new-next-btn');
        
        if (newPreviousBtn) {
            newPreviousBtn.disabled = false;
            newPreviousBtn.classList.remove('opacity-50');
            newPreviousBtn.innerHTML = `<i class="bi bi-chevron-left me-1"></i>${window.safeT ? window.safeT('learner.previous') : 'Previous'}`;
        }
        
        if (newNextBtn) {
            newNextBtn.disabled = false;
            newNextBtn.classList.remove('opacity-50');
            newNextBtn.innerHTML = `${window.safeT ? window.safeT('learner.next') : 'Next'}<i class="bi bi-chevron-right ms-1"></i>`;
        }
        
        console.log('🔄 [NAVIGATION-CONTROLS] Navigation buttons reset to default state');
    }
    
    /**
     * Get current progress percentage
     * @returns {number} Current progress percentage
     */
    getCurrentProgress() {
        const progressBar = document.getElementById('training-progress-bar');
        if (progressBar) {
            return parseInt(progressBar.getAttribute('aria-valuenow') || '0');
        }
        return 0;
    }
    
    /**
     * Check if at the beginning of training
     * @returns {boolean} True if at beginning
     */
    isAtBeginning() {
        const newPreviousBtn = document.getElementById('new-previous-btn');
        return newPreviousBtn ? newPreviousBtn.disabled : false;
    }
    
    /**
     * Check if at the end of training
     * @returns {boolean} True if at end
     */
    isAtEnd() {
        const newNextBtn = document.getElementById('new-next-btn');
        return newNextBtn ? newNextBtn.disabled && newNextBtn.innerHTML.includes('Complete') : false;
    }
    
    /**
     * Update complete slide data including breadcrumb, buttons, and progress
     * @param {Object} slideData - Complete slide data
     */
    updateNavigationComplete(slideData) {
        // Update breadcrumb
        this.updateBreadcrumb(slideData);
        
        // Update button states if position data is available
        if (slideData.position) {
            this.updateNavigationButtonStates(slideData);
        } else if (slideData.data && slideData.data.position) {
            this.updateNavigationButtonStates(slideData.data);
        }
        
        console.log('✅ [NAVIGATION-CONTROLS] Complete navigation update finished');
    }
    
    /**
     * Extract session token from current URL
     * @returns {string|null} Token if found, null otherwise
     */
    extractTokenFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('token');
    }
    
    /**
     * Get session limits from API with caching
     * @returns {Object} Session limits object
     */
    async getSessionLimits() {
        // Check for unlimited access first (access code unlock)
        if (this.hasUnlimitedAccess()) {
            console.log('🔓 [NAVIGATION-CONTROLS] Unlimited access detected - bypassing limitations');
            return this.getUnlimitedAccessLimits();
        }
        
        // Use cached limits if available
        if (this.sessionLimits) {
            return this.sessionLimits;
        }
        
        const token = this.currentToken;
        if (!token) {
            console.warn('⚠️ [NAVIGATION-CONTROLS] No token found, defaulting to B2B limits');
            return this.getDefaultB2BLimits();
        }
        
        try {
            console.log('🔍 [NAVIGATION-CONTROLS] Fetching session limits from API...');
            
            const response = await fetch(`/api/session/${token}/limits`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const limits = await response.json();
            
            // Cache the limits
            this.sessionLimits = limits;
            
            console.log(`✅ [NAVIGATION-CONTROLS] Session limits retrieved: ${limits.session_type}`, limits);
            return limits;
            
        } catch (error) {
            console.warn('⚠️ [NAVIGATION-CONTROLS] Failed to fetch session limits, using B2B defaults:', error);
            return this.getDefaultB2BLimits();
        }
    }
    
    /**
     * Get default B2B limits (safe fallback)
     * @returns {Object} B2B session limits
     */
    getDefaultB2BLimits() {
        return {
            session_type: 'B2B',
            max_slides: null,
            has_slide_limit: false,
            upgrade_required: false,
            contact_email: null,
            fallback: true
        };
    }
    
    /**
     * Check if unlimited access has been granted via access code
     * @returns {boolean} True if unlimited access is active
     */
    hasUnlimitedAccess() {
        const unlimitedAccess = sessionStorage.getItem('fia_unlimited_access');
        const grantedAt = sessionStorage.getItem('fia_access_granted_at');
        const accessToken = sessionStorage.getItem('fia_access_token');
        
        // Check if access exists and is for current token
        if (unlimitedAccess === 'true' && grantedAt && accessToken === this.currentToken) {
            // Optional: Check if access hasn't expired (24h limit)
            const grantedTime = parseInt(grantedAt);
            const now = Date.now();
            const hoursSinceGrant = (now - grantedTime) / (1000 * 60 * 60);
            
            if (hoursSinceGrant < 24) { // 24 hour expiration
                console.log(`🔓 [NAVIGATION-CONTROLS] Unlimited access valid (granted ${hoursSinceGrant.toFixed(1)}h ago)`);
                return true;
            } else {
                console.log('⏰ [NAVIGATION-CONTROLS] Unlimited access expired, clearing storage');
                this.clearUnlimitedAccess();
                return false;
            }
        }
        
        return false;
    }
    
    /**
     * Get unlimited access limits (bypass all restrictions)
     * @returns {Object} Unlimited session limits
     */
    getUnlimitedAccessLimits() {
        return {
            session_type: 'B2C_UNLIMITED',
            max_slides: null,
            has_slide_limit: false,
            upgrade_required: false,
            access_unlocked: true,
            contact_email: null,
            message: 'Access unlocked with code'
        };
    }
    
    /**
     * Clear unlimited access from storage
     */
    clearUnlimitedAccess() {
        sessionStorage.removeItem('fia_unlimited_access');
        sessionStorage.removeItem('fia_access_granted_at');
        sessionStorage.removeItem('fia_access_token');
        this.sessionLimits = null; // Clear cache
        console.log('🧹 [NAVIGATION-CONTROLS] Unlimited access cleared');
    }
    
    /**
     * Show B2C upgrade modal when slide limit is reached
     * @param {Object} sessionLimits - Session limits with contact info
     */
    showB2CUpgradeModal(sessionLimits) {
        console.log('💬 [NAVIGATION-CONTROLS] Showing B2C upgrade modal');
        console.log('🔍 [NAVIGATION-CONTROLS] window.safeT available:', typeof window.safeT);
        console.log('🔍 [NAVIGATION-CONTROLS] window.i18n available:', typeof window.i18n);
        
        // Test translation functions
        if (window.safeT) {
            console.log('🔍 [NAVIGATION-CONTROLS] Test translations:');
            console.log('   b2c.modal.title:', window.safeT('b2c.modal.title'));
            console.log('   b2c.modal.continueTraining:', window.safeT('b2c.modal.continueTraining'));
        }
        
        // Check if modal already exists to avoid duplicates
        let modal = document.getElementById('b2c-upgrade-modal');
        if (modal) {
            // Modal already exists, just show it
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
            return;
        }
        
        // Create modal HTML with i18n and Stripe payment buttons
        const modalHtml = `
            <div class="modal fade" id="b2c-upgrade-modal" tabindex="-1" aria-labelledby="b2c-upgrade-title" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered modal-lg">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title" id="b2c-upgrade-title">
                                <i class="bi bi-stars me-2"></i>
                                ${window.safeT ? window.safeT('b2c.modal.title') : 'Déverrouillez la Formation Complète'}
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body text-center py-4">
                            <div class="mb-4">
                                <i class="bi bi-lock-fill text-warning" style="font-size: 3rem;"></i>
                            </div>
                            <h6 class="mb-3">${window.safeT ? window.safeT('b2c.modal.limitReached') : 'Vous avez atteint la limite de prévisualisation'}</h6>
                            <p class="text-muted mb-4">
                                ${window.safeT ? window.safeT('b2c.modal.description') : 'Ceci est un aperçu de notre système de formation alimenté par l\'IA. Pour accéder à l\'expérience de formation complète avec des slides illimitées et du contenu personnalisé, choisissez une option ci-dessous.'}
                            </p>
                            
                            <!-- Stripe Payment Options -->
                            <div class="row g-3 mb-4">
                                <!-- Option 1: Continue Training - 6.90€ (Outline Blue) -->
                                <div class="col-12">
                                    <a href="https://buy.stripe.com/00w8wPfPwdqF4Vo7rsgnK0a" 
                                       class="btn btn-outline-primary btn-lg w-100 d-flex justify-content-between align-items-center">
                                        <span>
                                            <i class="bi bi-play-circle me-2"></i>
                                            ${window.safeT ? window.safeT('b2c.modal.continueTraining') : 'Continuer ma formation'}
                                        </span>
                                        <strong>6.90€</strong>
                                    </a>
                                </div>
                                
                                <!-- Option 2: Monthly Subscription - 14.90€ (Blue Background) -->
                                <div class="col-12">
                                    <a href="https://buy.stripe.com/8x214ndHo72hdrU6nognK0b" 
                                       class="btn btn-primary btn-lg w-100 d-flex justify-content-between align-items-center">
                                        <span>
                                            <i class="bi bi-calendar-month me-2"></i>
                                            ${window.safeT ? window.safeT('b2c.modal.monthlySubscription') : 'Abonnement un mois'}
                                        </span>
                                        <strong>14.90€</strong>
                                    </a>
                                </div>
                                
                                <!-- Option 3: Annual Subscription - 49.90€ (Blue Background) -->
                                <div class="col-12">
                                    <a href="https://buy.stripe.com/4gM5kD32KeuJ3RkeTUgnK0c" 
                                       class="btn btn-primary btn-lg w-100 d-flex justify-content-between align-items-center">
                                        <span>
                                            <i class="bi bi-calendar-month me-2"></i>
                                            ${window.safeT ? window.safeT('b2c.modal.annualSubscription') : 'Abonnement annuel'}
                                        </span>
                                        <strong>49.90€</strong>
                                    </a>
                                </div>
                            </div>
                            
                            <!-- Access Code Section -->
                            <div class="mt-4 pt-3 border-top">
                                <h6 class="mb-3 text-center">
                                    ${window.safeT ? window.safeT('b2c.modal.accessCodeTitle') : '💎 Do you have an access code?'}
                                </h6>
                                <div class="input-group mb-3">
                                    <input type="text" id="access-code-input" class="form-control" 
                                           placeholder="${window.safeT ? window.safeT('b2c.modal.accessCodePlaceholder') : 'Enter your code (ex: 2541)'}" 
                                           maxlength="4" style="text-align: center; font-size: 1.1em; font-weight: bold;">
                                    <button class="btn btn-success" id="validate-access-code-btn" type="button">
                                        <i class="bi bi-unlock me-1"></i>
                                        ${window.safeT ? window.safeT('b2c.modal.unlockButton') : 'Unlock'}
                                    </button>
                                </div>
                                <!-- Success/Error Messages -->
                                <div id="access-code-feedback" class="d-none"></div>
                            </div>
                            
                            <!-- Contact Email Button -->
                            <div class="d-grid gap-2">
                                <a href="mailto:${sessionLimits.contact_email}?subject=Demande%20Accès%20Complet%20-%20Formation%20IA" 
                                   class="btn btn-outline-dark">
                                    <i class="bi bi-envelope me-2"></i>
                                    ${window.safeT ? window.safeT('b2c.modal.contactButton') : 'Contacter pour Accès Complet'}
                                </a>
                                <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
                                    ${window.safeT ? window.safeT('b2c.modal.browseContinue') : 'Continuer la Navigation'}
                                </button>
                            </div>
                        </div>
                        <div class="modal-footer bg-light">
                            <small class="text-muted mx-auto">
                                <i class="bi bi-info-circle me-1"></i>
                                ${(() => {
                                    const limitText = window.safeT ? window.safeT('b2c.modal.limitInfo') : 'Aperçu limité à {{count}} slides';
                                    return limitText.replace('{{count}}', sessionLimits.max_slides);
                                })()}
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Show the modal
        modal = document.getElementById('b2c-upgrade-modal');
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // Setup access code validation after modal is shown
        this.setupAccessCodeValidation();
        
        // Remove modal from DOM when hidden
        modal.addEventListener('hidden.bs.modal', function () {
            modal.remove();
        });
    }
    
    /**
     * Setup access code validation event listeners and logic
     */
    setupAccessCodeValidation() {
        console.log('🔒 [NAVIGATION-CONTROLS] Setting up access code validation');
        
        const accessCodeInput = document.getElementById('access-code-input');
        const validateBtn = document.getElementById('validate-access-code-btn');
        const feedbackDiv = document.getElementById('access-code-feedback');
        
        if (!accessCodeInput || !validateBtn || !feedbackDiv) {
            console.warn('⚠️ [NAVIGATION-CONTROLS] Access code elements not found');
            return;
        }
        
        // Event listener for button click
        validateBtn.addEventListener('click', () => {
            this.validateAccessCode(accessCodeInput.value.trim());
        });
        
        // Event listener for Enter key
        accessCodeInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.validateAccessCode(accessCodeInput.value.trim());
            }
        });
        
        // Auto-uppercase and limit to 4 digits
        accessCodeInput.addEventListener('input', (e) => {
            let value = e.target.value.replace(/[^0-9]/g, ''); // Only numbers
            if (value.length > 4) {
                value = value.substring(0, 4);
            }
            e.target.value = value;
        });
        
        console.log('✅ [NAVIGATION-CONTROLS] Access code validation setup complete');
    }
    
    /**
     * Validate access code against encrypted codes
     * @param {string} inputCode - User input code
     */
    validateAccessCode(inputCode) {
        console.log('🔍 [NAVIGATION-CONTROLS] Validating access code:', inputCode);
        
        // Disable button during validation
        const validateBtn = document.getElementById('validate-access-code-btn');
        if (validateBtn) {
            validateBtn.disabled = true;
            validateBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Validating...';
        }
        
        if (!inputCode || inputCode.length !== 4) {
            this.showAccessCodeFeedback(false, window.safeT ? window.safeT('b2c.modal.codeLength') : 'Please enter a 4-digit code');
            this.resetValidateButton();
            return;
        }
        
        // Encrypted access codes (base64 with salt for basic security)
        const ENCRYPTED_ACCESS_CODES = [
            btoa('2541_fia_salt'), // MjU0MV9maWFfc2FsdA==
            btoa('8455_fia_salt'), // ODQ1NV9maWFfc2FsdA==
            btoa('5421_fia_salt')  // NTQyMV9maWFfc2FsdA==
        ];
        
        // Encrypt input code and compare
        const encryptedInput = btoa(inputCode + '_fia_salt');
        const isValid = ENCRYPTED_ACCESS_CODES.includes(encryptedInput);
        
        if (isValid) {
            console.log('✅ [NAVIGATION-CONTROLS] Access code valid - granting unlimited access');
            this.grantUnlimitedAccess();
            
            // Show success with animation
            this.showAccessCodeSuccess();
            
            // Close modal after success animation
            setTimeout(() => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('b2c-upgrade-modal'));
                if (modal) {
                    modal.hide();
                }
                // Refresh navigation buttons to remove limitations
                this.refreshNavigationAfterUnlock();
            }, 2500);
            
        } else {
            console.log('❌ [NAVIGATION-CONTROLS] Access code invalid');
            this.showAccessCodeFeedback(false, window.safeT ? window.safeT('b2c.modal.codeError') : 'Invalid code. Please check your access code.');
            this.resetValidateButton();
        }
    }
    
    /**
     * Show feedback message for access code validation
     * @param {boolean} success - Whether validation was successful
     * @param {string} message - Message to display
     */
    showAccessCodeFeedback(success, message) {
        const feedbackDiv = document.getElementById('access-code-feedback');
        if (!feedbackDiv) return;
        
        const alertClass = success ? 'alert-success' : 'alert-danger';
        const icon = success ? 'bi-check-circle' : 'bi-exclamation-triangle';
        
        feedbackDiv.innerHTML = `
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                <i class="bi ${icon} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        feedbackDiv.classList.remove('d-none');
        
        // Auto-hide error messages after 5 seconds
        if (!success) {
            setTimeout(() => {
                feedbackDiv.classList.add('d-none');
            }, 5000);
        }
    }
    
    /**
     * Grant unlimited access and store in session
     */
    grantUnlimitedAccess() {
        console.log('🔓 [NAVIGATION-CONTROLS] Granting unlimited access');
        
        sessionStorage.setItem('fia_unlimited_access', 'true');
        sessionStorage.setItem('fia_access_granted_at', Date.now().toString());
        sessionStorage.setItem('fia_access_token', this.currentToken || 'unknown');
        
        // Clear cached session limits to force refresh
        this.sessionLimits = null;
        
        console.log('✅ [NAVIGATION-CONTROLS] Unlimited access granted and stored');
    }
    
    /**
     * Refresh navigation buttons after unlock
     */
    refreshNavigationAfterUnlock() {
        console.log('🔄 [NAVIGATION-CONTROLS] Refreshing navigation after unlock');
        
        const newNextBtn = document.getElementById('new-next-btn');
        if (newNextBtn) {
            // Re-enable next button and restore original appearance
            newNextBtn.disabled = false;
            newNextBtn.classList.remove('opacity-50');
            newNextBtn.innerHTML = `${window.safeT ? window.safeT('learner.next') : 'Next'}<i class="bi bi-chevron-right ms-1"></i>`;
            
            console.log('✅ [NAVIGATION-CONTROLS] Next button restored after unlock');
        }
    }
    
    /**
     * Reset validate button to original state
     */
    resetValidateButton() {
        const validateBtn = document.getElementById('validate-access-code-btn');
        if (validateBtn) {
            validateBtn.disabled = false;
            validateBtn.innerHTML = `<i class="bi bi-unlock me-1"></i>${window.safeT ? window.safeT('b2c.modal.unlockButton') : 'Unlock'}`;
        }
    }
    
    /**
     * Show animated success feedback for access code validation
     */
    showAccessCodeSuccess() {
        const feedbackDiv = document.getElementById('access-code-feedback');
        const accessCodeInput = document.getElementById('access-code-input');
        const validateBtn = document.getElementById('validate-access-code-btn');
        
        if (!feedbackDiv) return;
        
        // Success message with animation
        const successMessage = window.safeT ? window.safeT('b2c.modal.codeSuccess') : 'Access unlocked! You can now access all slides.';
        
        feedbackDiv.innerHTML = `
            <div class="alert alert-success alert-dismissible fade show animate__animated animate__fadeIn" role="alert">
                <div class="d-flex align-items-center">
                    <div class="spinner-border spinner-border-sm text-success me-2" role="status" style="display: none;"></div>
                    <i class="bi bi-check-circle-fill me-2" style="font-size: 1.2em;"></i>
                    <strong>${successMessage}</strong>
                </div>
            </div>
        `;
        
        feedbackDiv.classList.remove('d-none');
        
        // Update button to success state
        if (validateBtn) {
            validateBtn.disabled = true;
            validateBtn.classList.remove('btn-success');
            validateBtn.classList.add('btn-success');
            validateBtn.innerHTML = '<i class="bi bi-check-circle-fill me-1"></i>Unlocked!';
        }
        
        // Disable input field (already used)
        if (accessCodeInput) {
            accessCodeInput.disabled = true;
            accessCodeInput.classList.add('bg-light');
        }
        
        // Add success animation to the entire access code section
        const accessCodeSection = document.querySelector('.border-top');
        if (accessCodeSection) {
            accessCodeSection.style.border = '2px solid #198754';
            accessCodeSection.style.borderRadius = '8px';
            accessCodeSection.style.backgroundColor = '#f8fff9';
        }
    }
    
    /**
     * Test function to validate all access codes (for development)
     */
    testAllAccessCodes() {
        console.log('🧪 [NAVIGATION-CONTROLS] Testing all access codes...');
        const testCodes = ['2541', '8455', '5421', '0000']; // Including invalid code
        
        testCodes.forEach((code, index) => {
            console.log(`Testing code ${index + 1}: ${code}`);
            const isValid = this.isValidAccessCode(code);
            console.log(`Result: ${isValid ? '✅ Valid' : '❌ Invalid'}`);
        });
    }
    
    /**
     * Helper method to check if access code is valid (for testing)
     * @param {string} code - Code to test
     * @returns {boolean} True if valid
     */
    isValidAccessCode(code) {
        const ENCRYPTED_ACCESS_CODES = [
            btoa('2541_fia_salt'),
            btoa('8455_fia_salt'),
            btoa('5421_fia_salt')
        ];
        
        const encryptedInput = btoa(code + '_fia_salt');
        return ENCRYPTED_ACCESS_CODES.includes(encryptedInput);
    }
    
    /**
     * Get debug info about current access state (for testing)
     */
    getAccessDebugInfo() {
        return {
            hasUnlimitedAccess: this.hasUnlimitedAccess(),
            currentToken: this.currentToken,
            sessionStorage: {
                unlimited_access: sessionStorage.getItem('fia_unlimited_access'),
                granted_at: sessionStorage.getItem('fia_access_granted_at'),
                access_token: sessionStorage.getItem('fia_access_token')
            },
            sessionLimits: this.sessionLimits,
            validCodes: ['2541', '8455', '5421']
        };
    }
}

// Global testing functions for development/debugging
if (typeof window !== 'undefined') {
    window.fiaTesting = {
        testAccessCodes: function() {
            if (window.navigationControls) {
                window.navigationControls.testAllAccessCodes();
            } else {
                console.warn('NavigationControls not initialized');
            }
        },
        getDebugInfo: function() {
            if (window.navigationControls) {
                return window.navigationControls.getAccessDebugInfo();
            } else {
                console.warn('NavigationControls not initialized');
                return null;
            }
        },
        clearAccess: function() {
            sessionStorage.removeItem('fia_unlimited_access');
            sessionStorage.removeItem('fia_access_granted_at');
            sessionStorage.removeItem('fia_access_token');
            console.log('🧹 Access cleared from sessionStorage');
        },
        simulateCode: function(code) {
            if (window.navigationControls) {
                window.navigationControls.validateAccessCode(code);
            } else {
                console.warn('NavigationControls not initialized');
            }
        }
    };
    
    console.log('🧪 FIA Testing functions available:');
    console.log('   window.fiaTesting.testAccessCodes() - Test all codes');
    console.log('   window.fiaTesting.getDebugInfo() - Get current state');
    console.log('   window.fiaTesting.clearAccess() - Clear unlimited access');
    console.log('   window.fiaTesting.simulateCode("2541") - Test specific code');
}