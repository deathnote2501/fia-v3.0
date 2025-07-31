/**
 * FIA v3.0 - UI State Manager Component
 * Handles different UI states (loading, error, success) for the session page
 */

export class UIStateManager {
    constructor(container) {
        this.container = container;
        console.log('🎨 [UI-STATE-MANAGER] UIStateManager initialized');
    }
    
    /**
     * Show loading state with session validation message
     */
    showLoading() {
        console.log('⏳ [UI-STATE-MANAGER] Showing loading state');
        
        this.container.innerHTML = `
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card border-0 shadow-sm">
                        <div class="card-body text-center py-5">
                            <div class="spinner-border text-primary mb-3" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <h5 class="card-title">Validating Session</h5>
                            <p class="card-text text-muted">
                                Please wait while we verify your session token...
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Show error state with custom title and message
     * @param {string} title - Error title
     * @param {string} message - Error message
     */
    showError(title, message) {
        console.log('❌ [UI-STATE-MANAGER] Showing error state:', title);
        
        this.container.innerHTML = `
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card border-danger shadow-sm">
                        <div class="card-body text-center py-5">
                            <div class="text-danger mb-3">
                                <i class="bi bi-exclamation-triangle display-1"></i>
                            </div>
                            <h5 class="card-title text-danger">${title}</h5>
                            <p class="card-text text-muted mb-4">${message}</p>
                            <div class="d-grid gap-2">
                                <button class="btn btn-outline-primary" id="retry-btn">
                                    <i class="bi bi-arrow-clockwise me-2"></i>
                                    Try Again
                                </button>
                                <a href="/" class="btn btn-secondary">
                                    <i class="bi bi-house me-2"></i>
                                    Go to Homepage
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Setup retry button event listener
        this.setupRetryButton();
    }
    
    /**
     * Show success state with redirect to training page
     * @param {string} token - Session token for redirect
     */
    showSuccess(token) {
        console.log('✅ [UI-STATE-MANAGER] Showing success state');
        
        this.container.innerHTML = `
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card border-success shadow-sm">
                        <div class="card-body text-center py-5">
                            <div class="text-success mb-3">
                                <i class="bi bi-check-circle display-1"></i>
                            </div>
                            <h5 class="card-title text-success">Profile Saved Successfully!</h5>
                            <p class="card-text text-muted mb-4">
                                Your learning profile has been created. The AI is now generating your personalized training plan...
                            </p>
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Generating training plan...</span>
                            </div>
                            <p class="small text-muted mt-3">
                                This may take a few moments while we customize your learning experience.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Setup automatic redirect
        this.setupAutomaticRedirect(token);
    }
    
    /**
     * Show content in the container
     * @param {string} htmlContent - HTML content to display
     */
    showContent(htmlContent) {
        console.log('📄 [UI-STATE-MANAGER] Showing custom content');
        this.container.innerHTML = htmlContent;
    }
    
    /**
     * Clear container content
     */
    clearContent() {
        console.log('🧹 [UI-STATE-MANAGER] Clearing content');
        this.container.innerHTML = '';
    }
    
    /**
     * Setup retry button event listener
     * @private
     */
    setupRetryButton() {
        const retryBtn = document.getElementById('retry-btn');
        if (retryBtn) {
            retryBtn.addEventListener('click', () => {
                console.log('🔄 [UI-STATE-MANAGER] Retry button clicked');
                window.location.reload();
            });
        }
    }
    
    /**
     * Setup automatic redirect after success
     * @param {string} token - Session token for redirect URL
     * @private
     */
    setupAutomaticRedirect(token) {
        const redirectDelay = 5000; // 5 seconds
        
        console.log(`⏰ [UI-STATE-MANAGER] Setting up redirect in ${redirectDelay}ms`);
        
        setTimeout(() => {
            const redirectUrl = `/frontend/public/training.html?token=${token}`;
            console.log('🚀 [UI-STATE-MANAGER] Redirecting to training page:', redirectUrl);
            window.location.href = redirectUrl;
        }, redirectDelay);
    }
    
    /**
     * Show custom loading state with specific message
     * @param {string} title - Loading title
     * @param {string} message - Loading message
     */
    showCustomLoading(title, message) {
        console.log('⏳ [UI-STATE-MANAGER] Showing custom loading state:', title);
        
        this.container.innerHTML = `
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card border-0 shadow-sm">
                        <div class="card-body text-center py-5">
                            <div class="spinner-border text-primary mb-3" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <h5 class="card-title">${title}</h5>
                            <p class="card-text text-muted">${message}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Show warning state with custom message
     * @param {string} title - Warning title
     * @param {string} message - Warning message
     */
    showWarning(title, message) {
        console.log('⚠️ [UI-STATE-MANAGER] Showing warning state:', title);
        
        this.container.innerHTML = `
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card border-warning shadow-sm">
                        <div class="card-body text-center py-5">
                            <div class="text-warning mb-3">
                                <i class="bi bi-exclamation-triangle display-1"></i>
                            </div>
                            <h5 class="card-title text-warning">${title}</h5>
                            <p class="card-text text-muted mb-4">${message}</p>
                            <div class="d-grid gap-2">
                                <button class="btn btn-warning" id="continue-btn">
                                    <i class="bi bi-arrow-right me-2"></i>
                                    Continue Anyway
                                </button>
                                <button class="btn btn-outline-secondary" id="retry-btn">
                                    <i class="bi bi-arrow-clockwise me-2"></i>
                                    Try Again
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Setup buttons
        this.setupRetryButton();
        this.setupContinueButton();
    }
    
    /**
     * Setup continue button event listener
     * @private
     */
    setupContinueButton() {
        const continueBtn = document.getElementById('continue-btn');
        if (continueBtn) {
            continueBtn.addEventListener('click', () => {
                console.log('➡️ [UI-STATE-MANAGER] Continue button clicked');
                // Could emit a custom event or call a callback
                this.onContinueCallback?.();
            });
        }
    }
    
    /**
     * Set callback for continue button
     * @param {Function} callback - Function to call when continue is clicked
     */
    setOnContinueCallback(callback) {
        this.onContinueCallback = callback;
        console.log('✅ [UI-STATE-MANAGER] Continue callback set');
    }
    
    /**
     * Get current container element
     * @returns {HTMLElement} Container element
     */
    getContainer() {
        return this.container;
    }
    
    /**
     * Check if container exists and is valid
     * @returns {boolean} True if container is valid
     */
    isContainerValid() {
        return this.container && this.container instanceof HTMLElement;
    }
}