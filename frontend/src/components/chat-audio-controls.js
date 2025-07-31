/**
 * FIA v3.0 - Chat Audio Controls Component
 * Handles audio playback controls for chat messages
 */

export class ChatAudioControls {
    constructor(ttsManager) {
        this.ttsManager = ttsManager;
        console.log('🔊 [CHAT-AUDIO] ChatAudioControls initialized');
    }
    
    /**
     * Play audio for a specific message
     * @param {string} messageId - The message ID to play audio for
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
     * @param {string} messageId - The message ID to pause audio for
     */
    pauseMessageAudio(messageId) {
        this.ttsManager.pauseAudio();
        this.updateAudioControlButtons(messageId, 'paused');
    }
    
    /**
     * Stop audio for a specific message
     * @param {string} messageId - The message ID to stop audio for
     */
    stopMessageAudio(messageId) {
        this.ttsManager.stopAudio();
        this.updateAudioControlButtons(messageId, 'stopped');
    }
    
    /**
     * Update audio control button states
     * @param {string} messageId - The message ID to update controls for
     * @param {string} state - Button state: 'playing', 'paused', 'stopped'
     */
    updateAudioControlButtons(messageId, state) {
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        if (!messageElement) return;
        
        const playBtn = messageElement.querySelector('.audio-play-btn');
        const pauseBtn = messageElement.querySelector('.audio-pause-btn');
        const stopBtn = messageElement.querySelector('.audio-stop-btn');
        
        if (playBtn && pauseBtn && stopBtn) {
            switch (state) {
                case 'playing':
                    playBtn.style.display = 'none';
                    pauseBtn.style.display = 'inline-block';
                    stopBtn.style.display = 'inline-block';
                    break;
                case 'paused':
                case 'stopped':
                default:
                    playBtn.style.display = 'inline-block';
                    pauseBtn.style.display = 'none';
                    stopBtn.style.display = 'none';
                    break;
            }
        }
    }
    
    /**
     * Reset all audio control buttons to default state
     */
    resetAllAudioControls() {
        const messages = document.querySelectorAll('.message[data-message-id]');
        messages.forEach(messageElement => {
            const messageId = messageElement.dataset.messageId;
            this.updateAudioControlButtons(messageId, 'stopped');
        });
        console.log('🔊 [CHAT-AUDIO] All audio controls reset');
    }
    
    /**
     * Show/hide audio controls based on TTS enabled state
     * @param {boolean} enabled - Whether TTS is enabled
     */
    toggleAudioControlsVisibility(enabled) {
        const audioControls = document.querySelectorAll('.message-audio-controls');
        audioControls.forEach(controls => {
            controls.style.display = enabled ? 'block' : 'none';
        });
        console.log(`🔊 [CHAT-AUDIO] Audio controls visibility: ${enabled ? 'shown' : 'hidden'}`);
    }
}