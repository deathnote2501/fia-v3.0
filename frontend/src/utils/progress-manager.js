/**
 * FIA v3.0 - Progress Management Utility
 * Handles animated progress bars and loading states
 */

export class ProgressManager {
    constructor() {
        this.progressInterval = null;
        console.log('📊 [PROGRESS] ProgressManager initialized');
    }

    /**
     * Anime la progress bar de 0% à 100% en 1 minute
     * @param {string} progressBarId - ID de l'élément progress bar
     * @param {number} duration - Durée en millisecondes (défaut: 60000 = 1 minute)
     */
    startProgressAnimation(progressBarId = 'loading-progress-bar', duration = 60000) {
        const progressBar = document.getElementById(progressBarId);
        if (!progressBar) {
            console.warn(`📊 [PROGRESS] Progress bar not found: ${progressBarId}`);
            return;
        }
        
        // Arrêter toute animation en cours
        this.stopProgressAnimation();
        
        const intervalTime = 100; // Mise à jour toutes les 100ms
        const increment = 100 / (duration / intervalTime); // Pourcentage à ajouter à chaque intervalle
        
        let currentProgress = 0;
        
        console.log(`📊 [PROGRESS] Starting animation - Duration: ${duration}ms`);
        
        this.progressInterval = setInterval(() => {
            currentProgress += increment;
            
            if (currentProgress >= 100) {
                currentProgress = 100;
                this.stopProgressAnimation();
            }
            
            // Mettre à jour la progress bar
            progressBar.style.width = `${currentProgress}%`;
            progressBar.setAttribute('aria-valuenow', Math.round(currentProgress));
            
        }, intervalTime);
        
        console.log(`📊 [PROGRESS] Animation started for ${progressBarId}`);
    }

    /**
     * Arrête l'animation de la progress bar
     */
    stopProgressAnimation() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
            console.log('📊 [PROGRESS] Animation stopped');
        }
    }

    /**
     * Définit immédiatement la valeur de la progress bar
     * @param {string} progressBarId - ID de l'élément progress bar
     * @param {number} value - Valeur en pourcentage (0-100)
     */
    setProgress(progressBarId, value) {
        const progressBar = document.getElementById(progressBarId);
        if (!progressBar) {
            console.warn(`📊 [PROGRESS] Progress bar not found: ${progressBarId}`);
            return;
        }

        const clampedValue = Math.max(0, Math.min(100, value));
        progressBar.style.width = `${clampedValue}%`;
        progressBar.setAttribute('aria-valuenow', clampedValue);
        
        console.log(`📊 [PROGRESS] Progress set to ${clampedValue}% for ${progressBarId}`);
    }

    /**
     * Obtient la valeur actuelle de la progress bar
     * @param {string} progressBarId - ID de l'élément progress bar
     * @returns {number} Valeur actuelle en pourcentage
     */
    getProgress(progressBarId) {
        const progressBar = document.getElementById(progressBarId);
        if (!progressBar) {
            console.warn(`📊 [PROGRESS] Progress bar not found: ${progressBarId}`);
            return 0;
        }

        return parseInt(progressBar.getAttribute('aria-valuenow') || '0');
    }

    /**
     * Vérifie si une animation est en cours
     * @returns {boolean} True si animation en cours
     */
    isAnimating() {
        return this.progressInterval !== null;
    }

    /**
     * Nettoie les ressources (à appeler lors de la destruction)
     */
    destroy() {
        this.stopProgressAnimation();
        console.log('📊 [PROGRESS] ProgressManager destroyed');
    }
}