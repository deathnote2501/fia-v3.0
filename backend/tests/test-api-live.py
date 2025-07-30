#!/usr/bin/env python3
"""
Script de conversation naturelle avec Gemini Live API
Utilise le microphone pour l'input et les haut-parleurs pour l'output
Permet des interruptions naturelles et une conversation fluide

Prérequis:
- Compte Google Cloud avec Vertex AI activé
- Authentication Google Cloud (gcloud auth application-default login)
- Installation des dépendances (voir instructions ci-dessous)

Installation des dépendances:
# Sur Ubuntu
sudo apt-get install portaudio19-dev

# Sur macOS  
brew install portaudio

pip install google-genai pyaudio colorama google-auth google-cloud-core

# Authentication
gcloud auth application-default login
"""

import asyncio
import pyaudio
import signal
import sys
import os
import logging
import traceback
from typing import Optional
from colorama import Fore, Style, init
from google import genai
from google.genai import types
import json
from datetime import datetime

# Initialisation de colorama pour les couleurs dans le terminal
init(autoreset=True)

# Configuration du logging détaillé
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('gemini_live_debug.log')
    ]
)
logger = logging.getLogger(__name__)

def log_debug(message: str, data: any = None):
    """Log de debug avec timestamp et données optionnelles"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"{Fore.CYAN}[DEBUG {timestamp}] {message}")
    logger.debug(f"{message} - Data: {data if data else 'None'}")

def log_info(message: str):
    """Log d'information"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"{Fore.GREEN}[INFO {timestamp}] {message}")
    logger.info(message)

def log_error(message: str, error: Exception = None):
    """Log d'erreur avec traceback"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"{Fore.RED}[ERROR {timestamp}] {message}")
    logger.error(f"{message} - Error: {error}")
    if error:
        logger.error(traceback.format_exc())

# Configuration du projet (variables en dur pour développement local)
GOOGLE_CLOUD_PROJECT = "animemate-ddb62"
GOOGLE_CLOUD_LOCATION = "europe-west1"
# Configuration audio
CHUNK = 4200
FORMAT = pyaudio.paInt16
CHANNELS = 1
INPUT_RATE = 16000
OUTPUT_RATE = 24000
# Modèle Live API disponible publiquement
MODEL = 'gemini-live-2.5-flash-preview-native-audio'  # Version public preview

# Variables globales pour la gestion propre de l'arrêt
running = True
session = None

class ConversationManager:
    def __init__(self):
        log_info("🔧 Initialisation du ConversationManager")
        
        # Test de l'authentification (optionnel)
        auth_method = self._setup_authentication()
        
        log_debug("📡 Création du client avec authentification")
        try:
            if auth_method == "api_key":
                log_info("🔑 Utilisation de la clé API pour l'authentification")
                self.client = genai.Client(
                    api_key=GEMINI_API_KEY,
                    # Pour l'API key, on utilise le client standard (pas Vertex AI)
                )
            else:
                log_info("☁️ Utilisation de Vertex AI avec authentification par défaut")
                self.client = genai.Client(
                    vertexai=True,
                    project=GOOGLE_CLOUD_PROJECT,
                    location=GOOGLE_CLOUD_LOCATION,
                )
            log_info("✅ Client créé avec succès")
        except Exception as e:
            log_error("❌ Erreur création client", e)
            raise
            raise
        
        log_debug("🎛️ Configuration de la session Live API")
        # Configuration de la session avec voix française et transcription
        # Note: Le modèle native-audio ne supporte que response_modalities=["AUDIO"]
        self.config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Charon",  # Voix masculine française
                        # Alternatives: "Coral" (féminine), "River" (neutre)
                    )
                ),
                language_code="fr-FR",
            ),
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
            system_instruction=types.Content(
                parts=[types.Part(text="""Tu es un assistant IA conversationnel en français. 
                Réponds de manière naturelle, claire et concise. 
                Adapte ton ton à celui de l'utilisateur. 
                Si l'utilisateur pose une question technique, sois précis mais accessible.
                RÉPONDS TOUJOURS EN FRANÇAIS DE MANIÈRE NATURELLE.""")], 
                role='user'
            ),
            # Configuration pour des réponses plus rapides
            realtime_input_config=types.RealtimeInputConfig(
                automatic_activity_detection=types.AutomaticActivityDetection(
                    disabled=False,
                    start_of_speech_sensitivity=types.StartSensitivity.START_SENSITIVITY_HIGH,
                    end_of_speech_sensitivity=types.EndSensitivity.END_SENSITIVITY_LOW,
                    prefix_padding_ms=50,
                    silence_duration_ms=800,
                )
            ),
            # Fonctionnalités native audio (preview)
            enable_affective_dialog=True,  # Dialog affectif
        )
        log_info("✅ Configuration Live API native-audio créée")
        
        log_debug("🔊 Initialisation interface audio PyAudio")
        try:
            self.audio_interface = pyaudio.PyAudio()
            log_info("✅ Interface audio initialisée")
            
            # Affichage des devices audio disponibles
            self._list_audio_devices()
            
        except Exception as e:
            log_error("❌ Erreur initialisation audio", e)
            raise
    
    def _setup_authentication(self):
        """Configuration de l'authentification (Vertex AI ou API Key)"""
        log_debug("🔐 Configuration de l'authentification")
        
        # Priorité 1: Essayer l'authentification Vertex AI
        try:
            from google.auth import default
            credentials, project = default()
            log_info(f"✅ Authentification Vertex AI OK - Projet: {project}")
            
            if project != GOOGLE_CLOUD_PROJECT:
                log_debug(f"⚠️ Projet détecté ({project}) différent du configuré ({GOOGLE_CLOUD_PROJECT})")
                
            return "vertex_ai"
            
        except Exception as e:
            log_debug(f"⚠️ Authentification Vertex AI échouée: {e}")
            
            # Priorité 2: Utiliser la clé API
            if GEMINI_API_KEY:
                log_info("🔑 Basculement sur l'authentification par clé API")
                return "api_key"
            else:
                log_error("❌ Aucune méthode d'authentification disponible")
                print(f"{Fore.RED}🔧 Solutions possibles:")
                print(f"{Fore.YELLOW}   1. Authentification Vertex AI:")
                print(f"{Fore.YELLOW}      gcloud auth application-default login")
                print(f"{Fore.YELLOW}      gcloud config set project {GOOGLE_CLOUD_PROJECT}")
                print(f"{Fore.YELLOW}   2. Ou vérifiez votre clé API Gemini")
                raise Exception("Aucune authentification disponible")
    
    def _list_audio_devices(self):
        """Liste les devices audio disponibles"""
        log_debug("🎤 Liste des devices audio disponibles:")
        try:
            info = self.audio_interface.get_host_api_info_by_index(0)
            log_debug(f"API Audio: {info.get('name')}")
            
            for i in range(self.audio_interface.get_device_count()):
                device_info = self.audio_interface.get_device_info_by_index(i)
                log_debug(f"  Device {i}: {device_info.get('name')} "
                         f"(In: {device_info.get('maxInputChannels')}, "
                         f"Out: {device_info.get('maxOutputChannels')})")
                         
        except Exception as e:
            log_error("⚠️ Erreur listage devices audio", e)
        
    async def start_conversation(self):
        """Démarre une conversation interactive avec Gemini Live API"""
        log_info("🚀 Démarrage de la conversation avec Gemini Live API")
        print(f"{Fore.GREEN}🎤 Démarrage de la conversation avec Gemini Live API...")
        print(f"{Fore.YELLOW}📝 Parlez naturellement, l'IA vous répondra vocalement")
        print(f"{Fore.YELLOW}🛑 Ctrl+C pour arrêter la conversation")
        print(f"{Fore.CYAN}{'='*60}")
        
        global session
        try:
            log_debug("📡 Tentative de connexion à Live API")
            log_debug(f"Modèle: {MODEL}")
            log_debug(f"Config: {self.config}")
            
            # Note: Le modèle Live API pourrait ne pas être disponible avec la clé API standard
            # Dans ce cas, utilisez l'authentification Vertex AI
            async with self.client.aio.live.connect(model=MODEL, config=self.config) as session:
                log_info("✅ Connexion Live API établie")
                
                # Démarrage des tâches asynchrones
                log_debug("🔄 Démarrage des tâches audio")
                send_task = asyncio.create_task(self._send_audio())
                receive_task = asyncio.create_task(self._receive_audio())
                
                log_info("🎤 Tâches audio démarrées - Conversation active")
                # Attendre que les deux tâches se terminent
                await asyncio.gather(send_task, receive_task)
                
        except Exception as e:
            log_error("❌ Erreur lors de la connexion Live API", e)
            print(f"{Fore.RED}❌ Erreur lors de la connexion: {e}")
            
            # Diagnostic détaillé
            print(f"{Fore.YELLOW}🔍 Diagnostic:")
            print(f"  - Projet: {GOOGLE_CLOUD_PROJECT}")
            print(f"  - Région: {GOOGLE_CLOUD_LOCATION}")
            print(f"  - Modèle: {MODEL}")
            
            raise
            
    async def _send_audio(self):
        """Capture et envoie l'audio du microphone"""
        stream = None
        try:
            log_debug("🎤 Ouverture du stream d'entrée audio")
            stream = self.audio_interface.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=INPUT_RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            log_info("✅ Stream microphone ouvert")
            
            print(f"{Fore.GREEN}🎤 Microphone activé - Vous pouvez commencer à parler...")
            
            chunk_count = 0
            while running:
                try:
                    frame = stream.read(CHUNK, exception_on_overflow=False)
                    chunk_count += 1
                    
                    if chunk_count % 100 == 0:  # Log tous les 100 chunks
                        log_debug(f"📊 Chunk audio #{chunk_count} envoyé ({len(frame)} bytes)")
                    
                    await session.send_realtime_input(
                        media=types.Blob(data=frame, mime_type="audio/pcm;rate=16000")
                    )
                    await asyncio.sleep(0.001)  # Petite pause pour éviter la surcharge
                    
                except Exception as e:
                    if running:
                        log_error(f"⚠️ Erreur d'envoi audio chunk #{chunk_count}", e)
                    break
                    
        except Exception as e:
            log_error("❌ Erreur ouverture microphone", e)
        finally:
            if stream:
                log_debug("🔐 Fermeture du stream microphone")
                stream.stop_stream()
                stream.close()
                log_info("✅ Stream microphone fermé")
                
    async def _receive_audio(self):
        """Reçoit et joue l'audio de réponse"""
        output_stream = None
        message_count = 0
        
        try:
            log_debug("🔊 Ouverture du stream de sortie audio")
            output_stream = self.audio_interface.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=OUTPUT_RATE,
                output=True,
                frames_per_buffer=CHUNK
            )
            log_info("✅ Stream sortie audio ouvert")
            
            log_debug("👂 Écoute des messages Live API")
            async for message in session.receive():
                if not running:
                    break
                    
                message_count += 1
                log_debug(f"📨 Message #{message_count} reçu", {
                    'type': type(message).__name__,
                    'has_server_content': hasattr(message, 'server_content') and message.server_content is not None
                })
                
                # Affichage des transcriptions
                if hasattr(message, 'server_content') and message.server_content:
                    if message.server_content.input_transcription:
                        user_text = message.server_content.input_transcription.text
                        if user_text.strip():
                            log_info(f"🗣️ Transcription utilisateur: {user_text}")
                            print(f"{Fore.BLUE}👤 Vous: {Style.BRIGHT}{user_text}")
                            
                    if message.server_content.output_transcription:
                        ai_text = message.server_content.output_transcription.text
                        if ai_text.strip():
                            log_info(f"🤖 Transcription Gemini: {ai_text}")
                            print(f"{Fore.MAGENTA}🤖 Gemini: {Style.BRIGHT}{ai_text}")
                            
                    # Lecture de l'audio de réponse
                    if message.server_content.model_turn:
                        log_debug("🎵 Réception de données audio")
                        for part_idx, part in enumerate(message.server_content.model_turn.parts):
                            if part.inline_data and part.inline_data.data:
                                try:
                                    audio_size = len(part.inline_data.data)
                                    log_debug(f"🔊 Lecture audio part #{part_idx} ({audio_size} bytes)")
                                    output_stream.write(part.inline_data.data)
                                    await asyncio.sleep(0.001)
                                except Exception as e:
                                    if running:
                                        log_error(f"⚠️ Erreur lecture audio part #{part_idx}", e)
                                        
                    # Gestion des interruptions
                    if message.server_content.interrupted:
                        log_info("⏸️ Interruption détectée")
                        print(f"{Fore.YELLOW}⏸️  Interruption détectée")
                        
        except Exception as e:
            if running:
                log_error("❌ Erreur réception audio", e)
        finally:
            if output_stream:
                log_debug("🔐 Fermeture du stream sortie audio")
                output_stream.stop_stream()
                output_stream.close()
                log_info("✅ Stream sortie audio fermé")
                
    def cleanup(self):
        """Nettoyage des ressources"""
        try:
            self.audio_interface.terminate()
            print(f"{Fore.GREEN}✅ Ressources audio libérées")
        except Exception as e:
            print(f"{Fore.RED}⚠️  Erreur lors du nettoyage: {e}")

def signal_handler(signum, frame):
    """Gestionnaire pour arrêt propre avec Ctrl+C"""
    global running
    print(f"\n{Fore.YELLOW}🛑 Arrêt de la conversation...")
    running = False

def main():
    """Fonction principale"""
    # Configuration directe (variables en dur pour développement local)
    project_id = "animemate-ddb62"
    location = "europe-west1"
    
    print(f"{Fore.GREEN}✅ Configuration chargée:")
    print(f"{Fore.GREEN}   GOOGLE_CLOUD_PROJECT={project_id}")
    print(f"{Fore.GREEN}   GOOGLE_CLOUD_LOCATION={location}")
    
    # Configuration du gestionnaire de signal pour Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialisation et démarrage
    conversation = ConversationManager()
    
    try:
        print(f"{Fore.CYAN}🚀 Initialisation de la conversation avec Gemini Live API")
        print(f"{Fore.CYAN}📍 Projet: {project_id}")
        print(f"{Fore.CYAN}🌍 Région: {location}")
        
        asyncio.run(conversation.start_conversation())
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}🛑 Conversation interrompue par l'utilisateur")
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur inattendue: {e}")
    finally:
        conversation.cleanup()
        print(f"{Fore.GREEN}👋 Au revoir !")

if __name__ == "__main__":
    main()