/**
 * FIA v3.0 - VoiceChatHandler Component
 * Web Speech API Integration for voice recognition
 */

export class VoiceChatHandler {
    constructor(language = 'fr') {
        this.language = language;
        this.recognition = null;
        this.isSupported = this.checkSupport();
        this.isListening = false;
        this.hasPermission = false;
        
        // Callbacks for integration with main app
        this.onResult = null;
        this.onError = null;
        this.onStart = null;
        this.onEnd = null;
        
        console.log('🎤 [VOICE] VoiceChatHandler initialized:', {
            supported: this.isSupported,
            language: this.language
        });
    }
    
    /**
     * Check if Web Speech API is supported in current browser 
     */
    checkSupport() {
        const hasWebkitSpeech = 'webkitSpeechRecognition' in window;
        const hasSpeech = 'SpeechRecognition' in window;
        
        console.log('🎤 [VOICE] Browser support check:', {
            webkitSpeechRecognition: hasWebkitSpeech,
            SpeechRecognition: hasSpeech,
            userAgent: navigator.userAgent
        });
        
        return hasWebkitSpeech || hasSpeech;
    }
    
    /**
     * Check if Web Speech API is supported
     */
    isApiSupported() {
        return this.isSupported;
    }
    
    /**
     * Request microphone permissions
     */
    async requestPermissions() {
        try {
            console.log('🎤 [VOICE] Requesting microphone permissions...');
            
            // Test microphone access
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Stop the test stream immediately
            stream.getTracks().forEach(track => track.stop());
            
            this.hasPermission = true;
            console.log('✅ [VOICE] Microphone permissions granted');
            return true;
            
        } catch (error) {
            console.error('❌ [VOICE] Microphone permission denied:', error);
            this.hasPermission = false;
            return false;
        }
    }
    
    /**
     * Initialize speech recognition with proper configuration
     */
    initRecognition() {
        if (!this.isSupported) {
            console.error('❌ [VOICE] Speech recognition not supported');
            return false;
        }
        
        try {
            // Create recognition instance
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            // Configure recognition settings
            this.recognition.continuous = false;          // Single recognition session
            this.recognition.interimResults = false;      // Final results only
            this.recognition.maxAlternatives = 3;         // Multiple alternatives
            this.recognition.lang = this.language;        // Set language
            
            // Remove custom timeout - use browser default
            
            // Setup event handlers
            this.setupRecognitionEvents();
            
            console.log('✅ [VOICE] Speech recognition initialized:', {
                continuous: this.recognition.continuous,
                interimResults: this.recognition.interimResults,
                language: this.recognition.lang
            });
            
            return true;
            
        } catch (error) {
            console.error('❌ [VOICE] Failed to initialize speech recognition:', error);
            return false;
        }
    }
    
    /**
     * Setup speech recognition event handlers
     */
    setupRecognitionEvents() {
        if (!this.recognition) return;
        
        // Recognition started
        this.recognition.onstart = () => {
            console.log('🎤 [VOICE] Recognition started');
            this.isListening = true;
            if (this.onStart) this.onStart();
        };
        
        // Recognition ended
        this.recognition.onend = () => {
            console.log('🎤 [VOICE] Recognition ended');
            this.isListening = false;
            if (this.onEnd) this.onEnd();
        };
        
        // Recognition result received
        this.recognition.onresult = (event) => {
            console.log('🎤 [VOICE] Recognition result:', event);
            
            let transcript = '';
            let isFinal = false;
            
            // Process all results
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const result = event.results[i];
                transcript += result[0].transcript;
                
                if (result.isFinal) {
                    isFinal = true;
                }
            }
            
            console.log('🎤 [VOICE] Transcript:', {
                text: transcript,
                isFinal: isFinal,
                confidence: event.results[0]?.[0]?.confidence
            });
            
            // Call result callback
            if (this.onResult) {
                this.onResult(transcript, isFinal);
            }
        };
        
        // Recognition error
        this.recognition.onerror = (event) => {
            console.error('❌ [VOICE] Recognition error:', event.error);
            
            const errorMessage = this.getErrorMessage(event.error);
            
            if (this.onError) {
                this.onError(event.error, errorMessage);
            }
        };
    }
    
    /**
     * Get user-friendly error message
     */
    getErrorMessage(error) {
        const errorMessages = {
            'not-allowed': 'Microphone access denied. Please allow microphone permissions.',
            'no-speech': 'No speech detected. Please speak clearly.',
            'audio-capture': 'Microphone not available. Please check your microphone.',
            'network': 'Network error. Please check your internet connection.',
            'service-not-allowed': 'Speech recognition service not allowed.',
            'bad-grammar': 'Speech recognition grammar error.',
            'language-not-supported': 'Selected language not supported for speech recognition.'
        };
        
        return errorMessages[error] || `Speech recognition error: ${error}`;
    }
    
    /**
     * Set the recognition language
     */
    setLanguage(language) {
        this.language = language;
        if (this.recognition) {
            this.recognition.lang = language;
        }
        console.log('🎤 [VOICE] Language set to:', language);
    }
    
    /**
     * Start speech recognition
     */
    async startRecognition() {
        if (!this.isSupported) {
            throw new Error('Speech recognition not supported in this browser');
        }
        
        if (!this.hasPermission) {
            const hasPermission = await this.requestPermissions();
            if (!hasPermission) {
                throw new Error('Microphone permission required');
            }
        }
        
        if (!this.recognition) {
            const initialized = this.initRecognition();
            if (!initialized) {
                throw new Error('Failed to initialize speech recognition');
            }
        }
        
        if (this.isListening) {
            console.log('🎤 [VOICE] Already listening, ignoring start request');
            return;
        }
        
        try {
            console.log('🎤 [VOICE] Starting recognition...');
            this.recognition.start();
        } catch (error) {
            console.error('❌ [VOICE] Failed to start recognition:', error);
            throw error;
        }
    }
    
    /**
     * Stop speech recognition
     */
    stopRecognition() {
        if (!this.recognition || !this.isListening) {
            console.log('🎤 [VOICE] Not listening, ignoring stop request');
            return;
        }
        
        try {
            console.log('🎤 [VOICE] Stopping recognition...');
            this.recognition.stop();
        } catch (error) {
            console.error('❌ [VOICE] Failed to stop recognition:', error);
        }
    }
    
    /**
     * Get current status
     */
    getStatus() {
        return {
            isSupported: this.isSupported,
            hasPermission: this.hasPermission,
            isListening: this.isListening,
            language: this.language
        };
    }
}