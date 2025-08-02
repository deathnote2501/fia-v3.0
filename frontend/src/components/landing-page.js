/**
 * FIA v3.0 - Landing Page JavaScript
 * Simple workflow for creating AI-powered training from user input
 */

class LandingPageManager {
    constructor() {
        this.form = document.getElementById('landing-form');
        this.topicInput = document.getElementById('training-topic');
        this.submitBtn = document.getElementById('start-training-btn');
        this.contentOverlay = document.querySelector('.content-overlay');
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        // Focus on input after a small delay to ensure page is fully loaded
        setTimeout(() => this.topicInput.focus(), 100);
    }
    
    setupEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        
        // Add input validation feedback
        this.topicInput.addEventListener('input', () => this.validateInput());
    }
    
    validateInput() {
        const topic = this.topicInput.value.trim();
        if (topic.length > 0 && topic.length < 5) {
            this.topicInput.style.borderColor = '#dc3545';
        } else {
            this.topicInput.style.borderColor = '';
        }
    }
    
    async handleFormSubmit(event) {
        event.preventDefault();
        
        const topic = this.topicInput.value.trim();
        if (topic.length < 5) {
            this.showError('Please enter at least 5 characters.');
            return;
        }
        
        // Enhanced loading feedback with new design
        this.setLoadingState(true);
        
        try {
            await this.createTrainingWorkflow(topic);
        } catch (error) {
            console.error('❌ [LANDING] Error:', error);
            this.showError('Error during creation. Please try again.');
            this.setLoadingState(false);
        }
    }
    
    setLoadingState(isLoading) {
        if (isLoading) {
            this.submitBtn.disabled = true;
            this.contentOverlay.classList.add('loading-state');
            this.submitBtn.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2"></span>
                Creating Training...
            `;
            this.topicInput.disabled = true;
        } else {
            this.submitBtn.disabled = false;
            this.contentOverlay.classList.remove('loading-state');
            this.submitBtn.innerHTML = `
                <span data-i18n="landing.startButton">Start My Training</span>
                <i class="bi bi-chevron-right cta-icon"></i>
            `;
            this.topicInput.disabled = false;
            
            // Re-apply translations if available
            if (window.i18n) {
                window.i18n.updateDOM();
            }
        }
    }
    
    showError(message) {
        // Enhanced error display
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show mt-3';
        errorDiv.innerHTML = `
            <i class="bi bi-exclamation-triangle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Remove existing errors
        const existingErrors = this.contentOverlay.querySelectorAll('.alert-danger');
        existingErrors.forEach(error => error.remove());
        
        // Add new error message
        this.form.appendChild(errorDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentElement) {
                errorDiv.remove();
            }
        }, 5000);
    }
    
    async createTrainingWorkflow(topic) {
        // Use new public quick-start endpoint that handles everything
        const response = await fetch('/api/public/quick-start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                topic: topic
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Erreur HTTP ${response.status}`);
        }
        
        const result = await response.json();
        
        // Redirect to training page with token
        window.location.href = result.session_link;
    }
    
    
}

// Initialize landing page when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new LandingPageManager();
});