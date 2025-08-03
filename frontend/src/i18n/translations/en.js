/**
 * FIA v3.0 - English Translations
 * Translation keys for trainer and learner interface
 */

export const en = {
    // Page titles
    'page.title.trainer': 'Dashboard',
    'page.title.login': 'Trainer Login - FIA v3.0',
    'page.title.register': 'Trainer Registration - FIA v3.0',
    'page.title.admin': 'Admin Dashboard - FIA v3.0',
    'page.title.training': 'FIA v3.0 - Personal Training Plan',
    'page.title.landing': 'Get trained by an AI trainer',
    
    // Navigation and main title
    'app.title': 'FIA v3.0 Trainer',
    'nav.dashboard': 'Dashboard',
    'nav.training': 'Training',
    'nav.session': 'Session',
    'nav.profile': 'Profile',
    'nav.logout': 'Logout',
    
    // Dashboard
    'dashboard.title': 'Dashboard',
    'dashboard.trainings': 'Trainings',
    'dashboard.sessions': 'Active Sessions',
    'dashboard.learners': 'Unique Learners',
    'dashboard.totalTime': 'Total Time',
    'dashboard.slidesViewed': 'Slides Viewed',
    'dashboard.totalSlides': 'Total Slides',
    'dashboard.recentActivity': 'Recent Activity',
    'dashboard.noActivity': 'No recent activity',
    'dashboard.training': 'Training',
    'dashboard.createNewTraining': 'Create New Training',
    'dashboard.myTrainings': 'My Trainings',
    'dashboard.newSession': 'New Session',
    'dashboard.refreshTrainings': 'Refresh trainings list',
    
    // Training
    'training.title': 'Training',
    'training.create': 'Create New Training',
    'training.name': 'Training Name',
    'training.description': 'Description',
    'training.file': 'Upload Training Material',
    'training.fileSupport': 'Supported formats: PDF, PPT, PPTX (Max: 50MB)',
    'training.aiGenerated': 'Generated with AI',
    'training.generateWithAI': 'Generate Training with AI',
    'training.aiToggleHelp': 'Generate training content automatically using AI instead of uploading a file',
    'training.myTrainings': 'My Trainings',
    'training.refresh': 'Refresh',
    'training.loading': 'Loading trainings...',
    
    // Session
    'session.title': 'Session',
    'session.new': 'New Session',
    'session.selectTraining': 'Select Training',
    'session.chooseTraining': 'Choose a training...',
    'session.refreshTrainings': 'Refresh trainings list',
    'session.selectTrainingHelp': 'Select the training material for this session',
    'session.name': 'Session Name',
    'session.namePlaceholder': 'e.g., Morning Session - Team A',
    'session.description': 'Description',
    'session.descriptionPlaceholder': 'Optional description for this session',
    'session.generateLink': 'Generate Session Link',
    'session.linkGenerated': 'Session Created Successfully!',
    'session.shareLink': 'Share this link with your learners:',
    'session.copyLink': 'Copy link to clipboard',
    'session.linkHelp': 'Learners will use this link to access the training session',
    'session.details': 'Sessions Details',
    'session.filter': 'Filter',
    'session.sessionName': 'Session Name',
    'session.training': 'Training',
    'session.created': 'Created',
    'session.learners': 'Learners',
    'session.status': 'Status',
    'session.actions': 'Actions',
    'session.loadingSessions': 'Loading sessions...',
    
    // Profile
    'profile.title': 'Profile',
    'profile.firstName': 'First Name',
    'profile.lastName': 'Last Name',
    'profile.email': 'Email',
    'profile.language': 'Preferred Language',
    'profile.cancel': 'Cancel',
    'profile.saveChanges': 'Save Changes',
    
    // Form labels
    'form.label.email': 'Email Address',
    'form.label.firstName': 'First Name',
    'form.label.lastName': 'Last Name',
    'form.label.password': 'Password',
    'form.label.confirmPassword': 'Confirm Password',
    'form.label.trainingName': 'Training Name',
    'form.label.description': 'Description',
    'form.label.uploadMaterial': 'Upload Training Material',
    'form.label.selectTraining': 'Select Training',
    'form.label.sessionName': 'Session Name',
    'form.label.sessionDescription': 'Description',
    'form.label.rememberMe': 'Remember me',
    'form.label.agreeTerms': 'I agree to the <a href="#" class="text-primary">Terms of Service</a> and <a href="#" class="text-primary">Privacy Policy</a>',
    'form.label.aiGenerated': 'Generated with AI',
    
    // Form help texts
    'form.text.passwordMin': 'Minimum 8 characters',
    'form.text.fileFormats': 'Supported formats: PDF, PPT, PPTX (Max: 50MB)',
    'form.text.selectTrainingHelp': 'Select the training material for this session',
    'form.text.alreadyAccount': 'Already have an account?',
    'form.text.noAccount': 'Don\'t have an account?',
    'form.text.forgotPassword': 'Forgot your password?',
    
    // Common actions
    'button.create': 'Create',
    'button.save': 'Save',
    'button.cancel': 'Cancel',
    'button.delete': 'Delete',
    'button.edit': 'Edit',
    'button.download': 'Download',
    'button.refresh': 'Refresh',
    'button.close': 'Close',
    'button.copy': 'Copy',
    
    // Status messages
    'status.loading': 'Loading...',
    'status.saving': 'Saving...',
    'status.success': 'Success',
    'status.error': 'Error',
    'status.noData': 'No data available',
    'status.aiGenerating': 'AI is generating your training content...',
    'status.preparingUpload': 'Preparing upload...',
    'status.uploading': 'Uploading...',
    'status.uploadComplete': 'Upload complete!',
    'status.aiGenerated': 'AI training generated successfully!',
    'status.aiGenerationFailed': 'AI generation failed',
    'status.uploadFailed': 'Upload failed',
    'status.validatingSession': 'Validating Session',
    'status.validatingSessionMessage': 'Please wait while we verify your session token...',
    'status.generatingPlan': 'Generating Your Personalized Training Plan',
    'status.generatingPlanMessage': 'This may take a few moments...',
    'status.loadingSession': 'Loading Your Training Session',
    'status.loadingSessionMessage': 'Loading your current slide...',
    
    // Generic loading messages
    'status.loadingGeneric': 'Loading...',
    'status.loadingTrainings': 'Loading trainings...',
    'status.loadingSlideContent': 'Loading slide content...',
    'status.loadingData': 'Loading data...',
    
    // Learner training (training.html)
    'learner.trainingPlan': 'Training Plan',
    'learner.askTrainer': 'Ask your AI trainer...',
    'learner.enableAudio': 'Enable Audio',
    'learner.vocal': 'Vocal',
    'learner.previous': 'Previous',
    'learner.next': 'Next',
    'learner.simplify': 'Simplify',
    'learner.deepen': 'Deepen',
    'learner.chart': 'Chart',
    'learner.image': 'Image',
    
    // PHASE 4: Interface introduction popovers
    'intro.chatInput.title': '💬 Chat Zone',
    'intro.chatInput.content': 'Ask your AI trainer questions here. It will help you understand the content and answer your doubts.',
    'intro.voiceChat.title': '🎤 Voice Recognition',
    'intro.voiceChat.content': 'Click to speak directly to your AI trainer. Your voice will be converted to text.',
    'intro.audioToggle.title': '🔊 Audio Responses',
    'intro.audioToggle.content': 'Enable this option to hear AI responses out loud.',
    'intro.vocalChat.title': '🗣️ Voice Conversation',
    'intro.vocalChat.content': 'Start a real-time voice conversation with Gemini AI.',
    'intro.nextButton.title': '➡️ Next Navigation',
    'intro.nextButton.content': 'Navigate between the slides of your personalized training.',
    'intro.previousButton.title': '⬅️ Previous Navigation',
    'intro.previousButton.content': 'Navigate between the slides of your personalized training.',
    'intro.simplifyButton.title': '📝 Simplify Content',
    'intro.simplifyButton.content': 'Request a simplified version of the current content.',
    'intro.moreDetailsButton.title': '🔍 More Details',
    'intro.moreDetailsButton.content': 'Get more details and deeper insights on the subject.',
    'intro.chartButton.title': '📊 Generate Chart',
    'intro.chartButton.content': 'Generate a chart or diagram to illustrate the content.',
    'intro.closeButton': 'Got it',
    'intro.closeButtonTooltip': 'Close this help',
    
    // Phase 3: Slide Limitation Modal
    'learner.slideLimitTitle': 'Free Training Limit Reached',
    'learner.slideLimitMessage': 'You have reached the free preview limit of 10 slides.',
    'learner.slideLimitContact': 'To continue your personalized training, please contact us:',
    'learner.slideLimitThanks': 'Thank you for trying FIA v3.0 AI-powered training!',
    'learner.backToHome': 'Back to Home',
    
    // Landing Page
    'landing.title': 'What would you like to learn about?',
    'landing.placeholder': 'Example: Project management, Digital marketing...',
    'landing.startButton': 'Start My Training',
    'landing.brandName': 'Dice3.ai',
    'landing.progress.generating': 'Your AI trainer is creating your personalized training...',
    'landing.progress.status': 'Starting AI generation...',
    'landing.progress.analyzing': 'Analyzing your topic...',
    'landing.progress.creating': 'AI is creating your personalized content...',
    'landing.progress.generatingSlides': 'Generating interactive slides...',
    'landing.progress.preparing': 'Preparing your learning experience...',
    'landing.progress.finalizing': 'Almost ready! Finalizing details...',
    'landing.progress.ready': 'Training ready! Redirecting...',
    
    // Contextual actions
    'action.comment': 'Comment',
    'action.quiz': 'Quiz',
    'action.examples': 'Examples',
    'action.keyPoints': 'Key Points',

    // Chat button labels
    'chat.comment': 'Comment',
    'chat.quiz': 'Quiz',
    'chat.examples': 'Examples',
    'chat.keyPoints': 'Key Points',
    
    // Tooltips
    'tooltip.comment': 'Ask for comments or feedback on this slide',
    'tooltip.quiz': 'Generate a quiz to test your understanding',
    'tooltip.examples': 'Get practical examples related to this content',
    'tooltip.keyPoints': 'Highlight the key points of this slide',
    'tooltip.vocal': 'Start Live Voice Conversation with Gemini',
    'tooltip.voice': 'Click to start voice recording',
    'tooltip.previous': 'Go to previous slide',
    'tooltip.next': 'Go to next slide',
    'tooltip.simplify': 'Simplify the content of this slide',
    'tooltip.deepen': 'Get more details about this content',
    'tooltip.chart': 'Generate a chart to illustrate this content',
    'tooltip.image': 'Generate an image to illustrate this content',
    
    // Error messages
    'error.generic': 'An error occurred',
    'error.loadingTrainings': 'Error loading trainings',
    'error.loadingSessions': 'Error loading sessions',
    'error.loadingData': 'Error loading data',
    'error.network': 'Network connection failed. Please check your internet connection.',
    'error.server': 'Server error occurred. Please try again later.',
    'error.database': 'Database connection error. Please contact support.',
    'error.auth.failed': 'Authentication failed. Please check your credentials.',
    'error.auth.system': 'Authentication system error. Please contact support.',
    'error.validation': 'Please check your input and try again.',
    'error.file.upload': 'File upload failed. Please try again.',
    'error.file.size': 'File size too large. Maximum size is 50MB.',
    'error.file.format': 'Unsupported file format. Please use PDF, PPT, or PPTX.',
    'error.api.critical': 'Critical API error occurred. Please contact support.',
    'error.unexpected': 'An unexpected error occurred. Please contact support.',
    'error.system': 'System error. Please contact support.',
    'error.timeout': 'Request timed out. Please try again.',
    'error.forbidden': 'Access denied. You do not have permission for this action.',
    'error.notfound': 'Requested resource not found.',
    'error.session.expired': 'Your session has expired. Please log in again.',
    'error.session.invalid': 'Invalid session. Please log in again.',
    
    // Success messages
    'success.saved': 'Successfully saved!',
    'success.created': 'Successfully created!',
    'success.updated': 'Successfully updated!',
    'success.deleted': 'Successfully deleted!',
    'success.uploaded': 'File uploaded successfully!',
    'success.login': 'Login successful!',
    'success.logout': 'Logout successful!',
    'success.registered': 'Account created successfully!',
    
    // Warning messages
    'warning.unsaved': 'You have unsaved changes.',
    'warning.delete': 'This action cannot be undone.',
    'warning.session.expiring': 'Your session will expire soon.',
    
    // Info messages
    'info.loading': 'Loading...',
    'info.processing': 'Processing your request...',
    'info.uploading': 'Uploading file...',
    
    // Contact support
    'contact.support': 'Contact support: jerome.iavarone@gmail.com',
    
    // New i18n keys added for Phase 1
    'status.simplifying': 'Simplifying...',
    'status.generating': 'Generating...',
    'status.addingDetails': 'Adding details...',
    'status.creating': 'Creating...',
    'status.connecting': 'Connecting...',
    'status.connected': 'Connected',
    'status.redirecting': 'Redirecting...',
    'status.active': 'Active',
    'status.inactive': 'Inactive',
    'status.loadingSessions': 'Loading sessions...',
    
    'learner.complete': 'Complete',
    'learner.beginning': 'Beginning',
    'learner.limitReached': 'Limit Reached',
    
    'session.noTrainings': 'No trainings available - create one first',
    'session.noSessions': 'No sessions created yet',
    'session.createFirst': 'Create your first session using the form',
    
    'validation.correctErrors': 'Please correct the errors above',
    'validation.requiredFields': 'Please fill in all required fields',
    'validation.firstNameRequired': 'First name is required',
    'validation.lastNameRequired': 'Last name is required',
    'validation.passwordsDoNotMatch': 'Passwords do not match',
    'validation.confirmPassword': 'Please confirm your password',
    
    'success.linkCopied': 'Session link copied to clipboard!',
    'success.redirecting': 'Redirecting...',
    
    'error.copyFailed': 'Failed to copy link. Please copy manually.',
    'error.registrationFailed': 'Registration failed. Please try again.',
    'error.navigation': 'Navigation error',
    
    'warning.deleteSession': 'Are you sure you want to delete this session? This action cannot be undone.',
    
    'button.stop': 'Stop',
    
    // Backend API error keys (Phase 3)
    'error.auth.adminRequired': 'Admin privileges required',
    'error.api.trainersOverview': 'Failed to retrieve trainers overview',
    'error.api.traineesOverview': 'Failed to retrieve trainees overview',
    'error.api.trainingsOverview': 'Failed to retrieve trainings overview',
    'error.api.sessionsOverview': 'Failed to retrieve sessions overview',
    'error.api.adminStatistics': 'Failed to retrieve admin statistics',
    'error.api.platformHealth': 'Failed to retrieve platform health metrics',
    'error.api.trainerDetails': 'Failed to retrieve trainer details',
    
    // File validation errors
    'error.file.noFile': 'No file provided',
    'error.file.invalidType': 'File type not allowed. Supported formats: PDF, PPT, PPTX',
    'error.file.empty': 'File is empty',
    'error.file.tooLarge': 'File too large. Maximum size: 50MB',
    'error.file.invalidMimeType': 'Invalid file type. Expected: PDF, PPT, or PPTX',
    
    // Training validation
    'validation.trainingNameRequired': 'Training name cannot be empty',
    'validation.aiTrainingDescriptionRequired': 'Description is required for AI-generated trainings',
    
    // Additional training keys
    'training.noTrainings': 'No trainings yet',
    'training.createFirst': 'Create your first training to get started!',
    'training.noFile': 'No file',
    'training.noDescription': 'No description',
    
    // Additional session keys
    'session.noConversations': 'No conversations found for this session',
    'session.noChats': 'Learners haven\'t started chatting yet',
    
    // Additional validation keys
    'validation.selectDate': 'Please select at least one date to filter',
    
    // JavaScript alert messages
    'message.aiDescriptionRequired': 'Please provide a detailed description for AI generation.',
    'message.fileRequired': 'Please select a file to upload.',
    'message.sessionCreated': 'Session created successfully!',
    'message.sessionCreateFailed': 'Failed to create session. Please try again.',
    'message.profileUpdated': 'Profile updated successfully!',
    'message.profileUpdateFailed': 'Profile update failed.',
    'message.profileUpdateError': 'Failed to update profile. Please try again.',
    'message.invalidFileType': 'Invalid file type. Please select a PDF, PPT, or PPTX file.',
    'message.fileTooLarge': 'File too large. Maximum size is 50MB.',
    'message.loginRequired': 'Please login to download files.',
    'message.sessionExpired': 'Session expired. Please login again.',
    'message.accessDenied': 'Access denied. You can only download your own files.',
    'message.fileNotFound': 'File not found.',
    'message.downloadStarted': 'Download started!',
    'message.downloadFailed': 'Failed to download file. Please try again.',
    'message.deleteTrainingConfirm': 'Are you sure you want to delete "{name}"?\\n\\nThis action cannot be undone and will also delete the associated file.',
    'message.deleteTrainingLoginRequired': 'Please login to delete trainings.',
    'message.deleteTrainingAccessDenied': 'Access denied. You can only delete your own trainings.',
    'message.deleteTrainingNotFound': 'Training not found.',
    'message.trainingDeleted': 'Training deleted successfully!',
    'message.trainingDeleteFailed': 'Failed to delete training. Please try again.',
    'message.sessionReportDownloadStarted': 'Session report download started!',
    'message.sessionReportDownloadFailed': 'Failed to download session report. Please try again.',
    'message.deleteSessionLoginRequired': 'Please login to delete sessions.',
    'message.deleteSessionAccessDenied': 'Access denied. You can only delete sessions as an administrator.',
    'message.sessionNotFound': 'Session not found.',
    'message.sessionDeleted': 'Session deleted successfully!',
    'message.sessionDeleteFailed': 'Failed to delete session. Please try again.',
    'message.deleteSessionConfirm': 'Are you sure you want to delete session "{name}"?\\n\\nThis action cannot be undone and will also delete all associated learner data.',
    
    // Confirmation messages (confirm.* pattern)
    'confirm.deleteTraining': 'Are you sure you want to delete "{name}"?\\n\\nThis action cannot be undone and will also delete the associated file.',
    'confirm.deleteSession': 'Are you sure you want to delete this session?\\n\\nThis action cannot be undone.',
    'confirm.deleteSessionAdmin': 'Are you sure you want to delete session "{name}"?\\n\\nThis action cannot be undone and will also delete all associated learner data.'
};

export default en;