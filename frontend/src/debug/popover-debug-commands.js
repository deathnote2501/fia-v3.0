/**
 * FIA v3.0 - Commandes de Debug pour Popovers d'Introduction
 * 
 * Ces commandes sont disponibles dans la console du navigateur pour tester
 * et déboguer le système de popovers d'introduction d'interface.
 * 
 * Usage dans la console :
 * - window.debugPopovers.testBootstrap()
 * - window.debugPopovers.forceShow()
 * - window.debugPopovers.reset()
 * - window.debugPopovers.checkElements()
 * - window.debugPopovers.simulatePlanSlide()
 */

export class PopoverDebugCommands {
    constructor() {
        this.popoverInstance = null;
        console.log('🛠️ [DEBUG-POPOVERS] Commandes de debug disponibles dans window.debugPopovers');
    }
    
    /**
     * Tester si Bootstrap est correctement chargé
     */
    testBootstrap() {
        console.log('🔍 [DEBUG] === TEST BOOTSTRAP ===');
        
        if (typeof bootstrap !== 'undefined') {
            console.log('✅ Bootstrap chargé:', bootstrap);
            console.log('📦 Version:', bootstrap.Tooltip?.VERSION || 'N/A');
            
            if (bootstrap.Popover) {
                console.log('✅ Bootstrap.Popover disponible');
                
                // Test simple popover
                const testElement = document.body;
                const testPopover = new bootstrap.Popover(testElement, {
                    title: 'Test Debug',
                    content: 'Bootstrap fonctionne !',
                    placement: 'top',
                    trigger: 'manual'
                });
                
                console.log('✅ Test popover créé:', testPopover);
                return true;
            } else {
                console.error('❌ Bootstrap.Popover non disponible');
                return false;
            }
        } else {
            console.error('❌ Bootstrap non chargé');
            return false;
        }
    }
    
    /**
     * Vérifier tous les éléments d'interface requis
     */
    checkElements() {
        console.log('🔍 [DEBUG] === VÉRIFICATION ÉLÉMENTS ===');
        
        const requiredElements = [
            'chat-input',
            'voice-chat-btn',
            'tts-toggle', 
            'live-api-btn',
            'new-next-btn',
            'new-previous-btn',
            'new-simplify-btn',
            'new-more-details-btn',
            'generate-chart-btn'
        ];
        
        const results = {};
        let foundCount = 0;
        
        requiredElements.forEach(id => {
            const element = document.getElementById(id);
            results[id] = {
                found: !!element,
                element: element,
                visible: element ? element.offsetParent !== null : false
            };
            
            if (element) {
                foundCount++;
                console.log(`✅ ${id}: trouvé, visible=${results[id].visible}`);
            } else {
                console.error(`❌ ${id}: manquant`);
            }
        });
        
        console.log(`📊 Résultat: ${foundCount}/${requiredElements.length} éléments trouvés`);
        return results;
    }
    
    /**
     * Forcer l'affichage des popovers d'introduction
     */
    async forceShow() {
        console.log('🚀 [DEBUG] === FORCER AFFICHAGE POPOVERS ===');
        
        try {
            // Reset localStorage
            localStorage.removeItem('fia_interface_intro_completed');
            console.log('🔄 LocalStorage reset');
            
            // Import du composant
            console.log('📦 Import InterfaceIntroductionPopovers...');
            const { InterfaceIntroductionPopovers } = await import('../components/interface-introduction-popovers.js');
            
            // Créer instance
            this.popoverInstance = new InterfaceIntroductionPopovers();
            console.log('✅ Instance créée');
            
            // Vérifier éléments
            const elementsCheck = this.checkElements();
            
            // Forcer affichage
            console.log('📢 Lancement popovers...');
            this.popoverInstance.showIntroductionPopovers();
            
            console.log('✅ Popovers lancés !');
            console.log('💡 Utilisez debugPopovers.hideAll() pour les masquer');
            
            return this.popoverInstance;
            
        } catch (error) {
            console.error('❌ Erreur forceShow:', error);
            return null;
        }
    }
    
    /**
     * Masquer tous les popovers
     */
    hideAll() {
        console.log('🙈 [DEBUG] === MASQUER TOUS POPOVERS ===');
        
        if (this.popoverInstance) {
            this.popoverInstance.hideAllPopovers();
            console.log('✅ Popovers masqués');
        } else {
            console.warn('⚠️ Aucune instance active');
        }
    }
    
    /**
     * Reset complet de l'état
     */
    reset() {
        console.log('🔄 [DEBUG] === RESET COMPLET ===');
        
        // Reset localStorage
        localStorage.removeItem('fia_interface_intro_completed');
        console.log('✅ LocalStorage reset');
        
        // Masquer popovers existants
        if (this.popoverInstance) {
            this.popoverInstance.hideAllPopovers();
            this.popoverInstance = null;
            console.log('✅ Instance popover reset');
        }
        
        console.log('✅ Reset terminé');
    }
    
    /**
     * Simuler la détection d'un slide de type "plan"
     */
    async simulatePlanSlide() {
        console.log('🎯 [DEBUG] === SIMULATION SLIDE PLAN ===');
        
        try {
            // Import du SlideContentManager
            console.log('📦 Import SlideContentManager...');
            const { SlideContentManager } = await import('../components/slide-content-manager.js');
            
            const manager = new SlideContentManager();
            console.log('✅ SlideContentManager créé');
            
            // Simuler slideData avec slide_type = "plan"
            const mockSlideData = {
                slide_type: 'plan',
                title: 'Plan de Formation Debug',
                slide_content: '# Plan de Formation Test\n\nCeci déclenche les popovers.'
            };
            
            console.log('📊 Mock slideData:', mockSlideData);
            
            // Déclencher la vérification
            console.log('🔄 Déclenchement checkAndTriggerInterfaceIntroduction...');
            manager.checkAndTriggerInterfaceIntroduction(mockSlideData);
            
            console.log('✅ Simulation déclenchée !');
            console.log('⏰ Attendre 1 seconde pour voir les popovers...');
            
            return true;
            
        } catch (error) {
            console.error('❌ Erreur simulation:', error);
            return false;
        }
    }
    
    /**
     * Inspecter l'état actuel du système
     */
    inspect() {
        console.log('🔍 [DEBUG] === INSPECTION SYSTÈME ===');
        
        const state = {
            bootstrap: typeof bootstrap !== 'undefined',
            popoverClass: typeof bootstrap?.Popover !== 'undefined',
            localStorage: localStorage.getItem('fia_interface_intro_completed'),
            currentInstance: !!this.popoverInstance,
            elements: this.checkElements()
        };
        
        console.log('📊 État du système:', state);
        return state;
    }
    
    /**
     * Test complet du système
     */
    async fullTest() {
        console.log('🧪 [DEBUG] === TEST COMPLET SYSTÈME ===');
        
        console.log('1️⃣ Test Bootstrap...');
        const bootstrapOk = this.testBootstrap();
        
        console.log('2️⃣ Vérification éléments...');
        const elementsResult = this.checkElements();
        
        console.log('3️⃣ Reset état...');
        this.reset();
        
        console.log('4️⃣ Test import composant...');
        try {
            const { InterfaceIntroductionPopovers } = await import('../components/interface-introduction-popovers.js');
            console.log('✅ Import composant OK');
        } catch (error) {
            console.error('❌ Erreur import composant:', error);
        }
        
        console.log('5️⃣ Test affichage forcé...');
        const instance = await this.forceShow();
        
        console.log('🏁 Test complet terminé !');
        return {
            bootstrap: bootstrapOk,
            elements: elementsResult,
            instance: !!instance
        };
    }
}

// Initialiser les commandes de debug et les rendre globales
window.debugPopovers = new PopoverDebugCommands();

console.log('🛠️ [DEBUG-POPOVERS] Commandes de debug disponibles :');
console.log('  window.debugPopovers.testBootstrap() - Tester Bootstrap');
console.log('  window.debugPopovers.checkElements() - Vérifier éléments interface');
console.log('  window.debugPopovers.forceShow() - Forcer affichage popovers');
console.log('  window.debugPopovers.hideAll() - Masquer tous popovers');
console.log('  window.debugPopovers.reset() - Reset complet');
console.log('  window.debugPopovers.simulatePlanSlide() - Simuler slide plan');
console.log('  window.debugPopovers.inspect() - Inspecter état système');
console.log('  window.debugPopovers.fullTest() - Test complet');