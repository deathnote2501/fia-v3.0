/**
 * FIA v3.0 - Mobile Fallback Initialization
 * Backup initialization for mobile interface when main initialization fails
 */

window.initMobileFallback = function() {
    console.log('🔄 [MOBILE-FALLBACK] Starting mobile fallback initialization...');
    
    // Basic mobile button mapping without full class functionality
    const mobileButtonMappings = {
        'mobile-previous-btn': 'new-previous-btn',
        'mobile-next-btn': 'new-next-btn',
        'mobile-simplify-btn': 'new-simplify-btn',
        'mobile-more-details-btn': 'new-more-details-btn',
        'mobile-chart-btn': 'generate-chart-btn',
        'mobile-comment-btn': 'comment-btn',
        'mobile-quiz-btn': 'quiz-btn',
        'mobile-examples-btn': 'examples-btn',
        'mobile-key-points-btn': 'key-points-btn',
        'mobile-live-api-btn': 'live-api-btn'
    };
    
    // Setup basic click forwarding
    Object.entries(mobileButtonMappings).forEach(([mobileId, desktopId]) => {
        const mobileBtn = document.getElementById(mobileId);
        const desktopBtn = document.getElementById(desktopId);
        
        if (mobileBtn && desktopBtn) {
            mobileBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log(`🔄 [MOBILE-FALLBACK] Forwarding ${mobileId} → ${desktopId}`);
                
                // Add loading spinner
                const originalHTML = mobileBtn.innerHTML;
                mobileBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
                mobileBtn.disabled = true;
                
                // Click desktop button
                desktopBtn.click();
                
                // Remove loading after delay
                setTimeout(() => {
                    mobileBtn.innerHTML = originalHTML;
                    mobileBtn.disabled = false;
                }, 2000);
            });
            
            console.log(`✅ [MOBILE-FALLBACK] ${mobileId} → ${desktopId} mapped`);
        } else {
            console.warn(`⚠️ [MOBILE-FALLBACK] Missing elements: ${mobileId}=${!!mobileBtn}, ${desktopId}=${!!desktopBtn}`);
        }
    });
    
    // Setup TTS toggle fallback
    const mobileTTSToggle = document.getElementById('mobile-tts-toggle');
    const desktopTTSToggle = document.getElementById('tts-toggle');
    
    if (mobileTTSToggle && desktopTTSToggle) {
        mobileTTSToggle.addEventListener('change', (e) => {
            console.log('🔄 [MOBILE-FALLBACK] TTS toggle changed:', e.target.checked);
            desktopTTSToggle.checked = e.target.checked;
            desktopTTSToggle.click();
        });
        
        desktopTTSToggle.addEventListener('change', (e) => {
            if (mobileTTSToggle.checked !== e.target.checked) {
                mobileTTSToggle.checked = e.target.checked;
            }
        });
        
        console.log('✅ [MOBILE-FALLBACK] TTS toggle mapped');
    }
    
    // Setup input sync fallback
    const mobileChatInput = document.getElementById('mobile-chat-input');
    const desktopChatInput = document.getElementById('chat-input');
    const mobileVoiceBtn = document.getElementById('mobile-voice-chat-btn');
    const desktopVoiceBtn = document.getElementById('voice-chat-btn');
    
    if (mobileChatInput && desktopChatInput) {
        // Sync mobile → desktop
        mobileChatInput.addEventListener('input', (e) => {
            desktopChatInput.value = e.target.value;
            
            // Update voice button state
            if (mobileVoiceBtn) {
                if (e.target.value.trim()) {
                    mobileVoiceBtn.innerHTML = '<i class="bi bi-send"></i>';
                    mobileVoiceBtn.classList.add('state-send');
                    mobileVoiceBtn.classList.remove('state-mic');
                } else {
                    mobileVoiceBtn.innerHTML = '<i class="bi bi-mic"></i>';
                    mobileVoiceBtn.classList.add('state-mic');
                    mobileVoiceBtn.classList.remove('state-send');
                }
            }
        });
        
        // Sync desktop → mobile (for voice transcription)
        let lastDesktopValue = desktopChatInput.value;
        setInterval(() => {
            if (desktopChatInput.value !== lastDesktopValue) {
                lastDesktopValue = desktopChatInput.value;
                mobileChatInput.value = desktopChatInput.value;
                
                // Trigger input event for voice button update
                const inputEvent = new Event('input', { bubbles: true });
                mobileChatInput.dispatchEvent(inputEvent);
            }
        }, 100);
        
        // Enter key handling
        mobileChatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (mobileChatInput.value.trim()) {
                    desktopChatInput.value = mobileChatInput.value;
                    const enterEvent = new KeyboardEvent('keydown', {
                        key: 'Enter',
                        code: 'Enter',
                        keyCode: 13,
                        which: 13,
                        bubbles: true
                    });
                    desktopChatInput.dispatchEvent(enterEvent);
                    mobileChatInput.value = '';
                }
            }
        });
        
        console.log('✅ [MOBILE-FALLBACK] Chat input mapped');
    }
    
    // Setup voice button fallback
    if (mobileVoiceBtn && desktopVoiceBtn) {
        mobileVoiceBtn.addEventListener('click', (e) => {
            e.preventDefault();
            
            if (mobileChatInput && mobileChatInput.value.trim() && mobileVoiceBtn.classList.contains('state-send')) {
                // Send message
                desktopChatInput.value = mobileChatInput.value;
                const enterEvent = new KeyboardEvent('keydown', {
                    key: 'Enter',
                    code: 'Enter',
                    keyCode: 13,
                    which: 13,
                    bubbles: true
                });
                desktopChatInput.dispatchEvent(enterEvent);
                mobileChatInput.value = '';
            } else {
                // Start voice recording
                desktopVoiceBtn.click();
            }
        });
        
        console.log('✅ [MOBILE-FALLBACK] Voice button mapped');
    }
    
    // Setup chat messages sync fallback
    const mobileChatMessages = document.getElementById('mobile-chat-messages');
    const desktopChatMessages = document.getElementById('chat-messages');
    
    if (mobileChatMessages && desktopChatMessages) {
        const syncMessages = () => {
            if (window.innerWidth <= 768) {
                mobileChatMessages.innerHTML = desktopChatMessages.innerHTML;
                mobileChatMessages.scrollTop = mobileChatMessages.scrollHeight;
            }
        };
        
        // Watch for changes
        if (window.MutationObserver) {
            const observer = new MutationObserver(syncMessages);
            observer.observe(desktopChatMessages, { childList: true, subtree: true });
        } else {
            // Fallback for older browsers
            setInterval(syncMessages, 1000);
        }
        
        // Initial sync
        syncMessages();
        
        // Sync on window resize
        window.addEventListener('resize', syncMessages);
        
        console.log('✅ [MOBILE-FALLBACK] Chat messages sync mapped');
    }
    
    console.log('✅ [MOBILE-FALLBACK] Mobile fallback initialization completed');
    window.mobileFallbackReady = true;
};

// Auto-initialize fallback if main mobile interface fails to load after 5 seconds
setTimeout(() => {
    if (!window.mobileInterfaceReady && window.innerWidth <= 768) {
        console.warn('⚠️ [MOBILE-FALLBACK] Main mobile interface not ready, initializing fallback...');
        window.initMobileFallback();
    }
}, 5000);

console.log('🔄 [MOBILE-FALLBACK] Mobile fallback system loaded');