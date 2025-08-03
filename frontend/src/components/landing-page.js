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
        this.progressContainer = document.getElementById('training-progress-container');
        this.progressBar = document.getElementById('training-progress-bar');
        this.progressText = document.getElementById('progress-text');
        this.progressStatus = document.getElementById('progress-status');
        
        // Progress tracking
        this.progressInterval = null;
        this.progressStartTime = null;
        this.PROGRESS_DURATION_MS = 120000; // 2 minutes
        
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
            this.showError(window.safeT ? window.safeT('landing.error.minLength') : 'Veuillez saisir au moins 5 caractères.');
            return;
        }
        
        // Enhanced loading feedback with new design
        this.setLoadingState(true);
        
        try {
            await this.createTrainingWorkflow(topic);
        } catch (error) {
            console.error('❌ [LANDING] Error:', error);
            this.showError(window.safeT ? window.safeT('landing.error.creation') : 'Erreur lors de la création. Veuillez réessayer.');
            this.setLoadingState(false);
        }
    }
    
    setLoadingState(isLoading) {
        if (isLoading) {
            this.submitBtn.disabled = true;
            this.contentOverlay.classList.add('loading-state');
            this.submitBtn.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2"></span>
                ${window.safeT ? window.safeT('status.creating') : 'Création...'}
            `;
            this.topicInput.disabled = true;
            
            // Show progress bar and start animation
            this.showProgressBar();
            this.startProgressAnimation();
        } else {
            this.submitBtn.disabled = false;
            this.contentOverlay.classList.remove('loading-state');
            this.submitBtn.innerHTML = `
                <span data-i18n="landing.startButton">Start My Training</span>
                <i class="bi bi-chevron-right cta-icon"></i>
            `;
            this.topicInput.disabled = false;
            
            // Hide progress bar and stop animation
            this.hideProgressBar();
            this.stopProgressAnimation();
            
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
    
    showProgressBar() {
        this.progressContainer.style.display = 'block';
        this.resetProgressBar();
    }
    
    hideProgressBar() {
        this.progressContainer.style.display = 'none';
        this.resetProgressBar();
    }
    
    resetProgressBar() {
        this.progressBar.style.width = '0%';
        this.progressBar.setAttribute('aria-valuenow', '0');
        this.progressText.textContent = '0%';
        this.progressStatus.textContent = window.safeT ? window.safeT('landing.progress.status') : 'Démarrage de la génération IA...';
    }
    
    startProgressAnimation() {
        this.progressStartTime = Date.now();
        this.progressInterval = setInterval(() => {
            this.updateProgress();
        }, 100); // Update every 100ms for smooth animation
    }
    
    stopProgressAnimation() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
        this.progressStartTime = null;
    }
    
    updateProgress() {
        if (!this.progressStartTime) return;
        
        const elapsed = Date.now() - this.progressStartTime;
        const progressPercent = Math.min((elapsed / this.PROGRESS_DURATION_MS) * 100, 100);
        
        // Update progress bar
        this.progressBar.style.width = progressPercent + '%';
        this.progressBar.setAttribute('aria-valuenow', progressPercent.toString());
        this.progressText.textContent = Math.round(progressPercent) + '%';
        
        // Update status message based on progress
        this.updateProgressStatus(progressPercent);
        
        // Stop at 100%
        if (progressPercent >= 100) {
            this.stopProgressAnimation();
        }
    }
    
    updateProgressStatus(progressPercent) {
        let statusMessage = '';
        
        if (progressPercent < 20) {
            statusMessage = window.safeT ? window.safeT('landing.progress.analyzing') : 'Analyse de votre sujet...';
        } else if (progressPercent < 40) {
            statusMessage = window.safeT ? window.safeT('landing.progress.creating') : 'L\'IA crée votre contenu personnalisé...';
        } else if (progressPercent < 60) {
            statusMessage = window.safeT ? window.safeT('landing.progress.generatingSlides') : 'Génération des slides interactives...';
        } else if (progressPercent < 80) {
            statusMessage = window.safeT ? window.safeT('landing.progress.preparing') : 'Préparation de votre expérience d\'apprentissage...';
        } else if (progressPercent < 95) {
            statusMessage = window.safeT ? window.safeT('landing.progress.finalizing') : 'Presque prêt ! Finalisation des détails...';
        } else {
            statusMessage = window.safeT ? window.safeT('landing.progress.ready') : 'Formation prête ! Redirection...';
        }
        
        this.progressStatus.textContent = statusMessage;
    }
    
    
}

// Initialize landing page when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new LandingPageManager();
});