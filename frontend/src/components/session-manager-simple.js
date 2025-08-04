/**
 * FIA v3.0 - Session Manager (Version Simplifiée)
 * Gestion des sessions avec fetch() direct - KISS approach
 */

// ============================================================================
// CONFIGURATION
// ============================================================================

// Use relative URLs - no need for CORS since frontend and API are on same server
const API_BASE = '';

// Note: Now using window.buildSecureApiUrl() from api.js for HTTPS compatibility
// The local buildApiUrl() function has been removed to avoid conflicts

// ============================================================================
// UTILITAIRES
// ============================================================================

/**
 * Get auth token from localStorage
 */
function getAuthToken() {
    return localStorage.getItem('fia_auth_token');
}

/**
 * Get default headers for authenticated requests
 */
function getAuthHeaders() {
    // Use global authManager if available for better token validation
    if (window.authManager && window.authManager.isAuthenticated()) {
        return {
            'Content-Type': 'application/json',
            ...window.authManager.getAuthHeader()
        };
    }
    
    // Fallback to direct localStorage access
    const token = getAuthToken();
    if (!token) {
        console.error('❌ [AUTH] No authentication token found');
        throw new Error('Authentication required');
    }
    
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

/**
 * Show alert message - Enhanced with ErrorManager integration
 */
function showAlert(message, type = 'info', duration = 5000) {
    // Try to use global ErrorManager if available
    if (window.errorManager) {
        return window.errorManager.showMessage(message, type, { duration });
    }

    // Fallback to legacy implementation
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertContainer.innerHTML = alertHtml;
    
    if (duration > 0) {
        setTimeout(() => {
            const alert = alertContainer.querySelector('.alert');
            if (alert) {
                alert.remove();
            }
        }, duration);
    }
}

// ============================================================================
// API FUNCTIONS
// ============================================================================

/**
 * Create new training session
 */
async function createSession() {
    const form = document.getElementById('session-form');
    const submitBtn = document.getElementById('create-session-btn');
    
    try {
        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<i class="bi bi-hourglass-split me-2"></i>${window.safeT ? window.safeT('status.creating') : 'Creating...'}`;
        
        // Get form data
        const formData = new FormData(form);
        const sessionData = {
            training_id: formData.get('training_id'),
            name: formData.get('name').trim(),
            description: formData.get('description').trim() || null
        };
        
        // Validate
        if (!sessionData.training_id || !sessionData.name) {
            throw new Error(window.safeT ? window.safeT('validation.requiredFields') : 'Please fill in all required fields');
        }
        
        // Direct fetch call with HTTPS-safe URL
        const sessionApiUrl = window.buildSecureApiUrl ? window.buildSecureApiUrl('/api/training-sessions') : '/api/training-sessions';
        console.log('🔧 [DEBUG] Session API URL generated:', sessionApiUrl);
        
        const response = await fetch(sessionApiUrl, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(sessionData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }
        
        const result = await response.json();
        
        // Show success
        displaySessionLink(result.session_link, result.name);
        form.reset();
        await loadSessions();
        showAlert(window.safeT ? window.safeT('success.created') : 'Session created successfully!', 'success');
        
    } catch (error) {
        console.error('Error creating session:', error);
        showAlert(error.message, 'danger');
    } finally {
        // Re-enable submit button
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i class="bi bi-calendar-plus me-2"></i>${window.safeT ? window.safeT('session.generateLink') : 'Generate Session Link'}`;
    }
}

/**
 * Load trainings for dropdown
 */
async function loadTrainings() {
    const select = document.getElementById('session-training');
    
    try {
        select.disabled = true;
        select.innerHTML = `<option value="">${window.safeT ? window.safeT('status.loadingTrainings') : 'Loading trainings...'}</option>`;
        
        console.log('🔧 [DEBUG] window.buildSecureApiUrl available:', !!window.buildSecureApiUrl);
        console.log('🔧 [DEBUG] typeof window.buildSecureApiUrl:', typeof window.buildSecureApiUrl);
        
        // FORCE buildSecureApiUrl - throw error if not available
        if (!window.buildSecureApiUrl) {
            throw new Error('❌ buildSecureApiUrl not available! This is the root cause of Mixed Content error.');
        }
        
        const apiUrl = window.buildSecureApiUrl('/api/trainings');
        console.log('🔧 [DEBUG] API URL generated:', apiUrl);
        console.log('🔧 [DEBUG] Current protocol:', window.location.protocol);
        console.log('🔧 [DEBUG] Current hostname:', window.location.hostname);
        
        // CRITICAL: Force HTTPS even if URL got corrupted by browser/server
        const secureApiUrl = apiUrl.replace(/^http:/, 'https:');
        if (secureApiUrl !== apiUrl) {
            console.log('🚨 [FORCE_HTTPS] session-manager-simple.js corrected:', apiUrl, '→', secureApiUrl);
        }
        
        const response = await fetch(secureApiUrl, {
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const trainings = await response.json();
        
        // Populate dropdown
        select.innerHTML = `<option value="">${window.safeT ? window.safeT('session.chooseTraining') : 'Choose a training...'}</option>`;
        
        if (trainings.length === 0) {
            select.innerHTML += `<option value="" disabled>${window.safeT ? window.safeT('session.noTrainings') : 'No trainings available'}</option>`;
        } else {
            trainings.forEach(training => {
                const option = document.createElement('option');
                option.value = training.id;
                option.textContent = `${training.name} (${training.file_type.toUpperCase()})`;
                select.appendChild(option);
            });
        }
        
    } catch (error) {
        console.error('Error loading trainings:', error);
        select.innerHTML = `<option value="">${window.safeT ? window.safeT('error.loadingTrainings') : 'Error loading trainings'}</option>`;
        showAlert(window.safeT ? window.safeT('error.loadingTrainings') : 'Failed to load trainings', 'warning');
    } finally {
        select.disabled = false;
    }
}

/**
 * Load existing sessions
 */
async function loadSessions(dateFrom = '', dateTo = '') {
    const tableBody = document.getElementById('sessions-table-body');
    
    try {
        // Show loading
        tableBody.innerHTML = `<tr><td colspan="5" class="text-center py-4">${window.safeT ? window.safeT('status.loadingGeneric') : 'Loading...'}</td></tr>`;
        
        // Build query parameters for date filtering
        let endpoint = '/api/training-sessions';
        const params = new URLSearchParams();
        if (dateFrom) params.append('date_from', dateFrom);
        if (dateTo) params.append('date_to', dateTo);
        if (params.toString()) endpoint += '?' + params.toString();
        
        const secureUrl = window.buildSecureApiUrl ? window.buildSecureApiUrl(endpoint) : endpoint;
        console.log('🔧 [DEBUG] Download API URL:', secureUrl);
        
        // CRITICAL: Force HTTPS even if URL got corrupted by browser/server
        const finalSecureUrl = secureUrl.replace(/^http:/, 'https:');
        if (finalSecureUrl !== secureUrl) {
            console.log('🚨 [FORCE_HTTPS] session-manager-simple.js loadSessions corrected:', secureUrl, '→', finalSecureUrl);
        }
        
        const response = await fetch(finalSecureUrl, {
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const sessions = await response.json();
        
        // Sort sessions by created_at DESC (most recent first)
        sessions.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        
        if (sessions.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="5" class="text-center py-4">${window.safeT ? window.safeT('session.noSessions') : 'No sessions found'}</td></tr>`;
        } else {            
            // Populate table view
            tableBody.innerHTML = sessions.map(session => `
                <tr>
                    <td><strong>${escapeHtml(session.name)}</strong></td>
                    <td><span class="badge ${session.training_is_ai_generated ? 'bg-primary' : 'bg-info'}">${session.training_is_ai_generated ? 'AI' : 'Human'}</span></td>
                    <td><small>${formatDate(session.created_at)}</small></td>
                    <td><span class="badge ${session.is_active ? 'bg-success' : 'bg-secondary'}">${session.is_active ? (window.safeT ? window.safeT('status.active') : 'Active') : (window.safeT ? window.safeT('status.inactive') : 'Inactive')}</span></td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary" onclick="copySessionLink('${session.session_token}')" title="Copy session link">
                                <i class="bi bi-link-45deg"></i>
                            </button>
                            <button class="btn btn-outline-info" onclick="showChatHistory('${session.id}', '${escapeHtml(session.name)}')" title="View conversation history">
                                <i class="bi bi-chat-dots"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');
        }
        
    } catch (error) {
        console.error('Error loading sessions:', error);
        sessionsList.innerHTML = `<div class="text-center text-danger py-4"><i class="bi bi-exclamation-triangle"></i><p class="mt-2">${window.safeT ? window.safeT('error.loadingSessions') : 'Error loading sessions'}</p></div>`;
        showAlert(window.safeT ? window.safeT('error.loadingSessions') : 'Failed to load sessions', 'danger');
    }
}

/**
 * Copy session link to clipboard
 */
async function copySessionLink(token) {
    try {
        // Build complete URL with current domain (works for localhost and Railway)
        const baseUrl = `${window.location.protocol}//${window.location.host}`;
        const link = `${baseUrl}/frontend/public/training.html?token=${token}`;
        await navigator.clipboard.writeText(link);
        showAlert(window.safeT ? window.safeT('success.linkCopied') : 'Session link copied to clipboard!', 'success', 3000);
    } catch (error) {
        console.error('Error copying link:', error);
        showAlert(window.safeT ? window.safeT('error.copyFailed') : 'Failed to copy link', 'warning');
    }
}

/**
 * Delete training session
 */
async function deleteSession(sessionId) {
    if (!confirm(window.safeT ? window.safeT('confirm.deleteSession') : 'Are you sure you want to delete this session?')) {
        return;
    }
    
    try {
        const deleteUrl = window.buildSecureApiUrl ? window.buildSecureApiUrl(`/api/training-sessions/${sessionId}`) : `/api/training-sessions/${sessionId}`;
        console.log('🔧 [DEBUG] Delete session URL:', deleteUrl);
        const response = await fetch(deleteUrl, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }
        
        await loadSessions();
        showAlert(window.safeT ? window.safeT('success.deleted') : 'Session deleted successfully', 'success');
        
    } catch (error) {
        console.error('Error deleting session:', error);
        showAlert(error.message, 'danger');
    }
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Display generated session link
 */
function displaySessionLink(link, sessionName) {
    const linkContainer = document.getElementById('session-link-container');
    const linkInput = document.getElementById('session-link');
    const copyBtn = document.getElementById('copy-link-btn');
    
    linkInput.value = link;
    linkContainer.classList.remove('d-none');
    
    copyBtn.onclick = () => copySessionLink(link.split('=')[1]); // Extract token
    
    linkInput.focus();
    linkInput.select();
}

/**
 * Escape HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Format date
 */
function formatDate(dateString) {
    // Use global localized date formatting if available
    if (window.formatLocalizedDateTime) {
        return window.formatLocalizedDateTime(dateString);
    }
    
    // Fallback to English format
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Set up session form
    const sessionForm = document.getElementById('session-form');
    if (sessionForm) {
        sessionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            createSession();
        });
    }
    
    // Set up date filter
    const filterDatesBtn = document.getElementById('filter-dates');
    if (filterDatesBtn) {
        filterDatesBtn.addEventListener('click', function() {
            applyDateFilter();
        });
    }
    
    // Set up clear filter
    const clearFilterBtn = document.getElementById('clear-filter');
    if (clearFilterBtn) {
        clearFilterBtn.addEventListener('click', function() {
            clearDateFilter();
        });
    }
    
    // Load data when Create Session tab is shown
    const createSessionTab = document.querySelector('a[href="#create-session"]');
    if (createSessionTab) {
        createSessionTab.addEventListener('shown.bs.tab', function() {
            loadTrainings();
            loadSessions();
        });
        
        // Load immediately if tab is already active
        if (createSessionTab.classList.contains('active')) {
            setTimeout(() => {
                loadTrainings();
                loadSessions();
            }, 100);
        }
    }
});

// ============================================================================
// NEW FUNCTIONS FOR SESSION IMPROVEMENTS
// ============================================================================

/**
 * Apply date filter to sessions table
 */
function applyDateFilter() {
    const dateFrom = document.getElementById('date-from').value;
    const dateTo = document.getElementById('date-to').value;
    
    if (!dateFrom && !dateTo) {
        showAlert(window.safeT ? window.safeT('validation.selectDate') : 'Please select at least one date to filter', 'warning');
        return;
    }
    
    loadSessions(dateFrom, dateTo);
}

/**
 * Clear date filter and reload all sessions
 */
function clearDateFilter() {
    // Clear date inputs
    document.getElementById('date-from').value = '';
    document.getElementById('date-to').value = '';
    
    // Reload all sessions without filter
    loadSessions();
}

/**
 * Show chat history modal for a session
 */
async function showChatHistory(sessionId, sessionName) {
    console.log(`🔍 [DEBUG] showChatHistory called with sessionId: ${sessionId}, sessionName: ${sessionName}`);
    
    const modal = new bootstrap.Modal(document.getElementById('chat-history-modal'));
    const content = document.getElementById('chat-history-content');
    const modalTitle = document.querySelector('#chat-history-modal .modal-title');
    
    // Update modal title without session name
    modalTitle.innerHTML = `<i class="bi bi-chat-dots me-2"></i>Conversation History`;
    console.log(`📝 [DEBUG] Modal title set to: Conversation History - ${sessionName}`);
    
    // Show loading state
    content.innerHTML = `
        <div class="text-center text-muted py-4">
            <i class="bi bi-hourglass-split display-6"></i>
            <p class="mt-2">${window.safeT ? window.safeT('status.loadingGeneric') : 'Loading conversation history...'}</p>
        </div>
    `;
    
    modal.show();
    console.log(`🖥️ [DEBUG] Modal displayed, loading chat history for session: ${sessionId}`);
    
    try {
        // Check authentication before making API call
        if (window.authManager && !window.authManager.isAuthenticated()) {
            console.error('❌ [DEBUG] User not authenticated');
            throw new Error('Authentication required. Please log in again.');
        }
        
        const endpoint = `/api/dashboard/chat-history/${sessionId}`;
        const url = window.buildSecureApiUrl ? window.buildSecureApiUrl(endpoint) : endpoint;
        console.log(`🌐 [DEBUG] Making API call to: ${url}`);
        console.log(`🔐 [DEBUG] Auth token exists: ${!!getAuthToken()}`);
        
        const headers = getAuthHeaders();
        console.log(`🔐 [DEBUG] Using headers:`, Object.keys(headers));
        
        const response = await fetch(url, {
            headers: headers
        });
        
        console.log(`📡 [DEBUG] API response status: ${response.status} ${response.statusText}`);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error(`❌ [DEBUG] API error response: ${errorText}`);
            
            if (response.status === 401) {
                console.error('❌ [DEBUG] Authentication failed - token may be expired');
                if (window.authManager) {
                    window.authManager.clearToken();
                    window.location.href = '/frontend/public/login.html';
                }
                throw new Error('Authentication expired. Please log in again.');
            }
            
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        
        const chatHistory = await response.json();
        console.log(`📊 [DEBUG] Received ${chatHistory.length} chat messages`);
        
        if (chatHistory.length === 0) {
            console.log(`ℹ️ [DEBUG] No conversations found for session ${sessionId}`);
            content.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="bi bi-chat-x display-6"></i>
                    <p class="mt-2">${window.safeT ? window.safeT('session.noConversations') : 'No conversations found for this session'}</p>
                    <small>${window.safeT ? window.safeT('session.noChats') : "Learners haven't started chatting yet"}</small>
                </div>
            `;
            return;
        }
        
        // Group messages by learner
        const messagesByLearner = {};
        chatHistory.forEach(msg => {
            console.log(`💬 [DEBUG] Processing message from: ${msg.learner_email}`);
            if (!messagesByLearner[msg.learner_email]) {
                messagesByLearner[msg.learner_email] = [];
            }
            messagesByLearner[msg.learner_email].push(msg);
        });
        
        // Render messages in simple table format
        let html = `
            <div class="table-responsive">
                <table class="table table-borderless">
                    <tbody>
        `;
        
        // Flatten all messages and sort by timestamp
        const allMessages = [];
        Object.keys(messagesByLearner).forEach(learnerEmail => {
            const messages = messagesByLearner[learnerEmail];
            console.log(`👤 [DEBUG] Processing ${messages.length} messages for learner: ${learnerEmail}`);
            
            messages.forEach((msg, index) => {
                console.log(`📝 [DEBUG] Message ${index + 1}: "${msg.learner_message?.substring(0, 50)}..." (type: ${msg.message_type})`);
                
                // Use message_type from database: 'question' = Learner, 'answer' = AI
                const messageType = msg.message_type === 'question' ? 'Learner' : 'AI';
                const displayMessage = msg.learner_message || msg.ai_response || 'No message';
                
                allMessages.push({
                    type: messageType,
                    message: displayMessage,
                    email: learnerEmail,
                    timestamp: msg.created_at
                });
            });
        });
        
        // Sort messages by timestamp (if available)
        allMessages.sort((a, b) => {
            if (!a.timestamp || !b.timestamp) return 0;
            return new Date(a.timestamp) - new Date(b.timestamp);
        });
        
        // Render each message as a table row
        allMessages.forEach((msg, index) => {
            html += `
                <tr>
                    <td width="80" class="text-muted fw-bold align-top">${msg.type}:</td>
                    <td class="align-top">${escapeHtml(msg.message)}</td>
                </tr>
                ${index < allMessages.length - 1 ? '<tr><td colspan="2"><hr class="my-2"></td></tr>' : ''}
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        console.log(`✅ [DEBUG] Rendering complete HTML for chat history`);
        content.innerHTML = html;
        
    } catch (error) {
        console.error('❌ [ERROR] Failed to load chat history:', error);
        content.innerHTML = `
            <div class="text-center text-danger py-4">
                <i class="bi bi-exclamation-triangle display-6"></i>
                <p class="mt-2">${window.safeT ? window.safeT('error.loadingData') : 'Failed to load conversation history'}</p>
                <small>Error: ${error.message}</small>
            </div>
        `;
    }
}