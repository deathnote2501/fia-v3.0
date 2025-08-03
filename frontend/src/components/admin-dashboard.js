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
        
        // Setup tab switching to load trainees when tab is activated
        this.setupTabSwitching();
        
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
                showAlert(window.safeT ? window.safeT('message.profileUpdated') : 'Profile updated successfully!', 'success');
                
                // Refresh user data from updated profile
                await this.refreshUserData();
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('profile-modal'));
                if (modal) modal.hide();
            } else {
                showAlert(result.message || (window.safeT ? window.safeT('message.profileUpdateFailed') : 'Profile update failed.'), 'error');
            }

        } catch (error) {
            console.error('Profile update error:', error);
            showAlert(window.safeT ? window.safeT('message.profileUpdateError') : 'Failed to update profile. Please try again.', 'error');
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

    setupTabSwitching() {
        const trainersTab = document.querySelector('a[href="#trainers"]');
        const traineesTab = document.querySelector('a[href="#trainees"]');
        const trainingsTab = document.querySelector('a[href="#trainings"]');
        const sessionsTab = document.querySelector('a[href="#sessions"]');
        
        if (trainersTab) {
            trainersTab.addEventListener('shown.bs.tab', () => {
                console.log('🔥 ADMIN - Trainers tab activated');
                this.loadTrainersOverview();
            });
        }
        
        if (traineesTab) {
            traineesTab.addEventListener('shown.bs.tab', () => {
                console.log('🔥 ADMIN - Trainees tab activated');
                this.loadTraineesOverview();
            });
        }
        
        if (trainingsTab) {
            trainingsTab.addEventListener('shown.bs.tab', () => {
                console.log('🔥 ADMIN - Trainings tab activated');
                this.loadTrainingsOverview();
            });
        }
        
        if (sessionsTab) {
            sessionsTab.addEventListener('shown.bs.tab', () => {
                console.log('🔥 ADMIN - Sessions tab activated');
                this.loadSessionsOverview();
            });
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

    // ============================================================================
    // TRAINEES OVERVIEW FUNCTIONALITY 
    // ============================================================================

    async loadTraineesOverview(retryCount = 0) {
        console.log('🔥 ADMIN - Loading trainees overview...');
        const tableBody = document.getElementById('trainees-overview-body');
        if (!tableBody) {
            console.error('🚨 ADMIN - Element trainees-overview-body not found!');
            return;
        }
        console.log('✅ ADMIN - Found trainees table body element:', tableBody);

        try {
            // Show loading state
            this.showTraineesLoadingState(tableBody);

            // Fetch trainees overview data
            console.log('📡 ADMIN - Fetching trainees overview data...');
            const traineesData = await apiClient.get('/api/admin/trainees-overview');
            console.log('📊 ADMIN - Received trainees data:', traineesData.length, 'trainees');

            // Validate response data structure
            if (!Array.isArray(traineesData)) {
                throw new Error('Invalid response format: Expected array of trainees');
            }

            if (traineesData.length === 0) {
                this.showTraineesEmptyState(tableBody);
                return;
            }

            // Validate each trainee object has required fields
            const requiredFields = ['email'];
            for (let i = 0; i < traineesData.length; i++) {
                const trainee = traineesData[i];
                for (const field of requiredFields) {
                    if (!trainee.hasOwnProperty(field)) {
                        console.warn(`Trainee at index ${i} missing required field: ${field}`);
                        trainee[field] = 'N/A';
                    }
                }
                
                // Ensure numeric fields are numbers
                const numericFields = [
                    'total_sessions', 'ai_sessions', 'trainer_sessions', 'total_slides_viewed'
                ];
                numericFields.forEach(field => {
                    if (trainee[field] === null || trainee[field] === undefined) {
                        trainee[field] = 0;
                    }
                });
            }

            // Render trainees data
            const traineesHtml = traineesData.map(trainee => `
                <tr data-trainee-email="${trainee.email}">
                    <td>
                        <strong>${this.escapeHtml(trainee.email)}</strong>
                    </td>
                    <td>
                        <span class="text-muted">${this.escapeHtml(trainee.level || 'N/A')}</span>
                    </td>
                    <td>
                        <span class="text-muted">${this.escapeHtml(trainee.job_sector || 'N/A')}</span>
                    </td>
                    <td>
                        <span class="text-muted">${this.escapeHtml(trainee.objective || 'N/A')}</span>
                    </td>
                    <td>
                        <div class="text-truncate" style="max-width: 200px;" title="${this.escapeHtml(JSON.stringify(trainee.enriched_profile || {}))}">
                            ${trainee.enriched_profile ? '<i class="bi bi-check-circle text-success me-1"></i>Enrichi' : '<i class="bi bi-circle text-muted me-1"></i>Basique'}
                        </div>
                    </td>
                    <td>
                        <span class="badge bg-secondary">${this.formatNumber(trainee.total_sessions)}</span>
                    </td>
                    <td>
                        <span class="badge bg-success">${this.formatNumber(trainee.ai_sessions)}</span>
                    </td>
                    <td>
                        <span class="badge bg-primary">${this.formatNumber(trainee.trainer_sessions)}</span>
                    </td>
                    <td>
                        <span class="text-muted">${trainee.total_time || '0min'}</span>
                    </td>
                    <td>
                        <span class="badge bg-info">${this.formatNumber(trainee.total_slides_viewed)}</span>
                    </td>
                </tr>
            `).join('');

            console.log('🎨 ADMIN - Setting trainees HTML:', traineesHtml.length, 'characters');
            tableBody.innerHTML = traineesHtml;
            console.log('✅ ADMIN - Trainees table updated with', traineesData.length, 'trainees');

        } catch (error) {
            console.error('🚨 ADMIN - Failed to load trainees overview:', error);
            
            // Enhanced error handling with specific messaging
            let errorMessage = 'Failed to load trainees overview. Please try again.';
            
            if (error.message.includes('403') || error.message.includes('Forbidden')) {
                errorMessage = 'Access denied: Administrator privileges required to view trainee statistics.';
            } else if (error.message.includes('401') || error.message.includes('Unauthorized')) {
                errorMessage = 'Authentication expired. Please log in again.';
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 2000);
            } else if (error.message.includes('500') || error.message.includes('Internal Server Error')) {
                errorMessage = 'Server error occurred while calculating trainee statistics.';
            } else if (error.message.includes('Network') || error.message.includes('fetch')) {
                errorMessage = 'Network connection error. Please check your internet connection and try again.';
            }
            
            this.showTraineesErrorState(tableBody, errorMessage);
            
            // Log additional context for debugging
            console.error('🚨 ADMIN - Trainees overview error context:', {
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent,
                url: window.location.href,
                error: error.toString(),
                stack: error.stack
            });
        }
    }

    showTraineesLoadingState(tableBody) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="10" class="text-center text-muted py-5">
                    <div>
                        <div class="spinner-border text-primary mb-3" role="status" style="width: 3rem; height: 3rem;">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mb-1 fw-medium">Loading trainees overview...</p>
                        <small class="text-muted">Fetching trainee statistics and learning data</small>
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

    showTraineesEmptyState(tableBody) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="10" class="text-center text-muted py-5">
                    <div>
                        <i class="bi bi-person-check display-4 mb-3 text-secondary"></i>
                        <h6 class="text-muted mb-2">No Trainees Found</h6>
                        <p class="small mb-3">There are currently no trainees who have participated in training sessions.</p>
                        <div class="d-flex gap-2 justify-content-center">
                            <button class="btn btn-sm btn-outline-primary" onclick="refreshTraineesOverview()">
                                <i class="bi bi-arrow-clockwise me-1"></i>
                                Refresh
                            </button>
                        </div>
                    </div>
                </td>
            </tr>
        `;
    }

    showTraineesErrorState(tableBody, errorMessage = 'Failed to load trainees overview') {
        tableBody.innerHTML = `
            <tr>
                <td colspan="10" class="text-center py-5">
                    <div>
                        <i class="bi bi-exclamation-triangle display-4 mb-3 text-warning"></i>
                        <h6 class="text-danger mb-2">${window.safeT ? window.safeT('error.loadingData', 'Error Loading Data') : 'Error Loading Data'}</h6>
                        <p class="text-muted small mb-3">${errorMessage}</p>
                        <div class="d-flex gap-2 justify-content-center">
                            <button class="btn btn-sm btn-outline-primary" onclick="refreshTraineesOverview()">
                                <i class="bi bi-arrow-clockwise me-1"></i>
                                Try Again
                            </button>
                        </div>
                    </div>
                </td>
            </tr>
        `;
    }

    // ============================================================================
    // TRAININGS OVERVIEW FUNCTIONALITY 
    // ============================================================================

    async loadTrainingsOverview(retryCount = 0) {
        console.log('🔥 ADMIN - Loading trainings overview...');
        const tableBody = document.getElementById('trainings-overview-body');
        if (!tableBody) {
            console.error('🚨 ADMIN - Element trainings-overview-body not found!');
            return;
        }
        console.log('✅ ADMIN - Found trainings table body element:', tableBody);

        try {
            // Show loading state
            this.showTrainingsLoadingState(tableBody);

            // Fetch trainings overview data
            console.log('📡 ADMIN - Fetching trainings overview data...');
            const trainingsData = await apiClient.get('/api/admin/trainings-overview');
            console.log('📊 ADMIN - Received trainings data:', trainingsData.length, 'trainings');

            // Validate response data structure
            if (!Array.isArray(trainingsData)) {
                throw new Error('Invalid response format: Expected array of trainings');
            }

            if (trainingsData.length === 0) {
                this.showTrainingsEmptyState(tableBody);
                return;
            }

            // Validate each training object has required fields
            const requiredFields = ['training_name'];
            for (let i = 0; i < trainingsData.length; i++) {
                const training = trainingsData[i];
                for (const field of requiredFields) {
                    if (!training.hasOwnProperty(field)) {
                        console.warn(`Training at index ${i} missing required field: ${field}`);
                        training[field] = 'N/A';
                    }
                }
                
                // Ensure numeric fields are numbers
                const numericFields = [
                    'total_sessions', 'total_learners', 'total_slides', 'avg_slides_per_session'
                ];
                numericFields.forEach(field => {
                    if (training[field] === null || training[field] === undefined) {
                        training[field] = 0;
                    }
                });
            }

            // Render trainings data
            const trainingsHtml = trainingsData.map(training => `
                <tr data-training-id="${training.training_id || 'unknown'}">
                    <td>
                        <strong>${this.escapeHtml(training.training_name)}</strong>
                    </td>
                    <td>
                        <span class="badge ${training.training_type === 'IA' ? 'bg-success' : 'bg-primary'}">
                            <i class="bi bi-${training.training_type === 'IA' ? 'robot' : 'person'} me-1"></i>
                            ${training.training_type || 'N/A'}
                        </span>
                    </td>
                    <td>
                        <span class="badge bg-info">${this.formatNumber(training.total_learners)}</span>
                    </td>
                    <td>
                        <span class="badge bg-secondary">${this.formatNumber(training.total_sessions)}</span>
                    </td>
                    <td>
                        <span class="text-muted">${training.total_time || '0min'}</span>
                    </td>
                    <td>
                        <span class="text-muted">${training.avg_time_per_session || '0min'}</span>
                    </td>
                    <td>
                        <span class="badge bg-primary">${this.formatNumber(training.total_slides)}</span>
                    </td>
                    <td>
                        <span class="text-muted">${this.formatDecimal(training.avg_slides_per_session)}</span>
                    </td>
                </tr>
            `).join('');

            console.log('🎨 ADMIN - Setting trainings HTML:', trainingsHtml.length, 'characters');
            tableBody.innerHTML = trainingsHtml;
            console.log('✅ ADMIN - Trainings table updated with', trainingsData.length, 'trainings');

        } catch (error) {
            console.error('🚨 ADMIN - Failed to load trainings overview:', error);
            
            // Enhanced error handling with specific messaging
            let errorMessage = 'Failed to load trainings overview. Please try again.';
            
            if (error.message.includes('403') || error.message.includes('Forbidden')) {
                errorMessage = 'Access denied: Administrator privileges required to view training statistics.';
            } else if (error.message.includes('401') || error.message.includes('Unauthorized')) {
                errorMessage = 'Authentication expired. Please log in again.';
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 2000);
            } else if (error.message.includes('500') || error.message.includes('Internal Server Error')) {
                errorMessage = 'Server error occurred while calculating training statistics.';
            } else if (error.message.includes('Network') || error.message.includes('fetch')) {
                errorMessage = 'Network connection error. Please check your internet connection and try again.';
            }
            
            this.showTrainingsErrorState(tableBody, errorMessage);
            
            // Log additional context for debugging
            console.error('🚨 ADMIN - Trainings overview error context:', {
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent,
                url: window.location.href,
                error: error.toString(),
                stack: error.stack
            });
        }
    }

    showTrainingsLoadingState(tableBody) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-muted py-5">
                    <div>
                        <div class="spinner-border text-primary mb-3" role="status" style="width: 3rem; height: 3rem;">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mb-1 fw-medium">Loading trainings overview...</p>
                        <small class="text-muted">Fetching training statistics and session data</small>
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

    showTrainingsEmptyState(tableBody) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-muted py-5">
                    <div>
                        <i class="bi bi-book display-4 mb-3 text-secondary"></i>
                        <h6 class="text-muted mb-2">No Trainings Found</h6>
                        <p class="small mb-3">There are currently no trainings created in the system.</p>
                        <div class="d-flex gap-2 justify-content-center">
                            <button class="btn btn-sm btn-outline-primary" onclick="refreshTrainingsOverview()">
                                <i class="bi bi-arrow-clockwise me-1"></i>
                                Refresh
                            </button>
                        </div>
                    </div>
                </td>
            </tr>
        `;
    }

    showTrainingsErrorState(tableBody, errorMessage = 'Failed to load trainings overview') {
        tableBody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center py-5">
                    <div>
                        <i class="bi bi-exclamation-triangle display-4 mb-3 text-warning"></i>
                        <h6 class="text-danger mb-2">${window.safeT ? window.safeT('error.loadingData', 'Error Loading Data') : 'Error Loading Data'}</h6>
                        <p class="text-muted small mb-3">${errorMessage}</p>
                        <div class="d-flex gap-2 justify-content-center">
                            <button class="btn btn-sm btn-outline-primary" onclick="refreshTrainingsOverview()">
                                <i class="bi bi-arrow-clockwise me-1"></i>
                                Try Again
                            </button>
                        </div>
                    </div>
                </td>
            </tr>
        `;
    }

    // ============================================================================
    // SESSIONS OVERVIEW FUNCTIONALITY 
    // ============================================================================

    async loadSessionsOverview(retryCount = 0) {
        console.log('🔥 ADMIN - Loading sessions overview...');
        const tableBody = document.getElementById('sessions-overview-body');
        if (!tableBody) {
            console.error('🚨 ADMIN - Element sessions-overview-body not found!');
            return;
        }
        console.log('✅ ADMIN - Found sessions table body element:', tableBody);

        try {
            // Show loading state
            this.showSessionsLoadingState(tableBody);

            // Fetch sessions overview data
            console.log('📡 ADMIN - Fetching sessions overview data...');
            const sessionsData = await apiClient.get('/api/admin/sessions-overview');
            console.log('📊 ADMIN - Received sessions data:', sessionsData.length, 'sessions');

            // Validate response data structure
            if (!Array.isArray(sessionsData)) {
                throw new Error('Invalid response format: Expected array of sessions');
            }

            if (sessionsData.length === 0) {
                this.showSessionsEmptyState(tableBody);
                return;
            }

            // Validate each session object has required fields
            const requiredFields = ['session_name'];
            for (let i = 0; i < sessionsData.length; i++) {
                const session = sessionsData[i];
                for (const field of requiredFields) {
                    if (!session.hasOwnProperty(field)) {
                        console.warn(`Session at index ${i} missing required field: ${field}`);
                        session[field] = 'N/A';
                    }
                }
                
                // Ensure numeric fields are numbers
                const numericFields = [
                    'total_slides', 'progress_percentage', 'input_tokens', 'output_tokens'
                ];
                numericFields.forEach(field => {
                    if (session[field] === null || session[field] === undefined) {
                        session[field] = 0;
                    }
                });
            }

            // Render sessions data
            const sessionsHtml = sessionsData.map(session => `
                <tr data-session-id="${session.session_id || 'unknown'}">
                    <td>
                        <strong>${this.escapeHtml(session.session_name)}</strong>
                    </td>
                    <td>
                        <span class="text-muted">${this.escapeHtml(session.training_name || 'N/A')}</span>
                    </td>
                    <td>
                        <span class="badge ${session.training_type === 'IA' ? 'bg-success' : 'bg-primary'}">
                            <i class="bi bi-${session.training_type === 'IA' ? 'robot' : 'person'} me-1"></i>
                            ${session.training_type || 'N/A'}
                        </span>
                    </td>
                    <td>
                        <small class="text-muted">${this.formatDate(session.session_date)}</small>
                    </td>
                    <td>
                        <span class="badge ${this.getStatusBadgeClass(session.status)}">
                            <i class="bi bi-${this.getStatusIcon(session.status)} me-1"></i>
                            ${session.status || 'N/A'}
                        </span>
                    </td>
                    <td>
                        <span class="badge bg-info">${this.formatNumber(session.total_slides)}</span>
                    </td>
                    <td>
                        <div class="d-flex align-items-center">
                            <div class="progress flex-grow-1 me-2" style="height: 20px;">
                                <div class="progress-bar ${this.getProgressBarClass(session.progress_percentage)}" 
                                     role="progressbar" 
                                     style="width: ${session.progress_percentage || 0}%"
                                     aria-valuenow="${session.progress_percentage || 0}" 
                                     aria-valuemin="0" 
                                     aria-valuemax="100">
                                </div>
                            </div>
                            <small class="text-muted">${Math.round(session.progress_percentage || 0)}%</small>
                        </div>
                    </td>
                    <td>
                        <div class="text-center">
                            <small class="text-success d-block">
                                <i class="bi bi-arrow-down-circle me-1"></i>
                                ${this.formatNumber(session.input_tokens || 0)} in
                            </small>
                            <small class="text-warning d-block">
                                <i class="bi bi-arrow-up-circle me-1"></i>
                                ${this.formatNumber(session.output_tokens || 0)} out
                            </small>
                            <small class="text-muted">
                                ${session.token_cost || '$0.00'}
                            </small>
                        </div>
                    </td>
                    <td>
                        <div class="btn-group btn-group-sm" role="group">
                            <button class="btn btn-outline-primary" 
                                    onclick="viewSessionDetails('${session.session_id}')" 
                                    title="View Details">
                                <i class="bi bi-eye"></i>
                            </button>
                            <button class="btn btn-outline-secondary" 
                                    onclick="downloadSessionReport('${session.session_id}')" 
                                    title="Download Report">
                                <i class="bi bi-download"></i>
                            </button>
                            <button class="btn btn-outline-danger" 
                                    onclick="deleteSession('${session.session_id}', '${session.session_name}')" 
                                    title="Delete Session">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');

            console.log('🎨 ADMIN - Setting sessions HTML:', sessionsHtml.length, 'characters');
            tableBody.innerHTML = sessionsHtml;
            console.log('✅ ADMIN - Sessions table updated with', sessionsData.length, 'sessions');

        } catch (error) {
            console.error('🚨 ADMIN - Failed to load sessions overview:', error);
            
            // Enhanced error handling with specific messaging
            let errorMessage = 'Failed to load sessions overview. Please try again.';
            
            if (error.message.includes('403') || error.message.includes('Forbidden')) {
                errorMessage = 'Access denied: Administrator privileges required to view session statistics.';
            } else if (error.message.includes('401') || error.message.includes('Unauthorized')) {
                errorMessage = 'Authentication expired. Please log in again.';
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 2000);
            } else if (error.message.includes('500') || error.message.includes('Internal Server Error')) {
                errorMessage = 'Server error occurred while calculating session statistics.';
            } else if (error.message.includes('Network') || error.message.includes('fetch')) {
                errorMessage = 'Network connection error. Please check your internet connection and try again.';
            }
            
            this.showSessionsErrorState(tableBody, errorMessage);
            
            // Log additional context for debugging
            console.error('🚨 ADMIN - Sessions overview error context:', {
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent,
                url: window.location.href,
                error: error.toString(),
                stack: error.stack
            });
        }
    }

    getStatusBadgeClass(status) {
        switch (status?.toLowerCase()) {
            case 'active': return 'bg-success';
            case 'completed': return 'bg-primary';
            case 'paused': return 'bg-warning';
            case 'cancelled': return 'bg-danger';
            case 'draft': return 'bg-secondary';
            default: return 'bg-secondary';
        }
    }

    getStatusIcon(status) {
        switch (status?.toLowerCase()) {
            case 'active': return 'play-circle';
            case 'completed': return 'check-circle';
            case 'paused': return 'pause-circle';
            case 'cancelled': return 'x-circle';
            case 'draft': return 'circle';
            default: return 'circle';
        }
    }

    getProgressBarClass(percentage) {
        if (percentage >= 100) return 'bg-success';
        if (percentage >= 75) return 'bg-info';
        if (percentage >= 50) return 'bg-warning';
        if (percentage >= 25) return 'bg-primary';
        return 'bg-secondary';
    }

    showSessionsLoadingState(tableBody) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-muted py-5">
                    <div>
                        <div class="spinner-border text-primary mb-3" role="status" style="width: 3rem; height: 3rem;">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mb-1 fw-medium">Loading sessions overview...</p>
                        <small class="text-muted">Fetching session data and progress information</small>
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

    showSessionsEmptyState(tableBody) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-muted py-5">
                    <div>
                        <i class="bi bi-calendar-event display-4 mb-3 text-secondary"></i>
                        <h6 class="text-muted mb-2">No Sessions Found</h6>
                        <p class="small mb-3">There are currently no training sessions created in the system.</p>
                        <div class="d-flex gap-2 justify-content-center">
                            <button class="btn btn-sm btn-outline-primary" onclick="refreshSessionsOverview()">
                                <i class="bi bi-arrow-clockwise me-1"></i>
                                Refresh
                            </button>
                        </div>
                    </div>
                </td>
            </tr>
        `;
    }

    showSessionsErrorState(tableBody, errorMessage = 'Failed to load sessions overview') {
        tableBody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center py-5">
                    <div>
                        <i class="bi bi-exclamation-triangle display-4 mb-3 text-warning"></i>
                        <h6 class="text-danger mb-2">${window.safeT ? window.safeT('error.loadingData', 'Error Loading Data') : 'Error Loading Data'}</h6>
                        <p class="text-muted small mb-3">${errorMessage}</p>
                        <div class="d-flex gap-2 justify-content-center">
                            <button class="btn btn-sm btn-outline-primary" onclick="refreshSessionsOverview()">
                                <i class="bi bi-arrow-clockwise me-1"></i>
                                Try Again
                            </button>
                        </div>
                    </div>
                </td>
            </tr>
        `;
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
                        <h6 class="text-danger mb-2">${window.safeT ? window.safeT('error.loadingData', 'Error Loading Data') : 'Error Loading Data'}</h6>
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

// Global function to refresh trainees overview
async function refreshTraineesOverview() {
    const refreshBtn = document.querySelector('button[onclick="refreshTraineesOverview()"]');
    
    const originalContent = refreshBtn.innerHTML;
    
    try {
        // Show loading state on button
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = `
            <span class="spinner-border spinner-border-sm me-1" role="status"></span>
            Refreshing...
        `;
        
        if (window.adminDashboard && window.adminDashboard.loadTraineesOverview) {
            await window.adminDashboard.loadTraineesOverview();
        }
    } catch (error) {
        console.error('🚨 ADMIN - Error refreshing trainees overview:', error);
    } finally {
        // Restore button state
        refreshBtn.disabled = false;
        refreshBtn.innerHTML = originalContent;
    }
}

// Global function to refresh trainings overview
async function refreshTrainingsOverview() {
    const refreshBtn = document.querySelector('button[onclick="refreshTrainingsOverview()"]');
    
    const originalContent = refreshBtn.innerHTML;
    
    try {
        // Show loading state on button
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = `
            <span class="spinner-border spinner-border-sm me-1" role="status"></span>
            Refreshing...
        `;
        
        if (window.adminDashboard && window.adminDashboard.loadTrainingsOverview) {
            await window.adminDashboard.loadTrainingsOverview();
        }
    } catch (error) {
        console.error('🚨 ADMIN - Error refreshing trainings overview:', error);
    } finally {
        // Restore button state
        refreshBtn.disabled = false;
        refreshBtn.innerHTML = originalContent;
    }
}

// Global function to refresh sessions overview
async function refreshSessionsOverview() {
    const refreshBtn = document.querySelector('button[onclick="refreshSessionsOverview()"]');
    
    const originalContent = refreshBtn.innerHTML;
    
    try {
        // Show loading state on button
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = `
            <span class="spinner-border spinner-border-sm me-1" role="status"></span>
            Refreshing...
        `;
        
        if (window.adminDashboard && window.adminDashboard.loadSessionsOverview) {
            await window.adminDashboard.loadSessionsOverview();
        }
    } catch (error) {
        console.error('🚨 ADMIN - Error refreshing sessions overview:', error);
    } finally {
        // Restore button state
        refreshBtn.disabled = false;
        refreshBtn.innerHTML = originalContent;
    }
}

// Global functions for session actions
async function viewSessionDetails(sessionId) {
    console.log('📋 ADMIN - Viewing session details for:', sessionId);
    try {
        const sessionDetails = await apiClient.get(`/api/admin/sessions/${sessionId}/details`);
        
        // For now, just show an alert with basic info
        // In the future, this could open a modal with detailed session information
        alert(`Session Details:\n\nID: ${sessionDetails.id}\nName: ${sessionDetails.name}\nStatus: ${sessionDetails.status}\nProgress: ${sessionDetails.progress_percentage}%`);
        
    } catch (error) {
        console.error('Error loading session details:', error);
        alert('Failed to load session details. Please try again.');
    }
}

async function downloadSessionReport(sessionId) {
    console.log('📊 ADMIN - Downloading session report for:', sessionId);
    try {
        const token = authManager.getToken();
        if (!token) {
            alert('Please login to download session reports.');
            return;
        }

        // Create download link
        const downloadUrl = `/api/admin/sessions/${sessionId}/report`;
        
        const response = await fetch(downloadUrl, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error(`Download failed: ${response.status}`);
        }

        // Get the blob and create download link
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `session-report-${sessionId}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        showAlert(window.safeT ? window.safeT('message.sessionReportDownloadStarted') : 'Session report download started!', 'success');

    } catch (error) {
        console.error('Download error:', error);
        showAlert(window.safeT ? window.safeT('message.sessionReportDownloadFailed') : 'Failed to download session report. Please try again.', 'error');
    }
}

async function deleteSession(sessionId, sessionName) {
    // Confirm deletion
    const message = window.safeT 
        ? window.safeT('confirm.deleteSessionAdmin').replace('{name}', sessionName)
        : `Are you sure you want to delete session "${sessionName}"?\n\nThis action cannot be undone and will also delete all associated learner data.`;
    const confirmed = confirm(message);
    
    if (!confirmed) return;

    try {
        const token = authManager.getToken();
        if (!token) {
            showAlert(window.safeT ? window.safeT('message.deleteSessionLoginRequired') : 'Please login to delete sessions.', 'error');
            return;
        }

        const response = await fetch(`/api/admin/sessions/${sessionId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                showAlert(window.safeT ? window.safeT('message.sessionExpired') : 'Session expired. Please login again.', 'error');
                authManager.logout();
                return;
            } else if (response.status === 403) {
                showAlert(window.safeT ? window.safeT('message.deleteSessionAccessDenied') : 'Access denied. You can only delete sessions as an administrator.', 'error');
                return;
            } else if (response.status === 404) {
                showAlert(window.safeT ? window.safeT('message.sessionNotFound') : 'Session not found.', 'error');
                return;
            }
            throw new Error(`Delete failed: ${response.status}`);
        }

        showAlert(window.safeT ? window.safeT('message.sessionDeleted') : 'Session deleted successfully!', 'success');
        
        // Refresh the sessions list
        if (window.adminDashboard) {
            window.adminDashboard.loadSessionsOverview();
        }

    } catch (error) {
        console.error('Delete error:', error);
        showAlert(window.safeT ? window.safeT('message.sessionDeleteFailed') : 'Failed to delete session. Please try again.', 'error');
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