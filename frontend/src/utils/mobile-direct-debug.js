/**
 * FIA v3.0 - Mobile Direct Debug (No ES6 modules)
 * Emergency mobile debugging without module dependencies
 */

(function() {
    'use strict';
    
    console.log('🔍 [DIRECT-DEBUG] Loading mobile direct debug...');
    
    // Emergency mobile button fix - No ES6, no modules
    function emergencyMobileFix() {
        console.log('🚨 [DIRECT-DEBUG] Emergency mobile fix starting...');
        
        // Mobile button mappings
        var mobileButtonMappings = {
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
        
        var setupCount = 0;
        
        // Setup each button mapping
        for (var mobileId in mobileButtonMappings) {
            if (mobileButtonMappings.hasOwnProperty(mobileId)) {
                var desktopId = mobileButtonMappings[mobileId];
                var mobileBtn = document.getElementById(mobileId);
                var desktopBtn = document.getElementById(desktopId);
                
                if (mobileBtn && desktopBtn) {
                    (function(mId, dId, mBtn, dBtn) {
                        mBtn.addEventListener('click', function(e) {
                            e.preventDefault();
                            console.log('🔄 [DIRECT-DEBUG] ' + mId + ' clicked → forwarding to ' + dId);
                            
                            // Add visual feedback
                            var originalHTML = mBtn.innerHTML;
                            mBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
                            mBtn.disabled = true;
                            
                            // Click desktop button
                            dBtn.click();
                            
                            // Restore after delay
                            setTimeout(function() {
                                mBtn.innerHTML = originalHTML;
                                mBtn.disabled = false;
                            }, 2000);
                        });
                    })(mobileId, desktopId, mobileBtn, desktopBtn);
                    
                    setupCount++;
                    console.log('✅ [DIRECT-DEBUG] ' + mobileId + ' → ' + desktopId + ' mapped');
                } else {
                    console.warn('⚠️ [DIRECT-DEBUG] Missing: ' + mobileId + '=' + !!mobileBtn + ', ' + desktopId + '=' + !!desktopBtn);
                }
            }
        }
        
        // Setup TTS toggle
        var mobileTTSToggle = document.getElementById('mobile-tts-toggle');
        var desktopTTSToggle = document.getElementById('tts-toggle');
        
        if (mobileTTSToggle && desktopTTSToggle) {
            mobileTTSToggle.addEventListener('change', function(e) {
                console.log('🔄 [DIRECT-DEBUG] Mobile TTS toggle changed: ' + e.target.checked);
                desktopTTSToggle.checked = e.target.checked;
                desktopTTSToggle.click();
            });
            
            desktopTTSToggle.addEventListener('change', function(e) {
                if (mobileTTSToggle.checked !== e.target.checked) {
                    mobileTTSToggle.checked = e.target.checked;
                }
            });
            
            setupCount++;
            console.log('✅ [DIRECT-DEBUG] TTS toggle mapped');
        }
        
        // Setup mobile input
        var mobileChatInput = document.getElementById('mobile-chat-input');
        var desktopChatInput = document.getElementById('chat-input');
        var mobileVoiceBtn = document.getElementById('mobile-voice-chat-btn');
        
        if (mobileChatInput && desktopChatInput) {
            // Mobile to desktop sync
            mobileChatInput.addEventListener('input', function(e) {
                desktopChatInput.value = e.target.value;
                
                // Update voice button
                if (mobileVoiceBtn) {
                    var icon = mobileVoiceBtn.querySelector('i');
                    if (icon) {
                        if (e.target.value.trim()) {
                            icon.className = 'bi bi-send';
                        } else {
                            icon.className = 'bi bi-mic';
                        }
                    }
                }
            });
            
            // Desktop to mobile sync (for voice transcription)
            var lastValue = desktopChatInput.value;
            setInterval(function() {
                if (desktopChatInput.value !== lastValue) {
                    lastValue = desktopChatInput.value;
                    mobileChatInput.value = desktopChatInput.value;
                }
            }, 100);
            
            // Enter key handling
            mobileChatInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    if (mobileChatInput.value.trim()) {
                        desktopChatInput.value = mobileChatInput.value;
                        
                        // Trigger enter on desktop
                        var enterEvent = new KeyboardEvent('keydown', {
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
            
            setupCount++;
            console.log('✅ [DIRECT-DEBUG] Chat input mapped');
        }
        
        // Setup voice button
        var desktopVoiceBtn = document.getElementById('voice-chat-btn');
        if (mobileVoiceBtn && desktopVoiceBtn) {
            mobileVoiceBtn.addEventListener('click', function(e) {
                e.preventDefault();
                console.log('🔄 [DIRECT-DEBUG] Mobile voice button clicked');
                
                if (mobileChatInput && mobileChatInput.value.trim()) {
                    // Send message
                    desktopChatInput.value = mobileChatInput.value;
                    var enterEvent = new KeyboardEvent('keydown', {
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
            
            setupCount++;
            console.log('✅ [DIRECT-DEBUG] Voice button mapped');
        }
        
        // Setup chat messages sync
        var mobileChatMessages = document.getElementById('mobile-chat-messages');
        var desktopChatMessages = document.getElementById('chat-messages');
        
        if (mobileChatMessages && desktopChatMessages) {
            function syncMessages() {
                if (window.innerWidth <= 768) {
                    mobileChatMessages.innerHTML = desktopChatMessages.innerHTML;
                    mobileChatMessages.scrollTop = mobileChatMessages.scrollHeight;
                }
            }
            
            // Watch for changes
            if (window.MutationObserver) {
                var observer = new MutationObserver(syncMessages);
                observer.observe(desktopChatMessages, { childList: true, subtree: true });
            } else {
                setInterval(syncMessages, 1000);
            }
            
            syncMessages();
            window.addEventListener('resize', syncMessages);
            
            setupCount++;
            console.log('✅ [DIRECT-DEBUG] Chat messages sync mapped');
        }
        
        console.log('✅ [DIRECT-DEBUG] Emergency mobile fix completed - ' + setupCount + ' components mapped');
        window.emergencyMobileReady = true;
        
        return setupCount;
    }
    
    // Diagnostic function
    function diagnoseDirectly() {
        console.log('🔍 [DIRECT-DEBUG] === DIAGNOSTIC DIRECT ===');
        
        var viewport = {
            width: window.innerWidth,
            height: window.innerHeight,
            isMobile: window.innerWidth <= 768
        };
        console.log('📱 Viewport:', viewport);
        
        // Check mobile elements
        var mobileElements = [
            'mobile-previous-btn', 'mobile-next-btn', 'mobile-simplify-btn',
            'mobile-more-details-btn', 'mobile-chart-btn', 'mobile-comment-btn',
            'mobile-quiz-btn', 'mobile-examples-btn', 'mobile-key-points-btn',
            'mobile-tts-toggle', 'mobile-live-api-btn', 'mobile-chat-input',
            'mobile-voice-chat-btn', 'mobile-chat-messages'
        ];
        
        var mobileStatus = {};
        mobileElements.forEach(function(id) {
            var element = document.getElementById(id);
            mobileStatus[id] = !!element;
        });
        
        console.log('📱 Mobile Elements:', mobileStatus);
        
        // Check desktop elements
        var desktopElements = [
            'new-previous-btn', 'new-next-btn', 'new-simplify-btn',
            'new-more-details-btn', 'generate-chart-btn', 'comment-btn',
            'quiz-btn', 'examples-btn', 'key-points-btn', 'tts-toggle',
            'live-api-btn', 'chat-input', 'voice-chat-btn', 'chat-messages'
        ];
        
        var desktopStatus = {};
        desktopElements.forEach(function(id) {
            var element = document.getElementById(id);
            desktopStatus[id] = !!element;
        });
        
        console.log('🖥️ Desktop Elements:', desktopStatus);
        
        // Check globals
        var globalStatus = {
            emergencyMobileReady: !!window.emergencyMobileReady,
            mobileInterfaceReady: !!window.mobileInterfaceReady,
            mobileFallbackReady: !!window.mobileFallbackReady,
            fiaApp: !!window.fiaApp
        };
        
        console.log('🌐 Globals:', globalStatus);
        
        return {
            viewport: viewport,
            mobileStatus: mobileStatus,
            desktopStatus: desktopStatus,
            globalStatus: globalStatus
        };
    }
    
    // Test button clicks
    function testButtonsDirectly() {
        console.log('🎯 [DIRECT-DEBUG] Testing mobile button clicks...');
        
        var testButtons = ['mobile-previous-btn', 'mobile-next-btn', 'mobile-simplify-btn'];
        
        testButtons.forEach(function(id) {
            var button = document.getElementById(id);
            if (button) {
                console.log('🔘 Testing ' + id + '...');
                try {
                    button.click();
                    console.log('✅ ' + id + ' click successful');
                } catch (error) {
                    console.error('❌ ' + id + ' click failed:', error);
                }
            } else {
                console.warn('⚠️ ' + id + ' not found');
            }
        });
    }
    
    // Make functions globally available
    window.emergencyMobileFix = emergencyMobileFix;
    window.diagnoseDirectly = diagnoseDirectly;
    window.testButtonsDirectly = testButtonsDirectly;
    
    // Auto-run emergency fix if we're on mobile
    function initEmergencyFix() {
        if (window.innerWidth <= 768) {
            console.log('🚨 [DIRECT-DEBUG] Mobile viewport detected, running emergency fix...');
            emergencyMobileFix();
        } else {
            console.log('🖥️ [DIRECT-DEBUG] Desktop viewport, emergency fix on standby');
        }
    }
    
    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initEmergencyFix);
    } else {
        initEmergencyFix();
    }
    
    // Also run after a delay to catch late DOM changes
    setTimeout(function() {
        if (window.innerWidth <= 768 && !window.emergencyMobileReady) {
            console.log('🚨 [DIRECT-DEBUG] Delayed emergency fix...');
            emergencyMobileFix();
        }
    }, 3000);
    
    console.log('✅ [DIRECT-DEBUG] Direct debug system loaded');
    console.log('🔧 [DIRECT-DEBUG] Available commands: window.emergencyMobileFix(), window.diagnoseDirectly(), window.testButtonsDirectly()');
    
})();