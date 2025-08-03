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
    'session.filter': 'Filtrer',
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
    
    // PHASE 4: Popovers d'introduction de l'interface
    'intro.chatInput.title': '💬 Zone de Chat',
    'intro.chatInput.content': 'Posez vos questions à votre formateur IA ici. Il vous aidera à comprendre le contenu et répondra à vos doutes.',
    'intro.voiceChat.title': '🎤 Reconnaissance Vocale',
    'intro.voiceChat.content': 'Cliquez pour parler directement à votre formateur IA. Votre voix sera convertie en texte.',
    'intro.audioToggle.title': '🔊 Audio des Réponses',
    'intro.audioToggle.content': 'Activez cette option pour entendre les réponses de l\'IA à voix haute.',
    'intro.vocalChat.title': '🗣️ Conversation Vocale',
    'intro.vocalChat.content': 'Démarrez une conversation vocale en temps réel avec l\'IA Gemini.',
    'intro.nextButton.title': '➡️ Navigation Suivante',
    'intro.nextButton.content': 'Naviguez entre les slides de votre formation personnalisée.',
    'intro.previousButton.title': '⬅️ Navigation Précédente', 
    'intro.previousButton.content': 'Naviguez entre les slides de votre formation personnalisée.',
    'intro.simplifyButton.title': '📝 Simplifier le Contenu',
    'intro.simplifyButton.content': 'Demandez une version simplifiée du contenu actuel.',
    'intro.moreDetailsButton.title': '🔍 Plus de Détails',
    'intro.moreDetailsButton.content': 'Obtenez plus de détails et d\'approfondissement sur le sujet.',
    'intro.chartButton.title': '📊 Générer un Graphique',
    'intro.chartButton.content': 'Générez un graphique ou diagramme pour illustrer le contenu.',
    'intro.closeButton': 'Compris',
    'intro.closeButtonTooltip': 'Fermer cette aide',
    
    // Phase 3: Modal de limitation des slides
    'learner.slideLimitTitle': 'Limite de formation gratuite atteinte',
    'learner.slideLimitMessage': 'Vous avez atteint la limite de l\'aperçu gratuit de 10 slides.',
    'learner.slideLimitContact': 'Pour continuer votre formation personnalisée, veuillez nous contacter :',
    'learner.slideLimitThanks': 'Merci d\'avoir essayé la formation IA FIA v3.0 !',
    'learner.backToHome': 'Retour à l\'accueil',
    
    // Page d'accueil
    'landing.title': 'Sur quoi souhaitez-vous vous former ?',
    'landing.placeholder': 'Exemple : Gestion de projet, Marketing digital...',
    'landing.startButton': 'Démarrer ma formation',
    'landing.brandName': 'Dice3.ai',
    
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
    'contact.support': 'Contacter le support : jerome.iavarone@gmail.com',
    
    // Nouvelles clés i18n ajoutées pour la Phase 1
    'status.simplifying': 'Simplification...',
    'status.addingDetails': 'Ajout de détails...',
    'status.creating': 'Création...',
    'status.connecting': 'Connexion...',
    'status.connected': 'Connecté',
    'status.redirecting': 'Redirection...',
    'status.active': 'Actif',
    'status.inactive': 'Inactif',
    'status.loadingSessions': 'Chargement des sessions...',
    
    'learner.complete': 'Terminé',
    'learner.beginning': 'Début',
    'learner.limitReached': 'Limite atteinte',
    
    'session.noTrainings': 'Aucune formation disponible - créez-en une d\'abord',
    'session.noSessions': 'Aucune session créée pour le moment',
    'session.createFirst': 'Créez votre première session avec le formulaire',
    
    'validation.correctErrors': 'Veuillez corriger les erreurs ci-dessus',
    'validation.requiredFields': 'Veuillez remplir tous les champs obligatoires',
    'validation.firstNameRequired': 'Le prénom est requis',
    'validation.lastNameRequired': 'Le nom de famille est requis',
    'validation.passwordsDoNotMatch': 'Les mots de passe ne correspondent pas',
    'validation.confirmPassword': 'Veuillez confirmer votre mot de passe',
    
    'success.linkCopied': 'Lien de session copié dans le presse-papiers !',
    'success.redirecting': 'Redirection...',
    
    'error.copyFailed': 'Échec de la copie du lien. Veuillez copier manuellement.',
    'error.registrationFailed': 'Échec de l\'inscription. Veuillez réessayer.',
    'error.navigation': 'Erreur de navigation',
    
    'warning.deleteSession': 'Êtes-vous sûr de vouloir supprimer cette session ? Cette action ne peut pas être annulée.',
    
    'button.stop': 'Arrêter',
    
    // Clés d'erreur API backend (Phase 3)
    'error.auth.adminRequired': 'Privilèges administrateur requis',
    'error.api.trainersOverview': 'Échec de récupération de l\'aperçu des formateurs',
    'error.api.traineesOverview': 'Échec de récupération de l\'aperçu des apprenants',
    'error.api.trainingsOverview': 'Échec de récupération de l\'aperçu des formations',
    'error.api.sessionsOverview': 'Échec de récupération de l\'aperçu des sessions',
    'error.api.adminStatistics': 'Échec de récupération des statistiques admin',
    'error.api.platformHealth': 'Échec de récupération des métriques de santé de la plateforme',
    'error.api.trainerDetails': 'Échec de récupération des détails du formateur',
    
    // Erreurs de validation de fichier
    'error.file.noFile': 'Aucun fichier fourni',
    'error.file.invalidType': 'Type de fichier non autorisé. Formats supportés : PDF, PPT, PPTX',
    'error.file.empty': 'Le fichier est vide',
    'error.file.tooLarge': 'Fichier trop volumineux. Taille maximale : 50MB',
    'error.file.invalidMimeType': 'Type de fichier invalide. Attendu : PDF, PPT ou PPTX',
    
    // Validation de formation
    'validation.trainingNameRequired': 'Le nom de la formation ne peut pas être vide',
    'validation.aiTrainingDescriptionRequired': 'La description est requise pour les formations générées par IA',
    
    // Clés de formation supplémentaires
    'training.noTrainings': 'Aucune formation pour le moment',
    'training.createFirst': 'Créez votre première formation pour commencer !',
    'training.noFile': 'Aucun fichier',
    'training.noDescription': 'Aucune description',
    
    // Clés de session supplémentaires
    'session.noConversations': 'Aucune conversation trouvée pour cette session',
    'session.noChats': 'Les apprenants n\'ont pas encore commencé à discuter',
    
    // Clés de validation supplémentaires
    'validation.selectDate': 'Veuillez sélectionner au moins une date pour filtrer'
};

export default fr;