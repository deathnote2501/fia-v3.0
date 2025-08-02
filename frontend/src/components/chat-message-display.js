/**
 * FIA v3.0 - Chat Message Display Component
 * Handles rendering and displaying chat messages with metadata, badges, and audio controls
 */

export class ChatMessageDisplay {
    constructor(ttsManager) {
        this.ttsManager = ttsManager;
        console.log('💬 [CHAT-DISPLAY] ChatMessageDisplay initialized');
    }
    
    /**
     * Add a chat message to the chat interface
     * @param {string} role - 'user' or 'assistant' 
     * @param {string} content - Message content
     * @param {Object} metadata - Message metadata (action_type, suggested_actions, etc.)
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
                'comment': { class: 'border border-primary text-primary', icon: 'bi-chat-text', text: '' },
                'quiz': { class: 'border border-primary text-primary', icon: 'bi-question-circle', text: '' },
                'examples': { class: 'border border-primary text-primary', icon: 'bi-lightbulb', text: '' },
                'key-points': { class: 'border border-primary text-primary', icon: 'bi-star', text: '' }
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
                    <button class="audio-toggle-btn stopped" onclick="app.toggleMessageAudio('${messageId}')" data-message-id="${messageId}">
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
                                <!-- Confidence badge removed -->
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
        
        // Always generate TTS for assistant messages (for manual buttons)
        if (!isUser && !metadata.error) {
            const messageElement = chatMessages.querySelector(`[data-message-id="${messageId}"]`);
            if (messageElement) {
                // Generate audio, auto-play only if TTS enabled
                const autoPlay = this.ttsManager.enabled;
                this.ttsManager.generateAndPlaySpeech(content, messageElement, autoPlay);
            }
        }
        
        console.log('💬 [CHAT-DISPLAY] Message added:', { role, content: content.substring(0, 50) + '...', metadata });
    }
    
    /**
     * Clear all chat messages
     */
    clearMessages() {
        const chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
            chatMessages.innerHTML = '';
            console.log('💬 [CHAT-DISPLAY] All messages cleared');
        }
    }
    
    /**
     * Get all message elements
     * @returns {NodeList} All message elements
     */
    getAllMessages() {
        return document.querySelectorAll('#chat-messages .message');
    }
    
    /**
     * Get message element by ID
     * @param {string} messageId - The message ID to find
     * @returns {Element|null} The message element or null
     */
    getMessageById(messageId) {
        return document.querySelector(`[data-message-id="${messageId}"]`);
    }
    
    /**
     * Scroll chat to bottom
     */
    scrollToBottom() {
        const chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
}