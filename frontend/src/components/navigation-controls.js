/**
 * FIA v3.0 - Navigation Controls Component
 * Handles breadcrumb updates, progress bar, and navigation button states
 */

// Phase 3: Configuration for slide limitation (shared config)
const SLIDE_LIMIT_CONFIG = {
    MAX_FREE_SLIDES: 10,  // Change this number to modify the slide limit
    CONTACT_EMAIL: 'jerome.iavarone@gmail.com'
};

export class NavigationControls {
    constructor() {
        console.log('🧭 [NAVIGATION-CONTROLS] NavigationControls initialized');
        this.sessionLimits = null; // Cache for session limits
        this.currentToken = this.extractTokenFromURL();
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
     * Show B2C upgrade modal when slide limit is reached
     * @param {Object} sessionLimits - Session limits with contact info
     */
    showB2CUpgradeModal(sessionLimits) {
        console.log('💬 [NAVIGATION-CONTROLS] Showing B2C upgrade modal');
        
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
                                            <i class="bi bi-calendar-year me-2"></i>
                                            ${window.safeT ? window.safeT('b2c.modal.annualSubscription') : 'Abonnement annuel'}
                                        </span>
                                        <strong>49.90€</strong>
                                    </a>
                                </div>
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
                                ${window.safeT ? window.safeT('b2c.modal.limitInfo').replace('{{count}}', sessionLimits.max_slides) : `Aperçu limité à ${sessionLimits.max_slides} slides`}
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
        
        // Remove modal from DOM when hidden
        modal.addEventListener('hidden.bs.modal', function () {
            modal.remove();
        });
    }
}