/**
 * FIA v3.0 - Trainer Dashboard Component
 * Handles trainer dashboard functionality
 */

console.log('🚨 ÉTAPE 4 - trainer-dashboard.js RECHARGÉ À:', new Date().toISOString());

class TrainerDashboard {
    constructor() {
        console.log('🚨 ÉTAPE 4 - TrainerDashboard constructor appelé');
        this.init();
    }

    init() {
        console.log('🚀 ÉTAPE 3 - TrainerDashboard.init() démarré');
        
        // Require authentication
        if (!authManager.requireAuth()) {
            console.log('❌ ÉTAPE 3 - Authentication échouée, arrêt de init()');
            return;
        }
        console.log('✅ ÉTAPE 3 - Authentication OK');

        console.log('🔄 ÉTAPE 3 - Début loadUserData()');
        this.loadUserData();
        
        console.log('🔄 ÉTAPE 3 - Début checkAndShowAdminMenus()');
        this.checkAndShowAdminMenus();
        
        console.log('🔄 ÉTAPE 3 - Configuration des autres composants...');
        this.setupLogout();
        this.setupTrainingForm();
        this.setupAIToggle();
        // this.setupSessionForm(); // Disabled - handled by session-manager.js
        this.setupProfileModal();
        this.setupFileUpload();
        this.loadDashboardData();
        this.loadTrainings();
        
        console.log('✅ ÉTAPE 3 - TrainerDashboard.init() terminé');
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

    setupAIToggle() {
        const toggle = document.getElementById('ai-generated-toggle');
        const toggleIcon = document.getElementById('toggle-icon');
        const toggleText = document.getElementById('toggle-text');
        const toggleHelpText = document.getElementById('toggle-help-text');
        const fileSection = document.getElementById('training-file').closest('.mb-3');
        const descriptionField = document.getElementById('training-description');
        const submitBtn = document.getElementById('submit-training-btn');

        if (!toggle) return;

        // Initialize toggle state
        this.updateToggleUI(false);

        toggle.addEventListener('change', (e) => {
            const isAIGenerated = e.target.checked;
            this.updateToggleUI(isAIGenerated);
            this.updateFormValidation(isAIGenerated);
        });
    }

    updateToggleUI(isAIGenerated) {
        const toggleIcon = document.getElementById('toggle-icon');
        const toggleText = document.getElementById('toggle-text');
        const toggleHelpText = document.getElementById('toggle-help-text');
        const fileSection = document.getElementById('training-file').closest('.mb-3');
        const fileInput = document.getElementById('training-file');
        const descriptionField = document.getElementById('training-description');
        const submitBtn = document.getElementById('submit-training-btn');

        if (isAIGenerated) {
            // AI mode
            toggleIcon.className = 'bi bi-toggle-on me-2 text-primary';
            toggleText.textContent = 'Generated with AI';
            toggleHelpText.innerHTML = '<i class="bi bi-robot me-1 text-primary"></i>AI will generate comprehensive training content based on your description';
            
            // Disable file upload
            fileSection.style.opacity = '0.5';
            fileInput.disabled = true;
            fileInput.required = false;
            
            // Make description required
            descriptionField.required = true;
            descriptionField.placeholder = 'Describe the training topic in detail for AI generation...';
            
            // Update submit button
            submitBtn.innerHTML = '<i class="bi bi-robot me-2"></i>Generate Training with AI';
            submitBtn.className = 'btn btn-success';
            
        } else {
            // File upload mode
            toggleIcon.className = 'bi bi-toggle-off me-2';
            toggleText.textContent = 'Generated with AI';
            toggleHelpText.innerHTML = '<i class="bi bi-info-circle me-1"></i>Generate training content automatically using AI instead of uploading a file';
            
            // Enable file upload
            fileSection.style.opacity = '1';
            fileInput.disabled = false;
            fileInput.required = true;
            
            // Make description optional
            descriptionField.required = false;
            descriptionField.placeholder = '';
            
            // Reset submit button
            submitBtn.innerHTML = '<i class="bi bi-upload me-2"></i>Create Training';
            submitBtn.className = 'btn btn-primary';
        }
    }

    updateFormValidation(isAIGenerated) {
        const descriptionField = document.getElementById('training-description');
        const fileInput = document.getElementById('training-file');
        
        if (isAIGenerated) {
            // Clear any file selection
            fileInput.value = '';
            // Hide file info if visible
            const fileInfo = document.getElementById('file-info');
            if (fileInfo) {
                fileInfo.classList.add('d-none');
            }
        } else {
            // Clear description requirement styling if any
            descriptionField.classList.remove('is-invalid');
        }
    }

    async handleTrainingSubmission(form) {
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        const progressContainer = document.getElementById('upload-progress');
        const progressBar = progressContainer.querySelector('.progress-bar');
        const statusDiv = document.getElementById('upload-status');
        const toggle = document.getElementById('ai-generated-toggle');
        const isAIGenerated = toggle.checked;

        try {
            // Validate form data based on mode
            if (isAIGenerated) {
                const description = formData.get('description');
                if (!description || description.trim().length === 0) {
                    showAlert('Please provide a detailed description for AI generation.', 'error');
                    return;
                }
                // Set AI flag in form data
                formData.set('is_ai_generated', 'true');
            } else {
                const file = formData.get('file');
                if (!file || file.size === 0) {
                    showAlert('Please select a file to upload.', 'error');
                    return;
                }
                // Ensure AI flag is false
                formData.set('is_ai_generated', 'false');
            }

            // Show loading state
            submitBtn.disabled = true;
            
            if (isAIGenerated) {
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generating with AI...';
                // Show progress bar for AI generation
                progressContainer.classList.remove('d-none');
                progressBar.style.width = '30%';
                progressBar.setAttribute('aria-valuenow', '30');
                statusDiv.textContent = 'AI is generating your training content...';
                progressBar.className = 'progress-bar progress-bar-striped progress-bar-animated bg-success';
            } else {
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Uploading...';
                // Show progress bar for file upload
                progressContainer.classList.remove('d-none');
                progressBar.style.width = '0%';
                progressBar.setAttribute('aria-valuenow', '0');
                statusDiv.textContent = 'Preparing upload...';
                progressBar.className = 'progress-bar progress-bar-striped progress-bar-animated';
            }

            // Create XMLHttpRequest for upload progress
            const xhr = new XMLHttpRequest();
            const uploadPromise = new Promise((resolve, reject) => {
                
                // Track upload progress
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable && !isAIGenerated) {
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
                        
                        if (isAIGenerated) {
                            statusDiv.textContent = 'AI training generated successfully!';
                        } else {
                            statusDiv.textContent = 'Upload complete!';
                        }
                        
                        resolve(JSON.parse(xhr.responseText));
                    } else {
                        let errorMessage = `Failed: ${xhr.status} ${xhr.statusText}`;
                        if (xhr.status === 429) {
                            errorMessage = 'AI service is busy. Please try again in a few minutes.';
                        } else if (xhr.status === 503) {
                            errorMessage = 'AI service is temporarily unavailable.';
                        }
                        reject(new Error(errorMessage));
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

            if (isAIGenerated) {
                showAlert('AI training generated successfully! The AI has created comprehensive training content for you.', 'success');
            } else {
                showAlert('Training created successfully!', 'success');
            }
            
            // Reset form and file info
            form.reset();
            document.getElementById('file-info').classList.add('d-none');
            
            // Reset toggle to default state
            const toggle = document.getElementById('ai-generated-toggle');
            toggle.checked = false;
            this.updateToggleUI(false);
            
            // Refresh training list
            this.loadTrainings();

        } catch (error) {
            console.error('Training creation error:', error);
            
            let errorMessage = 'Failed to create training. Please try again.';
            
            if (isAIGenerated) {
                // AI-specific error messages
                if (error.message.includes('AI service is busy')) {
                    errorMessage = 'AI service is currently busy. Please try again in a few minutes.';
                } else if (error.message.includes('AI service is temporarily unavailable')) {
                    errorMessage = 'AI generation service is temporarily unavailable. You can try again later or create a training with a file upload.';
                } else if (error.message.includes('429')) {
                    errorMessage = 'Too many AI requests. Please wait a moment before trying again.';
                } else if (error.message.includes('503')) {
                    errorMessage = 'AI generation service is unavailable. Please try again later.';
                } else {
                    errorMessage = 'Failed to generate AI training. Please check your description and try again.';
                }
                statusDiv.textContent = 'AI generation failed';
            } else {
                // File upload error messages
                if (error.message.includes('413')) {
                    errorMessage = 'File too large. Maximum size is 50MB.';
                } else if (error.message.includes('400')) {
                    errorMessage = 'Invalid file type. Please use PDF, PPT, or PPTX files only.';
                } else if (error.message.includes('401')) {
                    errorMessage = 'Session expired. Please login again.';
                    authManager.logout();
                    return;
                }
                statusDiv.textContent = 'Upload failed';
            }
            
            showAlert(errorMessage, 'error');
        } finally {
            // Reset button state
            submitBtn.disabled = false;
            
            // Reset button to current mode
            const toggle = document.getElementById('ai-generated-toggle');
            if (toggle.checked) {
                submitBtn.innerHTML = '<i class="bi bi-robot me-2"></i>Generate Training with AI';
                submitBtn.className = 'btn btn-success';
            } else {
                submitBtn.innerHTML = '<i class="bi bi-upload me-2"></i>Create Training';
                submitBtn.className = 'btn btn-primary';
            }
            
            // Hide progress bar after delay
            setTimeout(() => {
                progressContainer.classList.add('d-none');
                statusDiv.textContent = '';
                progressBar.className = 'progress-bar progress-bar-striped progress-bar-animated';
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
            
            // Update stat cards with new metrics
            const statElements = {
                'trainings-count': stats.trainings_count || 0,
                'sessions-count': stats.active_sessions_count || 0,
                'learners-count': stats.unique_learners_count || 0,
                'total-time': stats.total_time_spent || '0h',
                'slides-viewed': stats.total_slides_viewed || 0,
                'total-slides': stats.total_slides_count || 0
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

    // ============================================================================
    // ADMIN FUNCTIONALITY 
    // ============================================================================

    checkAndShowAdminMenus() {
        // Debug: Vérifier les données utilisateur
        const user = authManager.getUser();
        console.log('🔍 ÉTAPE 2 - Données utilisateur récupérées:', user);
        console.log('🔍 ÉTAPE 2 - is_superuser:', user?.is_superuser);
        console.log('🔍 ÉTAPE 2 - isAuthenticated():', authManager.isAuthenticated());
        console.log('🔍 ÉTAPE 2 - isSuperUser():', authManager.isSuperUser());
        console.log('🔍 ÉTAPE 2 - hasAdminAccess():', authManager.hasAdminAccess());
        
        if (authManager.hasAdminAccess()) {
            console.log('✅ ÉTAPE 2 - Accès admin accordé, affichage des menus');
            this.showAdminMenus();
            this.setupAdminFunctionality();
        } else {
            console.log('❌ ÉTAPE 2 - Accès admin refusé');
        }
    }

    showAdminMenus() {
        console.log('🎯 ÉTAPE 3 - showAdminMenus() appelée');
        
        // Add admin class to body to show admin-only elements
        console.log('🎯 ÉTAPE 3 - Avant ajout is-admin, body.className:', document.body.className);
        document.body.classList.add('is-admin');
        console.log('🎯 ÉTAPE 3 - Après ajout is-admin, body.className:', document.body.className);
        console.log('🎯 ÉTAPE 3 - Vérification body.classList.contains("is-admin"):', document.body.classList.contains('is-admin'));
        
        // Check if admin elements exist
        const adminElements = document.querySelectorAll('.admin-only');
        console.log(`🎯 ÉTAPE 3 - Trouvé ${adminElements.length} éléments .admin-only`);
        
        // Detailed analysis of each admin element
        adminElements.forEach((element, index) => {
            const computedStyle = window.getComputedStyle(element);
            console.log(`🎯 ÉTAPE 3 - Élément ${index + 1}:`, {
                tagName: element.tagName,
                className: element.className,
                id: element.id,
                display: computedStyle.display,
                visibility: computedStyle.visibility,
                position: computedStyle.position,
                zIndex: computedStyle.zIndex
            });
            
            // Special check for nav item
            if (element.classList.contains('nav-item')) {
                console.log(`🎯 ÉTAPE 3 - Nav item content:`, element.innerHTML.replace(/\n\s+/g, ' ').trim());
            }
        });
        
        // Test CSS rules application
        console.log('🎯 ÉTAPE 3 - Test des règles CSS:');
        const navTestElement = document.querySelector('.nav-item.admin-only');
        if (navTestElement) {
            const navComputedStyle = window.getComputedStyle(navTestElement);
            console.log('🎯 ÉTAPE 3 - Nav .admin-only computed style:', {
                display: navComputedStyle.display,
                visibility: navComputedStyle.visibility,
                opacity: navComputedStyle.opacity
            });
        }
        
        const tabTestElement = document.querySelector('.tab-pane.admin-only');
        if (tabTestElement) {
            const tabComputedStyle = window.getComputedStyle(tabTestElement);
            console.log('🎯 ÉTAPE 3 - Tab .admin-only computed style:', {
                display: tabComputedStyle.display,
                visibility: tabComputedStyle.visibility,
                opacity: tabComputedStyle.opacity
            });
        }
        
        // Check if CSS file is loaded
        const cssLinks = document.querySelectorAll('link[rel="stylesheet"]');
        console.log('🎯 ÉTAPE 3 - Fichiers CSS chargés:', Array.from(cssLinks).map(link => link.href));
        
        // Test direct CSS rule
        try {
            const testDiv = document.createElement('div');
            testDiv.className = 'admin-only';
            document.body.appendChild(testDiv);
            const testStyle = window.getComputedStyle(testDiv);
            console.log('🎯 ÉTAPE 3 - Test direct .admin-only display:', testStyle.display);
            document.body.removeChild(testDiv);
            
            // Test with body.is-admin
            document.body.classList.add('test-admin-class');
            const testDiv2 = document.createElement('div');
            testDiv2.className = 'admin-only';
            document.body.appendChild(testDiv2);
            const testStyle2 = window.getComputedStyle(testDiv2);
            console.log('🎯 ÉTAPE 3 - Test .admin-only avec body.is-admin:', testStyle2.display);
            document.body.removeChild(testDiv2);
            document.body.classList.remove('test-admin-class');
            
            // Test spécifique nav-item
            const testNav = document.createElement('li');
            testNav.className = 'nav-item admin-only';
            document.body.appendChild(testNav);
            const testNavStyle = window.getComputedStyle(testNav);
            console.log('🎯 ÉTAPE 3 - Test .nav-item.admin-only display:', testNavStyle.display);
            document.body.removeChild(testNav);
            
        } catch (e) {
            console.error('🎯 ÉTAPE 3 - Erreur test CSS:', e);
        }
        
        // Check if main.css styles are applied
        const bodyStyle = window.getComputedStyle(document.body);
        console.log('🎯 ÉTAPE 3 - Body font-family (pour vérifier CSS):', bodyStyle.fontFamily);
        
        // Force d'affichage si nécessaire (temporaire pour debug)
        console.log('🎯 ÉTAPE 3 - Vérification finale de la visibilité des éléments admin');
        setTimeout(() => {
            const finalCheck = document.querySelectorAll('.admin-only');
            let visibleCount = 0;
            finalCheck.forEach(element => {
                const style = window.getComputedStyle(element);
                if (style.display !== 'none') {
                    visibleCount++;
                }
            });
            console.log(`🎯 ÉTAPE 3 - RÉSULTAT FINAL: ${visibleCount}/${finalCheck.length} éléments admin visibles`);
            
            if (visibleCount === 0) {
                console.log('🚨 ÉTAPE 3 - AUCUN élément admin visible, forçage d\'affichage...');
                finalCheck.forEach(element => {
                    if (element.classList.contains('nav-item')) {
                        element.style.display = 'list-item';
                        console.log('🔧 ÉTAPE 3 - Forcé nav-item à list-item');
                    } else if (element.classList.contains('tab-pane')) {
                        element.style.display = 'block';
                        console.log('🔧 ÉTAPE 3 - Forcé tab-pane à block');
                    } else {
                        element.style.display = 'block';
                        console.log('🔧 ÉTAPE 3 - Forcé autre élément à block');
                    }
                });
            } else {
                console.log('✅ ÉTAPE 3 - Des éléments admin sont visibles !');
            }
        }, 100);
    }

    setupAdminFunctionality() {
        // Setup admin-specific event handlers and functionality
        this.setupTrainersOverviewTab();
        
        // Pre-load trainers data for admin users
        console.log('Pre-loading trainers data for admin user');
        setTimeout(() => {
            this.loadTrainersOverview();
        }, 500); // Small delay to ensure DOM is ready
    }

    setupTrainersOverviewTab() {
        // Setup click handler for admin trainers tab
        const trainersTab = document.querySelector('a[href="#admin-trainers"]');
        console.log('Setting up trainers tab event listener, found element:', trainersTab);
        if (trainersTab) {
            trainersTab.addEventListener('shown.bs.tab', () => {
                console.log('Trainers tab shown event triggered');
                this.loadTrainersOverview();
            });
            
            // Also try to load immediately if this tab is already active
            if (trainersTab.classList.contains('active')) {
                console.log('Trainers tab is already active, loading immediately');
                this.loadTrainersOverview();
            }
        }
    }

    async loadTrainersOverview(retryCount = 0) {
        console.log('Loading trainers overview...');
        const tableBody = document.getElementById('trainers-overview-body');
        if (!tableBody) {
            console.error('Element trainers-overview-body not found!');
            return;
        }
        console.log('Found table body element:', tableBody);

        try {
            // Show loading state - consistent with existing patterns
            this.showTrainersLoadingState(tableBody);

            // Fetch trainers overview data
            console.log('Fetching trainers overview data...');
            const trainersData = await apiClient.get('/api/admin/trainers-overview');
            console.log('Received trainers data:', trainersData.length, 'trainers');

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
                        // Set default value to prevent rendering errors
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

            // Render trainers data with enhanced formatting
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

            console.log('Setting trainers HTML:', trainersHtml.length, 'characters');
            tableBody.innerHTML = trainersHtml;
            console.log('Trainers table updated with', trainersData.length, 'trainers');

            // Setup table sorting if not already done
            this.setupTableSorting();

        } catch (error) {
            console.error('Failed to load trainers overview:', error);
            
            // Enhanced error handling with specific messaging
            let errorMessage = 'Failed to load trainers overview. Please try again.';
            let isTemporary = true;
            
            if (error.message.includes('403') || error.message.includes('Forbidden')) {
                errorMessage = 'Access denied: Administrator privileges required to view trainer statistics.';
                isTemporary = false;
            } else if (error.message.includes('401') || error.message.includes('Unauthorized')) {
                errorMessage = 'Authentication expired. Please log in again.';
                isTemporary = false;
                // Redirect to login after short delay
                setTimeout(() => {
                    authManager.logout();
                }, 2000);
            } else if (error.message.includes('500') || error.message.includes('Internal Server Error')) {
                errorMessage = 'Server error occurred while calculating trainer statistics. The development team has been notified.';
            } else if (error.message.includes('502') || error.message.includes('503') || error.message.includes('504')) {
                errorMessage = 'Service temporarily unavailable. Please try again in a few moments.';
                // Auto-retry for temporary server errors
                if (retryCount < 2) {
                    console.log(`Retrying trainers overview request (attempt ${retryCount + 1}/3)`);
                    setTimeout(() => {
                        this.loadTrainersOverview(retryCount + 1);
                    }, 2000 * (retryCount + 1)); // Exponential backoff
                    return;
                }
            } else if (error.message.includes('Network') || error.message.includes('fetch')) {
                errorMessage = 'Network connection error. Please check your internet connection and try again.';
            } else if (error.message.includes('timeout')) {
                errorMessage = 'Request timed out. The server may be busy, please try again.';
            }
            
            this.showTrainersErrorState(tableBody, errorMessage);
            
            // Log additional context for debugging
            console.error('Trainers overview error context:', {
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
        
        // Reset all headers - remove sort classes and reset icons
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
        
        // Sort rows with enhanced multi-type sorting
        rows.sort((a, b) => {
            const aValue = this.getCellValue(a, column);
            const bValue = this.getCellValue(b, column);
            
            let comparison = this.compareValues(aValue, bValue, column);
            return newSort === 'desc' ? -comparison : comparison;
        });
        
        // Reorder DOM with smooth visual feedback
        rows.forEach(row => tbody.appendChild(row));
        
        // Store current sort state for persistence
        this.currentSortColumn = column;
        this.currentSortDirection = newSort;
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
        
        // Time duration columns (like "2h 30min" or "45min")
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
        // Convert duration strings like "2h 30min" or "45min" to minutes for comparison
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
    // TABLE STATE MANAGEMENT - Consistent with existing patterns
    // ============================================================================

    showTrainersLoadingState(tableBody) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="13" class="text-center text-muted py-5 admin-table-loading">
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
                <td colspan="13" class="text-center text-muted py-5 admin-table-empty">
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

// Global function to refresh trainers overview (admin) with debouncing
let refreshDebounceTimeout = null;
async function refreshTrainersOverview() {
    const refreshBtn = document.querySelector('button[onclick="refreshTrainersOverview()"]');
    
    // Debounce rapid clicks
    if (refreshDebounceTimeout) {
        return;
    }
    
    const originalContent = refreshBtn.innerHTML;
    
    try {
        // Show loading state on button
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = `
            <span class="spinner-border spinner-border-sm me-1" role="status"></span>
            Refreshing...
        `;
        
        // Set debounce timeout
        refreshDebounceTimeout = setTimeout(() => {
            refreshDebounceTimeout = null;
        }, 1000);
        
        if (window.trainerDashboard && window.trainerDashboard.loadTrainersOverview) {
            await window.trainerDashboard.loadTrainersOverview();
        }
    } catch (error) {
        console.error('Error refreshing trainers overview:', error);
    } finally {
        // Restore button state
        refreshBtn.disabled = false;
        refreshBtn.innerHTML = originalContent;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🌐 ÉTAPE 3 - DOM chargé, instanciation TrainerDashboard');
    window.trainerDashboard = new TrainerDashboard();
});