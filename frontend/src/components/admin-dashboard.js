/**
 * FIA v3.0 - Admin Dashboard Component
 * Handles admin dashboard functionality and trainers overview
 */

console.log('🔥 ADMIN - admin-dashboard.js chargé à:', new Date().toISOString());

class AdminDashboard {
    constructor() {
        console.log('🔥 ADMIN - AdminDashboard constructor appelé');
        this.init();
    }

    init() {
        console.log('🚀 ADMIN - AdminDashboard.init() démarré');
        
        // Vérifier que authManager existe
        if (typeof authManager === 'undefined') {
            console.error('🚨 ADMIN - authManager non défini !');
            return;
        }
        console.log('✅ ADMIN - authManager trouvé:', authManager);
        
        // Require authentication
        try {
            if (!authManager.requireAuth()) {
                console.log('❌ ADMIN - Authentication échouée, arrêt de init()');
                return;
            }
            console.log('✅ ADMIN - Authentication OK');
        } catch (error) {
            console.error('🚨 ADMIN - Erreur dans requireAuth():', error);
            return;
        }

        // Vérifier les droits admin
        if (!authManager.hasAdminAccess()) {
            console.warn('❌ ADMIN - Accès admin requis, redirection vers trainer.html');
            window.location.href = 'trainer.html';
            return;
        }
        console.log('✅ ADMIN - Droits admin confirmés');

        console.log('🔄 ADMIN - Début loadUserData()');
        this.loadUserData();
        
        console.log('🔄 ADMIN - Configuration des composants...');
        this.setupLogout();
        this.setupProfileModal();
        this.setupTableSorting();
        
        // Charger immédiatement les données du tableau
        console.log('🔄 ADMIN - Chargement tableau trainers...');
        this.loadTrainersOverview();
        
        console.log('✅ ADMIN - AdminDashboard.init() terminé');
    }

    loadUserData() {
        const user = authManager.getUser();
        if (user) {
            const adminNameElement = document.getElementById('admin-name');
            if (adminNameElement) {
                adminNameElement.textContent = `${user.first_name} ${user.last_name}`;
            }

            // Populate profile modal
            this.populateProfileModal(user);
        }
    }

    populateProfileModal(user) {
        const fields = {
            'profile-first-name': user.first_name,
            'profile-last-name': user.last_name,
            'profile-email': user.email
        };

        Object.entries(fields).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.value = value || '';
            }
        });
    }

    setupLogout() {
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                // Admin logout redirects to login.html
                authManager.logout();
                window.location.href = 'login.html';
            });
        }
    }

    setupProfileModal() {
        const saveBtn = document.getElementById('save-profile-btn');
        if (!saveBtn) return;

        saveBtn.addEventListener('click', async () => {
            await this.handleProfileUpdate();
        });
    }

    async handleProfileUpdate() {
        const form = document.getElementById('profile-form');
        const formData = new FormData(form);
        
        const profileData = {
            first_name: formData.get('first_name'),
            last_name: formData.get('last_name')
        };

        try {
            const result = await authManager.updateProfile(profileData);
            
            if (result.success) {
                showAlert('Profile updated successfully!', 'success');
                
                // Refresh user data from updated profile
                await this.refreshUserData();
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('profile-modal'));
                if (modal) modal.hide();
            } else {
                showAlert(result.message || 'Profile update failed.', 'error');
            }

        } catch (error) {
            console.error('Profile update error:', error);
            showAlert('Failed to update profile. Please try again.', 'error');
        }
    }

    async refreshUserData() {
        try {
            const userProfile = await authManager.getUserProfile();
            if (userProfile) {
                authManager.setUser(userProfile);
                this.loadUserData();
            }
        } catch (error) {
            console.error('Failed to refresh user data:', error);
        }
    }

    // ============================================================================
    // TRAINERS OVERVIEW FUNCTIONALITY 
    // ============================================================================

    async loadTrainersOverview(retryCount = 0) {
        console.log('🔥 ADMIN - Loading trainers overview...');
        const tableBody = document.getElementById('trainers-overview-body');
        if (!tableBody) {
            console.error('🚨 ADMIN - Element trainers-overview-body not found!');
            return;
        }
        console.log('✅ ADMIN - Found table body element:', tableBody);

        try {
            // Show loading state
            this.showTrainersLoadingState(tableBody);

            // Fetch trainers overview data
            console.log('📡 ADMIN - Fetching trainers overview data...');
            const trainersData = await apiClient.get('/api/admin/trainers-overview');
            console.log('📊 ADMIN - Received trainers data:', trainersData.length, 'trainers');

            // Validate response data structure
            if (!Array.isArray(trainersData)) {
                throw new Error('Invalid response format: Expected array of trainers');
            }

            if (trainersData.length === 0) {
                this.showTrainersEmptyState(tableBody);
                return;
            }

            // Validate each trainer object has required fields
            const requiredFields = ['id', 'first_name', 'last_name', 'email'];
            for (let i = 0; i < trainersData.length; i++) {
                const trainer = trainersData[i];
                for (const field of requiredFields) {
                    if (!trainer.hasOwnProperty(field)) {
                        console.warn(`Trainer at index ${i} missing required field: ${field}`);
                        trainer[field] = field === 'id' ? `missing-${i}` : 'N/A';
                    }
                }
                
                // Ensure numeric fields are numbers
                const numericFields = [
                    'trainings_with_support', 'trainings_ai_generated', 
                    'active_sessions', 'total_sessions', 'unique_learners',
                    'total_slides_generated', 'average_slides_per_training'
                ];
                numericFields.forEach(field => {
                    if (trainer[field] === null || trainer[field] === undefined) {
                        trainer[field] = 0;
                    }
                });
            }

            // Render trainers data
            const trainersHtml = trainersData.map(trainer => `
                <tr data-trainer-id="${trainer.id}" class="${!trainer.is_active ? 'table-secondary' : ''}">
                    <td>
                        <strong class="${!trainer.is_active ? 'text-muted' : ''}">${this.escapeHtml(trainer.first_name)}</strong>
                    </td>
                    <td>
                        <strong class="${!trainer.is_active ? 'text-muted' : ''}">${this.escapeHtml(trainer.last_name)}</strong>
                    </td>
                    <td>
                        <div class="admin-indicator">
                            <span class="text-muted">${this.escapeHtml(trainer.email)}</span>
                            ${trainer.is_superuser ? '<i class="bi bi-shield-check text-warning ms-1" title="Administrator"></i>' : ''}
                            ${!trainer.is_active ? '<i class="bi bi-pause-circle text-secondary ms-1" title="Inactive"></i>' : ''}
                        </div>
                    </td>
                    <td>
                        <small class="text-muted" title="${this.formatDateFull(trainer.created_at)}">${this.formatDate(trainer.created_at)}</small>
                    </td>
                    <td>
                        <span class="badge bg-primary" title="Non-AI trainings with uploaded files">${this.formatNumber(trainer.trainings_with_support)}</span>
                    </td>
                    <td>
                        <span class="badge bg-success" title="AI-generated trainings">${this.formatNumber(trainer.trainings_ai_generated)}</span>
                    </td>
                    <td>
                        <span class="badge bg-info" title="Currently active sessions">${this.formatNumber(trainer.active_sessions)}</span>
                    </td>
                    <td>
                        <span class="badge bg-secondary" title="All sessions created">${this.formatNumber(trainer.total_sessions)}</span>
                    </td>
                    <td>
                        <span class="badge bg-warning text-dark" title="Unique learners across all sessions">${this.formatNumber(trainer.unique_learners)}</span>
                    </td>
                    <td>
                        <span class="text-muted" title="Total learning time from all learners">${trainer.total_time_all_learners || '0min'}</span>
                    </td>
                    <td>
                        <span class="text-muted" title="Average time spent per slide">${trainer.average_time_per_slide || '0min'}</span>
                    </td>
                    <td>
                        <span class="badge bg-dark" title="Total slides generated across all trainings">${this.formatNumber(trainer.total_slides_generated)}</span>
                    </td>
                    <td>
                        <span class="text-muted" title="Average slides per training">${this.formatDecimal(trainer.average_slides_per_training)}</span>
                    </td>
                </tr>
            `).join('');

            console.log('🎨 ADMIN - Setting trainers HTML:', trainersHtml.length, 'characters');
            tableBody.innerHTML = trainersHtml;
            console.log('✅ ADMIN - Trainers table updated with', trainersData.length, 'trainers');

        } catch (error) {
            console.error('🚨 ADMIN - Failed to load trainers overview:', error);
            
            // Enhanced error handling with specific messaging
            let errorMessage = 'Failed to load trainers overview. Please try again.';
            
            if (error.message.includes('403') || error.message.includes('Forbidden')) {
                errorMessage = 'Access denied: Administrator privileges required to view trainer statistics.';
            } else if (error.message.includes('401') || error.message.includes('Unauthorized')) {
                errorMessage = 'Authentication expired. Please log in again.';
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 2000);
            } else if (error.message.includes('500') || error.message.includes('Internal Server Error')) {
                errorMessage = 'Server error occurred while calculating trainer statistics.';
            } else if (error.message.includes('Network') || error.message.includes('fetch')) {
                errorMessage = 'Network connection error. Please check your internet connection and try again.';
            }
            
            this.showTrainersErrorState(tableBody, errorMessage);
            
            // Log additional context for debugging
            console.error('🚨 ADMIN - Trainers overview error context:', {
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent,
                url: window.location.href,
                error: error.toString(),
                stack: error.stack
            });
        }
    }

    setupTableSorting() {
        const table = document.getElementById('trainers-overview-table');
        if (!table || table.hasAttribute('data-sorting-enabled')) return;

        table.setAttribute('data-sorting-enabled', 'true');
        
        const headers = table.querySelectorAll('th.sortable');
        headers.forEach(header => {
            header.addEventListener('click', () => {
                this.sortTable(header);
            });
            
            // Add hover effect for better UX
            header.style.cursor = 'pointer';
            header.title = `Click to sort by ${header.textContent.trim()}`;
        });
    }

    sortTable(header) {
        const table = header.closest('table');
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const column = header.getAttribute('data-column');
        const currentSort = header.classList.contains('sort-asc') ? 'asc' : 
                           header.classList.contains('sort-desc') ? 'desc' : null;
        
        // Reset all headers
        table.querySelectorAll('th.sortable').forEach(h => {
            h.classList.remove('sort-asc', 'sort-desc');
            const icon = h.querySelector('.sort-icon');
            if (icon) {
                icon.className = 'bi bi-arrow-up-down sort-icon';
            }
        });

        // Determine new sort direction
        let newSort = 'asc';
        if (currentSort === 'asc') newSort = 'desc';
        
        // Update header classes and icon
        header.classList.add(`sort-${newSort}`);
        const icon = header.querySelector('.sort-icon');
        if (icon) {
            icon.className = `bi bi-arrow-${newSort === 'asc' ? 'up' : 'down'} sort-icon text-primary`;
        }
        
        // Sort rows
        rows.sort((a, b) => {
            const aValue = this.getCellValue(a, column);
            const bValue = this.getCellValue(b, column);
            
            let comparison = this.compareValues(aValue, bValue, column);
            return newSort === 'desc' ? -comparison : comparison;
        });
        
        // Reorder DOM
        rows.forEach(row => tbody.appendChild(row));
    }
    
    compareValues(aValue, bValue, column) {
        // Handle empty values
        if (!aValue && !bValue) return 0;
        if (!aValue) return 1;
        if (!bValue) return -1;
        
        // Date columns
        if (column === 'created_at') {
            const aDate = new Date(aValue);
            const bDate = new Date(bValue);
            return aDate - bDate;
        }
        
        // Time duration columns
        if (column === 'total_time_all_learners' || column === 'average_time_per_slide') {
            return this.compareDurations(aValue, bValue);
        }
        
        // Numeric columns
        if (this.isNumeric(aValue) && this.isNumeric(bValue)) {
            return parseFloat(aValue) - parseFloat(bValue);
        }
        
        // String columns (case-insensitive)
        return aValue.toLowerCase().localeCompare(bValue.toLowerCase());
    }
    
    compareDurations(aDuration, bDuration) {
        const parseMinutes = (duration) => {
            if (!duration || duration === '0min') return 0;
            
            let totalMinutes = 0;
            const hourMatch = duration.match(/(\d+)h/);
            const minuteMatch = duration.match(/(\d+)min/);
            
            if (hourMatch) totalMinutes += parseInt(hourMatch[1]) * 60;
            if (minuteMatch) totalMinutes += parseInt(minuteMatch[1]);
            
            return totalMinutes;
        };
        
        return parseMinutes(aDuration) - parseMinutes(bDuration);
    }

    getCellValue(row, column) {
        const cellIndex = Array.from(row.parentNode.parentNode.querySelectorAll('th')).findIndex(th => 
            th.getAttribute('data-column') === column
        );
        
        if (cellIndex === -1) return '';
        
        const cell = row.cells[cellIndex];
        return cell ? cell.textContent.trim() : '';
    }

    isNumeric(str) {
        return !isNaN(str) && !isNaN(parseFloat(str));
    }

    // ============================================================================
    // UTILITY FUNCTIONS
    // ============================================================================

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    formatDateFull(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    formatNumber(value) {
        if (value === null || value === undefined) return '0';
        return Number(value).toLocaleString('en-US');
    }

    formatDecimal(value) {
        if (value === null || value === undefined || value === 0) return '0';
        return Number(value).toFixed(1);
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // ============================================================================
    // TABLE STATE MANAGEMENT
    // ============================================================================

    showTrainersLoadingState(tableBody) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="13" class="text-center text-muted py-5">
                    <div>
                        <div class="spinner-border text-primary mb-3" role="status" style="width: 3rem; height: 3rem;">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mb-1 fw-medium">Loading trainers overview...</p>
                        <small class="text-muted">Fetching trainer statistics and performance data</small>
                        <div class="mt-2">
                            <div class="progress" style="height: 4px; width: 200px; margin: 0 auto;">
                                <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 100%"></div>
                            </div>
                        </div>
                    </div>
                </td>
            </tr>
        `;
    }

    showTrainersEmptyState(tableBody) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="13" class="text-center text-muted py-5">
                    <div>
                        <i class="bi bi-people display-4 mb-3 text-secondary"></i>
                        <h6 class="text-muted mb-2">No Trainers Found</h6>
                        <p class="small mb-3">There are currently no trainers registered in the system.</p>
                        <div class="d-flex gap-2 justify-content-center">
                            <button class="btn btn-sm btn-outline-primary" onclick="refreshTrainersOverview()">
                                <i class="bi bi-arrow-clockwise me-1"></i>
                                Refresh
                            </button>
                        </div>
                    </div>
                </td>
            </tr>
        `;
    }

    showTrainersErrorState(tableBody, errorMessage = 'Failed to load trainers overview') {
        tableBody.innerHTML = `
            <tr>
                <td colspan="13" class="text-center py-5">
                    <div>
                        <i class="bi bi-exclamation-triangle display-4 mb-3 text-warning"></i>
                        <h6 class="text-danger mb-2">Error Loading Data</h6>
                        <p class="text-muted small mb-3">${errorMessage}</p>
                        <div class="d-flex gap-2 justify-content-center">
                            <button class="btn btn-sm btn-outline-primary" onclick="refreshTrainersOverview()">
                                <i class="bi bi-arrow-clockwise me-1"></i>
                                Try Again
                            </button>
                        </div>
                    </div>
                </td>
            </tr>
        `;
    }
}

// Global function to refresh trainers overview
async function refreshTrainersOverview() {
    const refreshBtn = document.querySelector('button[onclick="refreshTrainersOverview()"]');
    
    const originalContent = refreshBtn.innerHTML;
    
    try {
        // Show loading state on button
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = `
            <span class="spinner-border spinner-border-sm me-1" role="status"></span>
            Refreshing...
        `;
        
        if (window.adminDashboard && window.adminDashboard.loadTrainersOverview) {
            await window.adminDashboard.loadTrainersOverview();
        }
    } catch (error) {
        console.error('🚨 ADMIN - Error refreshing trainers overview:', error);
    } finally {
        // Restore button state
        refreshBtn.disabled = false;
        refreshBtn.innerHTML = originalContent;
    }
}

// Initialize when DOM is loaded
console.log('🔥 ADMIN - Ajout du listener DOMContentLoaded');
document.addEventListener('DOMContentLoaded', () => {
    console.log('🌐 ADMIN - DOM chargé, instanciation AdminDashboard');
    console.log('🌐 ADMIN - document.readyState:', document.readyState);
    window.adminDashboard = new AdminDashboard();
});

// Fallback si le DOM est déjà chargé
if (document.readyState === 'loading') {
    console.log('🔥 ADMIN - DOM en cours de chargement, attente DOMContentLoaded');
} else {
    console.log('🔥 ADMIN - DOM déjà chargé, instanciation immédiate');
    window.adminDashboard = new AdminDashboard();
}