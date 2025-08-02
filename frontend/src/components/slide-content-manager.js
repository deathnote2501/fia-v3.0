/**
 * FIA v3.0 - Slide Content Manager Component
 * Handles slide content display, markdown processing, and content transformations
 */

export class SlideContentManager {
    constructor() {
        this.currentSlideContent = null; // Store current slide markdown content
        this.container = null; // Main container element
        this.updateBreadcrumb = null; // Callback to update breadcrumb
        this.stopProgressAnimation = null; // Callback to stop progress animation
        
        console.log('🎨 [SLIDE-CONTENT] SlideContentManager initialized');
    }
    
    /**
     * Set the main container element
     * @param {HTMLElement} container - Main container element
     */
    setContainer(container) {
        this.container = container;
        console.log('🎨 [SLIDE-CONTENT] Container set');
    }
    
    /**
     * Set callback to update breadcrumb
     * @param {Function} callback - Breadcrumb update callback
     */
    setUpdateBreadcrumbCallback(callback) {
        this.updateBreadcrumb = callback;
        console.log('🎨 [SLIDE-CONTENT] updateBreadcrumb callback set');
    }
    
    /**
     * Set callback to stop progress animation
     * @param {Function} callback - Stop progress animation callback
     */
    setStopProgressAnimationCallback(callback) {
        this.stopProgressAnimation = callback;
        console.log('🎨 [SLIDE-CONTENT] stopProgressAnimation callback set');
    }
    
    /**
     * Display slide content in the main container
     * @param {Object} slideData - Slide data to display
     * @returns {Object} Processed slide data with title and content
     */
    displaySlideContent(slideData) {
        console.log('🎨 [SLIDE-CONTENT] === DÉBUT ANALYSE DES DONNÉES ===');
        console.log('🎨 [SLIDE-CONTENT] slideData TYPE:', typeof slideData);
        console.log('🎨 [SLIDE-CONTENT] slideData COMPLET:', slideData);
        console.log('🎨 [SLIDE-CONTENT] slideData.title:', slideData.title);
        console.log('🎨 [SLIDE-CONTENT] slideData.slide_content:', slideData.slide_content);
        console.log('🎨 [SLIDE-CONTENT] slideData.content:', slideData.content);
        console.log('🎨 [SLIDE-CONTENT] slideData.slide:', slideData.slide);
        
        // KISS: Extract content directly from the data structure
        // slideData peut contenir slide_content (format JSON), content, ou slide.content
        let title, content;
        
        // Priorité: slide_content d'abord (peu importe si title existe)
        if (slideData.slide_content) {
            console.log('🎯 [SLIDE-CONTENT] BRANCHE 1: slide_content détecté (priorité haute)');
            title = slideData.title || 'Formation Content';
            content = slideData.slide_content;
            console.log('🎯 [SLIDE-CONTENT] BRANCHE 1: title =', title);
            console.log('🎯 [SLIDE-CONTENT] BRANCHE 1: content =', content);
        } else if (slideData.title && slideData.content) {
            // Structure directe
            console.log('🎯 [SLIDE-CONTENT] BRANCHE 2: title + content détectés');
            title = slideData.title;
            content = slideData.content;
            console.log('🎯 [SLIDE-CONTENT] BRANCHE 2: title =', title);
            console.log('🎯 [SLIDE-CONTENT] BRANCHE 2: content =', content);
        } else if (slideData.slide) {
            // Structure avec "slide" wrapper
            console.log('🎯 [SLIDE-CONTENT] BRANCHE 3: slide wrapper détecté');
            title = slideData.slide.title;
            content = slideData.slide.content || slideData.slide.slide_content;
            console.log('🎯 [SLIDE-CONTENT] BRANCHE 3: title =', title);
            console.log('🎯 [SLIDE-CONTENT] BRANCHE 3: content =', content);
        } else {
            // Fallback - essayer de parser si c'est un JSON string contenant slide_content
            console.log('🎯 [SLIDE-CONTENT] BRANCHE 4: FALLBACK - tentative parsing JSON');
            try {
                if (typeof slideData === 'string') {
                    const parsed = JSON.parse(slideData);
                    if (parsed.slide_content) {
                        console.log('🎯 [SLIDE-CONTENT] BRANCHE 4: JSON parsé avec slide_content trouvé');
                        title = parsed.title || 'Formation Content';
                        content = parsed.slide_content;
                    } else {
                        throw new Error('No slide_content in parsed JSON');
                    }
                } else {
                    throw new Error('Not a JSON string');
                }
            } catch (e) {
                console.log('🎯 [SLIDE-CONTENT] BRANCHE 4: VRAI FALLBACK utilisé');
                title = 'Formation Content';
                content = slideData.content || JSON.stringify(slideData);
            }
            console.log('🎯 [SLIDE-CONTENT] BRANCHE 4: title =', title);
            console.log('🎯 [SLIDE-CONTENT] BRANCHE 4: content =', content);
        }
        
        console.log('📝 [SLIDE-CONTENT] EXTRACTION FINALE:');
        console.log('📝 [SLIDE-CONTENT] title FINAL =', title);
        console.log('📝 [SLIDE-CONTENT] content FINAL (type):', typeof content);
        console.log('📝 [SLIDE-CONTENT] content FINAL (longueur):', content ? content.length : 'NULL');
        console.log('📝 [SLIDE-CONTENT] content FINAL (preview):', content ? content.substring(0, 100) + '...' : 'NULL');
        console.log('🎨 [SLIDE-CONTENT] === AVANT PASSAGE À MARKDOWN ===');
        
        // CORRECTION: Vérifier si le contenu est un objet JSON avec slide_content
        if (typeof content === 'object' && content !== null && content.slide_content) {
            console.log('🔧 [SLIDE-CONTENT] CORRECTION: Contenu est un objet JSON avec slide_content');
            content = content.slide_content;
            console.log('🔧 [SLIDE-CONTENT] CORRECTION: Contenu extrait:', content.substring(0, 100) + '...');
        } else if (typeof content === 'string' && content.startsWith('{') && content.includes('slide_content')) {
            console.log('🔧 [SLIDE-CONTENT] CORRECTION: Contenu est une string JSON avec slide_content');
            try {
                const parsed = JSON.parse(content);
                if (parsed.slide_content) {
                    content = parsed.slide_content;
                    console.log('🔧 [SLIDE-CONTENT] CORRECTION: Contenu extrait depuis JSON string:', content.substring(0, 100) + '...');
                }
            } catch (e) {
                console.log('🔧 [SLIDE-CONTENT] CORRECTION: Échec parsing JSON, utilisation contenu original');
            }
        }
        
        // Stocker le contenu markdown original pour les fonctionnalités d'interaction
        this.currentSlideContent = content;
        console.log('💾 [SLIDE-CONTENT] Current slide content stored for interactions');
        
        // Mettre à jour le fil d'Ariane (breadcrumb) via callback
        if (this.updateBreadcrumb) {
            this.updateBreadcrumb(slideData);
        }
        
        // Process and transform content
        const htmlTransformed = this.processSlideContent(content);
        
        // Arrêter l'animation de la progress bar si elle est en cours
        if (this.stopProgressAnimation) {
            this.stopProgressAnimation();
        }
        
        // Update container with processed content
        if (this.container) {
            this.container.innerHTML = `
                <div class="row">
                    <!-- Main slide content (full width) -->
                    <div class="col-lg-12">
                        <!-- Slide content in markdown format -->
                        <div id="slide-content" class="slide-content">
                            ${htmlTransformed}
                        </div>
                    </div>
                </div>
            `;
            
            // Ajouter l'animation slide-in légère
            const slideContentDiv = this.container.querySelector('#slide-content');
            if (slideContentDiv) {
                slideContentDiv.classList.add('slide-animate');
                // Nettoyer la classe après l'animation pour permettre la répétition
                setTimeout(() => {
                    slideContentDiv.classList.remove('slide-animate');
                }, 600); // Durée de l'animation CSS
            }
        }
        
        return { title, content, htmlTransformed };
    }
    
    /**
     * Process slide content with cleaning and markdown conversion
     * @param {string} content - Raw content to process
     * @returns {string} Processed HTML content
     */
    processSlideContent(content) {
        console.log('🔧 [SLIDE-CONTENT] ========== DÉBUT TRANSFORMATION MARKDOWN POUR AFFICHAGE ==========');
        console.log('🔧 [SLIDE-CONTENT] Content brut reçu TYPE:', typeof content);
        console.log('🔧 [SLIDE-CONTENT] Content brut reçu LONGUEUR:', content ? content.length : 'N/A');
        console.log('🔧 [SLIDE-CONTENT] Content brut reçu PREVIEW (500 chars):');
        console.log('🔧 [SLIDE-CONTENT] ---START RAW CONTENT---');
        console.log(content ? content.substring(0, 500) + '...' : 'CONTENT NULL');
        console.log('🔧 [SLIDE-CONTENT] ---END RAW CONTENT---');
        
        // ========== NETTOYAGE AUTOMATIQUE DES BACKTICKS ==========
        let cleanedContent = content;
        if (content.includes('```markdown') || content.includes('```')) {
            console.log('🧹 [SLIDE-CONTENT] DÉTECTION BACKTICKS - Nettoyage automatique');
            
            // Nettoyer les backticks markdown
            cleanedContent = content
                .replace(/^```markdown\s*\n?/i, '')  // Supprimer ```markdown au début
                .replace(/\n?```\s*$/i, '')         // Supprimer ``` à la fin
                .trim();
            
            console.log('🧹 [SLIDE-CONTENT] Content AVANT nettoyage:', content.substring(0, 100));
            console.log('🧹 [SLIDE-CONTENT] Content APRÈS nettoyage:', cleanedContent.substring(0, 100));
        }
        
        // ========== CONVERSION AUTOMATIQUE JSON → MARKDOWN ==========
        if (cleanedContent.trim().startsWith('{') && cleanedContent.includes('"slide"')) {
            console.log('🔄 [SLIDE-CONTENT] DÉTECTION JSON - Conversion automatique vers Markdown');
            
            try {
                const jsonData = JSON.parse(cleanedContent);
                console.log('🔄 [SLIDE-CONTENT] JSON parsé avec succès:', jsonData);
                
                if (jsonData.slide) {
                    const slide = jsonData.slide;
                    let markdownContent = '';
                    
                    // Titre principal
                    if (slide.title) {
                        markdownContent += `# ${slide.title}\n\n`;
                    }
                    
                    // Si c'est un quiz avec questions
                    if (slide.questions && Array.isArray(slide.questions)) {
                        slide.questions.forEach((q, index) => {
                            markdownContent += `- ${q.question}\n`;
                        });
                        
                        if (slide.instructions || slide.instruction) {
                            markdownContent += `\n*${slide.instructions || slide.instruction}*\n`;
                        }
                    }
                    // Si c'est du contenu structuré
                    else if (slide.content) {
                        markdownContent += slide.content;
                    }
                    
                    cleanedContent = markdownContent;
                    console.log('🔄 [SLIDE-CONTENT] Conversion JSON → Markdown réussie');
                    console.log('🔄 [SLIDE-CONTENT] Markdown généré:', cleanedContent.substring(0, 200));
                }
            } catch (e) {
                console.error('❌ [SLIDE-CONTENT] Erreur conversion JSON:', e);
                // Garder le contenu original si la conversion échoue
            }
        }
        
        // Transformer avec markdownToHtml
        const htmlTransformed = this.markdownToHtml(cleanedContent);
        console.log('🔧 [SLIDE-CONTENT] HTML transformé TYPE:', typeof htmlTransformed);
        console.log('🔧 [SLIDE-CONTENT] HTML transformé LONGUEUR:', htmlTransformed ? htmlTransformed.length : 'N/A');
        console.log('🔧 [SLIDE-CONTENT] HTML transformé PREVIEW (500 chars):');
        console.log('🔧 [SLIDE-CONTENT] ---START HTML TRANSFORMED---');
        console.log(htmlTransformed ? htmlTransformed.substring(0, 500) + '...' : 'HTML NULL');
        console.log('🔧 [SLIDE-CONTENT] ---END HTML TRANSFORMED---');
        console.log('🔧 [SLIDE-CONTENT] ========== FIN TRANSFORMATION MARKDOWN POUR AFFICHAGE ==========');
        
        return htmlTransformed;
    }
    
    /**
     * Convert markdown to HTML using marked.js
     * @param {string} markdown - Markdown content to convert
     * @returns {string} HTML content
     */
    markdownToHtml(markdown) {
        console.log('📖 [SLIDE-CONTENT] ============== DÉBUT TRAITEMENT MARKDOWN ==============');
        console.log('📖 [SLIDE-CONTENT] markdown TYPE:', typeof markdown);
        console.log('📖 [SLIDE-CONTENT] markdown NULL/UNDEFINED?', markdown == null);
        console.log('📖 [SLIDE-CONTENT] markdown LONGUEUR:', markdown ? markdown.length : 'N/A');
        console.log('📖 [SLIDE-CONTENT] markdown IS STRING?:', typeof markdown === 'string');
        console.log('📖 [SLIDE-CONTENT] markdown PREVIEW (300 chars):');
        console.log('📖 [SLIDE-CONTENT] ---START PREVIEW---');
        console.log(markdown && typeof markdown === 'string' ? markdown.substring(0, 300) : 'NOT_STRING:', typeof markdown, markdown);
        console.log('📖 [SLIDE-CONTENT] ---END PREVIEW---');
        console.log('📖 [SLIDE-CONTENT] marked DISPONIBLE?:', typeof marked !== 'undefined');
        console.log('📖 [SLIDE-CONTENT] marked.parse DISPONIBLE?:', typeof marked?.parse === 'function');
        
        // Analyse détaillée du contenu
        if (markdown && typeof markdown === 'string') {
            console.log('🔍 [SLIDE-CONTENT] ANALYSE DÉTAILLÉE DU CONTENU:');
            console.log('🔍 [SLIDE-CONTENT] Contient des # (titres)?', markdown.includes('#'));
            console.log('🔍 [SLIDE-CONTENT] Contient des * (listes)?', markdown.includes('*'));
            console.log('🔍 [SLIDE-CONTENT] Contient des | (tableaux)?', markdown.includes('|'));
            console.log('🔍 [SLIDE-CONTENT] Contient des \\n (sauts de ligne)?', markdown.includes('\n'));
            console.log('🔍 [SLIDE-CONTENT] Nombre de sauts de ligne:', (markdown.match(/\n/g) || []).length);
            
            // Afficher les premières et dernières lignes
            const lines = markdown.split('\n');
            console.log('🔍 [SLIDE-CONTENT] Nombre total de lignes:', lines.length);
            console.log('🔍 [SLIDE-CONTENT] Premières 5 lignes:');
            lines.slice(0, 5).forEach((line, index) => {
                console.log(`🔍 [SLIDE-CONTENT] Ligne ${index + 1}: "${line}"`);
            });
            
            if (lines.length > 10) {
                console.log('🔍 [SLIDE-CONTENT] ... (lignes intermédiaires cachées) ...');
                console.log('🔍 [SLIDE-CONTENT] Dernières 3 lignes:');
                lines.slice(-3).forEach((line, index) => {
                    console.log(`🔍 [SLIDE-CONTENT] Ligne ${lines.length - 3 + index + 1}: "${line}"`);
                });
            }
        }
        
        if (!markdown) {
            console.log('⚠️ [SLIDE-CONTENT] CONTENU VIDE - Retour message par défaut');
            const defaultHtml = '<p>Content is being generated...</p>';
            console.log('🔄 [SLIDE-CONTENT] DEFAULT HTML:', defaultHtml);
            return defaultHtml;
        }
        
        try {
            console.log('🔄 [SLIDE-CONTENT] DÉBUT PARSING avec marked.parse...');
            console.log('🔄 [SLIDE-CONTENT] Input exact pour marked.parse:');
            console.log('🔄 [SLIDE-CONTENT] ---START INPUT---');
            console.log(typeof markdown === 'string' ? markdown.substring(0, 500) : 'NOT_STRING:', typeof markdown, markdown);
            console.log('🔄 [SLIDE-CONTENT] ---END INPUT---');
            
            // Vérifier et traiter le contenu markdown
            if (typeof markdown !== 'string') {
                console.error('❌ [SLIDE-CONTENT] markdown n\'est pas une string:', typeof markdown, markdown);
                // Essayer de convertir en string
                if (typeof markdown === 'object' && markdown !== null) {
                    markdown = JSON.stringify(markdown);
                    console.log('🔄 [SLIDE-CONTENT] Conversion objet -> JSON string:', markdown.substring(0, 200));
                } else {
                    markdown = String(markdown);
                    console.log('🔄 [SLIDE-CONTENT] Conversion forcée -> string:', markdown.substring(0, 200));
                }
            }
            
            // Vérifier si le contenu est un JSON avec un champ "markdown"
            if (markdown.startsWith('{') && markdown.includes('"markdown"')) {
                console.log('🔍 [SLIDE-CONTENT] JSON détecté avec champ markdown - extraction...');
                try {
                    const jsonData = JSON.parse(markdown);
                    if (jsonData.markdown) {
                        markdown = jsonData.markdown;
                        console.log('✅ [SLIDE-CONTENT] Markdown extrait du JSON:', markdown.substring(0, 300));
                    } else if (jsonData.slide_content) {
                        markdown = jsonData.slide_content;
                        console.log('✅ [SLIDE-CONTENT] Slide content extrait du JSON:', markdown.substring(0, 300));
                    }
                } catch (e) {
                    console.error('❌ [SLIDE-CONTENT] Erreur parsing JSON:', e);
                }
            }
            
            // KISS: Use marked.js for proper markdown parsing
            const htmlResult = marked.parse(markdown);
            
            console.log('✅ [SLIDE-CONTENT] PARSING RÉUSSI!');
            console.log('📝 [SLIDE-CONTENT] HTML RÉSULTAT TYPE:', typeof htmlResult);
            console.log('📝 [SLIDE-CONTENT] HTML RÉSULTAT LONGUEUR:', htmlResult ? htmlResult.length : 'N/A');
            console.log('📝 [SLIDE-CONTENT] HTML RÉSULTAT IS STRING?:', typeof htmlResult === 'string');
            console.log('📝 [SLIDE-CONTENT] HTML RÉSULTAT PREVIEW (400 chars):');
            console.log('📝 [SLIDE-CONTENT] ---START HTML RESULT---');
            console.log(htmlResult ? htmlResult.substring(0, 400) + '...' : 'NULL');
            console.log('📝 [SLIDE-CONTENT] ---END HTML RESULT---');
            
            // Analyser le HTML généré
            if (htmlResult) {
                console.log('🔍 [SLIDE-CONTENT] ANALYSE HTML GÉNÉRÉ:');
                console.log('🔍 [SLIDE-CONTENT] Contient <h1>?', htmlResult.includes('<h1>'));
                console.log('🔍 [SLIDE-CONTENT] Contient <h2>?', htmlResult.includes('<h2>'));
                console.log('🔍 [SLIDE-CONTENT] Contient <ul>?', htmlResult.includes('<ul>'));
                console.log('🔍 [SLIDE-CONTENT] Contient <table>?', htmlResult.includes('<table>'));
                console.log('🔍 [SLIDE-CONTENT] Contient <p>?', htmlResult.includes('<p>'));
                
                // Compter les balises
                const h1Count = (htmlResult.match(/<h1>/g) || []).length;
                const h2Count = (htmlResult.match(/<h2>/g) || []).length;
                const tableCount = (htmlResult.match(/<table>/g) || []).length;
                const pCount = (htmlResult.match(/<p>/g) || []).length;
                
                console.log('🔍 [SLIDE-CONTENT] Nombre de <h1>:', h1Count);
                console.log('🔍 [SLIDE-CONTENT] Nombre de <h2>:', h2Count);
                console.log('🔍 [SLIDE-CONTENT] Nombre de <table>:', tableCount);
                console.log('🔍 [SLIDE-CONTENT] Nombre de <p>:', pCount);
            }
            
            console.log('📖 [SLIDE-CONTENT] ============== FIN TRAITEMENT MARKDOWN SUCCÈS ==============');
            return htmlResult;
            
        } catch (error) {
            console.error('❌ [SLIDE-CONTENT] ERREUR PARSING:', error);
            console.error('❌ [SLIDE-CONTENT] ERROR MESSAGE:', error.message);
            console.error('❌ [SLIDE-CONTENT] ERROR STACK:', error.stack);
            console.log('🔄 [SLIDE-CONTENT] FALLBACK: Conversion simple \\n -> <br>');
            
            // Fallback to plain text with line breaks
            const fallbackResult = markdown.replace(/\n/g, '<br>');
            console.log('📝 [SLIDE-CONTENT] FALLBACK RÉSULTAT LONGUEUR:', fallbackResult.length);
            console.log('📝 [SLIDE-CONTENT] FALLBACK RÉSULTAT PREVIEW (300 chars):', fallbackResult.substring(0, 300) + '...');
            console.log('📖 [SLIDE-CONTENT] ============== FIN TRAITEMENT MARKDOWN FALLBACK ==============');
            return fallbackResult;
        }
    }
    
    /**
     * Get current slide markdown content
     * @returns {string} Current slide markdown content
     */
    getCurrentSlideMarkdown() {
        return this.currentSlideContent || 'No slide content available';
    }
    
    /**
     * Update current slide content
     * @param {string} content - New slide content
     */
    updateCurrentSlideContent(content) {
        this.currentSlideContent = content;
        console.log('💾 [SLIDE-CONTENT] Current slide content updated');
    }
    
    /**
     * Get current slide content element
     * @returns {HTMLElement|null} Slide content element
     */
    getCurrentSlideElement() {
        return document.getElementById('slide-content');
    }
    
    /**
     * Update slide content HTML directly
     * @param {string} htmlContent - New HTML content
     */
    updateSlideHTML(htmlContent) {
        const slideContentEl = this.getCurrentSlideElement();
        if (slideContentEl) {
            slideContentEl.innerHTML = htmlContent;
            console.log('🎨 [SLIDE-CONTENT] Slide HTML updated directly');
        }
    }
    
    /**
     * Clear slide content
     */
    clearSlideContent() {
        if (this.container) {
            this.container.innerHTML = `<p>${window.safeT ? window.safeT('status.loadingSlideContent') : 'Loading slide content...'}</p>`;
        }
        this.currentSlideContent = null;
        console.log('🧹 [SLIDE-CONTENT] Slide content cleared');
    }
}