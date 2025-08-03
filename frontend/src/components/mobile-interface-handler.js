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
        this.retryCount = 0;
        this.maxRetries = 10;
        
        console.log('📱 [MOBILE-INTERFACE] Mobile Interface Handler initialized');
        
        // Delay initialization to ensure all DOM elements are ready (especially in production)
        this.initializeWithRetry();
    }
    
    /**
     * Initialize mobile handlers with retry mechanism for production environments
     */
    initializeWithRetry() {
        const attemptInit = () => {
            try {
                // Check if all required mobile elements exist
                const requiredElements = [
                    'mobile-previous-btn', 'mobile-next-btn', 'mobile-simplify-btn', 
                    'mobile-more-details-btn', 'mobile-chart-btn', 'mobile-comment-btn',
                    'mobile-quiz-btn', 'mobile-examples-btn', 'mobile-key-points-btn',
                    'mobile-tts-toggle', 'mobile-live-api-btn', 'mobile-chat-input',
                    'mobile-voice-chat-btn', 'mobile-chat-messages'
                ];
                
                const missingElements = requiredElements.filter(id => !document.getElementById(id));
                
                if (missingElements.length > 0) {
                    console.warn(`📱 [MOBILE-INTERFACE] Missing elements: ${missingElements.join(', ')}`);
                    
                    if (this.retryCount < this.maxRetries) {
                        this.retryCount++;
                        console.log(`📱 [MOBILE-INTERFACE] Retry ${this.retryCount}/${this.maxRetries} in 500ms...`);
                        setTimeout(attemptInit, 500);
                        return;
                    } else {
                        console.error('📱 [MOBILE-INTERFACE] Max retries reached, some mobile elements missing');
                    }
                }
                
                // Setup event handlers
                this.setupMobileEventHandlers();
                console.log('✅ [MOBILE-INTERFACE] Mobile interface fully initialized');
                
            } catch (error) {
                console.error('📱 [MOBILE-INTERFACE] Initialization error:', error);
                
                if (this.retryCount < this.maxRetries) {
                    this.retryCount++;
                    console.log(`📱 [MOBILE-INTERFACE] Error retry ${this.retryCount}/${this.maxRetries} in 1000ms...`);
                    setTimeout(attemptInit, 1000);
                } else {
                    console.error('📱 [MOBILE-INTERFACE] Max retries reached, mobile interface may not work properly');
                }
            }
        };
        
        // Start first attempt after a small delay to ensure DOM is ready
        setTimeout(attemptInit, 100);
    }
    
    /**
     * Setup all mobile-specific event handlers
     * Connects mobile UI elements to existing desktop functionality
     */
    setupMobileEventHandlers() {
        try {
            console.log('📱 [MOBILE-INTERFACE] Setting up mobile event handlers...');
            
            // Setup each handler with individual error protection
            this.safeSetup('setupMobileToolbarEvents');
            this.safeSetup('setupMobileChatActionEvents');
            this.safeSetup('setupMobileTTSEvents');
            this.safeSetup('setupMobileInputEvents');
            this.safeSetup('setupMobileChatMessagesSync');
            
            console.log('✅ [MOBILE-INTERFACE] All mobile event handlers setup completed');
            
            // Add a global flag to indicate mobile interface is ready
            window.mobileInterfaceReady = true;
            
        } catch (error) {
            console.error('❌ [MOBILE-INTERFACE] Error setting up event handlers:', error);
            // Don't throw - allow partial functionality
        }
    }
    
    /**
     * Safe execution wrapper for setup methods
     */
    safeSetup(methodName) {
        try {
            if (typeof this[methodName] === 'function') {
                this[methodName]();
                console.log(`✅ [MOBILE-INTERFACE] ${methodName} completed successfully`);
            } else {
                console.warn(`⚠️ [MOBILE-INTERFACE] Method ${methodName} not found`);
            }
        } catch (error) {
            console.error(`❌ [MOBILE-INTERFACE] Error in ${methodName}:`, error);
            // Continue with other setup methods instead of failing completely
        }
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
                
                // Show loading spinner
                this.showButtonLoading(mobilePreviousBtn);
                
                // Click desktop button
                desktopPreviousBtn.click();
                
                // Scroll to top after slide transition
                setTimeout(() => {
                    this.scrollToSlideTop();
                }, 1000);
                
                // Hide loading after a delay (slide transition time)
                setTimeout(() => {
                    this.hideButtonLoading(mobilePreviousBtn);
                }, 2000);
            });
        }
        
        // Mobile Next Button → Desktop Next Button
        const mobileNextBtn = document.getElementById('mobile-next-btn');
        const desktopNextBtn = document.getElementById('new-next-btn');
        
        if (mobileNextBtn && desktopNextBtn) {
            mobileNextBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('📱 [MOBILE-INTERFACE] Mobile next button clicked');
                
                // Show loading spinner
                this.showButtonLoading(mobileNextBtn);
                
                // Click desktop button
                desktopNextBtn.click();
                
                // Scroll to top after slide transition
                setTimeout(() => {
                    this.scrollToSlideTop();
                }, 1000);
                
                // Hide loading after a delay (slide transition time)
                setTimeout(() => {
                    this.hideButtonLoading(mobileNextBtn);
                }, 2000);
            });
        }
        
        // Mobile Simplify Button → Desktop Simplify Button
        const mobileSimplifyBtn = document.getElementById('mobile-simplify-btn');
        const desktopSimplifyBtn = document.getElementById('new-simplify-btn');
        
        if (mobileSimplifyBtn && desktopSimplifyBtn) {
            mobileSimplifyBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('📱 [MOBILE-INTERFACE] Mobile simplify button clicked');
                
                // Show loading spinner
                this.showButtonLoading(mobileSimplifyBtn);
                
                // Click desktop button
                desktopSimplifyBtn.click();
                
                // Scroll to top after content generation
                setTimeout(() => {
                    this.scrollToSlideTop();
                }, 2000);
                
                // Hide loading after content generation
                setTimeout(() => {
                    this.hideButtonLoading(mobileSimplifyBtn);
                }, 3000);
            });
        }
        
        // Mobile More Details Button → Desktop More Details Button
        const mobileMoreDetailsBtn = document.getElementById('mobile-more-details-btn');
        const desktopMoreDetailsBtn = document.getElementById('new-more-details-btn');
        
        if (mobileMoreDetailsBtn && desktopMoreDetailsBtn) {
            mobileMoreDetailsBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('📱 [MOBILE-INTERFACE] Mobile more details button clicked');
                
                // Show loading spinner
                this.showButtonLoading(mobileMoreDetailsBtn);
                
                // Click desktop button
                desktopMoreDetailsBtn.click();
                
                // Scroll to top after content generation
                setTimeout(() => {
                    this.scrollToSlideTop();
                }, 2000);
                
                // Hide loading after content generation
                setTimeout(() => {
                    this.hideButtonLoading(mobileMoreDetailsBtn);
                }, 3000);
            });
        }
        
        // Mobile Chart Button → Desktop Chart Button
        const mobileChartBtn = document.getElementById('mobile-chart-btn');
        const desktopChartBtn = document.getElementById('generate-chart-btn');
        
        if (mobileChartBtn && desktopChartBtn) {
            mobileChartBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('📱 [MOBILE-INTERFACE] Mobile chart button clicked');
                
                // Show loading spinner
                this.showButtonLoading(mobileChartBtn);
                
                // Click desktop button
                desktopChartBtn.click();
                
                // Scroll to first chart after chart generation
                setTimeout(() => {
                    this.scrollToFirstChart();
                }, 3000);
                
                // Hide loading after chart generation
                setTimeout(() => {
                    this.hideButtonLoading(mobileChartBtn);
                }, 4000);
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
                
                // Update desktop toggle state
                desktopTTSToggle.checked = e.target.checked;
                
                // Trigger desktop TTS click event (which activates TTS functionality)
                desktopTTSToggle.click();
                
                console.log('📱 [MOBILE-INTERFACE] Desktop TTS toggle synchronized and activated');
            });
            
            // Sync desktop toggle changes back to mobile (without triggering infinite loop)
            desktopTTSToggle.addEventListener('change', (e) => {
                // Only sync if mobile toggle state is different to avoid loops
                if (mobileTTSToggle.checked !== e.target.checked) {
                    mobileTTSToggle.checked = e.target.checked;
                    console.log('📱 [MOBILE-INTERFACE] Mobile TTS toggle synced from desktop:', e.target.checked);
                }
            });
            
            // Additional sync for TTS manager state changes
            const syncTTSStates = () => {
                // Get TTS manager state from ChatInterface if available
                if (window.fiaApp && window.fiaApp.chatInterface && window.fiaApp.chatInterface.ttsManager) {
                    const ttsEnabled = window.fiaApp.chatInterface.ttsManager.enabled;
                    if (mobileTTSToggle.checked !== ttsEnabled) {
                        mobileTTSToggle.checked = ttsEnabled;
                        console.log('📱 [MOBILE-INTERFACE] Mobile TTS synced with TTS Manager state:', ttsEnabled);
                    }
                    if (desktopTTSToggle.checked !== ttsEnabled) {
                        desktopTTSToggle.checked = ttsEnabled;
                        console.log('📱 [MOBILE-INTERFACE] Desktop TTS synced with TTS Manager state:', ttsEnabled);
                    }
                }
            };
            
            // Sync states periodically and on page interactions
            setInterval(syncTTSStates, 1000); // Every second
            document.addEventListener('click', syncTTSStates);
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
            
            // Sync Live API button states from desktop to mobile
            this.syncLiveAPIButtonStates(desktopLiveAPIBtn, mobileLiveAPIBtn);
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
            
            // Sync content mobile → desktop
            mobileChatInput.addEventListener('input', (e) => {
                desktopChatInput.value = e.target.value;
                
                // Update mobile voice button state based on text content
                this.updateMobileVoiceButtonState(e.target.value);
            });
            
            // Sync content desktop → mobile (for voice transcription)
            this.syncDesktopToMobileInput(desktopChatInput, mobileChatInput);
            
            // Handle mobile Enter key (use keypress like desktop)
            mobileChatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    console.log('📱 [MOBILE-INTERFACE] Mobile Enter key pressed');
                    this.sendMobileMessage();
                }
            });
        }
        
        // Mobile Voice Chat Button → Desktop Voice Chat Button
        if (mobileVoiceChatBtn && desktopVoiceChatBtn) {
            mobileVoiceChatBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('📱 [MOBILE-INTERFACE] Mobile voice chat button clicked');
                
                // Check if we should send text or start voice recording
                const currentText = mobileChatInput ? mobileChatInput.value.trim() : '';
                const hasStateClass = mobileVoiceChatBtn.classList.contains('state-send');
                
                console.log('📱 [MOBILE-INTERFACE] Button state:', {
                    currentText: currentText,
                    hasStateClass: hasStateClass,
                    buttonClasses: mobileVoiceChatBtn.className,
                    inputExists: !!mobileChatInput
                });
                
                if (currentText && hasStateClass) {
                    // Send text message
                    console.log('📱 [MOBILE-INTERFACE] Sending message via mobile button...');
                    this.sendMobileMessage();
                } else {
                    // Start voice recording - sync with desktop
                    console.log('📱 [MOBILE-INTERFACE] Starting voice recording...');
                    desktopVoiceChatBtn.click();
                    
                    // Set mobile button to recording state
                    this.setMobileVoiceButtonState('recording');
                }
            });
            
            // Sync button states from desktop to mobile
            this.syncDesktopVoiceButtonStates(desktopVoiceChatBtn, mobileVoiceChatBtn);
        }
        
        console.log('📱 [MOBILE-INTERFACE] Mobile input events configured');
    }
    
    /**
     * Send message from mobile input
     */
    sendMobileMessage() {
        const mobileChatInput = document.getElementById('mobile-chat-input');
        const desktopChatInput = document.getElementById('chat-input');
        
        console.log('📱 [MOBILE-INTERFACE] sendMobileMessage called', {
            mobileInputExists: !!mobileChatInput,
            desktopInputExists: !!desktopChatInput,
            mobileValue: mobileChatInput ? mobileChatInput.value : 'N/A',
            desktopValue: desktopChatInput ? desktopChatInput.value : 'N/A'
        });
        
        if (mobileChatInput && desktopChatInput && mobileChatInput.value.trim()) {
            const messageText = mobileChatInput.value.trim();
            console.log('📱 [MOBILE-INTERFACE] Sending mobile message:', messageText);
            
            // Method 1: Use ChatInterface sendChatMessage directly if available
            if (window.fiaApp && window.fiaApp.chatInterface && typeof window.fiaApp.chatInterface.sendChatMessage === 'function') {
                console.log('📱 [MOBILE-INTERFACE] Using ChatInterface.sendChatMessage directly');
                window.fiaApp.chatInterface.sendChatMessage(messageText);
            } else {
                // Method 2: Copy to desktop input and trigger keypress (not keydown)
                console.log('📱 [MOBILE-INTERFACE] Using desktop input simulation');
                desktopChatInput.value = messageText;
                desktopChatInput.focus();
                
                // Trigger keypress event (same as desktop)
                const keypressEvent = new KeyboardEvent('keypress', {
                    key: 'Enter',
                    code: 'Enter',
                    keyCode: 13,
                    which: 13,
                    bubbles: true,
                    cancelable: true
                });
                
                console.log('📱 [MOBILE-INTERFACE] Dispatching keypress Enter event...');
                const result = desktopChatInput.dispatchEvent(keypressEvent);
                console.log('📱 [MOBILE-INTERFACE] Keypress event result:', result);
            }
            
            // Clear mobile input and update button state
            mobileChatInput.value = '';
            this.resetTextareaHeight(mobileChatInput);
            this.updateMobileVoiceButtonState('');
            
            console.log('📱 [MOBILE-INTERFACE] Mobile input cleared and button state updated');
        } else {
            console.warn('📱 [MOBILE-INTERFACE] Cannot send message - missing elements or empty input:', {
                mobileChatInput: !!mobileChatInput,
                desktopChatInput: !!desktopChatInput,
                hasText: mobileChatInput ? !!mobileChatInput.value.trim() : false
            });
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
     * Setup mobile chat messages synchronization
     * Syncs messages between desktop chat panel and mobile chat messages zone
     */
    setupMobileChatMessagesSync() {
        const mobileChatMessages = document.getElementById('mobile-chat-messages');
        const desktopChatMessages = document.getElementById('chat-messages');
        
        if (!mobileChatMessages || !desktopChatMessages) {
            console.warn('📱 [MOBILE-INTERFACE] Chat messages containers not found');
            return;
        }
        
        // Function to sync messages from desktop to mobile
        const syncMessages = () => {
            if (this.isMobileViewport()) {
                // Copy all messages from desktop to mobile
                mobileChatMessages.innerHTML = desktopChatMessages.innerHTML;
                
                // Scroll to bottom of mobile messages
                mobileChatMessages.scrollTop = mobileChatMessages.scrollHeight;
            }
        };
        
        // Initial sync
        syncMessages();
        
        // Set up MutationObserver to watch for new messages in desktop chat
        const observer = new MutationObserver(() => {
            syncMessages();
        });
        
        // Observe changes in desktop chat messages
        observer.observe(desktopChatMessages, {
            childList: true,
            subtree: true
        });
        
        // Sync on viewport resize (desktop ↔ mobile switching)
        window.addEventListener('resize', () => {
            setTimeout(syncMessages, 100); // Small delay to ensure layout is updated
        });
        
        console.log('📱 [MOBILE-INTERFACE] Mobile chat messages sync configured');
    }
    
    /**
     * Update mobile voice button state based on text content
     * @param {string} textValue - Current text input value
     */
    updateMobileVoiceButtonState(textValue) {
        const mobileVoiceBtn = document.getElementById('mobile-voice-chat-btn');
        const mobileVoiceBtnIcon = document.getElementById('mobile-voice-btn-icon');
        
        if (!mobileVoiceBtn || !mobileVoiceBtnIcon) return;
        
        if (textValue.trim()) {
            // Switch to send mode
            this.setMobileVoiceButtonState('send');
        } else {
            // Switch back to mic mode
            this.setMobileVoiceButtonState('mic');
        }
    }
    
    /**
     * Set mobile voice button state
     * @param {string} state - Button state: 'mic', 'recording', 'send'
     */
    setMobileVoiceButtonState(state) {
        const mobileVoiceBtn = document.getElementById('mobile-voice-chat-btn');
        const mobileVoiceBtnIcon = document.getElementById('mobile-voice-btn-icon');
        
        if (!mobileVoiceBtn || !mobileVoiceBtnIcon) return;
        
        // Remove all state classes
        mobileVoiceBtn.classList.remove('state-mic', 'state-recording', 'state-send');
        
        // Add new state class
        mobileVoiceBtn.classList.add(`state-${state}`);
        
        // Update icon
        switch (state) {
            case 'mic':
                mobileVoiceBtnIcon.className = 'bi bi-mic';
                break;
            case 'recording':
                mobileVoiceBtnIcon.className = 'bi bi-stop-fill';
                break;
            case 'send':
                mobileVoiceBtnIcon.className = 'bi bi-send';
                break;
        }
        
        console.log(`📱 [MOBILE-INTERFACE] Mobile voice button state set to: ${state}`);
    }
    
    /**
     * Sync desktop voice button states to mobile
     * @param {HTMLButtonElement} desktopBtn - Desktop voice button
     * @param {HTMLButtonElement} mobileBtn - Mobile voice button
     */
    syncDesktopVoiceButtonStates(desktopBtn, mobileBtn) {
        if (!desktopBtn || !mobileBtn) return;
        
        // Watch for class changes on desktop button
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    const desktopClasses = desktopBtn.className;
                    
                    if (desktopClasses.includes('state-recording')) {
                        this.setMobileVoiceButtonState('recording');
                    } else if (desktopClasses.includes('state-send')) {
                        this.setMobileVoiceButtonState('send');
                    } else {
                        // Check if there's text in input
                        const mobileInput = document.getElementById('mobile-chat-input');
                        if (mobileInput && mobileInput.value.trim()) {
                            this.setMobileVoiceButtonState('send');
                        } else {
                            this.setMobileVoiceButtonState('mic');
                        }
                    }
                }
            });
        });
        
        observer.observe(desktopBtn, { attributes: true });
        console.log('📱 [MOBILE-INTERFACE] Desktop voice button state sync configured');
    }
    
    /**
     * Sync Live API button states from desktop to mobile
     * @param {HTMLButtonElement} desktopBtn - Desktop Live API button
     * @param {HTMLButtonElement} mobileBtn - Mobile Live API button
     */
    syncLiveAPIButtonStates(desktopBtn, mobileBtn) {
        if (!desktopBtn || !mobileBtn) return;
        
        // Watch for class changes on desktop button
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    const desktopClasses = desktopBtn.className;
                    
                    // Remove all mobile states
                    mobileBtn.classList.remove('recording', 'connecting');
                    
                    // Apply matching state
                    if (desktopClasses.includes('recording')) {
                        mobileBtn.classList.add('recording');
                        console.log('📱 [MOBILE-INTERFACE] Mobile Live API → Recording state');
                    } else if (desktopClasses.includes('connecting')) {
                        mobileBtn.classList.add('connecting');
                        console.log('📱 [MOBILE-INTERFACE] Mobile Live API → Connecting state');
                    } else {
                        console.log('📱 [MOBILE-INTERFACE] Mobile Live API → Default state');
                    }
                }
            });
        });
        
        observer.observe(desktopBtn, { attributes: true });
        console.log('📱 [MOBILE-INTERFACE] Live API button state sync configured');
    }
    
    /**
     * Sync input content from desktop to mobile (for voice transcription)
     * @param {HTMLTextAreaElement} desktopInput - Desktop chat input
     * @param {HTMLTextAreaElement} mobileInput - Mobile chat input
     */
    syncDesktopToMobileInput(desktopInput, mobileInput) {
        if (!desktopInput || !mobileInput) return;
        
        // Watch for value changes in desktop input (voice transcription)
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'value') {
                    this.syncInputValues(desktopInput, mobileInput);
                }
            });
        });
        
        // Also listen for input events
        desktopInput.addEventListener('input', () => {
            this.syncInputValues(desktopInput, mobileInput);
        });
        
        // Listen for property changes (programmatic value changes)
        let lastValue = desktopInput.value;
        setInterval(() => {
            if (desktopInput.value !== lastValue) {
                lastValue = desktopInput.value;
                this.syncInputValues(desktopInput, mobileInput);
            }
        }, 100); // Check every 100ms
        
        console.log('📱 [MOBILE-INTERFACE] Desktop to mobile input sync configured');
    }
    
    /**
     * Sync input values and update mobile button state
     * @param {HTMLTextAreaElement} desktopInput - Desktop input
     * @param {HTMLTextAreaElement} mobileInput - Mobile input
     */
    syncInputValues(desktopInput, mobileInput) {
        if (desktopInput.value !== mobileInput.value) {
            mobileInput.value = desktopInput.value;
            
            // Adjust mobile textarea height
            this.adjustTextareaHeight(mobileInput);
            
            // Update mobile voice button state
            this.updateMobileVoiceButtonState(mobileInput.value);
            
            console.log('📱 [MOBILE-INTERFACE] Input synced from desktop to mobile:', desktopInput.value.substring(0, 50));
        }
    }
    
    /**
     * Show loading spinner on button
     * @param {HTMLButtonElement} button - Button to show loading state
     */
    showButtonLoading(button) {
        if (button) {
            button.classList.add('loading');
            button.disabled = true;
            console.log('📱 [MOBILE-INTERFACE] Button loading state enabled');
        }
    }
    
    /**
     * Hide loading spinner on button
     * @param {HTMLButtonElement} button - Button to hide loading state
     */
    hideButtonLoading(button) {
        if (button) {
            button.classList.remove('loading');
            button.disabled = false;
            console.log('📱 [MOBILE-INTERFACE] Button loading state disabled');
        }
    }
    
    /**
     * Check if the current viewport is mobile
     * @returns {boolean} True if mobile viewport
     */
    isMobileViewport() {
        return window.innerWidth <= 768;
    }
    
    /**
     * Scroll to top of slide content on mobile
     * Used for navigation, simplify, and more details actions
     */
    scrollToSlideTop() {
        if (!this.isMobileViewport()) {
            console.log('📱 [MOBILE-INTERFACE] Not mobile viewport - skipping scroll');
            return;
        }
        
        // Find the slide content container
        const slideContent = document.getElementById('slide-content');
        const mainContainer = document.querySelector('.training-container');
        const slideContainer = document.querySelector('#slide-container');
        
        // Priority order for scrolling target
        const scrollTarget = slideContent || slideContainer || mainContainer || window;
        
        if (scrollTarget === window) {
            // Scroll to top of page
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
            console.log('📱 [MOBILE-INTERFACE] Scrolled to top of page');
        } else {
            // Scroll to top of container
            scrollTarget.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
            console.log('📱 [MOBILE-INTERFACE] Scrolled to top of slide content');
        }
    }
    
    /**
     * Scroll to first chart on mobile after chart generation
     * Used specifically for chart button action
     */
    scrollToFirstChart() {
        if (!this.isMobileViewport()) {
            console.log('📱 [MOBILE-INTERFACE] Not mobile viewport - skipping chart scroll');
            return;
        }
        
        // Wait a bit for chart to be rendered
        setTimeout(() => {
            // Look for generated charts container
            const chartContainer = document.querySelector('.generated-charts-container');
            const chartCanvas = document.querySelector('.generated-charts-container canvas');
            const chartElement = document.querySelector('.chart-container');
            
            // Priority order for chart targets
            const chartTarget = chartCanvas || chartContainer || chartElement;
            
            if (chartTarget) {
                // Scroll to the chart with some offset for better UX
                const offsetTop = chartTarget.offsetTop - 20; // 20px offset from top
                
                // Find the scrollable container
                const scrollContainer = document.getElementById('slide-content') || 
                                      document.querySelector('.training-container') || 
                                      window;
                
                if (scrollContainer === window) {
                    window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });
                } else {
                    scrollContainer.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });
                }
                
                console.log('📱 [MOBILE-INTERFACE] Scrolled to first chart');
            } else {
                console.log('📱 [MOBILE-INTERFACE] No chart found to scroll to, scrolling to top instead');
                this.scrollToSlideTop();
            }
        }, 500); // Wait 500ms for chart rendering
    }
}