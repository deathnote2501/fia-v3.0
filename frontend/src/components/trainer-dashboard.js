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
        // this.setupSessionForm(); // Disabled - handled by session-manager.js
        this.setupProfileModal();
        this.setupFileUpload();
        this.loadDashboardData();
        this.loadTrainings();
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
        const submitBtn = form.querySelector('button[type="submit"]');
        const progressContainer = document.getElementById('upload-progress');
        const progressBar = progressContainer.querySelector('.progress-bar');
        const statusDiv = document.getElementById('upload-status');

        try {
            // Validate form data
            const file = formData.get('file');
            if (!file || file.size === 0) {
                showAlert('Please select a file to upload.', 'error');
                return;
            }

            // Show loading state
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Uploading...';
            
            // Show progress bar
            progressContainer.classList.remove('d-none');
            progressBar.style.width = '0%';
            progressBar.setAttribute('aria-valuenow', '0');
            statusDiv.textContent = 'Preparing upload...';

            // Create XMLHttpRequest for upload progress
            const xhr = new XMLHttpRequest();
            const uploadPromise = new Promise((resolve, reject) => {
                
                // Track upload progress
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const percentComplete = Math.round((e.loaded / e.total) * 100);
                        progressBar.style.width = percentComplete + '%';
                        progressBar.setAttribute('aria-valuenow', percentComplete);
                        statusDiv.textContent = `Uploading... ${percentComplete}%`;
                    }
                });

                // Handle completion
                xhr.addEventListener('load', () => {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        progressBar.style.width = '100%';
                        progressBar.setAttribute('aria-valuenow', '100');
                        statusDiv.textContent = 'Upload complete!';
                        resolve(JSON.parse(xhr.responseText));
                    } else {
                        reject(new Error(`Upload failed: ${xhr.status} ${xhr.statusText}`));
                    }
                });

                // Handle errors
                xhr.addEventListener('error', () => {
                    reject(new Error('Upload failed: Network error'));
                });

                // Setup request
                const token = authManager.getToken();
                xhr.open('POST', `${apiClient.baseURL}/api/trainings/`);
                xhr.setRequestHeader('Authorization', `Bearer ${token}`);
                
                // Send data
                xhr.send(formData);
            });

            const response = await uploadPromise;

            showAlert('Training created successfully!', 'success');
            
            // Reset form and file info
            form.reset();
            document.getElementById('file-info').classList.add('d-none');
            
            // Refresh training list
            this.loadTrainings();

        } catch (error) {
            console.error('Training creation error:', error);
            
            let errorMessage = 'Failed to create training. Please try again.';
            if (error.message.includes('413')) {
                errorMessage = 'File too large. Maximum size is 50MB.';
            } else if (error.message.includes('400')) {
                errorMessage = 'Invalid file type. Please use PDF, PPT, or PPTX files only.';
            } else if (error.message.includes('401')) {
                errorMessage = 'Session expired. Please login again.';
                authManager.logout();
                return;
            }
            
            showAlert(errorMessage, 'error');
            statusDiv.textContent = 'Upload failed';
        } finally {
            // Reset button state
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-upload me-2"></i>Create Training';
            
            // Hide progress bar after delay
            setTimeout(() => {
                progressContainer.classList.add('d-none');
                statusDiv.textContent = '';
            }, 3000);
        }
    }

    setupSessionForm() {
        const sessionForm = document.getElementById('session-form');
        if (!sessionForm) return;

        // Load trainings for session creation
        this.loadTrainingsForSession();

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

    async loadTrainingsForSession() {
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

    setupFileUpload() {
        const fileInput = document.getElementById('training-file');
        if (!fileInput) return;

        fileInput.addEventListener('change', (e) => {
            this.handleFileSelection(e.target);
        });
    }

    handleFileSelection(fileInput) {
        const file = fileInput.files[0];
        const fileInfo = document.getElementById('file-info');
        const fileName = document.getElementById('file-name');
        const fileSize = document.getElementById('file-size');

        if (!file) {
            fileInfo.classList.add('d-none');
            return;
        }

        // Validate file type
        const allowedTypes = ['application/pdf', 'application/vnd.ms-powerpoint', 
                             'application/vnd.openxmlformats-officedocument.presentationml.presentation'];
        
        if (!allowedTypes.includes(file.type) && !file.name.match(/\.(pdf|ppt|pptx)$/i)) {
            showAlert('Invalid file type. Please select a PDF, PPT, or PPTX file.', 'error');
            fileInput.value = '';
            fileInfo.classList.add('d-none');
            return;
        }

        // Validate file size (50MB = 50 * 1024 * 1024 bytes)
        const maxSize = 50 * 1024 * 1024;
        if (file.size > maxSize) {
            showAlert('File too large. Maximum size is 50MB.', 'error');
            fileInput.value = '';
            fileInfo.classList.add('d-none');
            return;
        }

        // Display file info
        fileName.textContent = file.name;
        fileSize.textContent = this.formatFileSize(file.size);
        fileInfo.classList.remove('d-none');
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    async loadTrainings() {
        const container = document.getElementById('trainings-list');
        if (!container) return;

        try {
            // Show loading state
            container.innerHTML = `
                <div class="text-center text-muted py-3">
                    <i class="bi bi-hourglass-split display-6"></i>
                    <p class="mt-2">Loading trainings...</p>
                </div>
            `;

            const trainings = await apiClient.get('/api/trainings/');

            if (trainings.length === 0) {
                container.innerHTML = `
                    <div class="text-center text-muted py-4">
                        <i class="bi bi-book display-6"></i>
                        <p class="mt-2">No trainings yet</p>
                        <p class="small">Create your first training to get started!</p>
                    </div>
                `;
                return;
            }

            // Render trainings list
            const trainingsHtml = trainings.map(training => `
                <div class="card mb-3">
                    <div class="card-body">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <h6 class="card-title mb-1">${training.name}</h6>
                                <p class="card-text text-muted small mb-2">${training.description || 'No description'}</p>
                                <div class="d-flex align-items-center text-muted small">
                                    <i class="bi bi-file-earmark me-1"></i>
                                    <span class="me-3">${training.file_name || 'No file'}</span>
                                    ${training.file_size ? `<span class="badge bg-secondary me-3">${this.formatFileSize(training.file_size)}</span>` : ''}
                                    <i class="bi bi-calendar me-1"></i>
                                    <span>${new Date(training.created_at).toLocaleDateString()}</span>
                                </div>
                            </div>
                            <div class="col-md-4 text-end">
                                ${training.file_path ? `
                                    <button class="btn btn-outline-primary btn-sm me-2" 
                                            onclick="downloadTraining('${training.id}', '${training.file_name}')">
                                        <i class="bi bi-download me-1"></i>
                                        Download
                                    </button>
                                ` : ''}
                                <button class="btn btn-outline-danger btn-sm" 
                                        onclick="deleteTraining('${training.id}', '${training.name}')">
                                    <i class="bi bi-trash me-1"></i>
                                    Delete
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');

            container.innerHTML = trainingsHtml;

        } catch (error) {
            console.error('Failed to load trainings:', error);
            container.innerHTML = `
                <div class="text-center text-danger py-3">
                    <i class="bi bi-exclamation-triangle display-6"></i>
                    <p class="mt-2">Failed to load trainings</p>
                    <button class="btn btn-sm btn-outline-primary" onclick="loadTrainings()">
                        <i class="bi bi-arrow-clockwise me-1"></i>
                        Try Again
                    </button>
                </div>
            `;
        }
    }
}

// Global functions for training management
async function downloadTraining(trainingId, fileName) {
    try {
        const token = authManager.getToken();
        if (!token) {
            showAlert('Please login to download files.', 'error');
            return;
        }

        // Create download link
        const downloadUrl = `${apiClient.baseURL}/api/trainings/${trainingId}/download`;
        
        const response = await fetch(downloadUrl, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                showAlert('Session expired. Please login again.', 'error');
                authManager.logout();
                return;
            } else if (response.status === 403) {
                showAlert('Access denied. You can only download your own files.', 'error');
                return;
            } else if (response.status === 404) {
                showAlert('File not found.', 'error');
                return;
            }
            throw new Error(`Download failed: ${response.status}`);
        }

        // Get the blob and create download link
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName || 'training-file';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        showAlert('Download started!', 'success');

    } catch (error) {
        console.error('Download error:', error);
        showAlert('Failed to download file. Please try again.', 'error');
    }
}

async function deleteTraining(trainingId, trainingName) {
    // Confirm deletion
    const confirmed = confirm(`Are you sure you want to delete "${trainingName}"?\n\nThis action cannot be undone and will also delete the associated file.`);
    
    if (!confirmed) return;

    try {
        const token = authManager.getToken();
        if (!token) {
            showAlert('Please login to delete trainings.', 'error');
            return;
        }

        const response = await fetch(`${apiClient.baseURL}/api/trainings/${trainingId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                showAlert('Session expired. Please login again.', 'error');
                authManager.logout();
                return;
            } else if (response.status === 403) {
                showAlert('Access denied. You can only delete your own trainings.', 'error');
                return;
            } else if (response.status === 404) {
                showAlert('Training not found.', 'error');
                return;
            }
            throw new Error(`Delete failed: ${response.status}`);
        }

        showAlert('Training deleted successfully!', 'success');
        
        // Refresh the trainings list
        if (window.trainerDashboard) {
            window.trainerDashboard.loadTrainings();
        }

    } catch (error) {
        console.error('Delete error:', error);
        showAlert('Failed to delete training. Please try again.', 'error');
    }
}

// Global function to refresh trainings list
function loadTrainings() {
    if (window.trainerDashboard) {
        window.trainerDashboard.loadTrainings();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.trainerDashboard = new TrainerDashboard();
});