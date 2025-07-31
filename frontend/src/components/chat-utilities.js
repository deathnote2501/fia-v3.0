/**
 * FIA v3.0 - Chat Utilities Component
 * Handles typing animations, chat history, and utility functions
 */

export class ChatUtilities {
    constructor() {
        console.log('🛠️ [CHAT-UTILS] ChatUtilities initialized');
    }
    
    /**
     * Show typing animation in chat
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
        
        console.log('💭 [CHAT-UTILS] Typing animation shown');
    }
    
    /**
     * Hide typing animation from chat
     */
    hideTypingAnimation() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
            console.log('💭 [CHAT-UTILS] Typing animation hidden');
        }
    }
    
    /**
     * Get chat history from DOM
     * @returns {Array} Array of message objects
     */
    getChatHistory() {
        // Récupérer l'historique des messages du DOM
        const messages = [];
        const messageElements = document.querySelectorAll('#chat-messages .message');
        
        messageElements.forEach(element => {
            const role = element.classList.contains('assistant') ? 'assistant' : 'user';
            const content = element.querySelector('.message-content p')?.textContent || '';
            const timestamp = element.querySelector('small')?.textContent || new Date().toISOString();
            
            if (content.trim()) {
                messages.push({
                    role: role,
                    content: content,
                    timestamp: timestamp,
                    metadata: {}
                });
            }
        });
        
        console.log('📝 [CHAT-UTILS] Chat history retrieved:', messages.length, 'messages');
        return messages.slice(-10); // Garder seulement les 10 derniers messages pour le contexte
    }
    
    /**
     * Clear typing animation if it exists
     */
    clearTypingIfExists() {
        const existingTyping = document.getElementById('typing-indicator');
        if (existingTyping) {
            this.hideTypingAnimation();
        }
    }
    
    /**
     * Get total message count
     * @returns {number} Number of messages in chat
     */
    getMessageCount() {
        const messageElements = document.querySelectorAll('#chat-messages .message');
        return messageElements.length;
    }
    
    /**
     * Get last message from chat
     * @returns {Object|null} Last message object or null if no messages
     */
    getLastMessage() {
        const messageElements = document.querySelectorAll('#chat-messages .message');
        if (messageElements.length === 0) return null;
        
        const lastElement = messageElements[messageElements.length - 1];
        const role = lastElement.classList.contains('assistant') ? 'assistant' : 'user';
        const content = lastElement.querySelector('.message-content p')?.textContent || '';
        
        return {
            role,
            content,
            element: lastElement
        };
    }
    
    /**
     * Check if chat is empty
     * @returns {boolean} True if chat has no messages
     */
    isChatEmpty() {
        return this.getMessageCount() === 0;
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