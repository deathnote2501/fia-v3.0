/**
 * FIA v3.0 - English Translations
 * Translation keys for trainer and learner interface
 */

export const en = {
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
    
    // Contextual actions
    'action.comment': 'Comment',
    'action.quiz': 'Quiz',
    'action.examples': 'Examples',
    'action.keyPoints': 'Key Points',
    
    // Tooltips
    'tooltip.comment': 'Ask for comments or feedback on this slide',
    'tooltip.quiz': 'Generate a quiz to test your understanding',
    'tooltip.examples': 'Get practical examples related to this content',
    'tooltip.keyPoints': 'Highlight the key points of this slide',
    'tooltip.vocal': 'Start Live Voice Conversation with Gemini',
    'tooltip.voice': 'Click to start voice recording',
    
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
    'contact.support': 'Contact support: jerome.iavarone@gmail.com'
};

export default en;