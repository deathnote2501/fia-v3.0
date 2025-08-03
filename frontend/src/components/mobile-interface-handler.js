/**
 * FIA v3.0 - Mobile Interface Handler
 * Handles mobile-specific interface interactions and connects mobile UI elements
 * to existing desktop functionality for seamless cross-platform experience.
 */

export class MobileInterfaceHandler {
    constructor({ slideControls, chatInterface, navigationControls }) {
        this.slideControls = slideControls;
        this.chatInterface = chatInterface;
        this.navigationControls = navigationControls;
        
        console.log('📱 [MOBILE-INTERFACE] Mobile Interface Handler initialized');
        
        this.setupMobileEventHandlers();
    }
    
    /**
     * Setup all mobile-specific event handlers
     * Connects mobile UI elements to existing desktop functionality
     */
    setupMobileEventHandlers() {
        this.setupMobileToolbarEvents();
        this.setupMobileChatActionEvents();
        this.setupMobileTTSEvents();
        this.setupMobileInputEvents();
        
        console.log('📱 [MOBILE-INTERFACE] All mobile event handlers configured');
    }
    
    /**
     * Setup mobile toolbar navigation events
     * Connects to existing NavigationControls functionality
     */
    setupMobileToolbarEvents() {
        // Mobile Previous Button → Desktop Previous Button
        const mobilePreviousBtn = document.getElementById('mobile-previous-btn');
        const desktopPreviousBtn = document.getElementById('new-previous-btn');
        
        if (mobilePreviousBtn && desktopPreviousBtn) {
            mobilePreviousBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('📱 [MOBILE-INTERFACE] Mobile previous button clicked');
                desktopPreviousBtn.click();
            });
        }
        
        // Mobile Next Button → Desktop Next Button
        const mobileNextBtn = document.getElementById('mobile-next-btn');
        const desktopNextBtn = document.getElementById('new-next-btn');
        
        if (mobileNextBtn && desktopNextBtn) {
            mobileNextBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('📱 [MOBILE-INTERFACE] Mobile next button clicked');
                desktopNextBtn.click();
            });
        }
        
        // Mobile Simplify Button → Desktop Simplify Button
        const mobileSimplifyBtn = document.getElementById('mobile-simplify-btn');
        const desktopSimplifyBtn = document.getElementById('new-simplify-btn');
        
        if (mobileSimplifyBtn && desktopSimplifyBtn) {
            mobileSimplifyBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('📱 [MOBILE-INTERFACE] Mobile simplify button clicked');
                desktopSimplifyBtn.click();
            });
        }
        
        // Mobile More Details Button → Desktop More Details Button
        const mobileMoreDetailsBtn = document.getElementById('mobile-more-details-btn');
        const desktopMoreDetailsBtn = document.getElementById('new-more-details-btn');
        
        if (mobileMoreDetailsBtn && desktopMoreDetailsBtn) {
            mobileMoreDetailsBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('📱 [MOBILE-INTERFACE] Mobile more details button clicked');
                desktopMoreDetailsBtn.click();
            });
        }
        
        // Mobile Chart Button → Desktop Chart Button
        const mobileChartBtn = document.getElementById('mobile-chart-btn');
        const desktopChartBtn = document.getElementById('generate-chart-btn');
        
        if (mobileChartBtn && desktopChartBtn) {
            mobileChartBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('📱 [MOBILE-INTERFACE] Mobile chart button clicked');
                desktopChartBtn.click();
            });
        }
        
        console.log('📱 [MOBILE-INTERFACE] Mobile toolbar events configured');
    }
    
    /**
     * Setup mobile chat action events
     * Connects to existing ChatInterface contextual actions
     */
    setupMobileChatActionEvents() {
        // Mobile Comment Button → Desktop Comment Button
        const mobileCommentBtn = document.getElementById('mobile-comment-btn');
        const desktopCommentBtn = document.getElementById('comment-btn');
        
        if (mobileCommentBtn && desktopCommentBtn) {
            mobileCommentBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('📱 [MOBILE-INTERFACE] Mobile comment button clicked');
                desktopCommentBtn.click();
            });
        }
        
        // Mobile Quiz Button → Desktop Quiz Button
        const mobileQuizBtn = document.getElementById('mobile-quiz-btn');
        const desktopQuizBtn = document.getElementById('quiz-btn');
        
        if (mobileQuizBtn && desktopQuizBtn) {
            mobileQuizBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('📱 [MOBILE-INTERFACE] Mobile quiz button clicked');
                desktopQuizBtn.click();
            });
        }
        
        // Mobile Examples Button → Desktop Examples Button
        const mobileExamplesBtn = document.getElementById('mobile-examples-btn');
        const desktopExamplesBtn = document.getElementById('examples-btn');
        
        if (mobileExamplesBtn && desktopExamplesBtn) {
            mobileExamplesBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('📱 [MOBILE-INTERFACE] Mobile examples button clicked');
                desktopExamplesBtn.click();
            });
        }
        
        // Mobile Key Points Button → Desktop Key Points Button
        const mobileKeyPointsBtn = document.getElementById('mobile-key-points-btn');
        const desktopKeyPointsBtn = document.getElementById('key-points-btn');
        
        if (mobileKeyPointsBtn && desktopKeyPointsBtn) {
            mobileKeyPointsBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('📱 [MOBILE-INTERFACE] Mobile key points button clicked');
                desktopKeyPointsBtn.click();
            });
        }
        
        console.log('📱 [MOBILE-INTERFACE] Mobile chat action events configured');
    }
    
    /**
     * Setup mobile TTS control events
     * Connects to existing TTS functionality
     */
    setupMobileTTSEvents() {
        // Mobile TTS Toggle → Desktop TTS Toggle
        const mobileTTSToggle = document.getElementById('mobile-tts-toggle');
        const desktopTTSToggle = document.getElementById('tts-toggle');
        
        if (mobileTTSToggle && desktopTTSToggle) {
            // Sync mobile toggle with desktop toggle
            mobileTTSToggle.addEventListener('change', (e) => {
                console.log('📱 [MOBILE-INTERFACE] Mobile TTS toggle changed:', e.target.checked);
                desktopTTSToggle.checked = e.target.checked;
                desktopTTSToggle.dispatchEvent(new Event('change'));
            });
            
            // Sync desktop toggle changes back to mobile
            desktopTTSToggle.addEventListener('change', (e) => {
                mobileTTSToggle.checked = e.target.checked;
            });
        }
        
        // Mobile Live API Button → Desktop Live API Button
        const mobileLiveAPIBtn = document.getElementById('mobile-live-api-btn');
        const desktopLiveAPIBtn = document.getElementById('live-api-btn');
        
        if (mobileLiveAPIBtn && desktopLiveAPIBtn) {
            mobileLiveAPIBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('📱 [MOBILE-INTERFACE] Mobile Live API button clicked');
                desktopLiveAPIBtn.click();
            });
        }
        
        console.log('📱 [MOBILE-INTERFACE] Mobile TTS events configured');
    }
    
    /**
     * Setup mobile input events
     * Connects mobile chat input to existing chat functionality
     */
    setupMobileInputEvents() {
        const mobileChatInput = document.getElementById('mobile-chat-input');
        const desktopChatInput = document.getElementById('chat-input');
        const mobileVoiceChatBtn = document.getElementById('mobile-voice-chat-btn');
        const desktopVoiceChatBtn = document.getElementById('voice-chat-btn');
        
        // Sync mobile input with desktop input
        if (mobileChatInput && desktopChatInput) {
            // Auto-expanding textarea for mobile
            this.setupAutoExpandingTextarea(mobileChatInput);
            
            // Sync content between mobile and desktop inputs
            mobileChatInput.addEventListener('input', (e) => {
                desktopChatInput.value = e.target.value;
            });
            
            // Handle mobile Enter key
            mobileChatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMobileMessage();
                }
            });
        }
        
        // Mobile Voice Chat Button → Desktop Voice Chat Button
        if (mobileVoiceChatBtn && desktopVoiceChatBtn) {
            mobileVoiceChatBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('📱 [MOBILE-INTERFACE] Mobile voice chat button clicked');
                desktopVoiceChatBtn.click();
            });
        }
        
        console.log('📱 [MOBILE-INTERFACE] Mobile input events configured');
    }
    
    /**
     * Send message from mobile input
     */
    sendMobileMessage() {
        const mobileChatInput = document.getElementById('mobile-chat-input');
        const desktopChatInput = document.getElementById('chat-input');
        
        if (mobileChatInput && desktopChatInput && mobileChatInput.value.trim()) {
            console.log('📱 [MOBILE-INTERFACE] Sending mobile message:', mobileChatInput.value);
            
            // Copy to desktop input and trigger send
            desktopChatInput.value = mobileChatInput.value;
            
            // Trigger desktop send mechanism
            const sendEvent = new KeyboardEvent('keydown', {
                key: 'Enter',
                code: 'Enter',
                keyCode: 13,
                which: 13,
                bubbles: true
            });
            desktopChatInput.dispatchEvent(sendEvent);
            
            // Clear mobile input
            mobileChatInput.value = '';
            this.resetTextareaHeight(mobileChatInput);
        }
    }
    
    /**
     * Setup auto-expanding textarea for mobile
     * @param {HTMLTextAreaElement} textarea - The textarea element
     */
    setupAutoExpandingTextarea(textarea) {
        if (!textarea) return;
        
        textarea.addEventListener('input', () => {
            this.adjustTextareaHeight(textarea);
        });
        
        // Initial adjustment
        this.adjustTextareaHeight(textarea);
    }
    
    /**
     * Adjust textarea height based on content
     * @param {HTMLTextAreaElement} textarea - The textarea element
     */
    adjustTextareaHeight(textarea) {
        // Reset height to get accurate scrollHeight
        textarea.style.height = 'auto';
        
        // Calculate new height (max 4 lines)
        const lineHeight = parseInt(window.getComputedStyle(textarea).lineHeight);
        const maxLines = 4;
        const maxHeight = lineHeight * maxLines;
        
        const newHeight = Math.min(textarea.scrollHeight, maxHeight);
        textarea.style.height = newHeight + 'px';
    }
    
    /**
     * Reset textarea height to single line
     * @param {HTMLTextAreaElement} textarea - The textarea element
     */
    resetTextareaHeight(textarea) {
        textarea.style.height = 'auto';
    }
    
    /**
     * Update mobile button states to match desktop buttons
     * Called by NavigationControls when button states change
     */
    updateMobileButtonStates() {
        // Update mobile navigation buttons
        this.syncButtonState('mobile-previous-btn', 'new-previous-btn');
        this.syncButtonState('mobile-next-btn', 'new-next-btn');
        this.syncButtonState('mobile-simplify-btn', 'new-simplify-btn');
        this.syncButtonState('mobile-more-details-btn', 'new-more-details-btn');
        this.syncButtonState('mobile-chart-btn', 'generate-chart-btn');
        
        console.log('📱 [MOBILE-INTERFACE] Mobile button states updated');
    }
    
    /**
     * Sync button state from desktop to mobile
     * @param {string} mobileId - Mobile button ID
     * @param {string} desktopId - Desktop button ID
     */
    syncButtonState(mobileId, desktopId) {
        const mobileBtn = document.getElementById(mobileId);
        const desktopBtn = document.getElementById(desktopId);
        
        if (mobileBtn && desktopBtn) {
            mobileBtn.disabled = desktopBtn.disabled;
            
            // Copy classes for visual state
            if (desktopBtn.disabled) {
                mobileBtn.classList.add('opacity-50');
            } else {
                mobileBtn.classList.remove('opacity-50');
            }
        }
    }
    
    /**
     * Check if the current viewport is mobile
     * @returns {boolean} True if mobile viewport
     */
    isMobileViewport() {
        return window.innerWidth <= 768;
    }
}