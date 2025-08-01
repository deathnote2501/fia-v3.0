/**
 * FIA v3.0 - Session Manager (Version Simplifiée)
 * Gestion des sessions avec fetch() direct - KISS approach
 */

// ============================================================================
// CONFIGURATION
// ============================================================================

const API_BASE = 'http://localhost:8000';

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
    const token = getAuthToken();
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info', duration = 5000) {
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
        submitBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Creating...';
        
        // Get form data
        const formData = new FormData(form);
        const sessionData = {
            training_id: formData.get('training_id'),
            name: formData.get('name').trim(),
            description: formData.get('description').trim() || null
        };
        
        // Validate
        if (!sessionData.training_id || !sessionData.name) {
            throw new Error('Please fill in all required fields');
        }
        
        // Direct fetch call
        const response = await fetch(`${API_BASE}/api/training-sessions`, {
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
        showAlert('Session created successfully!', 'success');
        
    } catch (error) {
        console.error('Error creating session:', error);
        showAlert(error.message, 'danger');
    } finally {
        // Re-enable submit button
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-calendar-plus me-2"></i>Generate Session Link';
    }
}

/**
 * Load trainings for dropdown
 */
async function loadTrainings() {
    const select = document.getElementById('session-training');
    
    try {
        select.disabled = true;
        select.innerHTML = '<option value="">Loading trainings...</option>';
        
        const response = await fetch(`${API_BASE}/api/trainings`, {
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const trainings = await response.json();
        
        // Populate dropdown
        select.innerHTML = '<option value="">Choose a training...</option>';
        
        if (trainings.length === 0) {
            select.innerHTML += '<option value="" disabled>No trainings available</option>';
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
        select.innerHTML = '<option value="">Error loading trainings</option>';
        showAlert('Failed to load trainings', 'warning');
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
        tableBody.innerHTML = '<tr><td colspan="6" class="text-center py-4">Loading...</td></tr>';
        
        // Build query parameters for date filtering
        let url = `${API_BASE}/api/training-sessions`;
        const params = new URLSearchParams();
        if (dateFrom) params.append('date_from', dateFrom);
        if (dateTo) params.append('date_to', dateTo);
        if (params.toString()) url += '?' + params.toString();
        
        const response = await fetch(url, {
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const sessions = await response.json();
        
        // Sort sessions by created_at DESC (most recent first)
        sessions.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        
        if (sessions.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="6" class="text-center py-4">No sessions found</td></tr>';
        } else {            
            // Populate table view
            tableBody.innerHTML = sessions.map(session => `
                <tr>
                    <td><strong>${escapeHtml(session.name)}</strong></td>
                    <td><span class="badge bg-info">Training</span></td>
                    <td><small>${formatDate(session.created_at)}</small></td>
                    <td><span class="badge bg-secondary">0</span></td>
                    <td><span class="badge ${session.is_active ? 'bg-success' : 'bg-secondary'}">${session.is_active ? 'Active' : 'Inactive'}</span></td>
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
        sessionsList.innerHTML = '<div class="text-center text-danger py-4"><i class="bi bi-exclamation-triangle"></i><p class="mt-2">Error loading sessions</p></div>';
        showAlert('Failed to load sessions', 'danger');
    }
}

/**
 * Copy session link to clipboard
 */
async function copySessionLink(token) {
    try {
        const link = `${window.location.origin}/frontend/public/training.html?token=${token}`;
        await navigator.clipboard.writeText(link);
        showAlert('Session link copied to clipboard!', 'success', 3000);
    } catch (error) {
        console.error('Error copying link:', error);
        showAlert('Failed to copy link', 'warning');
    }
}

/**
 * Delete training session
 */
async function deleteSession(sessionId) {
    if (!confirm('Are you sure you want to delete this session?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/training-sessions/${sessionId}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }
        
        await loadSessions();
        showAlert('Session deleted successfully', 'success');
        
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
        showAlert('Please select at least one date to filter', 'warning');
        return;
    }
    
    loadSessions(dateFrom, dateTo);
}

/**
 * Show chat history modal for a session
 */
async function showChatHistory(sessionId, sessionName) {
    const modal = new bootstrap.Modal(document.getElementById('chat-history-modal'));
    const content = document.getElementById('chat-history-content');
    const modalTitle = document.querySelector('#chat-history-modal .modal-title');
    
    // Update modal title
    modalTitle.innerHTML = `<i class="bi bi-chat-dots me-2"></i>Conversation History - ${escapeHtml(sessionName)}`;
    
    // Show loading state
    content.innerHTML = `
        <div class="text-center text-muted py-4">
            <i class="bi bi-hourglass-split display-6"></i>
            <p class="mt-2">Loading conversation history...</p>
        </div>
    `;
    
    modal.show();
    
    try {
        const response = await fetch(`${API_BASE}/api/dashboard/chat-history/${sessionId}`, {
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const chatHistory = await response.json();
        
        if (chatHistory.length === 0) {
            content.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="bi bi-chat-x display-6"></i>
                    <p class="mt-2">No conversations found for this session</p>
                    <small>Learners haven't started chatting yet</small>
                </div>
            `;
            return;
        }
        
        // Group messages by learner
        const messagesByLearner = {};
        chatHistory.forEach(msg => {
            if (!messagesByLearner[msg.learner_email]) {
                messagesByLearner[msg.learner_email] = [];
            }
            messagesByLearner[msg.learner_email].push(msg);
        });
        
        // Render messages
        let html = '';
        Object.keys(messagesByLearner).forEach(learnerEmail => {
            const messages = messagesByLearner[learnerEmail];
            html += `
                <div class="mb-4">
                    <h6 class="text-primary border-bottom pb-2">
                        <i class="bi bi-person me-2"></i>
                        ${escapeHtml(learnerEmail)}
                        <small class="text-muted">(${messages.length} messages)</small>
                    </h6>
            `;
            
            messages.forEach(msg => {
                html += `
                    <div class="mb-3">
                        <div class="card border-start border-primary border-3">
                            <div class="card-body py-2">
                                <div class="row">
                                    <div class="col-md-6">
                                        <small class="text-muted fw-bold">Learner Question:</small>
                                        <p class="mb-1">${escapeHtml(msg.learner_message || 'No message')}</p>
                                    </div>
                                    <div class="col-md-6">
                                        <small class="text-muted fw-bold">AI Response:</small>
                                        <p class="mb-1">${escapeHtml(msg.ai_response || 'No response')}</p>
                                    </div>
                                </div>
                                <small class="text-muted">
                                    <i class="bi bi-clock me-1"></i>
                                    ${msg.created_at || 'Unknown time'}
                                </small>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
        });
        
        content.innerHTML = html;
        
    } catch (error) {
        console.error('Failed to load chat history:', error);
        content.innerHTML = `
            <div class="text-center text-danger py-4">
                <i class="bi bi-exclamation-triangle display-6"></i>
                <p class="mt-2">Failed to load conversation history</p>
                <small>Please try again later</small>
            </div>
        `;
    }
}