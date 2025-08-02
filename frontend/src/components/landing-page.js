/**
 * FIA v3.0 - Landing Page JavaScript
 * Simple workflow for creating AI-powered training from user input
 */

class LandingPageManager {
    constructor() {
        this.form = document.getElementById('landing-form');
        this.topicInput = document.getElementById('training-topic');
        this.submitBtn = this.form.querySelector('button[type="submit"]');
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.topicInput.focus();
    }
    
    setupEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleFormSubmit(e));
    }
    
    async handleFormSubmit(event) {
        event.preventDefault();
        
        const topic = this.topicInput.value.trim();
        if (topic.length < 5) {
            alert('Veuillez saisir au moins 5 caractères.');
            return;
        }
        
        // Simple loading feedback
        this.submitBtn.disabled = true;
        this.submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Création en cours...';
        
        try {
            await this.createTrainingWorkflow(topic);
        } catch (error) {
            console.error('Erreur:', error);
            alert('Erreur lors de la création. Veuillez réessayer.');
            this.submitBtn.disabled = false;
            this.submitBtn.innerHTML = 'Démarrer ma formation';
        }
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