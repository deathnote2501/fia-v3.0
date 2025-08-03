/**
 * Text-to-Speech Manager Component
 * 
 * This component manages text-to-speech functionality for the FIA v3.0 training platform.
 * It provides audio generation, playback controls, and UI state management for learner messages.
 * 
 * Features:
 * - Speech generation using backend TTS API
 * - Audio playback controls with loading and playing states
 * - Queue management for multiple audio requests
 * - Text cleaning and preprocessing for TTS
 * - Voice and language configuration
 * 
 * @author FIA v3.0 Platform
 * @version 1.0.0
 */

export class TTSManager {
    constructor() {
        this.enabled = false;
        this.currentAudio = null;
        this.audioQueue = [];
        this.currentPlayingMessageId = null;
        this.defaultVoice = 'Kore';
        this.defaultLanguage = 'fr';
        
        console.log('🔊 TTS [MANAGER] Initialized');
    }
    
    /**
     * Enable or disable TTS functionality
     */
    setEnabled(enabled) {
        this.enabled = enabled;
        console.log(`🔊 TTS [MANAGER] ${enabled ? 'Enabled' : 'Disabled'}`);
        
        // Update UI state
        this.updateToggleUI(enabled);
        this.updateMessageAudioControls(enabled);
        
        if (enabled) {
            // When enabling TTS, generate audio for existing assistant messages
            this.generateAudioForExistingMessages();
        } else {
            // Stop current playback if disabling
            if (this.currentAudio) {
                this.stopAudio();
            }
        }
    }
    
    /**
     * Update toggle button UI
     */
    updateToggleUI(enabled) {
        const toggle = document.getElementById('tts-toggle');
        const icon = document.getElementById('tts-icon');
        
        if (toggle && icon) {
            if (enabled) {
                toggle.classList.add('enabled');
                icon.className = 'bi bi-toggle-on';
            } else {
                toggle.classList.remove('enabled');
                icon.className = 'bi bi-toggle-off';
            }
        }
    }
    
    /**
     * Update audio controls visibility on all messages (always visible now)
     */
    updateMessageAudioControls(enabled) {
        const messages = document.querySelectorAll('.message.assistant');
        messages.forEach(message => {
            const controls = message.querySelector('.message-audio-controls');
            if (controls) {
                // Always visible - the toggle only controls auto-play functionality
                controls.style.display = 'block';
            }
        });
    }
    
    /**
     * Generate audio for the last assistant message only
     * Used when a new message is received and TTS is enabled
     */
    async generateAudioForLastMessage() {
        if (!this.enabled) {
            console.log('🔊 TTS [MANAGER] TTS disabled - not generating audio for last message');
            return;
        }
        
        console.log('🔊 TTS [MANAGER] Generating audio for last assistant message...');
        
        const assistantMessages = document.querySelectorAll('.message.assistant');
        if (assistantMessages.length === 0) {
            console.log('🔊 TTS [MANAGER] No assistant messages found');
            return;
        }
        
        // Get the last assistant message
        const lastMessage = assistantMessages[assistantMessages.length - 1];
        
        // Skip if audio already exists
        if (lastMessage.ttsAudio) {
            console.log('🔊 TTS [MANAGER] Last message already has audio - skipping');
            return;
        }
        
        try {
            // Extract text content from the message
            const contentElement = lastMessage.querySelector('.message-content p');
            if (!contentElement) {
                console.log('🔊 TTS [MANAGER] No content element found in last message');
                return;  
            }
            
            const textContent = contentElement.textContent || contentElement.innerText;
            if (!textContent || textContent.trim().length === 0) {
                console.log('🔊 TTS [MANAGER] Last message has empty text content');
                return;
            }
            
            console.log(`🔊 TTS [MANAGER] Processing last message: ${textContent.substring(0, 50)}...`);
            
            // Generate audio with auto-playing for the new message
            await this.generateAndPlaySpeech(textContent, lastMessage, true);
            
            console.log('✅ TTS [MANAGER] Last message audio generated successfully');
            
        } catch (error) {
            console.error('🔊 TTS [MANAGER] Failed to generate audio for last message:', error);
        }
    }
    
    /**
     * Generate audio for existing assistant messages when TTS is enabled
     * Used only when manually enabling TTS toggle
     */
    async generateAudioForExistingMessages() {
        console.log('🔊 TTS [MANAGER] Generating audio for existing assistant messages...');
        
        const assistantMessages = document.querySelectorAll('.message.assistant');
        let processedCount = 0;
        
        for (const messageElement of assistantMessages) {
            // Skip if audio already exists
            if (messageElement.ttsAudio) {
                console.log('🔊 TTS [MANAGER] Skipping message - audio already exists');
                continue;
            }
            
            try {
                // Extract text content from the message
                const contentElement = messageElement.querySelector('.message-content p');
                if (!contentElement) {
                    console.log('🔊 TTS [MANAGER] Skipping message - no content element found');
                    continue;  
                }
                
                const textContent = contentElement.textContent || contentElement.innerText;
                if (!textContent || textContent.trim().length === 0) {
                    console.log('🔊 TTS [MANAGER] Skipping message - empty text content');
                    continue;
                }
                
                console.log(`🔊 TTS [MANAGER] Processing message ${processedCount + 1}: ${textContent.substring(0, 50)}...`);
                
                // Generate audio without auto-playing (autoPlay = false)
                await this.generateAndPlaySpeech(textContent, messageElement, false);
                processedCount++;
                
                // Add a small delay to avoid overwhelming the API
                if (processedCount % 3 === 0) {
                    await new Promise(resolve => setTimeout(resolve, 500));
                }
                
            } catch (error) {
                console.error('🔊 TTS [MANAGER] Failed to generate audio for existing message:', error);
                // Continue with other messages even if one fails
            }
        }
        
        console.log(`✅ TTS [MANAGER] Processed ${processedCount} existing messages`);
        
        // Don't auto-play any existing messages when enabling TTS
        // Only new messages received after TTS is enabled should auto-play
        console.log('🔊 TTS [MANAGER] TTS enabled - existing messages prepared for manual playback only');
    }
    
    /**
     * Generate speech for text and auto-play if enabled
     */
    async generateAndPlaySpeech(text, messageElement, autoPlay = true) {
        // Always generate audio for manual playback, but respect autoPlay setting
        if (!this.enabled && autoPlay) {
            console.log('🔊 TTS [MANAGER] TTS disabled, generating audio without auto-play');
            autoPlay = false; // Generate audio but don't auto-play
        }
        
        if (!text || text.trim().length === 0) {
            console.log('🔊 TTS [MANAGER] Empty text, skipping speech generation');
            return;
        }
        
        try {
            console.log(`🔊 TTS [MANAGER] Generating speech for text: ${text.substring(0, 100)}...`);
            
            // Show loading state on message and global TTS spinners
            this.showLoadingState(messageElement);
            this.showGlobalTTSSpinner();
            
            // Send raw text to backend for consistent cleaning
            const cleanText = text;
            
            // Call TTS API
            const response = await fetch('/api/tts/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: cleanText,
                    voice: this.defaultVoice,
                    language: this.defaultLanguage
                })
            });
            
            if (!response.ok) {
                throw new Error(`TTS API error: ${response.status}`);
            }
            
            const ttsData = await response.json();
            
            // Create data URL from base64 audio (more reliable than blobs)
            const audioUrl = `data:${ttsData.mime_type};base64,${ttsData.audio_data}`;
            
            // Create audio element with proper settings
            const audio = new Audio();
            audio.preload = 'auto';
            
            // Set up error handling before setting src
            audio.onerror = (e) => {
                console.error('❌ TTS [MANAGER] Audio load error:', e);
                console.error('❌ TTS [MANAGER] Audio URL:', audioUrl.substring(0, 100) + '...');
            };
            
            // Set src after error handler
            audio.src = audioUrl;
            
            // Store audio data on message element
            messageElement.ttsAudio = audio;
            messageElement.ttsData = ttsData;
            messageElement.audioUrl = audioUrl;
            
            // Hide loading state
            this.hideLoadingState(messageElement);
            
            // Auto-play if requested - KISS approach: direct play after generation
            if (autoPlay) {
                console.log('🔊 TTS [MANAGER] Auto-play enabled - triggering immediate playback');
                // Use a small delay to ensure audio element is properly set up
                setTimeout(() => {
                    this.playAudio(messageElement);
                    this.hideGlobalTTSSpinner(); // Hide spinner when audio starts playing
                }, 100);
            } else {
                // Hide spinner immediately if no auto-play
                this.hideGlobalTTSSpinner();
            }
            
            console.log(`✅ TTS [MANAGER] Speech generated successfully - Duration: ${ttsData.duration}s`);
            
        } catch (error) {
            console.error('❌ TTS [MANAGER] Speech generation failed:', error);
            this.hideLoadingState(messageElement);
            this.hideGlobalTTSSpinner(); // Hide spinner on error
            this.showError(messageElement, 'Speech generation failed');
        }
    }
    
    /**
     * Play audio for a specific message
     */
    async playAudio(messageElement) {
        if (!messageElement.ttsAudio) {
            console.log('🔊 TTS [MANAGER] No audio data available for message');
            return;
        }
        
        try {
            // Stop current audio if playing
            if (this.currentAudio && !this.currentAudio.paused) {
                this.currentAudio.pause();
                this.currentAudio.currentTime = 0;
            }
            
            // Set current audio
            this.currentAudio = messageElement.ttsAudio;
            this.currentPlayingMessageId = messageElement.dataset.messageId;
            
            // Show playing state
            this.showPlayingState(messageElement);
            
            // Set up audio event listeners
            this.currentAudio.onended = () => {
                this.hidePlayingState(messageElement);
                
                // Reset button to play state
                const messageId = messageElement.getAttribute('data-message-id');
                if (messageId && window.chatInterface) {
                    window.chatInterface.updateAudioControlButtons(messageId, 'stopped');
                }
                
                this.currentAudio = null;
                this.currentPlayingMessageId = null;
            };
            
            this.currentAudio.onerror = () => {
                console.error('❌ TTS [MANAGER] Audio playback error');
                this.hidePlayingState(messageElement);
                this.currentAudio = null;
                this.currentPlayingMessageId = null;
            };
            
            // Play audio
            await this.currentAudio.play();
            console.log('🔊 TTS [MANAGER] Audio playback started');
            
        } catch (error) {
            console.error('❌ TTS [MANAGER] Audio playback failed:', error);
            this.hidePlayingState(messageElement);
        }
    }
    
    /**
     * Pause current audio playback
     */
    pauseAudio() {
        if (this.currentAudio && !this.currentAudio.paused) {
            this.currentAudio.pause();
            console.log('⏸️ TTS [MANAGER] Audio paused');
        }
    }
    
    /**
     * Stop current audio playback
     */
    stopAudio() {
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio.currentTime = 0;
            
            // Clear playing state
            const playingMessage = document.querySelector('.message.playing-audio');
            if (playingMessage) {
                this.hidePlayingState(playingMessage);
            }
            
            this.currentAudio = null;
            this.currentPlayingMessageId = null;
            console.log('⏹️ TTS [MANAGER] Audio stopped');
        }
    }
    
    /**
     * Clean text for TTS (remove HTML, markdown, etc.)
     */
    cleanTextForTTS(text) {
        // Remove HTML tags
        let cleaned = text.replace(/<[^>]*>/g, '');
        
        // Remove markdown formatting
        cleaned = cleaned.replace(/\*\*(.*?)\*\*/g, '$1'); // Bold
        cleaned = cleaned.replace(/\*(.*?)\*/g, '$1'); // Italic
        cleaned = cleaned.replace(/`(.*?)`/g, '$1'); // Code
        cleaned = cleaned.replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1'); // Links
        
        // Clean up whitespace
        cleaned = cleaned.replace(/\s+/g, ' ').trim();
        
        // Gemini 2.5 TTS can handle much longer texts without artificial limits
        
        return cleaned;
    }
    
    /**
     * Convert base64 to blob
     */
    base64ToBlob(base64, mimeType) {
        try {
            const byteCharacters = atob(base64);
            const byteNumbers = new Array(byteCharacters.length);
            
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            
            const byteArray = new Uint8Array(byteNumbers);
            return new Blob([byteArray], { type: mimeType || 'audio/wav' });
        } catch (error) {
            console.error('❌ TTS [MANAGER] Failed to convert base64 to blob:', error);
            throw error;
        }
    }
    
    /**
     * Show loading state on message
     */
    showLoadingState(messageElement) {
        messageElement.classList.add('loading-audio');
        const indicator = messageElement.querySelector('.audio-loading-indicator');
        if (indicator) {
            // Removed generating speech text
        }
    }
    
    /**
     * Hide loading state on message
     */
    hideLoadingState(messageElement) {
        messageElement.classList.remove('loading-audio');
    }
    
    /**
     * Show playing state on message
     */
    showPlayingState(messageElement) {
        // Remove playing state from other messages
        document.querySelectorAll('.message.playing-audio').forEach(msg => {
            msg.classList.remove('playing-audio');
        });
        
        // Add playing state to current message
        messageElement.classList.add('playing-audio');
    }
    
    /**
     * Hide playing state on message
     */
    hidePlayingState(messageElement) {
        messageElement.classList.remove('playing-audio');
    }
    
    /**
     * Show error state on message
     */
    showError(messageElement, errorMessage) {
        const indicator = messageElement.querySelector('.audio-loading-indicator');
        if (indicator) {
            indicator.textContent = `❌ ${errorMessage}`;
            indicator.style.display = 'block';
            
            // Hide error after 3 seconds
            setTimeout(() => {
                indicator.style.display = 'none';
            }, 3000);
        }
    }
    
    /**
     * Set language for TTS
     */
    setLanguage(language) {
        this.defaultLanguage = language;
        console.log(`🔊 TTS [MANAGER] Language set to: ${language}`);
    }
    
    /**
     * Set voice for TTS
     */
    setVoice(voice) {
        this.defaultVoice = voice;
        console.log(`🔊 TTS [MANAGER] Voice set to: ${voice}`);
    }
    
    /**
     * Show global TTS spinner next to Enable Audio labels
     * Only shows if TTS is actually enabled
     */
    showGlobalTTSSpinner() {
        // Only show spinner if TTS is enabled
        if (!this.enabled) {
            console.log('🔊 TTS [MANAGER] TTS disabled - not showing spinner');
            return;
        }
        
        const spinner = document.querySelector('.tts-spinner');
        const mobileSpinner = document.querySelector('.mobile-tts-spinner');
        
        if (spinner) {
            spinner.classList.remove('d-none');
        }
        if (mobileSpinner) {
            mobileSpinner.classList.remove('d-none');
        }
        
        console.log('🔊 TTS [MANAGER] Global TTS spinner shown (TTS enabled)');
    }
    
    /**
     * Hide global TTS spinner next to Enable Audio labels
     */
    hideGlobalTTSSpinner() {
        const spinner = document.querySelector('.tts-spinner');
        const mobileSpinner = document.querySelector('.mobile-tts-spinner');
        
        if (spinner) {
            spinner.classList.add('d-none');
        }
        if (mobileSpinner) {
            mobileSpinner.classList.add('d-none');
        }
        
        console.log('🔊 TTS [MANAGER] Global TTS spinner hidden');
    }
}