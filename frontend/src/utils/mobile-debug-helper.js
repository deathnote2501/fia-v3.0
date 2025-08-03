/**
 * FIA v3.0 - Mobile Debug Helper
 * Diagnostic tools for mobile interface issues in production
 */

export class MobileDebugHelper {
    static diagnose() {
        console.log('🔍 [MOBILE-DEBUG] === DIAGNOSTIC MOBILE INTERFACE ===');
        
        // Check viewport
        const viewport = {
            width: window.innerWidth,
            height: window.innerHeight,
            isMobile: window.innerWidth <= 768
        };
        console.log('📱 [MOBILE-DEBUG] Viewport:', viewport);
        
        // Check if all mobile elements exist
        const requiredElements = [
            'mobile-previous-btn', 'mobile-next-btn', 'mobile-simplify-btn', 
            'mobile-more-details-btn', 'mobile-chart-btn', 'mobile-comment-btn',
            'mobile-quiz-btn', 'mobile-examples-btn', 'mobile-key-points-btn',
            'mobile-tts-toggle', 'mobile-live-api-btn', 'mobile-chat-input',
            'mobile-voice-chat-btn', 'mobile-chat-messages'
        ];
        
        const elementStatus = {};
        requiredElements.forEach(id => {
            const element = document.getElementById(id);
            elementStatus[id] = {
                exists: !!element,
                visible: element ? !element.hidden && element.style.display !== 'none' : false,
                hasEventListeners: element ? element._hasEventListeners : false
            };
        });
        
        console.log('🎯 [MOBILE-DEBUG] Element Status:', elementStatus);
        
        // Check desktop counterparts
        const desktopElements = [
            'new-previous-btn', 'new-next-btn', 'new-simplify-btn',
            'new-more-details-btn', 'generate-chart-btn', 'comment-btn',
            'quiz-btn', 'examples-btn', 'key-points-btn', 'tts-toggle',
            'live-api-btn', 'chat-input', 'voice-chat-btn', 'chat-messages'
        ];
        
        const desktopStatus = {};
        desktopElements.forEach(id => {
            const element = document.getElementById(id);
            desktopStatus[id] = {
                exists: !!element,
                visible: element ? !element.hidden && element.style.display !== 'none' : false
            };
        });
        
        console.log('🖥️ [MOBILE-DEBUG] Desktop Elements:', desktopStatus);
        
        // Check JavaScript globals
        const globalStatus = {
            mobileInterfaceReady: !!window.mobileInterfaceReady,
            fiaApp: !!window.fiaApp,
            i18n: !!window.i18n,
            safeT: !!window.safeT,
            chatInterface: !!(window.fiaApp && window.fiaApp.chatInterface),
            mobileHandler: !!(window.fiaApp && window.fiaApp.mobileInterfaceHandler)
        };
        
        console.log('🌐 [MOBILE-DEBUG] Globals:', globalStatus);
        
        // Check CSS media queries
        const mediaQuery = window.matchMedia('(max-width: 768px)');
        console.log('📐 [MOBILE-DEBUG] CSS Mobile Query Match:', mediaQuery.matches);
        
        // Check any JavaScript errors
        const errors = window.mobileDebugErrors || [];
        if (errors.length > 0) {
            console.log('❌ [MOBILE-DEBUG] Stored Errors:', errors);
        } else {
            console.log('✅ [MOBILE-DEBUG] No stored errors');
        }
        
        // Summary
        const missingMobile = Object.keys(elementStatus).filter(id => !elementStatus[id].exists);
        const missingDesktop = Object.keys(desktopStatus).filter(id => !desktopStatus[id].exists);
        
        console.log('📊 [MOBILE-DEBUG] === SUMMARY ===');
        console.log(`📱 Missing Mobile Elements: ${missingMobile.length > 0 ? missingMobile.join(', ') : 'None'}`);
        console.log(`🖥️ Missing Desktop Elements: ${missingDesktop.length > 0 ? missingDesktop.join(', ') : 'None'}`);
        console.log(`🎯 Mobile Interface Ready: ${globalStatus.mobileInterfaceReady}`);
        console.log(`📐 Is Mobile Viewport: ${viewport.isMobile}`);
        
        return {
            viewport,
            elementStatus,
            desktopStatus,
            globalStatus,
            missingMobile,
            missingDesktop,
            mediaQueryMatches: mediaQuery.matches
        };
    }
    
    static startErrorCapture() {
        // Capture JavaScript errors for mobile debugging
        if (!window.mobileDebugErrors) {
            window.mobileDebugErrors = [];
        }
        
        const originalError = window.onerror;
        window.onerror = function(message, source, lineno, colno, error) {
            window.mobileDebugErrors.push({
                message,
                source,
                lineno,
                colno,
                error: error ? error.toString() : null,
                timestamp: new Date().toISOString()
            });
            
            if (originalError) {
                return originalError.apply(this, arguments);
            }
        };
        
        // Capture unhandled promise rejections
        window.addEventListener('unhandledrejection', function(event) {
            window.mobileDebugErrors.push({
                message: 'Unhandled Promise Rejection',
                error: event.reason ? event.reason.toString() : 'Unknown',
                timestamp: new Date().toISOString()
            });
        });
        
        console.log('🚨 [MOBILE-DEBUG] Error capture started');
    }
    
    static testMobileButtonClicks() {
        console.log('🎯 [MOBILE-DEBUG] Testing mobile button clicks...');
        
        const testButtons = [
            'mobile-previous-btn', 'mobile-next-btn', 'mobile-simplify-btn',
            'mobile-more-details-btn', 'mobile-chart-btn'
        ];
        
        testButtons.forEach(id => {
            const button = document.getElementById(id);
            if (button) {
                console.log(`🔘 [MOBILE-DEBUG] Testing ${id}...`);
                
                // Simulate click
                try {
                    button.click();
                    console.log(`✅ [MOBILE-DEBUG] ${id} click successful`);
                } catch (error) {
                    console.error(`❌ [MOBILE-DEBUG] ${id} click failed:`, error);
                }
            } else {
                console.warn(`⚠️ [MOBILE-DEBUG] ${id} not found`);
            }
        });
    }
}

// Make available globally for production debugging
window.MobileDebugHelper = MobileDebugHelper;

// Auto-start error capture in production
if (typeof window !== 'undefined') {
    MobileDebugHelper.startErrorCapture();
}

// Add a global command to diagnose mobile issues
window.diagnoseMobile = () => MobileDebugHelper.diagnose();
window.testMobileButtons = () => MobileDebugHelper.testMobileButtonClicks();

console.log('🔧 [MOBILE-DEBUG] Mobile Debug Helper loaded - Use window.diagnoseMobile() in console');