/**
 * FIA v3.0 - Training Page Initialization
 * External initialization script for training.html
 */

import { initializeFIAApp } from './main.js';

/**
 * Initialize the training page application
 */
async function initializeTrainingPage() {
    try {
        console.log('🌟 Training page loaded, initializing modular FIA app...');
        
        // Get token from URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token');
        
        if (!token) {
            throw new Error('No session token found in URL. Please access via proper session link.');
        }
        
        // Validate token and get session data from API
        console.log('🔑 [SESSION] Validating token:', token);
        const response = await fetch(`/api/session/${token}`);
        
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Invalid or expired session token');
            }
            throw new Error('Unable to validate session. Please try again.');
        }
        
        const sessionData = await response.json();
        console.log('✅ [SESSION] Session data loaded:', sessionData);
        
        // Extract learner session from session data
        const learnerSession = sessionData.learner_session || {
            id: sessionData.id,
            language: sessionData.language || 'fr'
        };
        
        // Initialize the modular FIA application
        await initializeFIAApp(learnerSession, sessionData);
        
        // Generate training plan and load first slide if learner session exists
        if (learnerSession && learnerSession.id) {
            console.log('🎯 [TRAINING] Starting training plan generation for learner session:', learnerSession.id);
            
            // Check if we have training_id
            if (!sessionData?.training_session?.training_id) {
                throw new Error('No training ID available in session data');
            }
            
            // Show progress animation
            document.getElementById('main-content').innerHTML = `
                <div class="text-center p-5">
                    <h3>Generating Your Personalized Training Plan</h3>
                    <div class="progress mt-3" style="height: 25px;">
                        <div id="loading-progress-bar" class="progress-bar progress-bar-striped progress-bar-animated" 
                             role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">
                             0%
                        </div>
                    </div>
                    <p class="mt-3 text-muted">This may take a few moments...</p>
                </div>
            `;
            
            // Start progress animation
            window.fiaApp.progressManager.startProgressAnimation();
            
            try {
                // First, check if a plan already exists (like training_old.html does)
                console.log('🔍 [TRAINING] Checking if training plan already exists...');
                const checkPlanRequest = {
                    training_id: sessionData.training_session.training_id,
                    learner_session_id: learnerSession.id,
                    learner_profile: {
                        experience_level: learnerSession.experience_level,
                        learning_style: learnerSession.learning_style,
                        job_position: learnerSession.job_position,
                        activity_sector: learnerSession.activity_sector,
                        country: learnerSession.country,
                        language: learnerSession.language
                    },
                    force_regenerate: false  // Check existing plan first
                };
                
                console.log('📝 Plan check request:', checkPlanRequest);
                const checkPlanResponse = await fetch('/api/generate-plan-integrated', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(checkPlanRequest)
                });
                
                let planResponse = checkPlanResponse;
                
                if (checkPlanResponse.ok) {
                    console.log('✅ [TRAINING] Existing plan found, using it...');
                } else {
                    // No existing plan found, generate a new one
                    console.log('📝 [TRAINING] No existing plan found, generating new plan...');
                    checkPlanRequest.force_regenerate = true;
                    
                    planResponse = await fetch('/api/generate-plan-integrated', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(checkPlanRequest)
                    });
                }
                
                if (!planResponse.ok) {
                    let errorMessage = 'Failed to handle training plan';
                    try {
                        const errorData = await planResponse.json();
                        if (typeof errorData.detail === 'string') {
                            errorMessage = errorData.detail;
                        } else if (typeof errorData.message === 'string') {
                            errorMessage = errorData.message;
                        } else if (typeof errorData.detail === 'object') {
                            errorMessage = JSON.stringify(errorData.detail);
                        } else {
                            errorMessage = JSON.stringify(errorData);
                        }
                        console.error('❌ [TRAINING] Plan handling error:', errorData);
                    } catch (parseError) {
                        const errorText = await planResponse.text();
                        console.error('❌ [TRAINING] Raw error response:', errorText);
                        errorMessage = `HTTP ${planResponse.status}: ${errorText || errorMessage}`;
                    }
                    throw new Error(errorMessage);
                }
                
                const planData = await planResponse.json();
                console.log('✅ [TRAINING] Training plan generated:', planData);
                
                // Now try to load the current slide
                console.log('📄 [TRAINING] Loading current slide...');
                const slideResponse = await fetch(`/api/slides/session/${learnerSession.id}/current`);
                
                if (slideResponse.ok) {
                    const slideData = await slideResponse.json();
                    console.log('✅ [TRAINING] Current slide loaded:', slideData);
                    
                    // Display the slide content
                    window.fiaApp.displaySlideContent(slideData.data || slideData);
                } else {
                    // If no current slide, try to generate the first one
                    console.log('🎯 [TRAINING] No current slide found, generating first slide...');
                    const firstSlideResponse = await fetch(`/api/slides/generate-first/${learnerSession.id}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    if (firstSlideResponse.ok) {
                        const firstSlideData = await firstSlideResponse.json();
                        console.log('✅ [TRAINING] First slide generated:', firstSlideData);
                        window.fiaApp.displaySlideContent(firstSlideData.data || firstSlideData);
                    } else {
                        let errorMessage = 'Failed to generate first slide';
                        try {
                            const errorData = await firstSlideResponse.json();
                            if (typeof errorData.detail === 'string') {
                                errorMessage = errorData.detail;
                            } else if (typeof errorData.message === 'string') {
                                errorMessage = errorData.message;
                            } else if (typeof errorData.detail === 'object') {
                                errorMessage = JSON.stringify(errorData.detail);
                            } else {
                                errorMessage = JSON.stringify(errorData);
                            }
                            console.error('❌ [TRAINING] First slide generation error:', errorData);
                        } catch (parseError) {
                            const errorText = await firstSlideResponse.text();
                            console.error('❌ [TRAINING] Raw first slide error:', errorText);
                            errorMessage = `HTTP ${firstSlideResponse.status}: ${errorText || errorMessage}`;
                        }
                        throw new Error(errorMessage);
                    }
                }
                
            } catch (error) {
                console.error('❌ [TRAINING] Error in training initialization:', error);
                showErrorWithRetry('Training Generation Failed', `Unable to generate your training plan: ${error.message}`);
            } finally {
                // Stop progress animation
                window.fiaApp.progressManager.stopProgressAnimation();
            }
        } else {
            console.log('⚠️ [TRAINING] No learner session ID, showing default message');
            document.getElementById('main-content').innerHTML = `
                <div class="text-center p-5">
                    <h3>Session Loading...</h3>
                    <p>Please wait while we prepare your training session.</p>
                </div>
            `;
        }
        
        console.log('✅ FIA Training App initialized successfully');
        
    } catch (error) {
        console.error('❌ Failed to initialize FIA Training App:', error);
        showErrorWithRetry('Application Error', `Failed to initialize the training application: ${error.message}`);
    }
}

/**
 * Show error message with retry button
 * @param {string} title - Error title
 * @param {string} message - Error message
 */
function showErrorWithRetry(title, message) {
    const container = document.getElementById('main-content');
    if (container) {
        container.innerHTML = `
            <div class="alert alert-danger m-4">
                <h4>${title}</h4>
                <p>${message}</p>
                <button class="btn btn-primary" id="retry-button">Try Again</button>
            </div>
        `;
        
        // Add event listener for retry button (no inline onclick)
        const retryButton = document.getElementById('retry-button');
        if (retryButton) {
            retryButton.addEventListener('click', () => {
                location.reload();
            });
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeTrainingPage);