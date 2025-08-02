// Test simple du chargement de contexte
// Node.js test pour vérifier la logique de base

const fetch = require('node-fetch');

// Mock de la classe GeminiLiveAPI pour les tests Node.js
class GeminiLiveAPITest {
    constructor() {
        this.learnerContext = null;
        this.learnerSessionId = null;
        this.defaultSystemInstruction = "Tu es un assistant vocal empathique et utile. Parle naturellement en français, adapte ton ton à l'humeur de l'utilisateur, reste concis et clair.";
    }
    
    log(category, message, data = null) {
        const ts = new Date().toISOString();
        const msg = `[${ts}] [${category}] ${message}`;
        if (data !== null) console.log(msg, data); else console.log(msg);
    }
    
    async loadLearnerContext(sessionId) {
        if (!sessionId) {
            this.log('CONTEXT', '⚠️ No session ID provided, using default context');
            this.learnerContext = null;
            this.learnerSessionId = null;
            return null;
        }
        
        try {
            this.log('CONTEXT', `🎯 Loading context for session: ${sessionId}`);
            
            const response = await fetch(`http://localhost:8000/api/config/live-context/${sessionId}`);
            if (!response.ok) {
                throw new Error(`Failed to load context: ${response.status} ${response.statusText}`);
            }
            
            const contextData = await response.json();
            this.learnerContext = contextData;
            this.learnerSessionId = sessionId;
            
            this.log('CONTEXT', `✅ Context loaded for ${contextData.learner_profile?.niveau || 'unknown'} level learner`);
            this.log('CONTEXT', `Current slide: ${contextData.slide_title || 'No specific slide'}`);
            
            return contextData;
            
        } catch (error) {
            this.log('CONTEXT', '❌ Failed to load learner context', error.message);
            this.learnerContext = null;
            this.learnerSessionId = sessionId;
            return null;
        }
    }
    
    getSystemInstruction() {
        if (!this.learnerContext || !this.learnerContext.system_instruction) {
            this.log('CONTEXT', '📝 Using default system instruction');
            return this.defaultSystemInstruction;
        }
        
        this.log('CONTEXT', '📝 Using personalized system instruction');
        return this.learnerContext.system_instruction;
    }
}

// Test principal
async function testContextLoading() {
    console.log('🧪 Démarrage des tests de chargement de contexte');
    
    const api = new GeminiLiveAPITest();
    const testSessionId = '58368a0d-e0ea-4bba-98a9-37982672b334';
    
    // Test 1: Chargement de contexte avec session ID valide
    console.log('\n📋 Test 1: Chargement contexte avec session ID valide');
    const context = await api.loadLearnerContext(testSessionId);
    
    if (context) {
        console.log('✅ Test 1 PASSED: Contexte chargé avec succès');
        console.log(`   - Session ID: ${context.learner_session_id}`);
        console.log(`   - Niveau: ${context.learner_profile?.niveau}`);
        console.log(`   - System instruction length: ${context.system_instruction?.length} chars`);
    } else {
        console.log('❌ Test 1 FAILED: Contexte non chargé');
    }
    
    // Test 2: System instruction personnalisée
    console.log('\n📝 Test 2: System instruction personnalisée');
    const instruction = api.getSystemInstruction();
    
    if (instruction && instruction !== api.defaultSystemInstruction) {
        console.log('✅ Test 2 PASSED: System instruction personnalisée utilisée');
        console.log(`   - Length: ${instruction.length} chars`);
        console.log(`   - Preview: ${instruction.substring(0, 100)}...`);
    } else {
        console.log('❌ Test 2 FAILED: System instruction par défaut utilisée');
    }
    
    // Test 3: Chargement avec session ID invalide
    console.log('\n🚫 Test 3: Chargement avec session ID invalide');
    const invalidContext = await api.loadLearnerContext('invalid-uuid');
    
    if (!invalidContext && api.learnerContext === null) {
        console.log('✅ Test 3 PASSED: Gestion d\'erreur correcte pour UUID invalide');
    } else {
        console.log('❌ Test 3 FAILED: Gestion d\'erreur incorrecte');
    }
    
    // Test 4: System instruction par défaut après échec
    console.log('\n🔄 Test 4: System instruction par défaut après échec');
    const defaultInstruction = api.getSystemInstruction();
    
    if (defaultInstruction === api.defaultSystemInstruction) {
        console.log('✅ Test 4 PASSED: Retour à l\'instruction par défaut après échec');
    } else {
        console.log('❌ Test 4 FAILED: Instruction par défaut non utilisée après échec');
    }
    
    console.log('\n🎉 Tests terminés');
}

// Exécuter les tests
testContextLoading().catch(console.error);