/**
 * FIA v3.0 - Trainer Dashboard Component
 * Handles trainer dashboard functionality
 */

class TrainerDashboard {
    constructor() {
        this.init();
    }

    init() {
        // Require authentication
        if (!authManager.requireAuth()) return;

        this.loadUserData();
        this.setupLogout();
        this.setupTrainingForm();
        this.setupSessionForm();
        this.setupProfileModal();
        this.loadDashboardData();
    }

    loadUserData() {
        const user = authManager.getUser();
        if (user) {
            const trainerNameElement = document.getElementById('trainer-name');
            if (trainerNameElement) {
                trainerNameElement.textContent = `${user.first_name} ${user.last_name}`;
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
                authManager.logout();
            });
        }
    }

    setupTrainingForm() {
        const trainingForm = document.getElementById('training-form');
        if (!trainingForm) return;

        trainingForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleTrainingSubmission(e.target);
        });
    }

    async handleTrainingSubmission(form) {
        const formData = new FormData(form);
        
        try {
            // Show loading state
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Creating...';

            const response = await apiClient.post('/api/trainings', formData, {
                headers: {
                    // Don't set Content-Type for FormData, browser will set it with boundary
                }
            });

            showAlert('Training created successfully!', 'success');
            form.reset();
            this.loadTrainings(); // Refresh training list

        } catch (error) {
            console.error('Training creation error:', error);
            showAlert('Failed to create training. Please try again.', 'error');
        } finally {
            // Reset button state
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-upload me-2"></i>Create Training';
        }
    }

    setupSessionForm() {
        const sessionForm = document.getElementById('session-form');
        if (!sessionForm) return;

        // Load trainings for session creation
        this.loadTrainings();

        sessionForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleSessionSubmission(e.target);
        });

        // Setup copy link functionality
        const copyBtn = document.getElementById('copy-link-btn');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => {
                const linkInput = document.getElementById('session-link');
                if (linkInput) {
                    linkInput.select();
                    document.execCommand('copy');
                    
                    // Show feedback
                    const icon = copyBtn.querySelector('i');
                    icon.className = 'bi bi-clipboard-check';
                    setTimeout(() => {
                        icon.className = 'bi bi-clipboard';
                    }, 2000);
                }
            });
        }
    }

    async loadTrainings() {
        try {
            const trainings = await apiClient.get('/api/trainings');
            const select = document.getElementById('session-training');
            
            if (select) {
                // Clear existing options except the first one
                select.innerHTML = '<option value="">Choose a training...</option>';
                
                trainings.forEach(training => {
                    const option = document.createElement('option');
                    option.value = training.id;
                    option.textContent = training.name;
                    select.appendChild(option);
                });
            }

        } catch (error) {
            console.error('Failed to load trainings:', error);
        }
    }

    async handleSessionSubmission(form) {
        const formData = new FormData(form);
        const sessionData = {
            training_id: formData.get('training_id'),
            name: formData.get('name'),
            description: formData.get('description')
        };

        try {
            // Show loading state
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generating...';

            const response = await apiClient.post('/api/sessions', sessionData);

            // Show session link
            const linkContainer = document.getElementById('session-link-container');
            const linkInput = document.getElementById('session-link');
            
            if (linkContainer && linkInput && response.session_link) {
                linkInput.value = response.session_link;
                linkContainer.classList.remove('d-none');
            }

            showAlert('Session created successfully!', 'success');
            form.reset();

        } catch (error) {
            console.error('Session creation error:', error);
            showAlert('Failed to create session. Please try again.', 'error');
        } finally {
            // Reset button state
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-calendar-plus me-2"></i>Generate Session Link';
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

    async loadDashboardData() {
        try {
            // Load dashboard statistics
            const stats = await apiClient.get('/api/dashboard/stats');
            
            // Update stat cards
            const statElements = {
                'trainings-count': stats.trainings_count || 0,
                'sessions-count': stats.active_sessions_count || 0,
                'learners-count': stats.total_learners || 0,
                'avg-time': stats.avg_session_time || '0m'
            };

            Object.entries(statElements).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) {
                    element.textContent = value;
                }
            });

            // Load recent activity
            this.loadRecentActivity();

        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        }
    }

    async loadRecentActivity() {
        try {
            const activities = await apiClient.get('/api/dashboard/recent-activity');
            const container = document.getElementById('recent-activity');
            
            if (container) {
                if (activities.length === 0) {
                    container.innerHTML = '<p class="text-muted">No recent activity</p>';
                } else {
                    const activityHtml = activities.map(activity => `
                        <div class="d-flex align-items-center mb-2">
                            <i class="bi bi-${activity.icon} me-3 text-primary"></i>
                            <div>
                                <div class="fw-medium">${activity.title}</div>
                                <small class="text-muted">${activity.timestamp}</small>
                            </div>
                        </div>
                    `).join('');
                    
                    container.innerHTML = activityHtml;
                }
            }

        } catch (error) {
            console.error('Failed to load recent activity:', error);
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new TrainerDashboard();
});