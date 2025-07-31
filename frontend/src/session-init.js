/**
 * FIA v3.0 - Session Page Initialization
 * External initialization script for session.html
 * Orchestrates all session-related components in a modular architecture
 */

import { SessionValidator } from './components/session-validator.js';
import { ProfileForm } from './components/profile-form.js';
import { UIStateManager } from './components/ui-state-manager.js';

/**
 * Main Session Application Class
 * Refactored to use modular components instead of monolithic approach
 */
class SessionApp {
    constructor() {
        // Get main container
        this.container = document.getElementById('app-container');
        if (!this.container) {
            console.error('❌ [SESSION-APP] App container not found');
            return;
        }
        
        // Initialize components
        this.sessionValidator = new SessionValidator();
        this.uiStateManager = new UIStateManager(this.container);
        this.profileForm = null; // Will be initialized after validation
        
        // Session data
        this.token = null;
        this.sessionData = null;
        
        console.log('🚀 [SESSION-APP] SessionApp initialized with modular components');
    }
    
    /**
     * Initialize the application workflow
     */
    async init() {
        try {
            console.log('🌟 [SESSION-APP] Starting session initialization workflow...');
            
            // Show loading state
            this.uiStateManager.showLoading();
            
            // Validate session
            const validationResult = await this.sessionValidator.validateSession();
            this.token = validationResult.token;
            this.sessionData = validationResult.sessionData;
            
            console.log('✅ [SESSION-APP] Session validation completed successfully');
            
            // Initialize and show profile form
            await this.initializeProfileForm();
            
        } catch (error) {
            console.error('❌ [SESSION-APP] Session initialization failed:', error);
            this.uiStateManager.showError('Session Error', error.message);
        }
    }
    
    /**
     * Initialize profile form component and display it
     */
    async initializeProfileForm() {
        try {
            console.log('📝 [SESSION-APP] Initializing profile form...');
            
            // Create profile form component
            this.profileForm = new ProfileForm(this.token, this.sessionData);
            
            // Set up callbacks
            this.profileForm.setOnSubmitSuccess(() => {
                console.log('✅ [SESSION-APP] Profile submission successful');
                this.uiStateManager.showSuccess(this.token);
            });
            
            this.profileForm.setOnSubmitError((error) => {
                console.error('❌ [SESSION-APP] Profile submission failed:', error);
                // Error is already displayed in the form, no need for additional UI state
            });
            
            // Generate and display form
            const formHTML = this.profileForm.generateFormHTML();
            this.uiStateManager.showContent(formHTML);
            
            // Setup form event listeners
            this.profileForm.setupFormEventListeners();
            
            console.log('✅ [SESSION-APP] Profile form initialized and displayed');
            
        } catch (error) {
            console.error('❌ [SESSION-APP] Profile form initialization failed:', error);
            this.uiStateManager.showError('Form Error', 'Unable to initialize the profile form. Please try again.');
        }
    }
    
    /**
     * Get current session data
     * @returns {Object} Current session data
     */
    getSessionData() {
        return {
            token: this.token,
            sessionData: this.sessionData
        };
    }
    
    /**
     * Cleanup resources when the app is destroyed
     */
    destroy() {
        console.log('🧹 [SESSION-APP] Cleaning up session app resources');
        
        // Clear UI
        if (this.uiStateManager) {
            this.uiStateManager.clearContent();
        }
        
        // Reset session data
        this.token = null;
        this.sessionData = null;
        this.profileForm = null;
    }
}

/**
 * Initialize the session application when DOM is loaded
 */
async function initializeSessionApp() {
    try {
        console.log('🌟 [SESSION-INIT] Session page loaded, initializing modular session app...');
        
        // Create and initialize the session application
        const sessionApp = new SessionApp();
        await sessionApp.init();
        
        // Make app globally available for debugging
        window.sessionApp = sessionApp;
        
        console.log('✅ [SESSION-INIT] Session app initialized successfully');
        
    } catch (error) {
        console.error('❌ [SESSION-INIT] Failed to initialize session app:', error);
        
        // Fallback error display
        const container = document.getElementById('app-container');
        if (container) {
            container.innerHTML = `
                <div class="row justify-content-center">
                    <div class="col-md-6">
                        <div class="alert alert-danger">
                            <h4>Application Error</h4>
                            <p>Failed to initialize the session application: ${error.message}</p>
                            <button class="btn btn-primary" onclick="location.reload()">Try Again</button>
                        </div>
                    </div>
                </div>
            `;
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeSessionApp);

// Export for potential external use
export { SessionApp, initializeSessionApp };