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
async function loadSessions() {
    const sessionsList = document.getElementById('sessions-list');
    const tableBody = document.getElementById('sessions-table-body');
    const totalCount = document.getElementById('sessions-total-count');
    
    try {
        // Show loading
        sessionsList.innerHTML = '<div class="text-center py-4"><i class="bi bi-hourglass-split"></i> Loading...</div>';
        tableBody.innerHTML = '<tr><td colspan="6" class="text-center py-4">Loading...</td></tr>';
        
        const response = await fetch(`${API_BASE}/api/training-sessions`, {
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const sessions = await response.json();
        
        // Update count
        totalCount.textContent = sessions.length;
        
        if (sessions.length === 0) {
            sessionsList.innerHTML = '<div class="text-center py-4"><i class="bi bi-calendar-x display-6"></i><p class="mt-2">No sessions created yet</p></div>';
            tableBody.innerHTML = '<tr><td colspan="6" class="text-center py-4">No sessions found</td></tr>';
        } else {
            // Populate list view
            sessionsList.innerHTML = sessions.map(session => `
                <div class="list-group-item">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">${escapeHtml(session.name)}</h6>
                        <small>${formatDate(session.created_at)}</small>
                    </div>
                    <p class="mb-1 text-muted small">${session.description || 'No description'}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="badge ${session.is_active ? 'bg-success' : 'bg-secondary'}">
                            ${session.is_active ? 'Active' : 'Inactive'}
                        </span>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteSession('${session.id}')">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            `).join('');
            
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
                            <button class="btn btn-outline-primary" onclick="copySessionLink('${session.session_token}')" title="Copy link">
                                <i class="bi bi-link-45deg"></i>
                            </button>
                            <button class="btn btn-outline-danger" onclick="deleteSession('${session.id}')" title="Delete">
                                <i class="bi bi-trash"></i>
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
        const link = `${window.location.origin}/frontend/public/session.html?token=${token}`;
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