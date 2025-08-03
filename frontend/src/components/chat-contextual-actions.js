/**
 * FIA v3.0 - Chat Contextual Actions Component
 * Handles contextual chat buttons (comment, quiz, examples, key-points)
 */

export class ChatContextualActions {
    constructor(chatUtilities, chatMessageDisplay) {
        this.chatUtilities = chatUtilities;
        this.chatMessageDisplay = chatMessageDisplay;
        console.log('🎯 [CONTEXTUAL] ChatContextualActions initialized');
    }
    
    /**
     * Setup event listeners for contextual chat buttons
     */
    setupContextualChatButtons() {
        const commentBtn = document.getElementById('comment-btn');
        const quizBtn = document.getElementById('quiz-btn');
        const examplesBtn = document.getElementById('examples-btn');
        const keyPointsBtn = document.getElementById('key-points-btn');
        
        if (commentBtn) {
            commentBtn.addEventListener('click', () => this.handleContextualAction('comment'));
            console.log('✅ [CONTEXTUAL] Comment button event listener added');
        }
        
        if (quizBtn) {
            quizBtn.addEventListener('click', () => this.handleContextualAction('quiz'));
            console.log('✅ [CONTEXTUAL] Quiz button event listener added');
        }
        
        if (examplesBtn) {
            examplesBtn.addEventListener('click', () => this.handleContextualAction('examples'));
            console.log('✅ [CONTEXTUAL] Examples button event listener added');
        }
        
        if (keyPointsBtn) {
            keyPointsBtn.addEventListener('click', () => this.handleContextualAction('key-points'));
            console.log('✅ [CONTEXTUAL] Key Points button event listener added');
        }
    }
    
    /**
     * Handle contextual action requests
     * @param {string} actionType - Type of action: 'comment', 'quiz', 'examples', 'key-points'
     */
    async handleContextualAction(actionType) {
        console.log(`💬 [CONTEXTUAL] Handling ${actionType} action`);
        
        // Get current slide data from parent app - need to be injected
        if (!this.getCurrentSlideData) {
            console.error('❌ [CONTEXTUAL] getCurrentSlideData callback not set');
            this.chatMessageDisplay.addChatMessage('assistant', 
                'I need slide content to provide this information. Please wait for the slide to load.',
                { error: true }
            );
            return;
        }
        
        const { currentSlideContent, currentSlide, learnerSession } = this.getCurrentSlideData();
        
        if (!currentSlideContent || !currentSlide) {
            console.error('❌ [CONTEXTUAL] No current slide content available');
            this.chatMessageDisplay.addChatMessage('assistant', 
                'I need slide content to provide this information. Please wait for the slide to load.',
                { error: true }
            );
            return;
        }
        
        // Disable all contextual buttons during processing
        this.setContextualButtonsEnabled(false, actionType);
        
        // Afficher l'animation de réflexion de l'IA
        this.chatUtilities.showTypingAnimation();
        
        try {
            // Prepare request payload
            const requestPayload = {
                learner_session_id: learnerSession.id,
                slide_content: currentSlideContent,
                slide_title: currentSlide.title || 'Current Slide'
            };
            
            console.log(`📤 [CONTEXTUAL] ${actionType} request payload:`, requestPayload);
            
            // Call the appropriate API endpoint
            const apiEndpoint = `/api/chat/${actionType}`;
            const response = await fetch(apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestPayload)
            });
            
            console.log(`📥 [CONTEXTUAL] ${actionType} response status:`, response.status);
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error(`❌ [CONTEXTUAL] ${actionType} error response:`, errorData);
                throw new Error(errorData.detail || `${actionType} service temporarily unavailable`);
            }
            
            const chatResponse = await response.json();
            console.log(`✅ [CONTEXTUAL] ${actionType} success response:`, chatResponse);
            
            // Supprimer l'animation de réflexion
            this.chatUtilities.hideTypingAnimation();
            
            // Add AI response to chat with appropriate metadata
            this.chatMessageDisplay.addChatMessage('assistant', chatResponse.response, {
                confidence: chatResponse.confidence_score,
                suggested_actions: chatResponse.suggested_actions,
                related_concepts: chatResponse.related_concepts,
                action_type: actionType
            });
            
        } catch (error) {
            console.error(`❌ [CONTEXTUAL] ${actionType} error:`, error);
            
            // Supprimer l'animation de réflexion en cas d'erreur
            this.chatUtilities.hideTypingAnimation();
            
            // Add error message to chat
            let errorMessage = `I'm sorry, I encountered an error while processing your ${actionType} request. Please try again.`;
            if (actionType === 'comment') errorMessage = 'I cannot comment on this slide right now. Please try again later.';
            else if (actionType === 'quiz') errorMessage = 'I cannot generate a quiz right now. Please try again later.';
            else if (actionType === 'examples') errorMessage = 'I cannot provide examples right now. Please try again later.';
            else if (actionType === 'key-points') errorMessage = 'I cannot extract key points right now. Please try again later.';
            
            this.chatMessageDisplay.addChatMessage('assistant', `${errorMessage} (${error.message})`, { error: true });
            
        } finally {
            // Re-enable contextual buttons
            this.setContextualButtonsEnabled(true);
        }
    }
    
    /**
     * Enable/disable contextual buttons
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
                    if (actionType === 'comment') button.innerHTML = '<i class="bi bi-chat-text me-1"></i>' + (window.safeT ? window.safeT('chat.comment') : 'Comment');
                    else if (actionType === 'quiz') button.innerHTML = '<i class="bi bi-question-circle me-1"></i>' + (window.safeT ? window.safeT('chat.quiz') : 'Quiz');
                    else if (actionType === 'examples') button.innerHTML = '<i class="bi bi-lightbulb me-1"></i>' + (window.safeT ? window.safeT('chat.examples') : 'Examples');
                    else if (actionType === 'key-points') button.innerHTML = '<i class="bi bi-star me-1"></i>' + (window.safeT ? window.safeT('chat.keyPoints') : 'Key Points');
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
     * Set callback to get current slide data from parent app
     * @param {Function} callback - Function that returns {currentSlideContent, currentSlide, learnerSession}
     */
    setGetCurrentSlideDataCallback(callback) {
        this.getCurrentSlideData = callback;
        console.log('🎯 [CONTEXTUAL] getCurrentSlideData callback set');
    }
}