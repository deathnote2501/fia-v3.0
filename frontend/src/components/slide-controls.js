/**
 * FIA v3.0 - Slide Controls Component
 * Handles slide navigation (next/previous) and simplification functionality
 */

// Note: Slide limitation configuration moved to NavigationControls for B2C/B2B detection

export class SlideControls {
    constructor() {
        this.getCurrentSlideData = null; // Callback to get current slide data
        this.displaySlideContent = null; // Callback to display slide content
        this.markdownToHtml = null; // Callback to convert markdown to HTML
        this.getCurrentSlideMarkdown = null; // Callback to get current slide markdown
        
        console.log('🎯 [SLIDE-CONTROLS] SlideControls initialized');
    }
    
    /**
     * Setup navigation buttons event listeners
     */
    setupNavigationButtons() {
        const newNextBtn = document.getElementById('new-next-btn');
        const newPreviousBtn = document.getElementById('new-previous-btn');
        const generateChartBtn = document.getElementById('generate-chart-btn');
        const generateImageBtn = document.getElementById('generate-image-btn');
        const newSimplifyBtn = document.getElementById('new-simplify-btn');
        const newMoreDetailsBtn = document.getElementById('new-more-details-btn');
        
        if (generateChartBtn) {
            generateChartBtn.addEventListener('click', () => this.generateSlideChart());
            console.log('✅ [SLIDE-CONTROLS] Generate chart button connected');
        }
        
        if (generateImageBtn) {
            generateImageBtn.addEventListener('click', () => this.generateSlideImage());
            console.log('✅ [SLIDE-CONTROLS] Generate image button connected');
        }
        
        if (newMoreDetailsBtn) {
            newMoreDetailsBtn.addEventListener('click', () => this.addMoreDetails());
            console.log('✅ [SLIDE-CONTROLS] More details button connected');
        }
        
        if (newNextBtn) {
            newNextBtn.addEventListener('click', () => this.navigateToNextSlide());
            console.log('✅ [SLIDE-CONTROLS] New next button connected');
        }
        
        if (newPreviousBtn) {
            newPreviousBtn.addEventListener('click', () => this.navigateToPreviousSlide());
            console.log('✅ [SLIDE-CONTROLS] New previous button connected');
        }
        
        if (newSimplifyBtn) {
            newSimplifyBtn.addEventListener('click', () => this.simplifySlideContent());
            console.log('✅ [SLIDE-CONTROLS] Simplify button connected');
        }
    }
    
    /**
     * Navigate to the next slide
     */
    async navigateToNextSlide() {
        const newNextBtn = document.getElementById('new-next-btn');
        
        const { currentSlide, learnerSession } = this.getCurrentSlideData();
        
        if (!currentSlide) {
            console.error('❌ [SLIDE-CONTROLS] No current slide data available');
            this.showNavigationError('No current slide information available');
            return;
        }
        
        // Note: Slide limitations are now handled by NavigationControls for B2C sessions
        // This allows proper B2C/B2B detection via API
        
        try {
            console.log('🎯 [SLIDE-CONTROLS] Starting navigation to next slide');
            
            // Désactiver le bouton pendant le traitement
            if (newNextBtn) {
                newNextBtn.disabled = true;
                newNextBtn.innerHTML = `<i class="bi bi-hourglass-split me-1"></i>${window.safeT ? window.safeT('status.loadingGeneric') : 'Loading...'}`;
            }
            
            // Obtenir l'ID de la slide actuelle
            const currentSlideId = currentSlide.slide_id || currentSlide.id;
            if (!currentSlideId) {
                console.error('❌ [SLIDE-CONTROLS] No current slide ID found');
                this.showNavigationError('Could not determine current slide');
                return;
            }
            
            console.log('📝 [SLIDE-CONTROLS] Current slide ID:', currentSlideId);
            console.log('📝 [SLIDE-CONTROLS] Learner session ID:', learnerSession.id);
            
            // Appeler l'API de navigation
            const response = await fetch(`/api/slides/next/${learnerSession.id}/${currentSlideId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            console.log('📥 [SLIDE-CONTROLS] Response status:', response.status);
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error('❌ [SLIDE-CONTROLS] Error response:', errorData);
                
                // Check if we've reached the end
                if (response.status === 404 || errorData.message?.includes('end')) {
                    this.showNavigationComplete();
                    return;
                }
                
                throw new Error(errorData.detail || 'Failed to navigate to next slide');
            }
            
            const navigationResult = await response.json();
            console.log('✅ [SLIDE-CONTROLS] Success response:', navigationResult);
            
            // Check if there's no next slide
            if (!navigationResult.success || !navigationResult.data.has_next) {
                this.showNavigationComplete();
                return;
            }
            
            // Display the next slide
            this.displaySlideContent(navigationResult.data);
            this.showNavigationSuccess(navigationResult.data);
            
        } catch (error) {
            console.error('❌ [SLIDE-CONTROLS] Error:', error);
            this.showNavigationError(error.message);
            
        } finally {
            // Réactiver le bouton
            if (newNextBtn) {
                newNextBtn.disabled = false;
                newNextBtn.innerHTML = `${window.safeT ? window.safeT('learner.next') : 'Next'}<i class="bi bi-chevron-right ms-1"></i>`;
            }
        }
    }
    
    /**
     * Navigate to the previous slide
     */
    async navigateToPreviousSlide() {
        const newPreviousBtn = document.getElementById('new-previous-btn');
        
        const { currentSlide, learnerSession } = this.getCurrentSlideData();
        
        if (!currentSlide) {
            console.error('❌ [SLIDE-CONTROLS] No current slide data available');
            this.showNavigationError('No current slide information available');
            return;
        }
        
        try {
            console.log('🎯 [SLIDE-CONTROLS] Starting navigation to previous slide');
            
            // Désactiver le bouton pendant le traitement
            if (newPreviousBtn) {
                newPreviousBtn.disabled = true;
                newPreviousBtn.innerHTML = `<i class="bi bi-hourglass-split me-1"></i>${window.safeT ? window.safeT('status.loadingGeneric') : 'Loading...'}`;
            }
            
            // Obtenir l'ID de la slide actuelle
            const currentSlideId = currentSlide.slide_id || currentSlide.id;
            if (!currentSlideId) {
                console.error('❌ [SLIDE-CONTROLS] No current slide ID found');
                this.showNavigationError('Could not determine current slide');
                return;
            }
            
            console.log('📝 [SLIDE-CONTROLS] Current slide ID:', currentSlideId);
            console.log('📝 [SLIDE-CONTROLS] Learner session ID:', learnerSession.id);
            
            // Appeler l'API de navigation précédente
            const response = await fetch(`/api/slides/previous/${learnerSession.id}/${currentSlideId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            console.log('📥 [SLIDE-CONTROLS] Response status:', response.status);
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error('❌ [SLIDE-CONTROLS] Error response:', errorData);
                
                // Check if we've reached the beginning
                if (response.status === 404 || errorData.message?.includes('beginning')) {
                    this.showNavigationBeginning();
                    return;
                }
                
                throw new Error(errorData.detail || 'Failed to navigate to previous slide');
            }
            
            const navigationResult = await response.json();
            console.log('✅ [SLIDE-CONTROLS] Success response:', navigationResult);
            
            // Check if there's no previous slide
            if (!navigationResult.success || !navigationResult.data.has_previous) {
                this.showNavigationBeginning();
                return;
            }
            
            // Display the previous slide
            this.displaySlideContent(navigationResult.data);
            this.showPreviousNavigationSuccess(navigationResult.data);
            
        } catch (error) {
            console.error('❌ [SLIDE-CONTROLS] Error:', error);
            this.showNavigationError(error.message);
            
        } finally {
            // Réactiver le bouton
            if (newPreviousBtn) {
                newPreviousBtn.disabled = false;
                newPreviousBtn.innerHTML = `<i class="bi bi-chevron-left me-1"></i>${window.safeT ? window.safeT('learner.previous') : 'Previous'}`;
            }
        }
    }
    
    /**
     * Simplify current slide content
     */
    async simplifySlideContent() {
        const newSimplifyBtn = document.getElementById('new-simplify-btn');
        const slideContentEl = document.getElementById('slide-content');
        
        if (!slideContentEl) {
            console.error('❌ [SLIDE-CONTROLS] Slide content element not found');
            return;
        }
        
        const { learnerSession } = this.getCurrentSlideData();
        
        try {
            console.log('🎯 [SLIDE-CONTROLS] Starting slide content simplification');
            
            // Désactiver le bouton pendant le traitement
            if (newSimplifyBtn) {
                newSimplifyBtn.disabled = true;
                newSimplifyBtn.innerHTML = `<i class="bi bi-hourglass-split me-1"></i>${window.safeT ? window.safeT('status.simplifying') : 'Simplifying...'}`;
            }
            
            // Obtenir le contenu markdown actuel
            const currentMarkdown = this.getCurrentSlideMarkdown();
            if (!currentMarkdown) {
                console.error('❌ [SLIDE-CONTROLS] No current slide content to simplify');
                return;
            }
            
            console.log('📝 [SLIDE-CONTROLS] Current content length:', currentMarkdown.length);
            console.log('📝 [SLIDE-CONTROLS] Current content preview:', currentMarkdown.substring(0, 100) + '...');
            
            // Appeler l'API de simplification
            const response = await fetch(`/api/slides/simplify/${learnerSession.id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    current_content: currentMarkdown
                })
            });
            
            if (!response.ok) {
                throw new Error(`API request failed: ${response.status} ${response.statusText}`);
            }
            
            const result = await response.json();
            console.log('✅ [SLIDE-CONTROLS] API response received:', result);
            
            if (result.success && result.data && result.data.slide_content) {
                // Remplacer le contenu de la slide avec la version simplifiée
                const simplifiedContent = result.data.slide_content;
                console.log('📝 [SLIDE-CONTROLS] Simplified content length:', simplifiedContent.length);
                console.log('📝 [SLIDE-CONTROLS] Simplified content preview:', simplifiedContent.substring(0, 100) + '...');
                
                // Mettre à jour l'affichage
                slideContentEl.innerHTML = this.markdownToHtml(simplifiedContent);
                
                // Sauvegarder le nouveau contenu pour usage futur (callback needed)
                if (this.updateCurrentSlideContent) {
                    this.updateCurrentSlideContent(simplifiedContent);
                }
                
                console.log('✅ [SLIDE-CONTROLS] Slide content simplified successfully');
                
                // Afficher un message de succès temporaire
                this.showSimplifySuccess(result.data);
                
            } else {
                console.error('❌ [SLIDE-CONTROLS] Invalid API response structure:', result);
                throw new Error('Invalid API response structure');
            }
            
        } catch (error) {
            console.error('❌ [SLIDE-CONTROLS] Simplification error:', error);
            this.showSimplifyError(error.message);
            
        } finally {
            // Réactiver le bouton
            if (newSimplifyBtn) {
                newSimplifyBtn.disabled = false;
                newSimplifyBtn.innerHTML = `<i class="bi bi-magic me-1"></i>${window.safeT ? window.safeT('learner.simplify') : 'Simplify'}`;
            }
        }
    }
    
    /**
     * Generate chart for current slide
     */
    async generateSlideChart() {
        const chartBtn = document.getElementById('generate-chart-btn');
        
        try {
            console.log('📊 [SLIDE-CONTROLS] Chart generation requested');
            
            // Get current slide data
            const { currentSlide, learnerSession } = this.getCurrentSlideData();
            
            if (!currentSlide || !learnerSession) {
                console.error('❌ [SLIDE-CONTROLS] No current slide or session available');
                return;
            }
            
            // Get current slide content
            const currentMarkdown = this.getCurrentSlideMarkdown();
            
            if (!currentMarkdown || currentMarkdown.trim().length < 10) {
                console.error('❌ [SLIDE-CONTROLS] No valid slide content for chart generation');
                return;
            }
            
            // Disable button during generation
            if (chartBtn) {
                chartBtn.disabled = true;
                chartBtn.innerHTML = `<i class="bi bi-hourglass-split me-1"></i>${window.safeT ? window.safeT('status.generating') : 'Generating...'}`;
            }
            
            console.log('📝 [CHART_GEN] Content length:', currentMarkdown.length);
            console.log('📝 [CHART_GEN] Content preview:', currentMarkdown.substring(0, 100) + '...');
            
            // Call chart generation API
            const response = await fetch(`/api/slides/${learnerSession.id}/generate-chart`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    slide_content: currentMarkdown,
                    slide_id: currentSlide.slide_id || currentSlide.id
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }
            
            const result = await response.json();
            console.log('✅ [CHART_GEN] Chart generated successfully:', result);
            
            // Display the generated charts in the slide content
            if (result.success && result.charts && result.charts.length > 0) {
                this.displayGeneratedCharts(result.charts);
            } else {
                console.warn('⚠️ [CHART_GEN] No charts generated or result unsuccessful');
            }
            
        } catch (error) {
            console.error('❌ [SLIDE-CONTROLS] Chart generation error:', error);
        } finally {
            // Re-enable button
            if (chartBtn) {
                chartBtn.disabled = false;
                chartBtn.innerHTML = `<i class="bi bi-bar-chart me-1"></i>${window.safeT ? window.safeT('learner.chart') : 'Chart'}`;
            }
        }
    }
    
    /**
     * Generate image for current slide content
     */
    async generateSlideImage() {
        const imageBtn = document.getElementById('generate-image-btn');
        
        try {
            console.log('🖼️ [SLIDE-CONTROLS] Image generation requested');
            
            // Get current slide data
            const { currentSlide, learnerSession } = this.getCurrentSlideData();
            
            if (!currentSlide || !learnerSession) {
                console.error('❌ [SLIDE-CONTROLS] No current slide or session available');
                return;
            }
            
            // Get current slide content
            const currentMarkdown = this.getCurrentSlideMarkdown();
            
            if (!currentMarkdown || currentMarkdown.trim().length < 10) {
                console.error('❌ [SLIDE-CONTROLS] No valid slide content for image generation');
                return;
            }
            
            // Disable button during generation
            if (imageBtn) {
                imageBtn.disabled = true;
                imageBtn.innerHTML = `<i class="bi bi-hourglass-split me-1"></i>${window.safeT ? window.safeT('status.generating') : 'Generating...'}`;
            }
            
            console.log('📝 [IMAGE_GEN] Content length:', currentMarkdown.length);
            console.log('📝 [IMAGE_GEN] Content preview:', currentMarkdown.substring(0, 100) + '...');
            
            // Call image generation API
            const response = await fetch('/api/image-generation/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    slide_content: currentMarkdown,
                    learner_session_id: learnerSession.id,
                    slide_id: currentSlide.slide_id || currentSlide.id
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }
            
            const result = await response.json();
            console.log('✅ [IMAGE_GEN] Image generated successfully:', result);
            
            // Display the generated image in the slide content
            if (result.success && result.image_data) {
                this.displayGeneratedImage(result.image_data, result.revised_prompt);
            }
            
        } catch (error) {
            console.error('❌ [SLIDE-CONTROLS] Image generation error:', error);
        } finally {
            // Re-enable button
            if (imageBtn) {
                imageBtn.disabled = false;
                imageBtn.innerHTML = `<i class="bi bi-image me-1"></i>${window.safeT ? window.safeT('learner.image') : 'Image'}`;
            }
        }
    }
    
    /**
     * Add more details to current slide content
     */
    async addMoreDetails() {
        const moreDetailsBtn = document.getElementById('new-more-details-btn');
        const slideContentEl = document.getElementById('slide-content');
        
        if (!slideContentEl) {
            console.error('❌ [SLIDE-CONTROLS] Slide content element not found');
            return;
        }
        
        const { learnerSession } = this.getCurrentSlideData();
        
        try {
            console.log('🔧 [SLIDE-CONTROLS] Starting slide content enhancement');
            
            // Disable button during processing
            if (moreDetailsBtn) {
                moreDetailsBtn.disabled = true;
                moreDetailsBtn.innerHTML = `<i class="bi bi-hourglass-split me-1"></i>${window.safeT ? window.safeT('status.addingDetails') : 'Adding details...'}`;
            }
            
            // Get current slide markdown content
            const currentMarkdown = this.getCurrentSlideMarkdown();
            if (!currentMarkdown) {
                console.error('❌ [SLIDE-CONTROLS] No current slide content to enhance');
                return;
            }
            
            console.log('📝 [SLIDE-CONTROLS] Current content length:', currentMarkdown.length);
            console.log('📝 [SLIDE-CONTROLS] Current content preview:', currentMarkdown.substring(0, 100) + '...');
            
            // Call the API to add more details
            const response = await fetch(`/api/slides/more-details/${learnerSession.id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    current_content: currentMarkdown
                })
            });
            
            if (!response.ok) {
                throw new Error(`API request failed: ${response.status} ${response.statusText}`);
            }
            
            const result = await response.json();
            console.log('✅ [SLIDE-CONTROLS] API response received:', result);
            
            if (result.success && result.data.enhanced_content) {
                // Replace slide content with enhanced version
                const enhancedContent = result.data.enhanced_content;
                console.log('📝 [SLIDE-CONTROLS] Enhanced content length:', enhancedContent.length);
                console.log('📝 [SLIDE-CONTROLS] Enhanced content preview:', enhancedContent.substring(0, 100) + '...');
                
                // Update the display
                slideContentEl.innerHTML = this.markdownToHtml(enhancedContent);
                
                // Save the new content for future use (callback needed)
                if (this.updateCurrentSlideContent) {
                    this.updateCurrentSlideContent(enhancedContent);
                }
                
                console.log('✅ [SLIDE-CONTROLS] Slide content enhanced successfully');
                
                // Show success message
                this.showEnhanceSuccess(result.data);
                
            } else {
                throw new Error('Invalid API response structure');
            }
            
        } catch (error) {
            console.error('❌ [SLIDE-CONTROLS] Enhancement error:', error);
            this.showEnhanceError(error.message);
            
        } finally {
            // Re-enable button
            if (moreDetailsBtn) {
                moreDetailsBtn.disabled = false;
                moreDetailsBtn.innerHTML = `<i class="bi bi-plus-circle me-1"></i>${window.safeT ? window.safeT('learner.deepen') : 'More Details'}`;
            }
        }
    }
    
    /**
     * Show navigation success message
     * @param {Object} slideData - Slide data
     */
    showNavigationSuccess(slideData) {
        console.log('🎯 [SLIDE-CONTROLS] Navigation successful:', slideData.title || 'Next slide');
    }
    
    /**
     * Show previous navigation success message
     * @param {Object} slideData - Slide data
     */
    showPreviousNavigationSuccess(slideData) {
        console.log('🎯 [SLIDE-CONTROLS] Previous navigation successful:', slideData.title || 'Previous slide');
    }
    
    /**
     * Show navigation complete state
     */
    showNavigationComplete() {
        console.log('🎯 [SLIDE-CONTROLS] Training complete!');
        
        // Disable the Next button
        const newNextBtn = document.getElementById('new-next-btn');
        if (newNextBtn) {
            newNextBtn.disabled = true;
            newNextBtn.innerHTML = `<i class="bi bi-check-circle me-1"></i>${window.safeT ? window.safeT('learner.complete') : 'Complete'}`;
        }
    }
    
    /**
     * Show navigation beginning state
     */
    showNavigationBeginning() {
        console.log('🎯 [SLIDE-CONTROLS] At the beginning!');
        
        // Disable the Previous button
        const newPreviousBtn = document.getElementById('new-previous-btn');
        if (newPreviousBtn) {
            newPreviousBtn.disabled = true;
            newPreviousBtn.innerHTML = `<i class="bi bi-stop-circle me-1"></i>${window.safeT ? window.safeT('learner.beginning') : 'Beginning'}`;
        }
        
        // Réactiver le bouton après 5 secondes
        setTimeout(() => {
            const { currentSlide } = this.getCurrentSlideData();
            if (newPreviousBtn && currentSlide && (currentSlide.position?.has_previous !== false)) {
                newPreviousBtn.disabled = false;
                newPreviousBtn.innerHTML = `<i class="bi bi-chevron-left me-1"></i>${window.safeT ? window.safeT('learner.previous') : 'Previous'}`;
            }
        }, 5000);
    }
    
    /**
     * Show navigation error
     * @param {string} errorMessage - Error message
     */
    showNavigationError(errorMessage) {
        console.error('❌ [SLIDE-CONTROLS] Error:', errorMessage);
    }
    
    /**
     * Show simplify success message
     * @param {Object} data - Simplify result data
     */
    showSimplifySuccess(data) {
        console.log('✅ [SLIDE-CONTROLS] Simplification successful');
    }
    
    /**
     * Show simplify error
     * @param {string} errorMessage - Error message
     */
    showSimplifyError(errorMessage) {
        console.error('❌ [SLIDE-CONTROLS] Simplification error:', errorMessage);
    }
    
    /**
     * Show enhance success message
     * @param {Object} data - Enhancement result data
     */
    showEnhanceSuccess(data) {
        console.log('✅ [SLIDE-CONTROLS] Enhancement successful');
    }
    
    /**
     * Show enhance error
     * @param {string} errorMessage - Error message
     */
    showEnhanceError(errorMessage) {
        console.error('❌ [SLIDE-CONTROLS] Enhancement error:', errorMessage);
    }
    
    /**
     * Display generated image in the slide content
     * @param {string} imageData - Base64 image data
     * @param {string} prompt - The prompt used to generate the image
     */
    displayGeneratedImage(imageData, prompt) {
        const slideContentEl = document.getElementById('slide-content');
        if (!slideContentEl) {
            console.error('❌ [SLIDE-CONTROLS] Slide content element not found for image display');
            return;
        }
        
        // Create image element
        const imageContainer = document.createElement('div');
        imageContainer.className = 'generated-image-container mt-4 mb-4';
        imageContainer.innerHTML = `
            <div class="card">
                <div class="card-body text-center">
                    <h6 class="card-title">📊 Generated Visual Content</h6>
                    <img src="data:image/png;base64,${imageData}" 
                         class="img-fluid rounded" 
                         alt="Generated slide image" 
                         style="max-width: 100%; height: auto; border: 1px solid #dee2e6;"
                    />
                    <p class="card-text mt-2 text-muted small">
                        <i class="bi bi-info-circle"></i> Generated based on: "${prompt.substring(0, 100)}..."
                    </p>
                </div>
            </div>
        `;
        
        // Remove any existing generated images
        const existingImages = slideContentEl.querySelectorAll('.generated-image-container');
        existingImages.forEach(img => img.remove());
        
        // Add the new image at the end of the slide content
        slideContentEl.appendChild(imageContainer);
        
        console.log('✅ [SLIDE-CONTROLS] Image displayed successfully in slide content');
    }
    
    /**
     * Display generated charts in the slide content
     * @param {Array} charts - Array of chart configurations
     */
    displayGeneratedCharts(charts) {
        const slideContentEl = document.getElementById('slide-content');
        if (!slideContentEl) {
            console.error('❌ [SLIDE-CONTROLS] Slide content element not found for chart display');
            return;
        }
        
        // Remove any existing generated charts
        const existingCharts = slideContentEl.querySelectorAll('.generated-charts-container');
        existingCharts.forEach(chart => chart.remove());
        
        // Create charts container
        const chartsContainer = document.createElement('div');
        chartsContainer.className = 'generated-charts-container mt-4 mb-4';
        
        // Generate unique timestamp for all charts in this batch
        const timestamp = Date.now();
        
        let chartsHtml = `
            <div class="card">
                <div class="card-body">
        `;
        
        // Display each chart at full width, one below the other
        charts.forEach((chart, index) => {
            const chartId = `chart-${timestamp}-${index}`;
            chartsHtml += `
                <div class="mb-4">
                    <div class="card border-secondary">
                        <div class="card-body">
                            <h6 class="card-subtitle mb-3 text-muted">${chart.title}</h6>
                            <div class="chart-wrapper" style="position: relative; height: 400px; width: 100%;">
                                <canvas id="${chartId}" style="width: 100%; height: 100%;"></canvas>
                            </div>
                            ${chart.description ? `<p class="card-text mt-3 small">${chart.description}</p>` : ''}
                        </div>
                    </div>
                </div>
            `;
        });
        
        chartsHtml += `
                    <p class="card-text mt-2 text-muted small">
                    </p>
                </div>
            </div>
        `;
        
        chartsContainer.innerHTML = chartsHtml;
        
        // Add the charts container to the slide content
        slideContentEl.appendChild(chartsContainer);
        
        // Render the actual charts using Chart.js if available - pass timestamp to ensure consistency
        this.renderCharts(charts, timestamp);
        
        console.log(`✅ [SLIDE-CONTROLS] ${charts.length} charts displayed successfully in slide content`);
    }
    
    /**
     * Render charts using Chart.js library
     * @param {Array} charts - Array of chart configurations
     * @param {number} timestamp - Timestamp used for chart IDs
     */
    renderCharts(charts, timestamp) {
        // Check if Chart.js is loaded
        if (typeof Chart === 'undefined') {
            console.warn('⚠️ [SLIDE-CONTROLS] Chart.js not loaded, displaying chart data as text');
            this.displayChartsAsText(charts, timestamp);
            return;
        }
        
        charts.forEach((chart, index) => {
            const chartId = `chart-${timestamp}-${index}`;
            const canvas = document.getElementById(chartId);
            
            if (!canvas) {
                console.error(`❌ [SLIDE-CONTROLS] Canvas element not found: ${chartId}`);
                return;
            }
            
            try {
                const ctx = canvas.getContext('2d');
                
                // Get color palette
                const colors = this.getChartColors(chart.color_palette || 'default');
                
                const chartConfig = {
                    type: chart.type,
                    data: {
                        labels: chart.labels,
                        datasets: [{
                            label: chart.title,
                            data: chart.data,
                            backgroundColor: colors.background,
                            borderColor: colors.border,
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: chart.type !== 'pie'
                            }
                        }
                    }
                };
                
                new Chart(ctx, chartConfig);
                console.log(`✅ [SLIDE-CONTROLS] Chart rendered: ${chart.title}`);
                
            } catch (error) {
                console.error(`❌ [SLIDE-CONTROLS] Error rendering chart ${chartId}:`, error);
            }
        });
    }
    
    /**
     * Display charts as text when Chart.js is not available
     * @param {Array} charts - Array of chart configurations
     * @param {number} timestamp - Timestamp used for chart IDs
     */
    displayChartsAsText(charts, timestamp) {
        charts.forEach((chart, index) => {
            const chartId = `chart-${timestamp}-${index}`;
            const canvas = document.getElementById(chartId);
            
            if (canvas) {
                const container = canvas.parentElement;
                container.innerHTML = `
                    <h6 class="card-subtitle mb-2 text-muted">${chart.title}</h6>
                    <div class="chart-data-text">
                        <strong>Type:</strong> ${chart.type}<br>
                        <strong>Labels:</strong> ${chart.labels.join(', ')}<br>
                        <strong>Data:</strong> ${chart.data.join(', ')}<br>
                        ${chart.description ? `<p class="mt-2 small">${chart.description}</p>` : ''}
                    </div>
                `;
            }
        });
    }
    
    /**
     * Get color palettes for charts
     * @param {string} palette - Color palette name
     * @returns {Object} Colors object with background and border arrays
     */
    getChartColors(palette) {
        const palettes = {
            default: {
                background: ['rgba(13, 110, 253, 0.2)', 'rgba(25, 135, 84, 0.2)', 'rgba(255, 193, 7, 0.2)', 'rgba(220, 53, 69, 0.2)', 'rgba(13, 202, 240, 0.2)', 'rgba(108, 117, 125, 0.2)'],
                border: ['#0d6efd', '#198754', '#ffc107', '#dc3545', '#0dcaf0', '#6c757d']
            },
            blues: {
                background: ['rgba(13, 110, 253, 0.2)', 'rgba(13, 202, 240, 0.2)', 'rgba(77, 171, 247, 0.2)', 'rgba(28, 126, 214, 0.2)', 'rgba(51, 154, 240, 0.2)', 'rgba(108, 117, 125, 0.2)'],
                border: ['#0d6efd', '#0dcaf0', '#4dabf7', '#1c7ed6', '#339af0', '#6c757d']
            },
            success: {
                background: ['rgba(25, 135, 84, 0.2)', 'rgba(81, 207, 102, 0.2)', 'rgba(55, 178, 77, 0.2)', 'rgba(47, 158, 68, 0.2)', 'rgba(13, 202, 240, 0.2)', 'rgba(13, 110, 253, 0.2)'],
                border: ['#198754', '#51cf66', '#37b24d', '#2f9e44', '#0dcaf0', '#0d6efd']
            }
        };
        
        return palettes[palette] || palettes.default;
    }
    
    /**
     * Set callback to get current slide data
     * @param {Function} callback - Function that returns {currentSlide, learnerSession}
     */
    setGetCurrentSlideDataCallback(callback) {
        this.getCurrentSlideData = callback;
        console.log('🎯 [SLIDE-CONTROLS] getCurrentSlideData callback set');
    }
    
    /**
     * Set callback to display slide content
     * @param {Function} callback - Function to display slide content
     */
    setDisplaySlideContentCallback(callback) {
        this.displaySlideContent = callback;
        console.log('🎯 [SLIDE-CONTROLS] displaySlideContent callback set');
    }
    
    /**
     * Set callback to convert markdown to HTML
     * @param {Function} callback - Function to convert markdown to HTML
     */
    setMarkdownToHtmlCallback(callback) {
        this.markdownToHtml = callback;
        console.log('🎯 [SLIDE-CONTROLS] markdownToHtml callback set');
    }
    
    /**
     * Set callback to get current slide markdown
     * @param {Function} callback - Function to get current slide markdown
     */
    setGetCurrentSlideMarkdownCallback(callback) {
        this.getCurrentSlideMarkdown = callback;
        console.log('🎯 [SLIDE-CONTROLS] getCurrentSlideMarkdown callback set');
    }
    
    /**
     * Set callback to update current slide content
     * @param {Function} callback - Function to update current slide content
     */
    setUpdateCurrentSlideContentCallback(callback) {
        this.updateCurrentSlideContent = callback;
        console.log('🎯 [SLIDE-CONTROLS] updateCurrentSlideContent callback set');
    }
    
    // Note: showSlideLimitModal() removed - slide limitations now handled by NavigationControls
    // This enables proper B2C/B2B session detection with Stripe payment integration
}