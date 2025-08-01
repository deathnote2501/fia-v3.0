/**
 * FIA v3.0 - Slide Image Manager
 * Gère l'affichage aléatoire d'images verticales avec effet fenêtre
 */

class SlideImageManager {
    constructor() {
        this.imageContainer = document.getElementById('slide-image-window');
        this.imageCount = 11; // bg_1.webp à bg_11.webp
        this.imagePath = '../src/image/';
        
        console.log('🖼️ [SLIDE-IMAGE] SlideImageManager initialized');
    }
    
    /**
     * Génère une image aléatoire avec position aléatoire pour effet fenêtre
     */
    generateRandomImageWindow() {
        if (!this.imageContainer) {
            console.warn('⚠️ [SLIDE-IMAGE] Image container not found');
            return;
        }
        
        // Image aléatoire (1 à 11)
        const randomImageIndex = Math.floor(Math.random() * this.imageCount) + 1;
        const imagePath = `${this.imagePath}bg_${randomImageIndex}.webp`;
        
        // Position aléatoire pour effet fenêtre
        // Les images étant plus grandes, on choisit une zone visible aléatoire
        const randomX = Math.floor(Math.random() * 60); // 0-60% horizontal
        const randomY = Math.floor(Math.random() * 60); // 0-60% vertical
        
        // Application de l'image et position
        this.imageContainer.style.backgroundImage = `url('${imagePath}')`;
        this.imageContainer.style.backgroundPosition = `${randomX}% ${randomY}%`;
        
        console.log(`🎨 [SLIDE-IMAGE] Applied bg_${randomImageIndex}.webp at ${randomX}%,${randomY}%`);
        
        // Petite animation d'entrée
        this.imageContainer.style.opacity = '0';
        setTimeout(() => {
            this.imageContainer.style.opacity = '0.75';
        }, 100);
    }
    
    /**
     * Nouvelle fenêtre d'image pour chaque slide
     * Appelé depuis slide-content-manager.js
     */
    refreshImageWindow() {
        this.generateRandomImageWindow();
    }
    
    /**
     * Précharge toutes les images pour performance
     */
    preloadImages() {
        for (let i = 1; i <= this.imageCount; i++) {
            const img = new Image();
            img.src = `${this.imagePath}bg_${i}.webp`;
        }
        console.log(`📦 [SLIDE-IMAGE] Preloaded ${this.imageCount} images`);
    }
    
    /**
     * Initialise le manager d'images
     */
    init() {
        // Précharger les images
        this.preloadImages();
        
        // Générer la première image
        this.generateRandomImageWindow();
        
        console.log('✅ [SLIDE-IMAGE] SlideImageManager ready');
    }
    
    /**
     * Vérifie si on est sur mobile (responsive)
     */
    isMobile() {
        return window.innerWidth <= 768;
    }
}

// Export pour utilisation dans training-init.js
export { SlideImageManager };