/**
 * Chat Interface Component
 * 
 * This component manages all chat-related functionality for the FIA v3.0 training platform.
 * It provides comprehensive chat features including text messaging, voice recognition,
 * contextual actions, TTS integration, and audio controls.
 * 
 * Features:
 * - Text-based chat messaging with AI trainer
 * - Voice recognition and speech-to-text functionality  
 * - Contextual chat actions (comment, quiz, examples, key points)
 * - Text-to-speech (TTS) integration with audio controls
 * - Auto-expanding textarea for message input
 * - Typing animations and visual feedback
 * - Voice fallback for unsupported browsers
 * - Smart button state management (mic/recording/send modes)
 * - Gemini Live API integration for real-time voice conversations
 * 
 * Dependencies:
 * - TTSManager: Text-to-speech functionality
 * - VoiceChatHandler: Voice recognition and speech processing
 * - GeminiLiveAPI: Real-time voice conversation with Gemini
 * - LearnerSession: User session data for context
 * - SessionData: Training session information
 * 
 * @author FIA v3.0 Platform
 * @version 1.0.0
 */

import { GeminiLiveAPI } from './gemini-live-api.js';

export class ChatInterface {
    /**
     * Initialize the Chat Interface component
     * 
     * @param {Object} dependencies - Required dependencies
     * @param {TTSManager} dependencies.ttsManager - Text-to-speech manager
     * @param {Object} dependencies.learnerSession - Learner session data
     * @param {Object} dependencies.sessionData - Training session data
     * @param {Object} dependencies.currentSlide - Current slide information
     * @param {string} dependencies.currentSlideContent - Current slide content
     */
    constructor({ ttsManager, learnerSession, sessionData, currentSlide, currentSlideContent }) {
        this.ttsManager = ttsManager;
        this.learnerSession = learnerSession;
        this.sessionData = sessionData;
        this.currentSlide = currentSlide;
        this.currentSlideContent = currentSlideContent;
        
        // Voice-related properties
        this.voiceHandler = null;
        this.currentButtonState = 'mic';
        this.resetSilenceTimeout = null;
        this.clearSilenceTimeout = null;
        this.isProcessingVoiceAction = false;
        
        // Gemini Live API
        this.geminiLiveAPI = new GeminiLiveAPI();
        this.isLiveAPIActive = false;
        
        console.log('💬 [CHAT_INTERFACE] Initialized with dependencies and Live API');
    }
    
    /**
     * Update current slide information for contextual chat
     * 
     * @param {Object} slide - Current slide data
     * @param {string} slideContent - Current slide content
     */
    updateCurrentSlide(slide, slideContent) {
        this.currentSlide = slide;
        this.currentSlideContent = slideContent;
        console.log('📄 [CHAT_INTERFACE] Current slide updated:', slide?.id);
    }
    
    /**
     * Setup all chat functionality including voice, TTS, and contextual actions
     */
    setupChatFunctionality() {
        const chatInput = document.getElementById('chat-input');
        const voiceChatBtn = document.getElementById('voice-chat-btn');
        const voiceBtnIcon = document.getElementById('voice-btn-icon');
        const voiceStatus = document.getElementById('voice-status');
        const chatMessages = document.getElementById('chat-messages');
        const sendBtnFallback = document.getElementById('send-message-btn-fallback');
        
        // Setup auto-expanding textarea
        this.setupAutoExpandingTextarea(chatInput);
        
        // Initialize voice handler based on learner language
        this.initializeVoiceHandler();
        
        // Setup TTS functionality
        this.setupTTSFunctionality();
        
        // Setup Gemini Live API functionality
        this.setupLiveAPIFunctionality();
        
        // Setup fallback for unsupported browsers
        this.setupVoiceFallback(sendBtnFallback, chatInput);
        
        if (chatInput && voiceChatBtn && chatMessages) {
            // Setup input change listener for adaptive button behavior
            this.setupInputChangeListener(chatInput, voiceChatBtn, voiceBtnIcon);
            
            // The actual send message and voice logic will be added in Phase 3 & 4
            console.log('✅ [CHAT] Chat functionality initialized with voice support');
        } else {
            console.error('❌ [CHAT] Missing chat elements');
        }
    }
    
    /**
     * Setup auto-expanding textarea functionality
     * 
     * @param {HTMLTextAreaElement} textarea - The textarea element to enhance
     */
    setupAutoExpandingTextarea(textarea) {
        if (!textarea) return;
        
        const autoResize = () => {
            // Reset height to auto to get the correct scrollHeight
            textarea.style.height = 'auto';
            
            // Calculate new height (max 3 lines)
            const lineHeight = parseFloat(getComputedStyle(textarea).lineHeight);
            const padding = parseFloat(getComputedStyle(textarea).paddingTop) + 
                           parseFloat(getComputedStyle(textarea).paddingBottom);
            const border = parseFloat(getComputedStyle(textarea).borderTopWidth) + 
                          parseFloat(getComputedStyle(textarea).borderBottomWidth);
            
            const minHeight = lineHeight + padding + border; // 1 line
            const maxHeight = (lineHeight * 3) + padding + border; // 3 lines
            
            let newHeight = Math.min(textarea.scrollHeight, maxHeight);
            newHeight = Math.max(newHeight, minHeight);
            
            textarea.style.height = newHeight + 'px';
            
            // Enable/disable scrolling based on content
            textarea.style.overflowY = textarea.scrollHeight > maxHeight ? 'auto' : 'hidden';
        };
        
        // Auto-resize on input
        textarea.addEventListener('input', autoResize);
        
        // Auto-resize on paste
        textarea.addEventListener('paste', () => {
            setTimeout(autoResize, 0);
        });
        
        // Initial resize
        autoResize();
    }
    
    /**
     * Setup TTS functionality and toggle listener
     */
    setupTTSFunctionality() {
        const ttsToggle = document.getElementById('tts-toggle');
        
        if (ttsToggle) {
            // TTS toggle functionality (works for both click and change events)
            const handleTTSToggle = () => {
                const newState = ttsToggle.checked;
                this.ttsManager.setEnabled(newState);
                
                console.log(`🔊 TTS [APP] TTS ${newState ? 'enabled' : 'disabled'} by user`);
            };
            
            // Setup TTS toggle listener for click events (desktop interaction)
            ttsToggle.addEventListener('click', () => {
                handleTTSToggle();
            });
            
            // Setup TTS toggle listener for change events (mobile synchronization)
            ttsToggle.addEventListener('change', () => {
                handleTTSToggle();
            });
            
            // Set language based on learner profile
            if (this.learnerSession && this.learnerSession.language) {
                this.ttsManager.setLanguage(this.learnerSession.language);
            }
            
            console.log('✅ [TTS] TTS functionality initialized with desktop & mobile sync');
        } else {
            console.error('❌ [TTS] TTS toggle not found');
        }
    }
    
    /**
     * Initialize voice handler synchronously (awaitable)
     */
    async initializeVoiceHandlerSync() {
        try {
            const { VoiceChatHandler } = await import('./voice-chat-handler.js');
            
            // Map learner language to speech recognition language codes
            const languageMap = {
                'fr': 'fr-FR',
                'en': 'en-US', 
                'es': 'es-ES',
                'de': 'de-DE'
            };
            
            const learnerLang = this.learnerSession?.language || 'fr';
            const speechLang = languageMap[learnerLang] || 'fr-FR';
            
            this.voiceHandler = new VoiceChatHandler(speechLang);
            
            console.log('✅ [VOICE] Voice handler initialized synchronously with language:', speechLang);
        } catch (error) {
            console.error('❌ [VOICE] Failed to load VoiceChatHandler synchronously:', error);
        }
    }
    
    /**
     * Initialize voice handler with learner's language (async version)
     */
    initializeVoiceHandler() {
        // Import VoiceChatHandler dynamically
        import('./voice-chat-handler.js').then(({ VoiceChatHandler }) => {
            // Map learner language to speech recognition language codes
            const languageMap = {
                'fr': 'fr-FR',
                'en': 'en-US', 
                'es': 'es-ES',
                'de': 'de-DE'
            };
            
            const learnerLang = this.learnerSession?.language || 'fr';
            const speechLang = languageMap[learnerLang] || 'fr-FR';
            
            this.voiceHandler = new VoiceChatHandler(speechLang);
            
            // Check if voice is supported
            if (!this.voiceHandler.isApiSupported()) {
                console.log('🎤 [VOICE] Web Speech API not supported, showing fallback');
                this.showVoiceFallback();
            } else {
                console.log('✅ [VOICE] Voice handler initialized with language:', speechLang);
            }
        }).catch(error => {
            console.error('❌ [VOICE] Failed to load VoiceChatHandler:', error);
            this.showVoiceFallback();
        });
    }
    
    /**
     * Setup voice fallback for unsupported browsers
     * 
     * @param {HTMLButtonElement} fallbackBtn - Fallback send button
     * @param {HTMLTextAreaElement} chatInput - Chat input element
     */
    setupVoiceFallback(fallbackBtn, chatInput) {
        if (fallbackBtn) {
            fallbackBtn.addEventListener('click', () => {
                this.sendChatMessage(chatInput.value.trim());
            });
        }
    }
    
    /**
     * Show message when voice recording is not supported
     */
    showVoiceNotSupportedMessage() {
        // Créer un message temporaire dans le chat
        const chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
            const messageHtml = `
                <div class="p-3">
                    <div class="message system mb-3">
                        <div class="d-flex align-items-start">
                            <div class="message-content">
                                <div class="bg-warning-subtle text-warning-emphasis p-2 rounded">
                                    <p class="mb-0 small">
                                        <i class="bi bi-mic-mute me-2"></i>
                                        Voice recording is not supported in your browser. Please type your message instead.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            chatMessages.insertAdjacentHTML('beforeend', messageHtml);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // Supprimer le message après 3 secondes
            setTimeout(() => {
                const systemMessage = chatMessages.querySelector('.message.system:last-child');
                if (systemMessage) {
                    systemMessage.remove();
                }
            }, 3000);
        }
    }
    
    /**
     * Show voice fallback UI for unsupported browsers
     */
    showVoiceFallback() {
        const chatInputContainer = document.querySelector('.chat-input');
        if (chatInputContainer) {
            chatInputContainer.classList.add('no-voice-support');
        }
    }
    
    /**
     * Setup input change listener for adaptive button behavior
     * 
     * @param {HTMLTextAreaElement} chatInput - Chat input element
     * @param {HTMLButtonElement} voiceChatBtn - Voice chat button
     * @param {HTMLElement} voiceBtnIcon - Voice button icon element
     */
    setupInputChangeListener(chatInput, voiceChatBtn, voiceBtnIcon) {
        const updateButtonState = () => {
            const hasText = chatInput.value.trim().length > 0;
            
            console.log('🔄 [DEBUG] updateButtonState called - hasText:', hasText, 'currentState:', this.currentButtonState);
            
            if (hasText && this.currentButtonState !== 'send') {
                // Switch to send mode
                console.log('🔄 [DEBUG] Switching to SEND mode');
                this.setButtonState('send', voiceChatBtn, voiceBtnIcon);
            } else if (!hasText && this.currentButtonState !== 'mic' && this.currentButtonState !== 'recording') {
                // Switch back to mic mode
                console.log('🔄 [DEBUG] Switching to MIC mode');
                this.setButtonState('mic', voiceChatBtn, voiceBtnIcon);
            }
        };
        
        // Listen for input changes
        chatInput.addEventListener('input', updateButtonState);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (this.currentButtonState === 'send') {
                    this.sendChatMessage(chatInput.value.trim());
                }
            }
        });
        
        // Initialize button state based on current input
        updateButtonState();
        
        // Setup voice recording press & hold (async)
        this.setupVoiceRecording(voiceChatBtn, voiceBtnIcon, chatInput);
    }
    
    /**
     * Set button state with visual feedback
     * 
     * @param {string} state - Button state ('mic', 'recording', 'send')
     * @param {HTMLButtonElement} button - Button element
     * @param {HTMLElement} icon - Icon element
     */
    setButtonState(state, button, icon) {
        // Remove all state classes
        button.classList.remove('state-mic', 'state-recording', 'state-send', 'state-processing');
        
        // Add new state class and update icon
        switch (state) {
            case 'mic':
                button.classList.add('state-mic');
                icon.className = 'bi bi-mic';
                button.title = window.safeT ? window.safeT('tooltip.voice') : 'Click to start voice recording';
                this.currentButtonState = 'mic';
                break;
                
            case 'recording':
                button.classList.add('state-recording');
                icon.className = 'bi bi-record-circle';
                button.title = 'Recording... Click to stop';
                this.currentButtonState = 'recording';
                break;
                
            case 'send':
                button.classList.add('state-send');
                icon.className = 'bi bi-send';
                button.title = 'Send message';
                this.currentButtonState = 'send';
                break;
                
            case 'processing':
                button.classList.add('state-processing');
                icon.className = 'bi bi-hourglass-split';
                button.title = 'Processing...';
                // Don't change currentButtonState during processing
                break;
        }
        
        console.log('🎤 [VOICE] Button state changed to:', state);
    }
    
    /**
     * Setup voice recording click on/off functionality
     * 
     * @param {HTMLButtonElement} voiceChatBtn - Voice chat button
     * @param {HTMLElement} voiceBtnIcon - Voice button icon
     * @param {HTMLTextAreaElement} chatInput - Chat input element
     */
    async setupVoiceRecording(voiceChatBtn, voiceBtnIcon, chatInput) {
        // Si voiceHandler n'est pas encore chargé, essayer de l'initialiser
        if (!this.voiceHandler) {
            console.log('🎤 [VOICE] VoiceHandler not loaded yet, attempting to initialize...');
            await this.initializeVoiceHandlerSync();
        }
        
        if (!this.voiceHandler || !this.voiceHandler.isApiSupported()) {
            console.log('🎤 [VOICE] Voice recording not supported, setting up send-only button');
            
            // Même sans support vocal, on doit configurer le bouton pour l'envoi de messages et la voix fallback
            voiceChatBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('🔍 [DEBUG] Button clicked (no voice support)! Current state:', this.currentButtonState);
                
                if (this.currentButtonState === 'send') {
                    console.log('✅ [DEBUG] Sending message via button click (no voice support)');
                    this.sendChatMessage(chatInput.value.trim());
                } else if (this.currentButtonState === 'mic') {
                    console.log('🎤 [DEBUG] Attempting voice recording (fallback mode)');
                    // Notification utilisateur
                    this.showVoiceNotSupportedMessage();
                }
            });
            
            return;
        }
        
        let isRecording = false;
        let silenceTimeout = null;
        let accumulatedTranscript = '';
        
        // Toggle recording function
        const toggleRecording = async (e) => {
            e.preventDefault();
            
            // 🔒 Debouncing: Ignore rapid clicks
            if (this.isProcessingVoiceAction) {
                console.log('🔒 [VOICE] Ignoring click - already processing voice action');
                return;
            }
            
            console.log('🔍 [DEBUG] Button clicked! Current state:', this.currentButtonState);
            console.log('🔍 [DEBUG] Chat input value:', chatInput.value);
            console.log('🔍 [DEBUG] Input has text:', chatInput.value.trim().length > 0);
            
            // If in send mode, send the message
            if (this.currentButtonState === 'send') {
                console.log('✅ [DEBUG] Sending message via button click');
                this.sendChatMessage(chatInput.value.trim());
                return;
            }
            
            // If not in mic mode, ignore
            if (this.currentButtonState !== 'mic' && this.currentButtonState !== 'recording') {
                console.log('🔍 [DEBUG] Ignoring click - not in mic/recording mode');
                return;
            }
            
            // 🔒 Lock voice actions
            this.isProcessingVoiceAction = true;
            
            // Show processing state
            this.setButtonState('processing', voiceChatBtn, voiceBtnIcon);
            
            try {
                if (!isRecording) {
                    console.log('🎤 [DEBUG] Starting voice recording');
                    await this.startVoiceRecording(voiceChatBtn, voiceBtnIcon, chatInput);
                    isRecording = true;
                } else {
                    console.log('🎤 [DEBUG] Stopping voice recording');
                    await this.stopVoiceRecording(voiceChatBtn, voiceBtnIcon, chatInput);
                    isRecording = false;
                }
            } catch (error) {
                console.error('❌ [VOICE] Error in voice action:', error);
                // Reset to mic state on error
                this.setButtonState('mic', voiceChatBtn, voiceBtnIcon);
            } finally {
                // 🔓 Unlock voice actions after a small delay to prevent rapid clicking
                setTimeout(() => {
                    this.isProcessingVoiceAction = false;
                }, 300); // 300ms debounce
            }
        };
        
        // Setup silence timeout function
        const resetSilenceTimeout = () => {
            if (silenceTimeout) {
                clearTimeout(silenceTimeout);
            }
            
            // Auto-stop after 10 seconds of silence
            silenceTimeout = setTimeout(async () => {
                if (isRecording) {
                    console.log('🎤 [VOICE] Auto-stopping after 10 seconds of silence');
                    this.isProcessingVoiceAction = true;
                    try {
                        await this.stopVoiceRecording(voiceChatBtn, voiceBtnIcon, chatInput);
                        isRecording = false;
                    } finally {
                        this.isProcessingVoiceAction = false;
                    }
                }
            }, 10000);
        };
        
        // Store timeout functions for access in other methods
        this.resetSilenceTimeout = resetSilenceTimeout;
        this.clearSilenceTimeout = () => {
            if (silenceTimeout) {
                clearTimeout(silenceTimeout);
                silenceTimeout = null;
            }
        };
        
        // Click event for toggle functionality
        voiceChatBtn.addEventListener('click', toggleRecording);
        
        // Prevent context menu on mobile
        voiceChatBtn.addEventListener('contextmenu', (e) => {
            e.preventDefault();
        });
        
        console.log('✅ [VOICE] Voice recording click on/off setup complete');
    }
    
    /**
     * Start voice recording
     * 
     * @param {HTMLButtonElement} voiceChatBtn - Voice chat button
     * @param {HTMLElement} voiceBtnIcon - Voice button icon
     * @param {HTMLTextAreaElement} chatInput - Chat input element
     */
    async startVoiceRecording(voiceChatBtn, voiceBtnIcon, chatInput) {
        console.log('🎤 [VOICE] Starting voice recording...');
        
        try {
            // Setup voice callbacks first
            this.setupVoiceCallbacks(voiceChatBtn, voiceBtnIcon, chatInput);
            
            // Start recording
            await this.voiceHandler.startRecognition();
            
            // Change to recording state
            this.setButtonState('recording', voiceChatBtn, voiceBtnIcon);
            this.updateVoiceStatus('Recording... Click again to stop');
            
            // Start silence timeout
            if (this.resetSilenceTimeout) {
                this.resetSilenceTimeout();
            }
            
        } catch (error) {
            console.error('❌ [VOICE] Failed to start recording:', error);
            this.updateVoiceStatus(`Error: ${error.message}`);
            this.setButtonState('mic', voiceChatBtn, voiceBtnIcon);
        }
    }
    
    /**
     * Stop voice recording
     * 
     * @param {HTMLButtonElement} voiceChatBtn - Voice chat button
     * @param {HTMLElement} voiceBtnIcon - Voice button icon
     * @param {HTMLTextAreaElement} chatInput - Chat input element
     */
    async stopVoiceRecording(voiceChatBtn, voiceBtnIcon, chatInput) {
        console.log('🎤 [VOICE] Stopping voice recording...');
        
        try {
            // Clear silence timeout
            if (this.clearSilenceTimeout) {
                this.clearSilenceTimeout();
            }
            
            // Stop recording
            this.voiceHandler.stopRecognition();
            
            // Show processing state
            this.setButtonState('mic', voiceChatBtn, voiceBtnIcon);
            this.updateVoiceStatus('Processing speech...');
            
        } catch (error) {
            console.error('❌ [VOICE] Failed to stop recording:', error);
            this.updateVoiceStatus(`Error: ${error.message}`);
            this.setButtonState('mic', voiceChatBtn, voiceBtnIcon);
        }
    }
    
    /**
     * Setup voice handler callbacks for recording session
     * 
     * @param {HTMLButtonElement} voiceChatBtn - Voice chat button
     * @param {HTMLElement} voiceBtnIcon - Voice button icon
     * @param {HTMLTextAreaElement} chatInput - Chat input element
     */
    setupVoiceCallbacks(voiceChatBtn, voiceBtnIcon, chatInput) {
        // Store partial transcript for continuous updates
        let partialTranscript = '';
        let finalTranscript = '';
        
        this.voiceHandler.onStart = () => {
            console.log('🎤 [VOICE] Recording started');
            this.updateVoiceStatus('Recording... Click again to stop');
            partialTranscript = '';
            finalTranscript = '';
        };
        
        this.voiceHandler.onEnd = () => {
            console.log('🎤 [VOICE] Recording ended');
            
            // Clear silence timeout
            if (this.clearSilenceTimeout) {
                this.clearSilenceTimeout();
            }
            
            // Process final accumulated transcript
            if (finalTranscript.trim()) {
                this.handleVoiceTranscript(finalTranscript.trim(), chatInput, voiceChatBtn, voiceBtnIcon);
            } else {
                console.log('🎤 [VOICE] No final transcript available');
                this.updateVoiceStatus('No speech detected');
                setTimeout(() => {
                    this.setButtonState('mic', voiceChatBtn, voiceBtnIcon);
                    this.updateVoiceStatus('');
                }, 2000);
            }
        };
        
        this.voiceHandler.onResult = (transcript, isFinal) => {
            console.log('🎤 [VOICE] Transcript received:', { 
                transcript, 
                isFinal, 
                length: transcript.length 
            });
            
            if (isFinal) {
                // Accumulate final results
                if (transcript.trim()) {
                    finalTranscript += (finalTranscript ? ' ' : '') + transcript.trim();
                    console.log('🎤 [VOICE] Final transcript accumulated:', finalTranscript);
                }
                
                // Reset silence timeout on final result
                if (this.resetSilenceTimeout) {
                    this.resetSilenceTimeout();
                }
                
            } else {
                // Partial result - show preview in status
                partialTranscript = transcript;
                const displayText = (finalTranscript + ' ' + transcript).trim();
                
                if (displayText) {
                    this.updateVoiceStatus(`Recognizing: "${displayText}"`);
                } else {
                    this.updateVoiceStatus('Recording... Click again to stop');
                }
                
                // Reset silence timeout on partial result (speech detected)
                if (transcript.trim() && this.resetSilenceTimeout) {
                    this.resetSilenceTimeout();
                }
            }
        };
        
        this.voiceHandler.onError = (error, message) => {
            console.error('❌ [VOICE] Recognition error:', error);
            this.updateVoiceStatus(`Error: ${message}`);
            
            // Clear silence timeout
            if (this.clearSilenceTimeout) {
                this.clearSilenceTimeout();
            }
            
            // Reset to mic state after error
            setTimeout(() => {
                this.setButtonState('mic', voiceChatBtn, voiceBtnIcon);
                this.updateVoiceStatus('');
            }, 3000);
        };
    }
    
    /**
     * Handle voice transcript result with smart text processing
     * 
     * @param {string} transcript - Voice transcript
     * @param {HTMLTextAreaElement} chatInput - Chat input element
     * @param {HTMLButtonElement} voiceChatBtn - Voice chat button
     * @param {HTMLElement} voiceBtnIcon - Voice button icon
     */
    handleVoiceTranscript(transcript, chatInput, voiceChatBtn, voiceBtnIcon) {
        console.log('🎤 [VOICE] Handling transcript:', transcript);
        
        // Clean and process transcript
        const processedTranscript = this.processTranscript(transcript);
        
        if (!processedTranscript) {
            console.log('🎤 [VOICE] Processed transcript is empty, ignoring');
            this.updateVoiceStatus('No valid speech detected');
            setTimeout(() => {
                this.setButtonState('mic', voiceChatBtn, voiceBtnIcon);
                this.updateVoiceStatus('');
            }, 2000);
            return;
        }
        
        // Check if there's existing text in input
        const existingText = chatInput.value.trim();
        let finalText = processedTranscript;
        
        if (existingText) {
            // Append to existing text with space
            finalText = existingText + ' ' + processedTranscript;
            console.log('🎤 [VOICE] Appending to existing text:', { existingText, processedTranscript, finalText });
        }
        
        // Insert final text into input field
        chatInput.value = finalText;
        
        // Trigger auto-resize
        chatInput.style.height = 'auto';
        chatInput.dispatchEvent(new Event('input', { bubbles: true }));
        
        // Show success feedback
        this.updateVoiceStatus('✓ Voice message transcribed');
        
        // Clear success message after 2 seconds
        setTimeout(() => {
            this.updateVoiceStatus('');
        }, 2000);
        
        console.log('✅ [VOICE] Transcript processed and inserted:', { 
            original: transcript, 
            processed: processedTranscript, 
            final: finalText 
        });
    }
    
    /**
     * Process and clean transcript text
     * 
     * @param {string} transcript - Raw transcript
     * @returns {string} Processed transcript
     */
    processTranscript(transcript) {
        if (!transcript || typeof transcript !== 'string') {
            return '';
        }
        
        // Clean transcript
        let processed = transcript.trim();
        
        // Capitalize first letter
        if (processed.length > 0) {
            processed = processed.charAt(0).toUpperCase() + processed.slice(1);
        }
        
        // Add punctuation if missing
        if (processed.length > 0 && !/[.!?]$/.test(processed)) {
            // Only add period for statements (not questions)
            if (!processed.toLowerCase().includes('comment') && 
                !processed.toLowerCase().includes('pourquoi') &&
                !processed.toLowerCase().includes('how') &&
                !processed.toLowerCase().includes('what') &&
                !processed.toLowerCase().includes('when') &&
                !processed.toLowerCase().includes('where') &&
                !processed.toLowerCase().includes('why')) {
                processed += '.';
            } else {
                processed += '?';
            }
        }
        
        return processed;
    }
    
    /**
     * Update voice status indicator
     * 
     * @param {string} message - Status message to display
     */
    updateVoiceStatus(message) {
        const voiceStatus = document.getElementById('voice-status');
        if (voiceStatus) {
            voiceStatus.textContent = message;
        }
    }
    
    /**
     * Send chat message to AI trainer
     * 
     * @param {string} message - Message to send
     */
    async sendChatMessage(message) {
        if (!message) return;
        
        console.log('💬 [CHAT] Sending message:', message);
        
        const chatInput = document.getElementById('chat-input');
        const voiceChatBtn = document.getElementById('voice-chat-btn');
        const voiceBtnIcon = document.getElementById('voice-btn-icon');
        const chatMessages = document.getElementById('chat-messages');
        
        if (!chatMessages) {
            console.error('❌ [CHAT] Chat messages container not found');
            return;
        }
        
        try {
            // Disable input and button during sending
            if (chatInput) chatInput.disabled = true;
            if (voiceChatBtn) voiceChatBtn.disabled = true;
            
            // Set button to loading state
            this.setButtonState('send', voiceChatBtn, voiceBtnIcon);
            if (voiceBtnIcon) voiceBtnIcon.className = 'bi bi-hourglass-split';
            
            // Add user message to chat
            this.addChatMessage('user', message);
            
            // Clear input and trigger resize
            if (chatInput) {
                chatInput.value = '';
                // Trigger resize to return to single line
                chatInput.style.height = 'auto';
                chatInput.dispatchEvent(new Event('input'));
            }
            
            // Show typing animation
            this.showTypingAnimation();
            
            // Prepare chat request
            const chatRequest = {
                message: message,
                context: {
                    training_id: this.sessionData.training_session.training_id,
                    learner_session_id: this.learnerSession.id,
                    current_slide_id: this.currentSlide?.id || null,
                    training_content: this.getCurrentSlideContent(),
                    learner_profile: this.getLearnerProfile(),
                    conversation_history: this.getChatHistory()
                },
                conversation_type: "general"
            };
            
            console.log('📤 [CHAT] Request payload:', chatRequest);
            
            // Call chat API
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(chatRequest)
            });
            
            console.log('📥 [CHAT] Response status:', response.status);
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error('❌ [CHAT] Error response:', errorData);
                throw new Error(errorData.detail || 'Chat service temporarily unavailable');
            }
            
            const chatResponse = await response.json();
            console.log('✅ [CHAT] Success response:', chatResponse);
            
            // Hide typing animation
            this.hideTypingAnimation();
            
            // Add AI response to chat
            this.addChatMessage('assistant', chatResponse.response, {
                confidence: chatResponse.confidence_score,
                suggested_actions: chatResponse.suggested_actions,
                related_concepts: chatResponse.related_concepts,
                conversation_type: chatResponse.conversation_type
            });
            
        } catch (error) {
            console.error('❌ [CHAT] Error:', error);
            
            // Hide typing animation on error
            this.hideTypingAnimation();
            
            // Show error message
            this.addChatMessage('assistant', 
                `I'm sorry, I encountered an error. Please try again. (${error.message})`,
                { error: true }
            );
            
        } finally {
            // Re-enable input and button
            if (chatInput) {
                chatInput.disabled = false;
                chatInput.focus();
            }
            if (voiceChatBtn) voiceChatBtn.disabled = false;
            
            // Reset button state
            this.setButtonState('mic', voiceChatBtn, voiceBtnIcon);
        }
    }
    
    /**
     * Get current slide content for context
     * 
     * @returns {string} Current slide content
     */
    getCurrentSlideContent() {
        if (this.currentSlide) {
            return this.currentSlide.content || 'Current slide content';
        }
        return 'Training session content';
    }
    
    /**
     * Get learner profile for context
     * 
     * @returns {Object} Learner profile data
     */
    getLearnerProfile() {
        if (!this.learnerSession) {
            return {};
        }
        
        return {
            experience_level: this.learnerSession.experience_level,
            learning_style: this.learnerSession.learning_style,
            job_position: this.learnerSession.job_position,
            activity_sector: this.learnerSession.activity_sector,
            country: this.learnerSession.country,
            language: this.learnerSession.language,
            objectives: this.learnerSession.objectives,
            training_duration: this.learnerSession.training_duration,
            enriched_profile: this.learnerSession.enriched_profile
        };
    }
    
    /**
     * Get conversation history for context
     * 
     * @returns {Array} Array of conversation messages
     */
    getChatHistory() {
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) return [];
        
        const messages = [];
        const messageElements = chatMessages.querySelectorAll('.message');
        
        messageElements.forEach(element => {
            const role = element.classList.contains('assistant') ? 'assistant' : 'user';
            const content = element.querySelector('.message-content p')?.textContent || '';
            const timestamp = element.querySelector('small')?.textContent || new Date().toISOString();
            
            if (content.trim()) {
                messages.push({
                    role: role,
                    content: content.trim(),
                    timestamp: timestamp
                });
            }
        });
        
        console.log('📝 [CHAT] Chat history retrieved:', messages.length, 'messages');
        // Return last 10 messages to avoid context overflow
        return messages.slice(-10);
    }
    
    /**
     * Add chat message to the conversation
     * 
     * @param {string} role - Message role ('user' or 'assistant')
     * @param {string} content - Message content
     * @param {Object} metadata - Additional message metadata
     */
    addChatMessage(role, content, metadata = {}) {
        const chatMessages = document.getElementById('chat-messages');
        
        const isUser = role === 'user';
        const messageClass = isUser ? 'justify-content-end' : '';
        const bubbleClass = isUser ? 'bg-primary text-white' : 'bg-light';
        
        // Add action type badge for contextual actions
        let actionTypeBadge = '';
        if (metadata.action_type) {
            const badgeConfig = {
                'comment': { class: 'border border-primary text-primary', icon: 'bi-chat-text', text: window.safeT ? window.safeT('chat.comment') : 'Comment' },
                'quiz': { class: 'border border-primary text-primary', icon: 'bi-question-circle', text: window.safeT ? window.safeT('chat.quiz') : 'Quiz' },
                'examples': { class: 'border border-primary text-primary', icon: 'bi-lightbulb', text: window.safeT ? window.safeT('chat.examples') : 'Examples' },
                'key-points': { class: 'border border-primary text-primary', icon: 'bi-star', text: window.safeT ? window.safeT('chat.keyPoints') : 'Key Points' }
            };
            
            const config = badgeConfig[metadata.action_type];
            if (config) {
                actionTypeBadge = `<div class="mt-1 mb-2"><span class="badge ${config.class}"><i class="${config.icon} me-1"></i>${config.text}</span></div>`;
            }
        }

        // Generate unique message ID for TTS
        const messageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        // Add audio controls for assistant messages (always visible)
        let audioControls = '';
        if (!isUser && !metadata.error) {
            audioControls = `
                <div class="message-audio-controls" style="display: block">
                    <button class="audio-toggle-btn stopped" onclick="window.chatInterface.toggleMessageAudio('${messageId}')" data-message-id="${messageId}">
                        <i class="bi bi-play-circle"></i>
                    </button>
                </div>
            `;
        }

        const messageHtml = `
            <div class="p-3">
                <div class="message ${role} mb-3" data-message-id="${messageId}" ${metadata.action_type ? `data-action-type="${metadata.action_type}"` : ''}>
                    <div class="d-flex align-items-start ${messageClass}">
                        <div class="message-content">
                            <div class="${bubbleClass} p-2 rounded">
                                ${actionTypeBadge}
                                <p class="mb-0 small">${content}</p>
                                ${metadata.suggested_actions && metadata.suggested_actions.length > 0 ? 
                                    `<div class="mt-2">
                                        <small class="text-muted">Suggestions:</small><br>
                                        ${metadata.suggested_actions.map(action => `<span class="badge border border-primary text-primary me-1">${action}</span>`).join('')}
                                    </div>` : ''}
                                ${metadata.related_concepts && metadata.related_concepts.length > 0 ? 
                                    `<div class="mt-2">
                                        <small class="text-muted">Related:</small><br>
                                        ${metadata.related_concepts.map(concept => `<span class="badge border border-primary text-primary me-1">${concept}</span>`).join('')}
                                    </div>` : ''}
                                ${metadata.error ? `<div class="mt-1"><span class="badge border border-primary text-primary">Error</span></div>` : ''}
                            </div>
                            ${audioControls}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        chatMessages.insertAdjacentHTML('beforeend', messageHtml);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Generate TTS for assistant messages only if TTS is enabled
        if (!isUser && !metadata.error && this.ttsManager.enabled) {
            // Use the new method that only processes the last message
            setTimeout(() => {
                this.ttsManager.generateAudioForLastMessage();
            }, 100); // Small delay to ensure DOM is updated
        }
        
        console.log('💬 [CHAT] Message added:', { role, content: content.substring(0, 50) + '...', metadata });
    }
    
    /**
     * Play audio for a specific message
     * 
     * @param {string} messageId - Message ID
     */
    async playMessageAudio(messageId) {
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        if (messageElement) {
            // If no audio data exists, generate it first
            if (!messageElement.ttsAudio) {
                const content = messageElement.querySelector('.message-content p').textContent;
                await this.ttsManager.generateAndPlaySpeech(content, messageElement, false);
            }
            
            // Play the audio
            await this.ttsManager.playAudio(messageElement);
            
            // Update button states
            this.updateAudioControlButtons(messageId, 'playing');
        }
    }
    
    /**
     * Pause audio for a specific message
     * 
     * @param {string} messageId - Message ID
     */
    pauseMessageAudio(messageId) {
        this.ttsManager.pauseAudio();
        this.updateAudioControlButtons(messageId, 'paused');
    }
    
    /**
     * Stop audio for a specific message
     * 
     * @param {string} messageId - Message ID
     */
    stopMessageAudio(messageId) {
        this.ttsManager.stopAudio();
        this.updateAudioControlButtons(messageId, 'stopped');
    }
    
    /**
     * Toggle audio play/pause for a specific message (simplified method)
     * 
     * @param {string} messageId - Message ID
     */
    async toggleMessageAudio(messageId) {
        const button = document.querySelector(`button[data-message-id="${messageId}"]`);
        if (!button) return;
        
        const isPlaying = button.classList.contains('playing');
        
        if (isPlaying) {
            // Currently playing, so pause
            this.ttsManager.pauseAudio();
            this.updateAudioControlButtons(messageId, 'paused');
        } else {
            // Currently stopped/paused, so play
            const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
            if (messageElement) {
                // If no audio data exists, generate it first
                if (!messageElement.ttsAudio) {
                    // Show loading state while generating audio
                    this.updateAudioControlButtons(messageId, 'loading');
                    const content = messageElement.querySelector('.message-content p').textContent;
                    await this.ttsManager.generateAndPlaySpeech(content, messageElement, false);
                }
                
                // Play or resume the audio
                await this.ttsManager.playAudio(messageElement);
                this.updateAudioControlButtons(messageId, 'playing');
            }
        }
    }
    
    /**
     * Update audio control button states
     * 
     * @param {string} messageId - Message ID
     * @param {string} state - Button state ('playing', 'paused', 'stopped')
     */
    updateAudioControlButtons(messageId, state) {
        const button = document.querySelector(`button[data-message-id="${messageId}"]`);
        if (!button) return;
        
        // Remove all state classes
        button.classList.remove('playing', 'stopped', 'paused', 'loading');
        
        switch (state) {
            case 'loading':
                button.classList.add('loading');
                button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span>';
                break;
            case 'playing':
                button.classList.add('playing');
                button.innerHTML = '<i class="bi bi-pause-circle"></i>';
                break;
            case 'paused':
                button.classList.add('stopped'); // Paused state shows play button (to resume)
                button.innerHTML = '<i class="bi bi-play-circle"></i>';
                break;
            case 'stopped':
            default:
                button.classList.add('stopped');
                button.innerHTML = '<i class="bi bi-play-circle"></i>';
                break;
        }
    }
    
    /**
     * Show typing animation while AI is processing
     */
    showTypingAnimation() {
        const chatMessages = document.getElementById('chat-messages');
        
        const typingHtml = `
            <div class="p-3" id="typing-indicator">
                <div class="message assistant mb-3">
                    <div class="d-flex align-items-start">
                        <div class="message-content">
                            <div class="bg-light p-2 rounded">
                                <div class="typing-animation">
                                    <div class="typing-dot"></div>
                                    <div class="typing-dot"></div>
                                    <div class="typing-dot"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        chatMessages.insertAdjacentHTML('beforeend', typingHtml);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        console.log('💭 [CHAT] Typing animation shown');
    }
    
    /**
     * Hide typing animation
     */
    hideTypingAnimation() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
            console.log('💭 [CHAT] Typing animation hidden');
        }
    }
    
    /**
     * Setup contextual chat buttons (comment, quiz, examples, key points)
     */
    setupContextualChatButtons() {
        const commentBtn = document.getElementById('comment-btn');
        const quizBtn = document.getElementById('quiz-btn');
        const examplesBtn = document.getElementById('examples-btn');
        const keyPointsBtn = document.getElementById('key-points-btn');
        
        if (commentBtn) {
            commentBtn.addEventListener('click', () => this.handleContextualAction('comment'));
            console.log('✅ [CONTEXTUAL_CHAT] Comment button event listener added');
        }
        
        if (quizBtn) {
            quizBtn.addEventListener('click', () => this.handleContextualAction('quiz'));
            console.log('✅ [CONTEXTUAL_CHAT] Quiz button event listener added');
        }
        
        if (examplesBtn) {
            examplesBtn.addEventListener('click', () => this.handleContextualAction('examples'));
            console.log('✅ [CONTEXTUAL_CHAT] Examples button event listener added');
        }
        
        if (keyPointsBtn) {
            keyPointsBtn.addEventListener('click', () => this.handleContextualAction('key-points'));
            console.log('✅ [CONTEXTUAL_CHAT] Key Points button event listener added');
        }
    }
    
    /**
     * Handle contextual chat action (comment, quiz, examples, key points)
     * 
     * @param {string} actionType - Type of contextual action
     */
    async handleContextualAction(actionType) {
        console.log(`💬 [CONTEXTUAL_CHAT] Handling ${actionType} action`);
        
        if (!this.currentSlideContent || !this.currentSlide) {
            console.error('❌ [CONTEXTUAL_CHAT] No current slide content available');
            this.addChatMessage('assistant', 
                'I need slide content to provide this information. Please wait for the slide to load.',
                { error: true }
            );
            return;
        }
        
        // Disable all contextual buttons during processing
        this.setContextualButtonsEnabled(false, actionType);
        
        // Show typing animation
        this.showTypingAnimation();
        
        try {
            // Prepare request payload
            const requestPayload = {
                learner_session_id: this.learnerSession.id,
                slide_content: this.currentSlideContent,
                slide_title: this.currentSlide.title || 'Current Slide'
            };
            
            console.log(`📤 [CONTEXTUAL_CHAT] ${actionType} request payload:`, requestPayload);
            
            // Call the appropriate API endpoint
            const apiEndpoint = `/api/chat/${actionType}`;
            const response = await fetch(apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestPayload)
            });
            
            console.log(`📥 [CONTEXTUAL_CHAT] ${actionType} response status:`, response.status);
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error(`❌ [CONTEXTUAL_CHAT] ${actionType} error response:`, errorData);
                throw new Error(errorData.detail || `${actionType} service temporarily unavailable`);
            }
            
            const chatResponse = await response.json();
            console.log(`✅ [CONTEXTUAL_CHAT] ${actionType} success response:`, chatResponse);
            
            // Hide typing animation
            this.hideTypingAnimation();
            
            // Add AI response to chat with appropriate metadata
            this.addChatMessage('assistant', chatResponse.response, {
                confidence: chatResponse.confidence_score,
                suggested_actions: chatResponse.suggested_actions,
                related_concepts: chatResponse.related_concepts,
                action_type: actionType
            });
            
        } catch (error) {
            console.error(`❌ [CONTEXTUAL_CHAT] ${actionType} error:`, error);
            
            // Hide typing animation on error
            this.hideTypingAnimation();
            
            // Add error message to chat
            let errorMessage = `I'm sorry, I encountered an error while processing your ${actionType} request. Please try again.`;
            if (actionType === 'comment') errorMessage = 'I cannot comment on this slide right now. Please try again later.';
            else if (actionType === 'quiz') errorMessage = 'I cannot generate a quiz right now. Please try again later.';
            else if (actionType === 'examples') errorMessage = 'I cannot provide examples right now. Please try again later.';
            else if (actionType === 'key-points') errorMessage = 'I cannot extract key points right now. Please try again later.';
            
            this.addChatMessage('assistant', `${errorMessage} (${error.message})`, { error: true });
            
        } finally {
            // Re-enable contextual buttons
            this.setContextualButtonsEnabled(true);
        }
    }
    
    /**
     * Enable/disable contextual chat buttons
     * 
     * @param {boolean} enabled - Whether buttons should be enabled
     * @param {string} activeActionType - Currently active action type
     */
    setContextualButtonsEnabled(enabled, activeActionType = null) {
        const buttons = {
            'comment': document.getElementById('comment-btn'),
            'quiz': document.getElementById('quiz-btn'),
            'examples': document.getElementById('examples-btn'),
            'key-points': document.getElementById('key-points-btn')
        };
        
        Object.entries(buttons).forEach(([actionType, button]) => {
            if (button) {
                if (enabled) {
                    button.disabled = false;
                    // Restore original content
                    if (actionType === 'comment') button.innerHTML = `<i class="bi bi-chat-text me-1"></i>${window.safeT ? window.safeT('chat.comment') : 'Comment'}`;
                    else if (actionType === 'quiz') button.innerHTML = `<i class="bi bi-question-circle me-1"></i>${window.safeT ? window.safeT('chat.quiz') : 'Quiz'}`;
                    else if (actionType === 'examples') button.innerHTML = `<i class="bi bi-lightbulb me-1"></i>${window.safeT ? window.safeT('chat.examples') : 'Examples'}`;
                    else if (actionType === 'key-points') button.innerHTML = `<i class="bi bi-star me-1"></i>${window.safeT ? window.safeT('chat.keyPoints') : 'Key Points'}`;
                } else {
                    if (actionType === activeActionType) {
                        button.disabled = true;
                        button.innerHTML = `<i class="bi bi-hourglass-split me-1"></i>${window.safeT ? window.safeT('status.loadingGeneric') : 'Loading...'}`;
                    } else {
                        button.disabled = true;
                    }
                }
            }
        });
    }
    
    /**
     * Setup Gemini Live API functionality
     */
    setupLiveAPIFunctionality() {
        const liveApiBtn = document.getElementById('live-api-btn');
        const liveApiIcon = document.getElementById('live-api-icon');
        const liveApiText = document.getElementById('live-api-text');
        
        if (!liveApiBtn || !this.geminiLiveAPI.isSupported()) {
            if (liveApiBtn) {
                liveApiBtn.style.display = 'none';
            }
            console.log('🎙️ [LIVE-API] Live API not supported or button not found');
            return;
        }
        
        // Configure callbacks pour intégration FIA
        this.geminiLiveAPI.setCallbacks({
            onStatusChange: (message, type) => {
                // Update button appearance based on status
                if (liveApiBtn && liveApiIcon && liveApiText) {
                    liveApiBtn.className = 'btn btn-success';
                    
                    switch (type) {
                        case 'connecting':
                            liveApiBtn.classList.add('connecting');
                            liveApiIcon.className = 'bi bi-hourglass-split me-1';
                            liveApiText.textContent = window.safeT ? window.safeT('status.connecting') : 'Connecting...';
                            break;
                        case 'connected':
                            liveApiBtn.classList.add('connected');
                            liveApiIcon.className = 'bi bi-soundwave me-1';
                            liveApiText.textContent = window.safeT ? window.safeT('status.connected') : 'Connected';
                            break;
                        case 'recording':
                            liveApiBtn.classList.add('recording');
                            liveApiIcon.className = 'bi bi-mic-fill me-1';
                            liveApiText.textContent = window.safeT ? window.safeT('button.stop') : 'Stop';
                            break;
                        case 'error':
                            liveApiBtn.classList.remove('connecting', 'connected', 'recording');
                            liveApiBtn.className = 'btn btn-danger';
                            liveApiIcon.className = 'bi bi-exclamation-triangle me-1';
                            liveApiText.textContent = window.safeT ? window.safeT('status.error') : 'Error';
                            break;
                        case 'disconnected':
                        default:
                            liveApiBtn.classList.remove('connecting', 'connected', 'recording');
                            liveApiIcon.className = 'bi bi-soundwave me-1';
                            liveApiText.textContent = window.safeT ? window.safeT('learner.vocal') : 'Vocal';
                            break;
                    }
                }
            },
            
            onTranscriptUpdate: (transcript) => {
                // Transcript logging supprimé
            },
            
            onMessageReceived: (message, isUser) => {
                // Message logging supprimé - Live API fonctionne en mode audio pur
            }
        });
        
        // Setup button click handler
        liveApiBtn.addEventListener('click', async () => {
            if (this.isLiveAPIActive) {
                // Stop Live API conversation
                this.geminiLiveAPI.stop();
                this.isLiveAPIActive = false;
                liveApiBtn.disabled = false;
            } else {
                // Start Live API conversation
                try {
                    liveApiBtn.disabled = true;
                    
                    // Load learner context if available
                    if (this.learnerSession && this.learnerSession.id) {
                        await this.geminiLiveAPI.loadLearnerContext(this.learnerSession.id);
                    }
                    
                    await this.geminiLiveAPI.start();
                    this.isLiveAPIActive = true;
                    liveApiBtn.disabled = false;
                } catch (error) {
                    console.error('❌ [LIVE-API] Failed to start Live API:', error);
                    liveApiBtn.disabled = false;
                    this.isLiveAPIActive = false;
                }
            }
        });
        
        console.log('✅ [LIVE-API] Live API functionality initialized');
    }
    
    /**
     * Initialize the chat interface - setup all functionality
     */
    initialize() {
        console.log('🚀 [CHAT_INTERFACE] Initializing chat interface...');
        
        // Make instance globally available for onclick handlers
        window.chatInterface = this;
        
        // Setup main chat functionality
        this.setupChatFunctionality();
        
        // Setup contextual chat buttons
        this.setupContextualChatButtons();
        
        console.log('✅ [CHAT_INTERFACE] Chat interface initialized successfully');
    }
}