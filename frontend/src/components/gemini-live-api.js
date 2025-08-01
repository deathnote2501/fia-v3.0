/**
 * FIA v3.0 - Gemini Live API Component
 * Intégration fluide de Gemini Live API pour conversations vocales en temps réel
 * 
 * Réutilise exactement le code optimisé du fichier index_fluide_on_attend_la_fin_v2.02.html
 * avec des adaptations pour l'architecture FIA v3.0
 */

export class GeminiLiveAPI {
    constructor() {
        // =============================================================================
        // CONFIGURATION - Copiée exactement du fichier HTML
        // =============================================================================
        
        // API Gemini (+ Affective Dialog via v1alpha)
        this.API_KEY = null; // Will be loaded from environment
        this.MODEL = "gemini-2.5-flash-preview-native-audio-dialog"; // modèle audio natif requis
        
        this.AUDIO_CONFIG = {
            bufferSize: 4096,
            initialBufferTime: 0.4,      // ✓ Plus de buffer initial
            scheduleAheadTime: 0.6,      // ✓ Plus de planification
            scheduleMargin: 120,         // ✓ Plus de marge
            sentenceTimeout: 800,        // ✓ Réduction timeout
            fadeTime: 0.015,             // ✓ Transitions plus douces
            minCoalesceSec: 0.2,         // ✓ Moins de fragmentation
            inputSampleRate: 16000,
            outputSampleRate: 24000
        };

        this.PCM_CONFIG = {
            captureRate: 48000,
            sendInterval: 300,           // ✓ Envoi plus fréquent
            bufferSize: 4096
        };
        
        // =============================================================================
        // VARIABLES - Copiées exactement du fichier HTML
        // =============================================================================
        this.isRecording = false;
        this.audioContext = null;        // capture
        this.analyser = null;
        this.session = null;
        this.scriptProcessor = null;
        
        // PCM
        this.rawPCMBuffer = [];
        this.pcmSendInterval = null;
        this.audioProcessingCount = 0;
        this.successfulAudioSends = 0;
        this.totalSamplesCaptured = 0;
        
        // Lecture
        this.playbackContext = null;     // lecture
        this.audioStreamer = null;
        this.lastChunkTimeout = null;
        
        // Anti-doublons simple
        this.lastPlayedMessageNo = -1;
        
        // Callbacks pour intégration FIA
        this.onStatusChange = null;
        this.onTranscriptUpdate = null;
        this.onMessageReceived = null;
        
        // Contexte de formation pour personnalisation
        this.learnerContext = null;
        this.learnerSessionId = null;
        this.defaultSystemInstruction = "Tu es un assistant vocal empathique et utile. Parle naturellement en français, adapte ton ton à l'humeur de l'utilisateur, reste concis et clair.";
        
        console.log('🎙️ [GEMINI-LIVE] GeminiLiveAPI component initialized');
    }
    
    /**
     * Load API key from environment via backend endpoint
     */
    async loadAPIKey() {
        if (this.API_KEY) return this.API_KEY;
        
        try {
            const response = await fetch('/api/config/gemini-key');
            if (!response.ok) {
                throw new Error(`Failed to load API key: ${response.status}`);
            }
            const data = await response.json();
            this.API_KEY = data.api_key;
            this.log('CONFIG', '✅ API key loaded from environment');
            return this.API_KEY;
        } catch (error) {
            this.log('CONFIG', '❌ Failed to load API key', error);
            throw new Error('Unable to load Gemini API key. Please check configuration.');
        }
    }
    
    /**
     * Load learner context from backend for personalized Live API responses
     */
    async loadLearnerContext(sessionId) {
        if (!sessionId) {
            this.log('CONTEXT', '⚠️ No session ID provided, using default context');
            this.learnerContext = null;
            this.learnerSessionId = null;
            return null;
        }
        
        try {
            this.log('CONTEXT', `🎯 Loading context for session: ${sessionId}`);
            
            const response = await fetch(`/api/config/live-context/${sessionId}`);
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
            this.log('CONTEXT', '❌ Failed to load learner context', error);
            this.learnerContext = null;
            this.learnerSessionId = sessionId; // Keep session ID even if context loading fails
            return null;
        }
    }
    
    /**
     * Update learner context (refresh from backend)
     */
    async updateContext(sessionId = null) {
        const targetSessionId = sessionId || this.learnerSessionId;
        if (!targetSessionId) {
            this.log('CONTEXT', '⚠️ No session ID available for context update');
            return null;
        }
        
        this.log('CONTEXT', `🔄 Updating context for session: ${targetSessionId}`);
        return await this.loadLearnerContext(targetSessionId);
    }
    
    /**
     * Get system instruction with learner context
     */
    getSystemInstruction() {
        if (!this.learnerContext || !this.learnerContext.system_instruction) {
            this.log('CONTEXT', '📝 Using default system instruction');
            return this.defaultSystemInstruction;
        }
        
        this.log('CONTEXT', '📝 Using personalized system instruction');
        return this.learnerContext.system_instruction;
    }
    
    // =============================================================================
    // LOG - Copié exactement du fichier HTML
    // =============================================================================
    log(category, message, data = null) {
        // 🎙️ Live API Logging pour debug facile
        console.log(`🎙️ [LIVE_API] [${category}] ${message}`);
        if (data) {
            console.log(`📋 [LIVE_API] [${category}_DATA]`, data);
        }
    }
    
    // =============================================================================
    // AUDIO – CAPTURE - Copié exactement du fichier HTML
    // =============================================================================
    async initAudio() {
        this.log('AUDIO_INIT', '🎙️ Init capture PCM');
        try {
            const constraints = {
                audio: {
                    sampleRate: { ideal: this.PCM_CONFIG.captureRate },
                    channelCount: { exact: 1 },
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            };
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.log('AUDIO_INIT', '✅ Accès microphone');
            
            const track = stream.getAudioTracks()[0];
            if (track) this.log('AUDIO_INIT', 'Mic settings:', track.getSettings());
            
            this.audioContext = new AudioContext();
            this.log('AUDIO_INIT', `AudioContext capture @ ${this.audioContext.sampleRate}Hz`);
            
            const source = this.audioContext.createMediaStreamSource(stream);
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;
            source.connect(this.analyser);
            
            // ScriptProcessor (compat large) — sortie muette pour éviter l'écho
            this.scriptProcessor = this.audioContext.createScriptProcessor(this.PCM_CONFIG.bufferSize, 1, 1);
            const muteGain = this.audioContext.createGain(); muteGain.gain.value = 0;
            source.connect(this.scriptProcessor);
            this.scriptProcessor.connect(muteGain);
            muteGain.connect(this.audioContext.destination);
            
            this.scriptProcessor.onaudioprocess = (e) => {
                if (!this.isRecording) return;
                const samples = e.inputBuffer.getChannelData(0);
                const pcm16 = new Int16Array(samples.length);
                for (let i = 0; i < samples.length; i++) {
                    const s = Math.max(-1, Math.min(1, samples[i]));
                    pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
                }
                this.rawPCMBuffer.push(pcm16);
                this.totalSamplesCaptured += samples.length;
                this.audioProcessingCount++;
                if (this.audioProcessingCount % 100 === 0) {
                    this.log('PCM_CAPTURE', `📊 ${this.audioProcessingCount} chunks (${this.totalSamplesCaptured} samples)`);
                }
            };
            
            this.log('AUDIO_INIT', '✅ Capture prête');
            return true;
        } catch (e) {
            this.log('AUDIO_INIT', '❌ Erreur init audio', e);
            if (this.onStatusChange) this.onStatusChange('Erreur micro', 'error');
            return false;
        }
    }
    
    // Resampling linéaire Int16 -> Int16 - Copié exactement du fichier HTML
    linearResampleInt16(int16, inRate, outRate) {
        if (inRate === outRate) return int16;
        const ratio = inRate / outRate;
        const newLen = Math.floor(int16.length / ratio);
        const out = new Int16Array(newLen);
        for (let i = 0; i < newLen; i++) {
            const pos = i * ratio;
            const i0 = Math.floor(pos);
            const i1 = Math.min(i0 + 1, int16.length - 1);
            const frac = pos - i0;
            out[i] = (int16[i0] * (1 - frac) + int16[i1] * frac) | 0;
        }
        return out;
    }
    
    processPCMBuffer() {
        if (this.rawPCMBuffer.length === 0 || !this.session) return;
        try {
            const chunks = this.rawPCMBuffer.splice(0);
            if (chunks.length === 0) return;
            
            let total = 0;
            for (const c of chunks) total += c.length;
            const combined = new Int16Array(total);
            let off = 0; for (const c of chunks) { combined.set(c, off); off += c.length; }
            
            this.log('PCM_PROCESS', `📦 PCM combiné: ${total} samples (${(total/(this.audioContext.sampleRate||48000)).toFixed(3)}s)`);
            
            const inRate = this.audioContext.sampleRate;
            const targetRate = this.AUDIO_CONFIG.inputSampleRate;
            const resampled = this.linearResampleInt16(combined, inRate, targetRate);
            this.log('PCM_PROCESS', `🔄 Rééchantillonné ${inRate}→${targetRate}: ${resampled.length} samples`);
            
            // Int16Array -> base64
            const uint8 = new Uint8Array(resampled.buffer);
            let bin = ""; for (let i = 0; i < uint8.length; i++) bin += String.fromCharCode(uint8[i]);
            const base64Audio = btoa(bin);
            this.log('PCM_PROCESS', `📤 Base64: ${base64Audio.length} chars`);
            
            this.session.sendRealtimeInput({
                audio: { data: base64Audio, mimeType: `audio/pcm;rate=${targetRate}` }
            });
            this.successfulAudioSends++;
            this.log('PCM_SEND', `✅ Envoi #${this.successfulAudioSends} (${(resampled.length/targetRate).toFixed(3)}s)`);
        } catch (e) {
            this.log('PCM_PROCESS', '❌ Erreur traitement PCM', e);
        }
    }
    
    // =============================================================================
    // GEMINI – LIVE (v1alpha + affective dialog) - Copié exactement du fichier HTML
    // =============================================================================
    async connectToGemini() {
        this.log('GEMINI_CONNECT', '🌐 Connexion Live API (v1alpha, affective)');
        try {
            // Load API key first
            await this.loadAPIKey();
            
            const { GoogleGenAI, Modality } = await import('https://esm.run/@google/genai');
            
            // 👉 v1alpha requis pour Affective Dialog
            const ai = new GoogleGenAI({
                apiKey: this.API_KEY,
                httpOptions: { apiVersion: "v1alpha" }
            });
            
            const systemInstruction = this.getSystemInstruction();
            
            // 🎙️ Log system instruction pour debug
            console.log('🎙️ [LIVE_API] [SYSTEM_PROMPT] System instruction envoyé à Gemini Live API:');
            console.log('📝 [LIVE_API] [SYSTEM_PROMPT_CONTENT]', systemInstruction);
            
            const config = {
                responseModalities: [Modality.AUDIO],
                enableAffectiveDialog: true, // 👉 active l'adaptation tonale
                systemInstruction: systemInstruction,
                inputAudioTranscription: {},   // pour afficher la transcription d'entrée si disponible
                outputAudioTranscription: {}   // idem pour la sortie
            };
            
            let messageCount = 0;
            this.session = await ai.live.connect({
                model: this.MODEL,
                config,
                callbacks: {
                    onopen: () => {
                        this.log('WEBSOCKET', '✅ Ouvert');
                        if (this.onStatusChange) this.onStatusChange('Connecté - Parlez maintenant !', 'connected');
                    },
                    onmessage: (message) => {
                        messageCount++;
                        this.handleGeminiResponse(message, messageCount);
                    },
                    onerror: (err) => {
                        this.log('WEBSOCKET', '❌ Erreur', err);
                        if (this.onStatusChange) this.onStatusChange('Erreur de connexion', 'error');
                    },
                    onclose: (evt) => {
                        this.log('WEBSOCKET', `🔌 Fermé: ${evt.code} / ${evt.reason}`);
                        if (this.onStatusChange) this.onStatusChange('Connexion fermée', 'disconnected');
                    }
                }
            });
            
            this.log('GEMINI_CONNECT', '✅ Session établie');
            return true;
        } catch (e) {
            this.log('GEMINI_CONNECT', '❌ Erreur connexion', e);
            if (this.onStatusChange) this.onStatusChange('Erreur: Impossible de se connecter à Gemini', 'error');
            return false;
        }
    }
    
    handleGeminiResponse(message, messageNumber) {
        this.log('GEMINI_RESPONSE', `📨 Message #${messageNumber}`);
        if (messageNumber <= this.lastPlayedMessageNo) return; // anti-doublon
        this.lastPlayedMessageNo = messageNumber;
        
        if (message.setupComplete) {
            this.log('GEMINI_RESPONSE', '✅ Setup complet');
        }
        
        if (message.serverContent) {
            const sc = message.serverContent;
            
            if (sc.inputTranscription?.text) {
                const userText = sc.inputTranscription.text;
                console.log('🎙️ [LIVE_API] [AUDIO_IN] Transcription utilisateur:', userText);
                this.log('GEMINI_RESPONSE', `🎤 Vous: "${userText}"`);
                if (this.onTranscriptUpdate) this.onTranscriptUpdate(`Vous: ${userText}`);
                if (this.onMessageReceived) this.onMessageReceived(userText, true);
            }
            
            if (sc.outputTranscription?.text) {
                const assistantText = sc.outputTranscription.text;
                console.log('🎙️ [LIVE_API] [AUDIO_OUT] Réponse assistant:', assistantText);
                this.log('GEMINI_RESPONSE', `🤖 Assistant: "${assistantText}"`);
                if (this.onMessageReceived) this.onMessageReceived(assistantText, false);
            }
            
            if (sc.interrupted) this.log('GEMINI_RESPONSE', '⚠️ Génération interrompue');
            
            if (sc.turnComplete) {
                this.log('GEMINI_RESPONSE', '🔄 Tour terminé → flush');
                if (this.audioStreamer) this.audioStreamer.flush();
                if (this.lastChunkTimeout) { clearTimeout(this.lastChunkTimeout); this.lastChunkTimeout = null; }
            }
        }
        
        // Audio natif (PCM16 base64)
        if (message.data) this.playAudioResponse(message.data, messageNumber);
        
        // Éventuel texte (ne PAS TTS si l'audio est fourni)
        if (message.text && this.onMessageReceived) this.onMessageReceived(message.text, false);
    }
    
    // =============================================================================
    // LECTURE – AUDIO STREAMER - Copié exactement du fichier HTML
    // =============================================================================
    initPlaybackSystem() {
        if (!this.playbackContext) {
            this.playbackContext = new AudioContext();
            this.log('AUDIO_STREAMER', `Contexte lecture @ ${this.playbackContext.sampleRate}Hz`);
            this.audioStreamer = new AudioStreamer(this.playbackContext, this.AUDIO_CONFIG);
        }
    }
    
    async playAudioResponse(base64AudioData, messageNumber) {
        this.initPlaybackSystem();
        try {
            const bin = atob(base64AudioData);
            const pcmBytes = new Uint8Array(bin.length);
            for (let i = 0; i < bin.length; i++) pcmBytes[i] = bin.charCodeAt(i);
            if (pcmBytes.length === 0) return;
            
            this.audioStreamer.addChunk(pcmBytes);
            
            // Fin de phrase (silence)
            if (this.lastChunkTimeout) clearTimeout(this.lastChunkTimeout);
            this.lastChunkTimeout = setTimeout(() => {
                this.log('AUDIO_PLAYBACK', '⏱️ Timeout fin de phrase → flush');
                this.audioStreamer.flush();
            }, this.AUDIO_CONFIG.sentenceTimeout);
        } catch (e) {
            this.log('AUDIO_PLAYBACK', '❌ Erreur playAudioResponse', e);
        }
    }
    
    // =============================================================================
    // FLOW – START / STOP - Copié exactement du fichier HTML
    // =============================================================================
    async startConversation() {
        this.log('APP_FLOW', '🚀 Démarrage conversation PCM (Affective)');
        if (this.isRecording) return;
        
        this.audioProcessingCount = 0;
        this.successfulAudioSends = 0;
        this.totalSamplesCaptured = 0;
        this.rawPCMBuffer = [];
        this.lastPlayedMessageNo = -1;
        
        if (this.onStatusChange) this.onStatusChange('Initialisation...', 'connecting');
        
        if (!await this.initAudio()) return;
        if (!await this.connectToGemini()) return;
        
        this.isRecording = true;
        
        this.pcmSendInterval = setInterval(() => {
            if (this.isRecording && this.rawPCMBuffer.length > 0) this.processPCMBuffer();
        }, this.PCM_CONFIG.sendInterval);
        
        if (this.onStatusChange) this.onStatusChange('🎙️ Enregistrement PCM - Parlez !', 'recording');
        
        console.log('🎙️ [LIVE_API] [MIC_START] Enregistrement audio démarré - Je vous écoute !');
        if (this.onMessageReceived) this.onMessageReceived("Conversation (Affective Dialog) démarrée. Je vous écoute !", false);
        this.log('APP_FLOW', '🎉 PCM actif');
    }
    
    stopConversation() {
        console.log('🎙️ [LIVE_API] [MIC_STOP] Arrêt de l\'enregistrement audio');
        this.log('APP_FLOW', '🛑 Arrêt conversation');
        if (!this.isRecording) return;
        this.isRecording = false;
        
        if (this.pcmSendInterval) { clearInterval(this.pcmSendInterval); this.pcmSendInterval = null; }
        if (this.rawPCMBuffer.length > 0) this.processPCMBuffer();
        if (this.scriptProcessor) { this.scriptProcessor.disconnect(); this.scriptProcessor = null; }
        if (this.session) { this.session.close(); this.session = null; }
        if (this.lastChunkTimeout) { clearTimeout(this.lastChunkTimeout); this.lastChunkTimeout = null; }
        if (this.audioStreamer) { this.audioStreamer.stop(); this.audioStreamer = null; }
        if (this.playbackContext) { this.playbackContext.close(); this.playbackContext = null; }
        if (this.audioContext) { this.audioContext.close(); this.audioContext = null; }
        
        if (this.onStatusChange) this.onStatusChange('Conversation arrêtée', 'disconnected');
        if (this.onTranscriptUpdate) this.onTranscriptUpdate('');
        
        if (this.onMessageReceived) this.onMessageReceived("Conversation PCM terminée.", false);
        
        this.log('APP_FLOW', `📊 Stats:
    - Samples: ${this.totalSamplesCaptured}  
    - Chunks: ${this.audioProcessingCount}
    - Envois: ${this.successfulAudioSends}
    - Durée: ${(this.totalSamplesCaptured / 48000).toFixed(2)}s`);
        this.log('APP_FLOW', '✅ Fin');
    }
    
    // =============================================================================
    // MÉTHODES PUBLIQUES POUR INTÉGRATION FIA
    // =============================================================================
    
    /**
     * Démarre la conversation Gemini Live API avec contexte optionnel
     * @param {string} sessionId - ID de session optionnel pour charger le contexte
     */
    async start(sessionId = null) {
        // Charger le contexte si un session ID est fourni
        if (sessionId) {
            await this.loadLearnerContext(sessionId);
        }
        
        return await this.startConversation();
    }
    
    /**
     * Arrête la conversation Gemini Live API
     */
    stop() {
        this.stopConversation();
    }
    
    /**
     * Vérifie si la conversation est active
     */
    isActive() {
        return this.isRecording;
    }
    
    /**
     * Configure les callbacks pour l'intégration FIA
     */
    setCallbacks({ onStatusChange, onTranscriptUpdate, onMessageReceived }) {
        this.onStatusChange = onStatusChange;
        this.onTranscriptUpdate = onTranscriptUpdate;
        this.onMessageReceived = onMessageReceived;
    }
    
    /**
     * Vérifie si le navigateur supporte Gemini Live API
     */
    isSupported() {
        return !!(navigator.mediaDevices?.getUserMedia);
    }
}

// =============================================================================
// AUDIO STREAMER CLASS - Copiée exactement du fichier HTML
// =============================================================================
class AudioStreamer {
    constructor(context, config) {
        this.context = context;
        this.config = config;
        this.audioQueue = [];         // Float32Array
        this.isPlaying = false;
        this.scheduledTime = 0;
        this.checkTimer = null;
        
        this.gainNode = this.context.createGain();
        this.gainNode.connect(this.context.destination);
        
        // Jitter/stitch buffer
        this.stitch = new Float32Array(0);
        this.minPlaybackSamples = Math.floor(this.config.outputSampleRate * this.config.minCoalesceSec);
        
        // Garde-fou
        this.maxQueueBuffers = 120; // ~20s @ 4096 / 24kHz
        
        // Audio streamer init log supprimé pour interface propre
    }
    
    _pcm16BytesToFloat32(pcmBytes) {
        const view = new DataView(pcmBytes.buffer, pcmBytes.byteOffset, pcmBytes.byteLength);
        const len = pcmBytes.byteLength / 2;
        const out = new Float32Array(len);
        for (let i = 0; i < len; i++) {
            const v = view.getInt16(i * 2, true);
            out[i] = v / 32768;
        }
        return out;
    }
    
    addChunk(pcmBytes) {
        const samples = this._pcm16BytesToFloat32(pcmBytes);
        
        // Merge avec stitch
        const merged = new Float32Array(this.stitch.length + samples.length);
        merged.set(this.stitch, 0);
        merged.set(samples, this.stitch.length);
        let offset = 0;
        
        // Pousser par tranches bufferSize
        while (merged.length - offset >= this.config.bufferSize) {
            this.audioQueue.push( merged.slice(offset, offset + this.config.bufferSize) );
            offset += this.config.bufferSize;
        }
        
        // Reste : si assez grand (> minCoalesce) on pousse, sinon on garde
        const remaining = merged.length - offset;
        if (remaining >= this.minPlaybackSamples) {
            this.audioQueue.push( merged.slice(offset) );
            this.stitch = new Float32Array(0);
        } else {
            this.stitch = merged.slice(offset);
        }
        
        // Garde-fou
        if (this.audioQueue.length > this.maxQueueBuffers) {
            // Queue warning log supprimé pour interface propre
            this.audioQueue.splice(0, this.audioQueue.length - this.maxQueueBuffers);
        }
        
        if (!this.isPlaying) this._startPlayback();
    }
    
    _startPlayback() {
        this.isPlaying = true;
        this.scheduledTime = this.context.currentTime + this.config.initialBufferTime;
        this._processQueue();
        // Playback start log supprimé pour interface propre
    }
    
    _createAudioBuffer(samples) {
        const buf = this.context.createBuffer(1, samples.length, this.config.outputSampleRate);
        buf.getChannelData(0).set(samples);
        return buf;
    }
    
    _processQueue() {
        while (this.audioQueue.length > 0 &&
               this.scheduledTime < this.context.currentTime + this.config.scheduleAheadTime) {
            this._playNextBuffer();
        }
        const nextMs = (this.scheduledTime - this.context.currentTime) * 1000 - this.config.scheduleMargin;
        this._armCheck(Math.max(10, nextMs));
    }
    
    _armCheck(delayMs) {
        if (this.checkTimer) clearTimeout(this.checkTimer);
        this.checkTimer = setTimeout(() => this._processQueue(), delayMs);
    }
    
    _playNextBuffer() {
        if (this.audioQueue.length === 0) return;
        
        const samples = this.audioQueue.shift();
        const buffer = this._createAudioBuffer(samples);
        const source = this.context.createBufferSource();
        const gain = this.context.createGain();
        
        source.buffer = buffer;
        source.connect(gain);
        gain.connect(this.gainNode);
        
        const now = this.context.currentTime;
        const start = Math.max(this.scheduledTime, now);
        const d = buffer.duration;
        const f = Math.min(this.config.fadeTime, d * 0.25); // borne à 25%
        
        gain.gain.setValueAtTime(0, start);
        gain.gain.linearRampToValueAtTime(1, start + f);
        gain.gain.setValueAtTime(1, start + d - f);
        gain.gain.linearRampToValueAtTime(0, start + d);
        
        source.start(start);
        this.scheduledTime = start + d;
        
        // Buffer log supprimé pour interface propre
    }
    
    flush() {
        // Flush log supprimé pour interface propre
        if (this.stitch.length > 0) {
            this.audioQueue.push(this.stitch);
            this.stitch = new Float32Array(0);
        }
        while (this.audioQueue.length > 0) this._playNextBuffer();
    }
    
    stop() {
        // Stop lecture log supprimé pour interface propre
        this.isPlaying = false;
        this.audioQueue = [];
        this.stitch = new Float32Array(0);
        if (this.checkTimer) { clearTimeout(this.checkTimer); this.checkTimer = null; }
        this.gainNode.gain.linearRampToValueAtTime(0, this.context.currentTime + 0.1);
    }
}