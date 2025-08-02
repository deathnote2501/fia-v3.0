/**
 * FIA v3.0 - Interface Introduction Popovers Component
 * 
 * This component manages Bootstrap popovers to introduce the interface elements
 * to learners when they arrive on their first "plan" slide. All popovers are shown
 * by default and can be closed individually by the learner.
 * 
 * Features:
 * - Auto-display on first plan slide visit
 * - Bootstrap 5 popovers with manual trigger control
 * - Individual popover dismissal
 * - LocalStorage persistence to prevent re-showing
 * - User-friendly explanations for each interface element
 * - Responsive positioning with Bootstrap auto-placement
 * 
 * Dependencies:
 * - Bootstrap 5.3.2 (Popover component)
 * - LocalStorage API for persistence
 * 
 * @author FIA v3.0 Platform
 * @version 1.0.0
 */

export class InterfaceIntroductionPopovers {
    constructor() {
        // Persistence key for localStorage
        this.STORAGE_KEY = 'fia_interface_intro_completed';
        
        // Popover instances storage
        this.popoverInstances = new Map();
        
        // Track which popovers are still open
        this.activePopovers = new Set();
        
        // Configuration for each interface element
        this.interfaceElements = this.getInterfaceElementsConfig();
        
        console.log('🎯 [INTERFACE-INTRO] InterfaceIntroductionPopovers initialized');
    }
    
    /**
     * Check if the interface introduction should be shown
     * @returns {boolean} True if introduction should be shown
     */
    shouldShowIntroduction() {
        // Check if introduction was already completed
        const completed = localStorage.getItem(this.STORAGE_KEY);
        const shouldShow = !completed;
        
        console.log(`🔍 [INTERFACE-INTRO] Should show introduction: ${shouldShow}`);
        return shouldShow;
    }
    
    /**
     * Show all introduction popovers
     */
    showIntroductionPopovers() {
        if (!this.shouldShowIntroduction()) {
            console.log('ℹ️ [INTERFACE-INTRO] Introduction already completed, skipping');
            return;
        }
        
        console.log('🚀 [INTERFACE-INTRO] Starting interface introduction...');
        
        // Wait a bit for the interface to be fully loaded
        setTimeout(() => {
            this.initializeAllPopovers();
            this.showAllPopovers();
        }, 500);
    }
    
    /**
     * Initialize all Bootstrap popover instances
     */
    initializeAllPopovers() {
        console.log('🛠️ [INTERFACE-INTRO] Initializing Bootstrap popovers...');
        
        this.interfaceElements.forEach((config, elementId) => {
            const element = document.getElementById(elementId);
            
            if (!element) {
                console.warn(`⚠️ [INTERFACE-INTRO] Element not found: ${elementId}`);
                return;
            }
            
            // Check if Bootstrap is available
            if (typeof bootstrap === 'undefined') {
                console.error('❌ [INTERFACE-INTRO] Bootstrap is not loaded');
                return;
            }
            
            // PHASE 4: Get translated content using i18n system
            const title = this.getTranslation(config.titleKey);
            const content = this.getTranslation(config.contentKey);
            
            // Create popover instance with enhanced Bootstrap configuration
            const popoverInstance = new bootstrap.Popover(element, {
                // PHASE 3: Contrôle programmatique complet
                trigger: 'manual',
                
                // PHASE 3: Positionnement automatique intelligent 
                placement: 'auto',
                
                // PHASE 3: Support HTML pour contenu riche
                html: true,
                
                // PHASE 3: Configuration avancée Bootstrap
                sanitize: false,        // Permet le HTML custom pour les boutons
                animation: true,        // Animations fluides
                delay: { show: 100, hide: 50 },  // Délais optimisés
                
                // PHASE 4: Contenu traduit via i18n
                title: title,
                content: this.generatePopoverContent(content, elementId),
                
                // PHASE 3: Template Bootstrap optimisé
                template: this.getPopoverTemplate(),
                
                // PHASE 3: Classes CSS personnalisées
                customClass: 'interface-intro-popover fia-intro-enhanced',
                
                // PHASE 3: Contrôle du conteneur d'affichage
                container: 'body',      // Évite les problèmes de z-index
                
                // PHASE 3: Configuration accessibilité
                fallbackPlacements: ['top', 'bottom', 'left', 'right']
            });
            
            // Store the instance
            this.popoverInstances.set(elementId, popoverInstance);
            this.activePopovers.add(elementId);
            
            console.log(`✅ [INTERFACE-INTRO] Popover initialized for: ${elementId}`);
        });
    }
    
    /**
     * Show all initialized popovers
     */
    showAllPopovers() {
        console.log('📢 [INTERFACE-INTRO] Showing all popovers...');
        
        this.popoverInstances.forEach((popoverInstance, elementId) => {
            try {
                popoverInstance.show();
                console.log(`👁️ [INTERFACE-INTRO] Popover shown: ${elementId}`);
            } catch (error) {
                console.error(`❌ [INTERFACE-INTRO] Error showing popover for ${elementId}:`, error);
            }
        });
        
        // Setup close button handlers after popovers are shown
        setTimeout(() => {
            this.setupCloseButtonHandlers();
        }, 100);
    }
    
    /**
     * Hide all popovers immediately
     */
    hideAllPopovers() {
        console.log('🙈 [INTERFACE-INTRO] Hiding all popovers...');
        
        this.popoverInstances.forEach((popoverInstance, elementId) => {
            try {
                popoverInstance.hide();
                console.log(`👁️‍🗨️ [INTERFACE-INTRO] Popover hidden: ${elementId}`);
            } catch (error) {
                console.error(`❌ [INTERFACE-INTRO] Error hiding popover for ${elementId}:`, error);
            }
        });
        
        // Clear active popovers set
        this.activePopovers.clear();
        
        // Mark introduction as completed
        this.markIntroductionCompleted();
    }
    
    /**
     * Hide a specific popover
     * @param {string} elementId - ID of the element to hide popover for
     */
    hidePopover(elementId) {
        const popoverInstance = this.popoverInstances.get(elementId);
        
        if (!popoverInstance) {
            console.warn(`⚠️ [INTERFACE-INTRO] No popover instance found for: ${elementId}`);
            return;
        }
        
        try {
            popoverInstance.hide();
            this.activePopovers.delete(elementId);
            
            console.log(`✅ [INTERFACE-INTRO] Popover closed: ${elementId}`);
            
            // Check if all popovers are closed
            if (this.activePopovers.size === 0) {
                console.log('🎯 [INTERFACE-INTRO] All popovers closed - marking introduction as completed');
                this.markIntroductionCompleted();
            }
            
        } catch (error) {
            console.error(`❌ [INTERFACE-INTRO] Error hiding popover for ${elementId}:`, error);
        }
    }
    
    /**
     * Mark introduction as completed in localStorage
     */
    markIntroductionCompleted() {
        localStorage.setItem(this.STORAGE_KEY, 'true');
        console.log('💾 [INTERFACE-INTRO] Introduction marked as completed');
    }
    
    /**
     * Reset introduction state (for testing purposes)
     */
    resetIntroductionState() {
        localStorage.removeItem(this.STORAGE_KEY);
        console.log('🔄 [INTERFACE-INTRO] Introduction state reset');
    }
    
    /**
     * Setup event handlers for close buttons in popovers
     */
    setupCloseButtonHandlers() {
        console.log('🔗 [INTERFACE-INTRO] Setting up close button handlers...');
        
        // Find all close buttons in popovers and attach handlers
        document.querySelectorAll('.interface-intro-close').forEach(closeBtn => {
            closeBtn.addEventListener('click', (event) => {
                event.preventDefault();
                event.stopPropagation();
                
                const elementId = closeBtn.getAttribute('data-element-id');
                if (elementId) {
                    this.hidePopover(elementId);
                }
            });
        });
    }
    
    /**
     * PHASE 4: Generate enhanced Bootstrap popover content with i18n support
     * @param {string} content - Main content text (already translated)
     * @param {string} elementId - Element ID for close button
     * @returns {string} Enhanced HTML content for popover
     */
    generatePopoverContent(content, elementId) {
        // PHASE 4: Get translated button texts
        const closeButtonText = this.getTranslation('intro.closeButton');
        const closeButtonTooltip = this.getTranslation('intro.closeButtonTooltip');
        
        return `
            <div class="interface-intro-content">
                <!-- PHASE 3: Contenu principal avec typographie Bootstrap -->
                <p class="mb-3 text-muted fw-normal lh-base">${content}</p>
                
                <!-- PHASE 3: Section action avec bouton Bootstrap enhanced -->
                <div class="d-flex justify-content-end align-items-center mt-3 pt-2 border-top border-light">
                    <button type="button" 
                            class="btn btn-sm btn-primary interface-intro-close shadow-sm" 
                            data-element-id="${elementId}"
                            data-bs-toggle="tooltip" 
                            title="${closeButtonTooltip}">
                        <i class="bi bi-check-circle me-1"></i>
                        <span class="fw-semibold">${closeButtonText}</span>
                    </button>
                </div>
            </div>
        `;
    }
    
    /**
     * PHASE 4: Get translation from i18n system with fallback
     * @param {string} key - Translation key
     * @returns {string} Translated text or fallback
     */
    getTranslation(key) {
        // Try to use global i18n service if available
        if (window.i18n && typeof window.i18n.t === 'function') {
            try {
                const translation = window.i18n.t(key);
                // Check if translation was found (key != translation)
                if (translation && translation !== key) {
                    return translation;
                }
            } catch (error) {
                console.warn(`⚠️ [INTERFACE-INTRO] Error getting translation for key: ${key}`, error);
            }
        }
        
        // Fallback to safeT helper if available
        if (window.safeT && typeof window.safeT === 'function') {
            try {
                return window.safeT(key);
            } catch (error) {
                console.warn(`⚠️ [INTERFACE-INTRO] Error with safeT for key: ${key}`, error);
            }
        }
        
        // Hard fallbacks in French (for MVP tests)
        const fallbacks = {
            'intro.chatInput.title': '💬 Zone de Chat',
            'intro.chatInput.content': 'Posez vos questions à votre formateur IA ici. Il vous aidera à comprendre le contenu et répondra à vos doutes.',
            'intro.voiceChat.title': '🎤 Reconnaissance Vocale',
            'intro.voiceChat.content': 'Cliquez pour parler directement à votre formateur IA. Votre voix sera convertie en texte.',
            'intro.audioToggle.title': '🔊 Audio des Réponses',
            'intro.audioToggle.content': 'Activez cette option pour entendre les réponses de l\'IA à voix haute.',
            'intro.vocalChat.title': '🗣️ Conversation Vocale',
            'intro.vocalChat.content': 'Démarrez une conversation vocale en temps réel avec l\'IA Gemini.',
            'intro.nextButton.title': '➡️ Navigation Suivante',
            'intro.nextButton.content': 'Naviguez entre les slides de votre formation personnalisée.',
            'intro.previousButton.title': '⬅️ Navigation Précédente',
            'intro.previousButton.content': 'Naviguez entre les slides de votre formation personnalisée.',
            'intro.simplifyButton.title': '📝 Simplifier le Contenu',
            'intro.simplifyButton.content': 'Demandez une version simplifiée du contenu actuel.',
            'intro.moreDetailsButton.title': '🔍 Plus de Détails',
            'intro.moreDetailsButton.content': 'Obtenez plus de détails et d\'approfondissement sur le sujet.',
            'intro.chartButton.title': '📊 Générer un Graphique',
            'intro.chartButton.content': 'Générez un graphique ou diagramme pour illustrer le contenu.',
            'intro.closeButton': 'Compris',
            'intro.closeButtonTooltip': 'Fermer cette aide'
        };
        
        return fallbacks[key] || `[${key}]`;
    }
    
    /**
     * PHASE 3: Get enhanced Bootstrap popover template with optimal styling
     * @returns {string} Enhanced Bootstrap popover template
     */
    getPopoverTemplate() {
        return `
            <div class="popover interface-intro-popover fia-intro-enhanced" role="tooltip">
                <!-- PHASE 3: Flèche de positionnement Bootstrap -->
                <div class="popover-arrow"></div>
                
                <!-- PHASE 3: Header avec style Bootstrap primary + icons -->
                <h3 class="popover-header bg-primary text-white fw-bold border-0">
                    <i class="bi bi-info-circle-fill me-2"></i>
                    <span class="popover-title-text"></span>
                </h3>
                
                <!-- PHASE 3: Body avec padding optimisé -->
                <div class="popover-body p-3"></div>
            </div>
        `;
    }
    
    /**
     * PHASE 4: Configuration for all interface elements with i18n support
     * @returns {Map} Map of element ID to configuration object
     */
    getInterfaceElementsConfig() {
        const config = new Map();
        
        // PHASE 4: Chat Input Field - Zone de saisie principale
        config.set('chat-input', {
            titleKey: 'intro.chatInput.title',
            contentKey: 'intro.chatInput.content',
            placement: 'top'  // Au-dessus pour ne pas masquer le clavier
        });
        
        // PHASE 4: Voice Chat Button (Microphone) - À côté du chat
        config.set('voice-chat-btn', {
            titleKey: 'intro.voiceChat.title',
            contentKey: 'intro.voiceChat.content',
            placement: 'top'  // Au-dessus comme le chat
        });
        
        // PHASE 4: TTS Toggle - Section audio en haut à gauche
        config.set('tts-toggle', {
            titleKey: 'intro.audioToggle.title',
            contentKey: 'intro.audioToggle.content',
            placement: 'bottom'  // En dessous car en haut de l'interface
        });
        
        // PHASE 4: Live API Button - Section audio en haut à gauche  
        config.set('live-api-btn', {
            titleKey: 'intro.vocalChat.title',
            contentKey: 'intro.vocalChat.content',
            placement: 'bottom'  // En dessous car en haut de l'interface
        });
        
        // PHASE 4: Next Button - Navigation principale droite
        config.set('new-next-btn', {
            titleKey: 'intro.nextButton.title',
            contentKey: 'intro.nextButton.content',
            placement: 'top'  // Au-dessus, bouton important
        });
        
        // PHASE 4: Previous Button - Navigation principale gauche  
        config.set('new-previous-btn', {
            titleKey: 'intro.previousButton.title',
            contentKey: 'intro.previousButton.content',
            placement: 'top'  // Au-dessus, bouton important
        });
        
        // PHASE 4: Simplify Button - Actions centrales
        config.set('new-simplify-btn', {
            titleKey: 'intro.simplifyButton.title',
            contentKey: 'intro.simplifyButton.content',
            placement: 'top'  // Au-dessus pour être visible
        });
        
        // PHASE 4: More Details Button - Actions centrales
        config.set('new-more-details-btn', {
            titleKey: 'intro.moreDetailsButton.title',
            contentKey: 'intro.moreDetailsButton.content',
            placement: 'top'  // Au-dessus pour être visible
        });
        
        // PHASE 4: Generate Chart Button - Actions avancées
        config.set('generate-chart-btn', {
            titleKey: 'intro.chartButton.title',
            contentKey: 'intro.chartButton.content',
            placement: 'top'  // Au-dessus pour être visible
        });
        
        return config;
    }
    
    /**
     * Cleanup method to destroy all popover instances
     */
    destroy() {
        console.log('🧹 [INTERFACE-INTRO] Destroying all popover instances...');
        
        this.popoverInstances.forEach((popoverInstance, elementId) => {
            try {
                popoverInstance.dispose();
                console.log(`🗑️ [INTERFACE-INTRO] Popover disposed: ${elementId}`);
            } catch (error) {
                console.error(`❌ [INTERFACE-INTRO] Error disposing popover for ${elementId}:`, error);
            }
        });
        
        this.popoverInstances.clear();
        this.activePopovers.clear();
        
        console.log('✅ [INTERFACE-INTRO] Cleanup completed');
    }
}