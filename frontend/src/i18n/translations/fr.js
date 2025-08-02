/**
 * FIA v3.0 - Traductions Françaises
 * Clés de traduction pour l'interface formateur et apprenant
 */

export const fr = {
    // Navigation et titre principal
    'app.title': 'FIA v3.0 Trainer',
    'nav.dashboard': 'Tableau de bord',
    'nav.training': 'Formation',
    'nav.session': 'Session',
    'nav.profile': 'Profil',
    'nav.logout': 'Déconnexion',
    
    // Dashboard
    'dashboard.title': 'Tableau de bord',
    'dashboard.trainings': 'Formations',
    'dashboard.sessions': 'Sessions actives',
    'dashboard.learners': 'Apprenants uniques',
    'dashboard.totalTime': 'Temps total',
    'dashboard.slidesViewed': 'Slides vues',
    'dashboard.totalSlides': 'Total slides',
    'dashboard.recentActivity': 'Activité récente',
    'dashboard.noActivity': 'Aucune activité récente',
    
    // Formation
    'training.title': 'Formation',
    'training.create': 'Créer une nouvelle formation',
    'training.name': 'Nom de la formation',
    'training.description': 'Description',
    'training.file': 'Matériel de formation',
    'training.fileSupport': 'Formats supportés : PDF, PPT, PPTX (Max : 50MB)',
    'training.aiGenerated': 'Générée avec IA',
    'training.generateWithAI': 'Générer la formation avec IA',
    'training.aiToggleHelp': 'Générer automatiquement le contenu de formation avec IA au lieu de télécharger un fichier',
    'training.myTrainings': 'Mes formations',
    'training.refresh': 'Actualiser',
    'training.loading': 'Chargement des formations...',
    
    // Session
    'session.title': 'Session',
    'session.new': 'Nouvelle session',
    'session.selectTraining': 'Sélectionner une formation',
    'session.chooseTraining': 'Choisir une formation...',
    'session.refreshTrainings': 'Actualiser la liste des formations',
    'session.selectTrainingHelp': 'Sélectionner le matériel de formation pour cette session',
    'session.name': 'Nom de la session',
    'session.namePlaceholder': 'ex: Session matinale - Équipe A',
    'session.description': 'Description',
    'session.descriptionPlaceholder': 'Description optionnelle pour cette session',
    'session.generateLink': 'Générer le lien de session',
    'session.linkGenerated': 'Session créée avec succès !',
    'session.shareLink': 'Partagez ce lien avec vos apprenants :',
    'session.copyLink': 'Copier le lien dans le presse-papiers',
    'session.linkHelp': 'Les apprenants utiliseront ce lien pour accéder à la session de formation',
    'session.details': 'Détails des sessions',
    'session.sessionName': 'Nom de la session',
    'session.training': 'Formation',
    'session.created': 'Créée',
    'session.learners': 'Apprenants',
    'session.status': 'Statut',
    'session.actions': 'Actions',
    'session.loadingSessions': 'Chargement des sessions...',
    
    // Profil
    'profile.title': 'Profil',
    'profile.firstName': 'Prénom',
    'profile.lastName': 'Nom de famille',
    'profile.email': 'Email',
    'profile.language': 'Langue préférée',
    'profile.cancel': 'Annuler',
    'profile.saveChanges': 'Sauvegarder les modifications',
    
    // Actions communes
    'button.create': 'Créer',
    'button.save': 'Sauvegarder',
    'button.cancel': 'Annuler',
    'button.delete': 'Supprimer',
    'button.edit': 'Modifier',
    'button.download': 'Télécharger',
    'button.refresh': 'Actualiser',
    'button.close': 'Fermer',
    'button.copy': 'Copier',
    
    // Messages d'état
    'status.loading': 'Chargement...',
    'status.saving': 'Sauvegarde...',
    'status.success': 'Succès',
    'status.error': 'Erreur',
    'status.noData': 'Aucune donnée disponible',
    'status.aiGenerating': 'L\'IA génère votre contenu de formation...',
    'status.preparingUpload': 'Préparation du téléchargement...',
    'status.uploading': 'Téléchargement...',
    'status.uploadComplete': 'Téléchargement terminé !',
    'status.aiGenerated': 'Formation IA générée avec succès !',
    'status.aiGenerationFailed': 'Échec de la génération IA',
    'status.uploadFailed': 'Échec du téléchargement',
    'status.validatingSession': 'Validation de la session',
    'status.validatingSessionMessage': 'Veuillez patienter pendant que nous vérifions votre token de session...',
    'status.generatingPlan': 'Génération de votre plan de formation personnalisé',
    'status.generatingPlanMessage': 'Cela peut prendre quelques instants...',
    'status.loadingSession': 'Chargement de votre session de formation',
    'status.loadingSessionMessage': 'Chargement de votre diapositive actuelle...',
    
    // Messages de chargement génériques
    'status.loadingGeneric': 'Chargement...',
    'status.loadingTrainings': 'Chargement des formations...',
    'status.loadingSlideContent': 'Chargement du contenu des diapositives...',
    'status.loadingData': 'Chargement des données...',
    
    // Formation des apprenants (training.html)
    'learner.trainingPlan': 'Plan de formation',
    'learner.askTrainer': 'Demandez à votre formateur IA...',
    'learner.enableAudio': 'Activer l\'audio',
    'learner.vocal': 'Vocal',
    'learner.previous': 'Précédent',
    'learner.next': 'Suivant',
    'learner.simplify': 'Simplifier',
    'learner.deepen': 'Approfondir',
    'learner.chart': 'Graphique',
    'learner.image': 'Image',
    
    // Actions contextuelles
    'action.comment': 'Commenter',
    'action.quiz': 'Quiz',
    'action.examples': 'Exemples',
    'action.keyPoints': 'Points clés',
    
    // Tooltips
    'tooltip.comment': 'Demander des commentaires ou avis sur cette diapositive',
    'tooltip.quiz': 'Générer un quiz pour tester votre compréhension',
    'tooltip.examples': 'Obtenir des exemples pratiques liés à ce contenu',
    'tooltip.keyPoints': 'Mettre en évidence les points clés de cette diapositive',
    'tooltip.vocal': 'Démarrer une conversation vocale en direct avec Gemini',
    'tooltip.voice': 'Cliquer pour commencer l\'enregistrement vocal',
    
    // Messages d'erreur
    'error.generic': 'Une erreur est survenue',
    'error.loadingTrainings': 'Erreur lors du chargement des formations',
    'error.loadingSessions': 'Erreur lors du chargement des sessions',
    'error.loadingData': 'Erreur lors du chargement des données',
    'error.network': 'Échec de la connexion réseau. Veuillez vérifier votre connexion internet.',
    'error.server': 'Erreur serveur. Veuillez réessayer plus tard.',
    'error.database': 'Erreur de connexion à la base de données. Veuillez contacter le support.',
    'error.auth.failed': 'Échec de l\'authentification. Veuillez vérifier vos identifiants.',
    'error.auth.system': 'Erreur système d\'authentification. Veuillez contacter le support.',
    'error.validation': 'Veuillez vérifier votre saisie et réessayer.',
    'error.file.upload': 'Échec du téléchargement de fichier. Veuillez réessayer.',
    'error.file.size': 'Taille de fichier trop importante. Maximum 50MB.',
    'error.file.format': 'Format de fichier non supporté. Veuillez utiliser PDF, PPT ou PPTX.',
    'error.api.critical': 'Erreur API critique. Veuillez contacter le support.',
    'error.unexpected': 'Une erreur inattendue s\'est produite. Veuillez contacter le support.',
    'error.system': 'Erreur système. Veuillez contacter le support.',
    'error.timeout': 'Délai d\'attente dépassé. Veuillez réessayer.',
    'error.forbidden': 'Accès refusé. Vous n\'avez pas la permission pour cette action.',
    'error.notfound': 'Ressource demandée non trouvée.',
    'error.session.expired': 'Votre session a expiré. Veuillez vous reconnecter.',
    'error.session.invalid': 'Session invalide. Veuillez vous reconnecter.',
    
    // Messages de succès
    'success.saved': 'Sauvegardé avec succès !',
    'success.created': 'Créé avec succès !',
    'success.updated': 'Mis à jour avec succès !',
    'success.deleted': 'Supprimé avec succès !',
    'success.uploaded': 'Fichier téléchargé avec succès !',
    'success.login': 'Connexion réussie !',
    'success.logout': 'Déconnexion réussie !',
    'success.registered': 'Compte créé avec succès !',
    
    // Messages d'avertissement
    'warning.unsaved': 'Vous avez des modifications non sauvegardées.',
    'warning.delete': 'Cette action ne peut pas être annulée.',
    'warning.session.expiring': 'Votre session va bientôt expirer.',
    
    // Messages d'information
    'info.loading': 'Chargement...',
    'info.processing': 'Traitement de votre demande...',
    'info.uploading': 'Téléchargement du fichier...',
    
    // Contact support
    'contact.support': 'Contacter le support : jerome.iavarone@gmail.com'
};

export default fr;