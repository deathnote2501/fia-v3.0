/**
 * FIA v3.0 - Session Manager
 * JavaScript functions for training session management
 */

// ============================================================================
// SESSION MANAGEMENT FUNCTIONS
// ============================================================================

/**
 * Create new training session
 * POST to /api/training-sessions
 */
async function createSession() {
    const form = document.getElementById('session-form');
    const submitBtn = document.getElementById('create-session-btn');
    const linkContainer = document.getElementById('session-link-container');
    
    try {
        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Creating...';
        
        // Hide previous link if any
        linkContainer.classList.add('d-none');
        
        // Get form data
        const formData = new FormData(form);
        const sessionData = {
            training_id: formData.get('training_id'),
            name: formData.get('name').trim(),
            description: formData.get('description').trim() || null
        };
        
        // Validate required fields
        if (!sessionData.training_id || !sessionData.name) {
            throw new Error('Please fill in all required fields');
        }
        
        // Log the data being sent
        console.log('Creating session with data:', sessionData);
        
        // Test headers by calling debug endpoint
        console.log('Testing headers with debug endpoint...');
        const debugResult = await apiClient.post('/api/debug-request', sessionData);
        console.log('Debug endpoint shows Content-Type:', debugResult.content_type);
        
        // Make API call
        const result = await apiClient.post('/api/training-sessions', sessionData);
        
        // Display success and session link
        displaySessionLink(result.session_link, result.name);
        
        // Reset form
        form.reset();
        
        // Reload sessions list
        await loadSessions();
        
        // Show success message
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
 * Load trainings for dropdown selection
 * GET from /api/trainings
 */
async function loadTrainings() {
    const select = document.getElementById('session-training');
    
    try {
        // Show loading state
        select.innerHTML = `<option value="">${window.safeT ? window.safeT('status.loadingTrainings') : 'Loading trainings...'}</option>`;
        select.disabled = true;
        
        // Make API call
        const trainings = await apiClient.get('/api/trainings');
        
        // Clear and populate dropdown
        select.innerHTML = '<option value="">Choose a training...</option>';
        
        if (trainings.length === 0) {
            select.innerHTML += '<option value="" disabled>No trainings available - create one first</option>';
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
        showAlert('Failed to load trainings. Please refresh the page.', 'warning');
    } finally {
        select.disabled = false;
    }
}

/**
 * Load existing sessions
 * GET from /api/training-sessions
 */
async function loadSessions() {
    const sessionsList = document.getElementById('sessions-list');
    const tableBody = document.getElementById('sessions-table-body');
    const totalCount = document.getElementById('sessions-total-count');
    
    try {
        // Show loading state
        sessionsList.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="bi bi-hourglass-split"></i>
                Loading sessions...
            </div>
        `;
        
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted py-4">
                    <i class="bi bi-hourglass-split"></i>
                    Loading sessions...
                </td>
            </tr>
        `;
        
        // Make API call
        const sessions = await apiClient.get('/api/training-sessions');
        
        // Update count
        totalCount.textContent = sessions.length;
        
        if (sessions.length === 0) {
            // Show empty state
            sessionsList.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="bi bi-calendar-x display-6"></i>
                    <p class="mt-2 mb-0">No sessions created yet</p>
                    <small>Create your first session using the form</small>
                </div>
            `;
            
            tableBody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-muted py-4">
                        No sessions found
                    </td>
                </tr>
            `;
        } else {
            // Populate sessions list (card view)
            sessionsList.innerHTML = sessions.map(session => `
                <div class="list-group-item">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">${escapeHtml(session.name)}</h6>
                        <small class="text-muted">${formatDate(session.created_at)}</small>
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
            
            // Populate sessions table
            tableBody.innerHTML = sessions.map(session => `
                <tr>
                    <td>
                        <strong>${escapeHtml(session.name)}</strong>
                        ${session.description ? `<br><small class="text-muted">${escapeHtml(session.description)}</small>` : ''}
                    </td>
                    <td>
                        <span class="badge bg-info">Training Info</span>
                    </td>
                    <td>
                        <small>${formatDate(session.created_at)}</small>
                    </td>
                    <td>
                        <span class="badge bg-secondary">0</span>
                    </td>
                    <td>
                        <span class="badge ${session.is_active ? 'bg-success' : 'bg-secondary'}">
                            ${session.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary" onclick="copySessionLink('${session.session_token}')" 
                                    title="Copy session link">
                                <i class="bi bi-link-45deg"></i>
                            </button>
                            <button class="btn btn-outline-danger" onclick="deleteSession('${session.id}')" 
                                    title="Delete session">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');
        }
        
    } catch (error) {
        console.error('Error loading sessions:', error);
        sessionsList.innerHTML = `
            <div class="text-center text-danger py-4">
                <i class="bi bi-exclamation-triangle"></i>
                <p class="mt-2">${window.safeT ? window.safeT('error.loadingSessions') : 'Error loading sessions'}</p>
            </div>
        `;
        showAlert('Failed to load sessions. Please try again.', 'danger');
    }
}

/**
 * Copy session link to clipboard
 * @param {string} token - Session token or full link
 */
async function copySessionLink(token) {
    try {
        // Use relative path to avoid HTTP/HTTPS issues
        const link = token.startsWith('http') ? token : `/session.html?token=${token}`;
        
        // Copy to clipboard
        await navigator.clipboard.writeText(link);
        
        // Show success feedback
        showAlert('Session link copied to clipboard!', 'success', 3000);
        
    } catch (error) {
        console.error('Error copying link:', error);
        
        // Fallback for older browsers
        try {
            const textArea = document.createElement('textarea');
            textArea.value = link;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            
            showAlert('Session link copied to clipboard!', 'success', 3000);
        } catch (fallbackError) {
            showAlert('Failed to copy link. Please copy manually.', 'warning');
        }
    }
}

/**
 * Delete training session
 * DELETE to /api/training-sessions/{id}
 * @param {string} sessionId - Session ID to delete
 */
async function deleteSession(sessionId) {
    if (!confirm('Are you sure you want to delete this session? This action cannot be undone.')) {
        return;
    }
    
    try {
        // Make API call
        await apiClient.request(`/api/training-sessions/${sessionId}`, {
            method: 'DELETE'
        });
        
        // Reload sessions list
        await loadSessions();
        
        // Show success message
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
 * @param {string} link - The session link
 * @param {string} sessionName - Name of the session
 */
function displaySessionLink(link, sessionName) {
    const linkContainer = document.getElementById('session-link-container');
    const linkInput = document.getElementById('session-link');
    const copyBtn = document.getElementById('copy-link-btn');
    
    // Set link value
    linkInput.value = link;
    
    // Show container
    linkContainer.classList.remove('d-none');
    
    // Update copy button handler
    copyBtn.onclick = () => copySessionLink(link);
    
    // Auto-select link for easy copying
    linkInput.focus();
    linkInput.select();
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Format date for display
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
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

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Set up session form submission
    const sessionForm = document.getElementById('session-form');
    if (sessionForm) {
        sessionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            createSession();
        });
    }
    
    // Load trainings when Create Session tab is shown
    const createSessionTab = document.querySelector('a[href="#create-session"]');
    if (createSessionTab) {
        createSessionTab.addEventListener('shown.bs.tab', function() {
            loadTrainings();
            loadSessions();
        });
        
        // Also load on first page load if Create Session tab is active
        if (createSessionTab.classList.contains('active')) {
            loadTrainings();
            loadSessions();
        }
    }
    
    // Load trainings immediately if we're already on create-session tab
    if (window.location.hash === '#create-session' || document.querySelector('#create-session.active')) {
        setTimeout(() => {
            loadTrainings();
            loadSessions();
        }, 100);
    }
});