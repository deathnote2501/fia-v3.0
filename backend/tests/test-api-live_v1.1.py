#!/usr/bin/env python3
"""
Script de conversation naturelle avec Gemini Live API - VERSION CORRIGÉE
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

# Configuration audio - Optimisée pour fluidité
CHUNK = 2048  # Augmenté pour plus de fluidité
FORMAT = pyaudio.paInt16
CHANNELS = 1
INPUT_RATE = 16000
OUTPUT_RATE = 24000
# Modèle Live API disponible publiquement
MODEL = 'gemini-2.5-flash-preview-native-audio-dialog'

# Variables globales pour la gestion propre de l'arrêt
running = True
session = None

class ConversationManager:
    def __init__(self):
        log_info("🔧 Initialisation du ConversationManager")
        
        # Test de l'authentification
        self._test_authentication()
        
        log_debug("📡 Création du client Vertex AI")
        try:
            self.client = genai.Client(
                vertexai=True,
                project=GOOGLE_CLOUD_PROJECT,
                location=GOOGLE_CLOUD_LOCATION,
            )
            log_info("✅ Client Vertex AI créé avec succès")
        except Exception as e:
            log_error("❌ Erreur création client Vertex AI", e)
            raise
        
        log_debug("🎛️ Configuration de la session Live API")
        # Configuration de la session avec voix française et transcription
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
                parts=[types.Part(text="""Tu es un assistant IA conversationnel en français avec une personnalité expressive et adaptative. 
                Adapte ton ton et style de réponse selon l'émotion et le ton de l'utilisateur :
                - Si l'utilisateur semble joyeux, sois enthousiaste
                - Si l'utilisateur semble inquiet, sois rassurant et calme
                - Si l'utilisateur semble pressé, sois concis et efficace
                - Si l'utilisateur semble détendu, sois conversationnel
                
                Réponds de manière naturelle, claire et avec de l'émotion dans la voix.
                Utilise des expressions françaises appropriées au contexte émotionnel.
                RÉPONDS TOUJOURS EN FRANÇAIS DE MANIÈRE NATURELLE ET EXPRESSIVE.""")], 
                role='user'
            ),
            # Configuration pour des réponses plus rapides et fluides
            realtime_input_config=types.RealtimeInputConfig(
                automatic_activity_detection=types.AutomaticActivityDetection(
                    disabled=False,
                    start_of_speech_sensitivity=types.StartSensitivity.START_SENSITIVITY_HIGH,
                    end_of_speech_sensitivity=types.EndSensitivity.END_SENSITIVITY_HIGH,
                    prefix_padding_ms=100,
                    silence_duration_ms=500,
                )
            ),
        )
        log_info("✅ Configuration Live API créée")
        
        log_debug("🔊 Initialisation interface audio PyAudio")
        try:
            self.audio_interface = pyaudio.PyAudio()
            log_info("✅ Interface audio initialisée")
            
            # Affichage des devices audio disponibles
            self._list_audio_devices()
            
        except Exception as e:
            log_error("❌ Erreur initialisation audio", e)
            raise
    
    def _test_authentication(self):
        """Test de l'authentification Google Cloud"""
        log_debug("🔐 Test de l'authentification Google Cloud")
        try:
            from google.auth import default
            credentials, project = default()
            log_info(f"✅ Authentification OK - Projet détecté: {project}")
            
            if project != GOOGLE_CLOUD_PROJECT:
                log_debug(f"⚠️ Projet détecté ({project}) différent du projet configuré ({GOOGLE_CLOUD_PROJECT})")
                
        except Exception as e:
            log_error("❌ Erreur d'authentification", e)
            print(f"{Fore.RED}🔧 Pour corriger l'authentification:")
            print(f"{Fore.YELLOW}   gcloud auth application-default login")
            print(f"{Fore.YELLOW}   gcloud config set project {GOOGLE_CLOUD_PROJECT}")
            raise
    
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
            
            async with self.client.aio.live.connect(model=MODEL, config=self.config) as session:
                log_info("✅ Connexion Live API établie")
                
                # Création des tâches asynchrones pour gérer les flux audio
                send_task = None
                receive_task = None
                
                try:
                    # Démarrage des tâches asynchrones
                    log_debug("🔄 Démarrage des tâches audio")
                    send_task = asyncio.create_task(self._send_audio())
                    receive_task = asyncio.create_task(self._receive_audio())
                    
                    log_info("🎤 Tâches audio démarrées - Conversation active")
                    
                    # Attendre que les tâches se terminent ou qu'une exception se produise
                    await asyncio.gather(send_task, receive_task, return_exceptions=True)
                    
                except Exception as e:
                    log_error("❌ Erreur dans les tâches audio", e)
                    # Annuler les tâches en cours
                    if send_task and not send_task.done():
                        send_task.cancel()
                    if receive_task and not receive_task.done():
                        receive_task.cancel()
                    raise
                
        except Exception as e:
            log_error("❌ Erreur lors de la connexion Live API", e)
            print(f"{Fore.RED}❌ Erreur lors de la connexion: {e}")
            
            # Diagnostic détaillé
            print(f"{Fore.YELLOW}🔍 Diagnostic:")
            print(f"  - Projet: {GOOGLE_CLOUD_PROJECT}")
            print(f"  - Région: {GOOGLE_CLOUD_LOCATION}")
            print(f"  - Modèle: {MODEL}")
            
            # Si erreur de modèle non trouvé, suggérer des alternatives
            if "was not fo" in str(e) or "not found" in str(e).lower():
                print(f"{Fore.YELLOW}💡 Le modèle Live API n'est pas disponible dans votre projet.")
                print(f"{Fore.YELLOW}   Solutions possibles:")
                print(f"{Fore.YELLOW}   1. Demander l'accès au modèle privé")
                print(f"{Fore.YELLOW}   2. Contacter votre équipe Google Cloud pour l'activation")
                print(f"{Fore.YELLOW}   3. Vérifier les quotas et limites de votre projet")
            elif "not supported" in str(e).lower():
                print(f"{Fore.YELLOW}💡 Modèle non supporté dans Live API.")
                print(f"{Fore.YELLOW}   Solutions:")
                print(f"{Fore.YELLOW}   1. Modèle corrigé vers: {MODEL}")
                print(f"{Fore.YELLOW}   2. Vérifiez la liste des modèles supportés")
                print(f"{Fore.YELLOW}   3. Utilisez un modèle Live API valide")
            
            raise
            
    async def _send_audio(self):
        """Capture et envoie l'audio du microphone - VERSION AMÉLIORÉE"""
        stream = None
        try:
            log_debug("🎤 Ouverture du stream d'entrée audio")
            stream = self.audio_interface.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=INPUT_RATE,
                input=True,
                frames_per_buffer=CHUNK,
                # Réduction de la latence
                input_device_index=None,  # Utilise le device par défaut
            )
            log_info("✅ Stream microphone ouvert")
            
            print(f"{Fore.GREEN}🎤 Microphone activé - Vous pouvez commencer à parler...")
            
            chunk_count = 0
            last_data_time = datetime.now()
            
            while running:
                try:
                    # Lecture non-bloquante du microphone
                    try:
                        frame = stream.read(CHUNK, exception_on_overflow=False)
                        chunk_count += 1
                        
                        # Log périodique pour éviter le spam
                        if chunk_count % 500 == 0:  # Log tous les 500 chunks (environ toutes les 10 secondes)
                            log_debug(f"📊 Chunk audio #{chunk_count} envoyé ({len(frame)} bytes)")
                        
                        # Envoi à Gemini via la session Live API
                        await session.send_realtime_input(
                            audio=types.Blob(data=frame, mime_type="audio/pcm;rate=16000")
                        )
                        
                        last_data_time = datetime.now()
                        
                        # Petite pause pour éviter la surcharge CPU
                        await asyncio.sleep(0.001)
                        
                    except Exception as read_error:
                        if running:
                            log_error(f"⚠️ Erreur lecture microphone chunk #{chunk_count}", read_error)
                        continue
                        
                except asyncio.CancelledError:
                    log_info("🛑 Tâche d'envoi audio annulée")
                    break
                except Exception as e:
                    if running:
                        log_error(f"⚠️ Erreur dans boucle d'envoi audio", e)
                    break
                    
        except Exception as e:
            log_error("❌ Erreur ouverture microphone", e)
            print(f"{Fore.RED}❌ Impossible d'ouvrir le microphone. Vérifiez que:")
            print(f"{Fore.YELLOW}   1. Votre microphone est connecté et fonctionne")
            print(f"{Fore.YELLOW}   2. Aucune autre application n'utilise le microphone")
            print(f"{Fore.YELLOW}   3. Les permissions microphone sont accordées")
        finally:
            if stream:
                log_debug("🔐 Fermeture du stream microphone")
                try:
                    stream.stop_stream()
                    stream.close()
                    log_info("✅ Stream microphone fermé")
                except Exception as close_error:
                    log_error("⚠️ Erreur fermeture microphone", close_error)
                
    async def _receive_audio(self):
        """Reçoit et joue l'audio de réponse - VERSION TRÈS AMÉLIORÉE"""
        output_stream = None
        message_count = 0
        audio_buffer = bytearray()
        
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
                
                # Log plus sélectif pour éviter le spam
                if message_count % 100 == 0:
                    log_debug(f"📨 Message #{message_count} reçu", {
                        'type': type(message).__name__,
                        'has_server_content': hasattr(message, 'server_content') and message.server_content is not None
                    })
                
                # Vérification de l'existence de server_content
                if not hasattr(message, 'server_content') or not message.server_content:
                    continue
                
                # 🔧 GESTION DES TRANSCRIPTIONS (améliorée)
                try:
                    if hasattr(message.server_content, 'input_transcription') and message.server_content.input_transcription:
                        user_text = message.server_content.input_transcription.text
                        if user_text and user_text.strip():
                            log_info(f"🗣️ Vous avez dit: {user_text}")
                            print(f"{Fore.BLUE}👤 Vous: {Style.BRIGHT}{user_text}")
                            
                    if hasattr(message.server_content, 'output_transcription') and message.server_content.output_transcription:
                        ai_text = message.server_content.output_transcription.text
                        if ai_text and ai_text.strip():
                            log_info(f"🤖 Gemini répond: {ai_text}")
                            print(f"{Fore.MAGENTA}🤖 Gemini: {Style.BRIGHT}{ai_text}")
                except Exception as transcription_error:
                    log_error("⚠️ Erreur traitement transcription", transcription_error)
                        
                # 🔧 GESTION DES INTERRUPTIONS (simplifiée et robuste)
                try:
                    if hasattr(message.server_content, 'interrupted') and message.server_content.interrupted:
                        log_info("⏸️ Interruption détectée - Nettoyage buffer audio")
                        print(f"{Fore.YELLOW}⏸️ Interruption détectée - Vous pouvez parler")
                        
                        # Vider le buffer audio seulement
                        audio_buffer.clear()
                        continue
                except Exception as interrupt_error:
                    log_error("⚠️ Erreur gestion interruption", interrupt_error)
                        
                # 🔧 GESTION DE L'AUDIO DE RÉPONSE (très améliorée)
                try:
                    if hasattr(message.server_content, 'model_turn') and message.server_content.model_turn:
                        model_turn = message.server_content.model_turn
                        
                        for part_idx, part in enumerate(model_turn.parts):
                            if hasattr(part, 'inline_data') and part.inline_data and part.inline_data.data:
                                try:
                                    audio_data = part.inline_data.data
                                    audio_size = len(audio_data)
                                    
                                    # Log sélectif pour éviter le spam
                                    if part_idx % 10 == 0:
                                        log_debug(f"🔊 Audio part #{part_idx} reçu ({audio_size} bytes)")
                                    
                                    # Ajouter au buffer pour un rendu fluide
                                    audio_buffer.extend(audio_data)
                                    
                                    # Lecture par chunks pour fluidité
                                    min_buffer_size = CHUNK * 2  # Buffer minimum réduit pour moins de latence
                                    while len(audio_buffer) >= min_buffer_size and output_stream and running:
                                        # Extraire un chunk du buffer
                                        chunk_to_play = bytes(audio_buffer[:min_buffer_size])
                                        audio_buffer = audio_buffer[min_buffer_size:]
                                        
                                        # Jouer le chunk
                                        try:
                                            output_stream.write(chunk_to_play)
                                            await asyncio.sleep(0.001)  # Micro-pause pour fluidité
                                        except Exception as play_error:
                                            log_error(f"⚠️ Erreur lecture chunk audio", play_error)
                                            break
                                            
                                except Exception as audio_error:
                                    if running:
                                        log_error(f"⚠️ Erreur traitement audio part #{part_idx}", audio_error)
                                        
                        # Jouer le buffer restant à la fin du tour de modèle
                        if len(audio_buffer) > 0 and output_stream and running:
                            try:
                                # Compléter avec du silence si nécessaire pour alignment
                                while len(audio_buffer) % 2 != 0:
                                    audio_buffer.append(0)
                                    
                                output_stream.write(bytes(audio_buffer))
                                audio_buffer.clear()
                            except Exception as final_audio_error:
                                if running:
                                    log_error("⚠️ Erreur lecture buffer final", final_audio_error)
                                    
                except Exception as model_turn_error:
                    log_error("⚠️ Erreur traitement model_turn", model_turn_error)
                        
        except asyncio.CancelledError:
            log_info("🛑 Tâche de réception audio annulée")
        except Exception as e:
            if running:
                log_error("❌ Erreur réception audio", e)
        finally:
            # Jouer le buffer restant avant fermeture
            if len(audio_buffer) > 0 and output_stream:
                try:
                    while len(audio_buffer) % 2 != 0:
                        audio_buffer.append(0)
                    output_stream.write(bytes(audio_buffer))
                    log_debug(f"🔊 Buffer final joué ({len(audio_buffer)} bytes)")
                except Exception as final_error:
                    log_error("⚠️ Erreur buffer final", final_error)
                    
            # Fermeture propre du stream
            if output_stream:
                log_debug("🔐 Fermeture du stream sortie audio")
                try:
                    output_stream.stop_stream()
                    output_stream.close()
                    log_info("✅ Stream sortie audio fermé")
                except Exception as close_error:
                    log_error("⚠️ Erreur fermeture stream sortie", close_error)
                
    def cleanup(self):
        """Nettoyage des ressources"""
        log_debug("🧹 Nettoyage des ressources")
        try:
            self.audio_interface.terminate()
            log_info("✅ Ressources audio libérées")
            print(f"{Fore.GREEN}✅ Ressources audio libérées")
        except Exception as e:
            log_error("⚠️ Erreur lors du nettoyage", e)
            print(f"{Fore.RED}⚠️ Erreur lors du nettoyage: {e}")

def signal_handler(signum, frame):
    """Gestionnaire pour arrêt propre avec Ctrl+C"""
    global running
    log_info("🛑 Signal d'arrêt reçu")
    print(f"\n{Fore.YELLOW}🛑 Arrêt de la conversation...")
    running = False

def main():
    """Fonction principale"""
    log_info("🚀 Démarrage de l'application Gemini Live API")
    
    # Configuration directe (variables en dur pour développement local)
    project_id = GOOGLE_CLOUD_PROJECT
    location = GOOGLE_CLOUD_LOCATION
    
    print(f"{Fore.GREEN}✅ Configuration chargée:")
    print(f"{Fore.GREEN}   GOOGLE_CLOUD_PROJECT={project_id}")
    print(f"{Fore.GREEN}   GOOGLE_CLOUD_LOCATION={location}")
    print(f"{Fore.GREEN}   MODEL={MODEL}")
    
    log_debug("Configuration système", {
        'project': project_id,
        'location': location,
        'model': MODEL,
        'python_version': sys.version,
        'working_directory': os.getcwd()
    })
    
    # Configuration du gestionnaire de signal pour Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    log_debug("🔧 Gestionnaire de signal configuré")
    
    # Initialisation et démarrage
    conversation = None
    try:
        log_debug("🏗️ Création du ConversationManager")
        conversation = ConversationManager()
        
        print(f"{Fore.CYAN}🚀 Initialisation de la conversation avec Gemini Live API")
        print(f"{Fore.CYAN}📍 Projet: {project_id}")
        print(f"{Fore.CYAN}🌍 Région: {location}")
        print(f"{Fore.CYAN}🤖 Modèle: {MODEL}")
        
        log_info("▶️ Lancement de la conversation")
        asyncio.run(conversation.start_conversation())
        
    except KeyboardInterrupt:
        log_info("🛑 Conversation interrompue par l'utilisateur")
        print(f"\n{Fore.YELLOW}🛑 Conversation interrompue par l'utilisateur")
    except Exception as e:
        log_error("❌ Erreur inattendue", e)
        print(f"{Fore.RED}❌ Erreur inattendue: {e}")
        print(f"{Fore.YELLOW}📋 Consultez le fichier 'gemini_live_debug.log' pour plus de détails")
    finally:
        if conversation:
            conversation.cleanup()
        log_info("👋 Fin de l'application")
        print(f"{Fore.GREEN}👋 Au revoir !")

if __name__ == "__main__":
    main()