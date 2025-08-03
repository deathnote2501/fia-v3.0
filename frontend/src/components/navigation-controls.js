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
    updateNavigationButtonStates(currentSlide) {
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
        
        // Update Next button
        if (newNextBtn) {
            // Phase 3: Check slide limitation (configurable limit for free users)
            const currentPosition = position.current_position || 0;
            
            if (currentPosition >= SLIDE_LIMIT_CONFIG.MAX_FREE_SLIDES) {
                newNextBtn.disabled = true;
                newNextBtn.classList.add('opacity-50');
                newNextBtn.innerHTML = '<i class="bi bi-lock me-1"></i>Limit Reached';
                console.log(`🚫 [NAVIGATION-CONTROLS] Next button disabled - slide limit reached (${currentPosition}/${SLIDE_LIMIT_CONFIG.MAX_FREE_SLIDES})`);
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
}