/**
 * Mobile Emergency Fix - Production-Ready External Module
 * 
 * This module fixes mobile button functionality that was failing in production.
 * It maps mobile toolbar buttons to their desktop counterparts for full functionality.
 * 
 * CRITICAL: This code was previously inline to guarantee loading in production.
 * Now externalized with enhanced debugging and multiple safety mechanisms.
 */

/**
 * Enhanced mobile button mapping with production debugging
 */
export function initializeMobileEmergencyFix() {
    // Only run on mobile devices
    if (window.innerWidth <= 768) {
        console.log('🚨 [MOBILE-EMERGENCY] Starting enhanced mobile button fix...');
        
        try {
            // Enhanced button mapping with error handling
            const buttonMappings = [
                {
                    mobile: 'mobile-previous-btn',
                    desktop: 'new-previous-btn',
                    action: 'Previous'
                },
                {
                    mobile: 'mobile-next-btn', 
                    desktop: 'new-next-btn',
                    action: 'Next'
                },
                {
                    mobile: 'mobile-simplify-btn',
                    desktop: 'new-simplify-btn', 
                    action: 'Simplify'
                },
                {
                    mobile: 'mobile-more-details-btn',
                    desktop: 'new-more-details-btn',
                    action: 'More Details'
                },
                {
                    mobile: 'mobile-chart-btn',
                    desktop: 'generate-chart-btn',
                    action: 'Chart'
                }
            ];

            let successCount = 0;
            let failureCount = 0;

            // Process each button mapping
            buttonMappings.forEach(mapping => {
                try {
                    const mobileBtn = document.getElementById(mapping.mobile);
                    const desktopBtn = document.getElementById(mapping.desktop);

                    if (mobileBtn && desktopBtn) {
                        // Remove existing event listeners to prevent duplicates
                        mobileBtn.onclick = null;
                        
                        // Add enhanced click handler
                        mobileBtn.onclick = function(e) {
                            e.preventDefault();
                            e.stopPropagation();
                            
                            console.log(`🚨 [MOBILE-EMERGENCY] ${mapping.action} button clicked`);
                            
                            // Trigger desktop button with safety checks
                            if (desktopBtn && typeof desktopBtn.click === 'function') {
                                desktopBtn.click();
                                console.log(`✅ [MOBILE-EMERGENCY] ${mapping.action} button triggered successfully`);
                            } else {
                                console.error(`❌ [MOBILE-EMERGENCY] Desktop ${mapping.action} button not clickable`);
                            }
                        };
                        
                        successCount++;
                        console.log(`✅ [MOBILE-EMERGENCY] ${mapping.action} button mapped successfully`);
                    } else {
                        failureCount++;
                        console.warn(`⚠️ [MOBILE-EMERGENCY] ${mapping.action} button elements not found:`, {
                            mobile: !!mobileBtn,
                            desktop: !!desktopBtn
                        });
                    }
                } catch (error) {
                    failureCount++;
                    console.error(`❌ [MOBILE-EMERGENCY] Error mapping ${mapping.action} button:`, error);
                }
            });

            // Summary report
            console.log(`✅ [MOBILE-EMERGENCY] Fix completed: ${successCount} success, ${failureCount} failures`);
            
            // Set global flag for external monitoring
            window.mobileEmergencyFixStatus = {
                initialized: true,
                success: successCount,
                failures: failureCount,
                timestamp: new Date().toISOString()
            };

        } catch (error) {
            console.error('❌ [MOBILE-EMERGENCY] Critical error in mobile fix:', error);
            window.mobileEmergencyFixStatus = {
                initialized: false,
                error: error.message,
                timestamp: new Date().toISOString()
            };
        }
    } else {
        console.log('📱 [MOBILE-EMERGENCY] Desktop detected, mobile fix skipped');
        window.mobileEmergencyFixStatus = {
            initialized: false,
            reason: 'desktop_device',
            timestamp: new Date().toISOString()
        };
    }
}

/**
 * Production-safe initialization with multiple fallback strategies
 */
export function setupMobileEmergencyFix() {
    console.log('🚨 [MOBILE-EMERGENCY] Setting up external mobile emergency fix...');

    // Strategy 1: DOM already ready
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        console.log('🚨 [MOBILE-EMERGENCY] DOM ready, initializing immediately');
        initializeMobileEmergencyFix();
    }
    
    // Strategy 2: Wait for DOM ready
    if (document.readyState === 'loading') {
        console.log('🚨 [MOBILE-EMERGENCY] DOM loading, waiting for ready state');
        document.addEventListener('DOMContentLoaded', initializeMobileEmergencyFix);
    }
    
    // Strategy 3: Delayed fallbacks (production safety)
    setTimeout(() => {
        console.log('🚨 [MOBILE-EMERGENCY] Executing 1s fallback');
        initializeMobileEmergencyFix();
    }, 1000);
    
    setTimeout(() => {
        console.log('🚨 [MOBILE-EMERGENCY] Executing 3s fallback');  
        initializeMobileEmergencyFix();
    }, 3000);

    // Strategy 4: Make function globally available for manual debugging
    window.initializeMobileEmergencyFix = initializeMobileEmergencyFix;
    window.setupMobileEmergencyFix = setupMobileEmergencyFix;
    
    console.log('🚨 [MOBILE-EMERGENCY] External mobile emergency system ready');
}

// Auto-initialize when module loads
setupMobileEmergencyFix();