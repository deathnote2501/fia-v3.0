/**
 * FIA v3.0 - Main Application Orchestrator
 * Replaces the monolithic TrainingApp class with a modular ES6 architecture
 */

// Import all the extracted components
import { VoiceChatHandler } from './components/voice-chat-handler.js';
import { TTSManager } from './components/tts-manager.js';
import { ChatInterface } from './components/chat-interface.js';
import { SlideControls } from './components/slide-controls.js';
import { NavigationControls } from './components/navigation-controls.js';
import { SlideContentManager } from './components/slide-content-manager.js';
import { ProgressManager } from './utils/progress-manager.js';
import { AutoExpandingTextarea } from './utils/auto-expanding-textarea.js';
import { GeminiLiveAPI } from './components/gemini-live-api.js';

/**
 * Main Application Class - Orchestrates all components
 */
export class FIATrainingApp {
    constructor() {
        // Core properties
        this.learnerSession = {};
        this.sessionData = {};
        this.currentSlide = null;
        this.currentSlideContent = null;
        this.container = null;
        
        // Component instances
        this.ttsManager = new TTSManager();
        this.chatInterface = null; // Will be initialized with dependencies
        this.slideControls = new SlideControls();
        this.navigationControls = new NavigationControls();
        this.slideContentManager = new SlideContentManager();
        this.progressManager = new ProgressManager();
        this.geminiLiveAPI = null; // Will use the one from ChatInterface
        
        console.log('🚀 [FIA-APP] FIATrainingApp orchestrator initialized');
    }
    
    /**
     * Initialize the application with session data
     * @param {Object} learnerSession - Learner session data
     * @param {Object} sessionData - Training session data
     */
    async initialize(learnerSession, sessionData) {
        try {
            console.log('🚀 [FIA-APP] Initializing application...');
            
            // Store session data
            this.learnerSession = learnerSession;
            this.sessionData = sessionData;
            
            // Get main container
            this.container = document.getElementById('main-content');
            if (!this.container) {
                throw new Error('Main content container not found');
            }
            
            // Initialize components with dependencies
            await this.initializeComponents();
            
            // Setup component callbacks and connections
            this.setupComponentCallbacks();
            
            // Initialize Chat Interface (which has complex dependencies)
            this.chatInterface = new ChatInterface({
                ttsManager: this.ttsManager,
                learnerSession: this.learnerSession,
                sessionData: this.sessionData,
                currentSlide: this.currentSlide,
                currentSlideContent: this.currentSlideContent
            });
            
            // Initialize chat interface
            this.chatInterface.initialize();
            
            // Setup navigation buttons
            this.slideControls.setupNavigationButtons();
            
            // Setup GeminiLiveAPI integration
            await this.setupGeminiLiveAPIIntegration();
            
            console.log('✅ [FIA-APP] Application initialized successfully');
            
        } catch (error) {
            console.error('❌ [FIA-APP] Application initialization failed:', error);
            throw error;
        }
    }
    
    /**
     * Initialize all components with their dependencies
     */
    async initializeComponents() {
        // Set container for slide content manager
        this.slideContentManager.setContainer(this.container);
        
        // GeminiLiveAPI will be initialized by ChatInterface
        
        console.log('✅ [FIA-APP] Components initialized');
    }
    
    /**
     * Setup GeminiLiveAPI integration - get reference from ChatInterface for context updates
     */
    async setupGeminiLiveAPIIntegration() {
        if (this.chatInterface && this.chatInterface.geminiLiveAPI) {
            // Get reference to the GeminiLiveAPI instance from ChatInterface for context updates
            this.geminiLiveAPI = this.chatInterface.geminiLiveAPI;
            
            console.log('✅ [FIA-APP] GeminiLiveAPI reference obtained from ChatInterface');
        } else {
            console.warn('⚠️ [FIA-APP] ChatInterface or GeminiLiveAPI not available');
        }
    }
    
    /**
     * Setup callbacks between components to enable communication
     */
    setupComponentCallbacks() {
        // === SLIDE CONTROLS CALLBACKS ===
        this.slideControls.setGetCurrentSlideDataCallback(() => ({
            currentSlide: this.currentSlide,
            learnerSession: this.learnerSession
        }));
        
        this.slideControls.setDisplaySlideContentCallback((slideData) => {
            this.displaySlideContent(slideData);
        });
        
        this.slideControls.setMarkdownToHtmlCallback((markdown) => {
            return this.slideContentManager.markdownToHtml(markdown);
        });
        
        this.slideControls.setGetCurrentSlideMarkdownCallback(() => {
            return this.slideContentManager.getCurrentSlideMarkdown();
        });
        
        this.slideControls.setUpdateCurrentSlideContentCallback((content) => {
            this.slideContentManager.updateCurrentSlideContent(content);
            this.currentSlideContent = content;
        });
        
        // === SLIDE CONTENT MANAGER CALLBACKS ===
        this.slideContentManager.setUpdateBreadcrumbCallback((slideData) => {
            this.navigationControls.updateBreadcrumb(slideData);
        });
        
        this.slideContentManager.setStopProgressAnimationCallback(() => {
            this.progressManager.stopProgressAnimation();
        });
        
        console.log('✅ [FIA-APP] Component callbacks configured');
    }
    
    /**
     * Display slide content using the slide content manager
     * @param {Object} slideData - Slide data to display
     */
    displaySlideContent(slideData) {
        // Store current slide data
        this.currentSlide = slideData;
        
        // Use slide content manager to display content
        const result = this.slideContentManager.displaySlideContent(slideData);
        
        // Update current slide content
        this.currentSlideContent = result.content;
        
        // Update chat interface with new slide data
        if (this.chatInterface) {
            this.chatInterface.updateCurrentSlide(slideData, result.content);
        }
        
        // Update navigation button states
        this.navigationControls.updateNavigationButtonStates(slideData);
        
        // Update GeminiLiveAPI context when slide changes
        if (this.geminiLiveAPI && this.learnerSession && this.learnerSession.id) {
            this.geminiLiveAPI.updateContext(this.learnerSession.id).catch(error => {
                // Context update error supprimé pour interface propre
            });
        }
        
        console.log('✅ [FIA-APP] Slide content displayed and components updated');
    }
    
    /**
     * Generate first slide and start training
     * @param {string} email - Learner email for session creation
     */
    async generateFirstSlide(email) {
        try {
            console.log('🎯 [FIA-APP] Generating first slide for email:', email);
            
            // Start progress animation
            this.progressManager.startProgressAnimation();
            
            // Show generating message
            this.container.innerHTML = `
                <div class="text-center p-5">
                    <h3>Generating Your Personalized Training Plan</h3>
                    <div class="progress mt-3" style="height: 25px;">
                        <div id="loading-progress-bar" class="progress-bar progress-bar-striped progress-bar-animated" 
                             role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">
                             0%
                        </div>
                    </div>
                </div>
            `;
            
            // Generate first slide via API
            const response = await fetch(`/api/slides/first/${this.sessionData.training_session.id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email: email })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to generate first slide');
            }
            
            const result = await response.json();
            console.log('✅ [FIA-APP] First slide generated:', result);
            
            // Store learner session
            this.learnerSession = result.learner_session;
            
            // Update chat interface with learner session
            if (this.chatInterface) {
                this.chatInterface.learnerSession = this.learnerSession;
            }
            
            // Display the generated slide
            this.displaySlideContent(result.slide_data || result.data);
            
        } catch (error) {
            console.error('❌ [FIA-APP] Error generating first slide:', error);
            this.container.innerHTML = `
                <div class="alert alert-danger">
                    <h4>Error</h4>
                    <p>Failed to generate training content: ${error.message}</p>
                    <button class="btn btn-primary" onclick="location.reload()">Try Again</button>
                </div>
            `;
        } finally {
            // Stop progress animation
            this.progressManager.stopProgressAnimation();
        }
    }
    
    /**
     * Stop progress animation
     */
    stopProgressAnimation() {
        this.progressManager.stopProgressAnimation();
    }
    
    /**
     * Audio control methods - delegated to chat interface
     */
    async playMessageAudio(messageId) {
        if (this.chatInterface) {
            return await this.chatInterface.playMessageAudio(messageId);
        } else {
            console.warn('❌ [FIA-APP] ChatInterface not available for audio playback');
        }
    }
    
    async toggleMessageAudio(messageId) {
        if (this.chatInterface) {
            return await this.chatInterface.toggleMessageAudio(messageId);
        } else {
            console.warn('❌ [FIA-APP] ChatInterface not available for audio toggle');
        }
    }
    
    pauseMessageAudio(messageId) {
        if (this.chatInterface) {
            this.chatInterface.pauseMessageAudio(messageId);
        } else {
            console.warn('❌ [FIA-APP] ChatInterface not available for audio pause');
        }
    }
    
    stopMessageAudio(messageId) {
        if (this.chatInterface) {
            this.chatInterface.stopMessageAudio(messageId);
        } else {
            console.warn('❌ [FIA-APP] ChatInterface not available for audio stop');
        }
    }
    
    /**
     * Navigation methods - delegated to slide controls
     */
    async navigateToNextSlide() {
        return this.slideControls.navigateToNextSlide();
    }
    
    async navigateToPreviousSlide() {
        return this.slideControls.navigateToPreviousSlide();
    }
    
    async simplifySlideContent() {
        return this.slideControls.simplifySlideContent();
    }
    
    async addMoreDetails() {
        return this.slideControls.addMoreDetails();
    }
    
    async generateSlideImage() {
        return this.slideControls.generateSlideImage();
    }
    
    async generateSlideChart() {
        return this.slideControls.generateSlideChart();
    }
    
    /**
     * Get current slide data for components
     * @returns {Object} Current slide and session data
     */
    getCurrentSlideData() {
        return {
            currentSlide: this.currentSlide,
            currentSlideContent: this.currentSlideContent,
            learnerSession: this.learnerSession,
            sessionData: this.sessionData
        };
    }
    
    /**
     * Cleanup resources when the app is destroyed
     */
    destroy() {
        if (this.chatInterface) {
            this.chatInterface.destroy();
        }
        this.progressManager.destroy();
        console.log('🧹 [FIA-APP] Application resources cleaned up');
    }
}

// Global app instance - will replace the global 'app' variable
window.fiaApp = null;

/**
 * Initialize the FIA Training Application
 * This function replaces the old TrainingApp initialization
 */
export const initializeFIAApp = async function(learnerSession, sessionData) {
    try {
        // Create and initialize the application
        window.fiaApp = new FIATrainingApp();
        await window.fiaApp.initialize(learnerSession, sessionData);
        
        // Make methods globally available for onclick handlers (backward compatibility)
        window.app = {
            generateFirstSlide: (email) => window.fiaApp.generateFirstSlide(email),
            displaySlideContent: (slideData) => window.fiaApp.displaySlideContent(slideData),
            playMessageAudio: (messageId) => window.fiaApp.playMessageAudio(messageId),
            pauseMessageAudio: (messageId) => window.fiaApp.pauseMessageAudio(messageId),
            stopMessageAudio: (messageId) => window.fiaApp.stopMessageAudio(messageId),
            toggleMessageAudio: (messageId) => window.fiaApp.toggleMessageAudio(messageId),
            navigateToNextSlide: () => window.fiaApp.navigateToNextSlide(),
            navigateToPreviousSlide: () => window.fiaApp.navigateToPreviousSlide(),
            simplifySlideContent: () => window.fiaApp.simplifySlideContent(),
            addMoreDetails: () => window.fiaApp.addMoreDetails(),
            generateSlideImage: () => window.fiaApp.generateSlideImage(),
            generateSlideChart: () => window.fiaApp.generateSlideChart()
        };
        
        console.log('✅ [FIA-APP] Global app interface configured');
        
    } catch (error) {
        console.error('❌ [FIA-APP] Failed to initialize FIA application:', error);
        throw error;
    }
};

// Exports:
// - FIATrainingApp (class export above)
// - initializeFIAApp (function export above)