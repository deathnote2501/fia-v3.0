"""
FIA v3.0 - Live API Client
Infrastructure client for Vertex AI Live API WebSocket connections
"""

import asyncio
import json
import logging
import websockets
from typing import Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass
from urllib.parse import urlencode

from app.infrastructure.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class AudioData:
    """Audio data container for Live API"""
    data: bytes
    mime_type: str = "audio/pcm;rate=16000"
    sample_rate: int = 16000


@dataclass
class LiveResponse:
    """Live API response container"""
    text: Optional[str] = None  
    audio_data: Optional[bytes] = None
    metadata: Optional[Dict[str, Any]] = None
    is_complete: bool = False
    error: Optional[str] = None


class LiveAPIError(Exception):
    """Exception for Live API operations"""
    pass


class LiveAPIClient:
    """Client for connecting to Vertex AI Live API via WebSocket"""
    
    def __init__(self):
        """Initialize Live API client"""
        self.websocket = None
        self.is_connected = False
        self.session_id = None
        self.project_id = settings.google_cloud_project
        self.region = settings.google_cloud_region
        
        # Live API specific settings
        self.model_name = "gemini-2.5-flash-live"  # Live API model
        self.api_version = "v1alpha"  # Required for Live API
        
        logger.info(f"🎙️ LIVE_API [CLIENT] Initialized - Project: {self.project_id}, Region: {self.region}")
    
    async def connect(self, session_config: Dict[str, Any]) -> bool:
        """
        Connect to Live API WebSocket endpoint
        
        Args:
            session_config: Configuration for the Live API session
                - response_modalities: ["AUDIO"] or ["TEXT"]  
                - system_instruction: System instruction for the AI
                - speech_config: Voice configuration (optional)
                - context: Slide content and learner profile context
        
        Returns:
            bool: True if connection successful
        """
        try:
            logger.info("🔗 LIVE_API [CONNECT] Starting connection to Live API...")
            
            # Build WebSocket URL for Live API
            ws_url = self._build_websocket_url()
            
            # Set up headers with authentication
            headers = await self._get_auth_headers()
            
            # Connect to WebSocket
            logger.info(f"🔗 LIVE_API [CONNECT] Connecting to: {ws_url}")
            self.websocket = await websockets.connect(
                ws_url,
                additional_headers=headers,  # Fixed: use additional_headers instead of extra_headers
                ping_interval=30,  # Keep connection alive
                ping_timeout=10
            )
            
            # Send setup message with session configuration
            setup_message = self._build_setup_message(session_config)
            await self._send_message(setup_message)
            
            # Wait for setup confirmation
            setup_response = await self._receive_message()
            if setup_response.get("setup_complete"):
                self.is_connected = True
                self.session_id = setup_response.get("session_id")
                logger.info(f"✅ LIVE_API [CONNECT] Connected successfully - Session: {self.session_id}")
                return True
            else:
                logger.error(f"❌ LIVE_API [CONNECT] Setup failed: {setup_response}")
                return False
                
        except websockets.exceptions.WebSocketException as e:
            logger.error(f"❌ LIVE_API [CONNECT] WebSocket error: {str(e)}")
            self.is_connected = False
            raise LiveAPIError(f"WebSocket connection failed: {str(e)}")
        except Exception as e:
            logger.error(f"❌ LIVE_API [CONNECT] Connection error: {str(e)}")
            self.is_connected = False
            raise LiveAPIError(f"Connection failed: {str(e)}")
    
    async def send_audio(self, audio_data: AudioData) -> bool:
        """
        Send audio data to Live API
        
        Args:
            audio_data: AudioData container with audio bytes and metadata
            
        Returns:
            bool: True if audio sent successfully
        """
        try:
            if not self.is_connected or not self.websocket:
                raise LiveAPIError("Not connected to Live API")
            
            logger.info(f"🎙️ LIVE_API [SEND_AUDIO] Sending {len(audio_data.data)} bytes of audio")
            
            # Build audio message for Live API
            audio_message = {
                "realtime_input": {
                    "audio": {
                        "data": audio_data.data.hex(),  # Convert bytes to hex string
                        "mime_type": audio_data.mime_type
                    }
                }
            }
            
            await self._send_message(audio_message)
            logger.info("✅ LIVE_API [SEND_AUDIO] Audio sent successfully")
            return True
            
        except websockets.exceptions.ConnectionClosed:
            logger.error("❌ LIVE_API [SEND_AUDIO] WebSocket connection closed")
            self.is_connected = False
            raise LiveAPIError("Connection closed while sending audio")
        except Exception as e:
            logger.error(f"❌ LIVE_API [SEND_AUDIO] Error: {str(e)}")
            raise LiveAPIError(f"Failed to send audio: {str(e)}")
    
    async def receive_response(self) -> AsyncGenerator[LiveResponse, None]:
        """
        Receive responses from Live API (streaming)
        
        Yields:
            LiveResponse: Response objects with text, audio, or metadata
        """
        try:
            if not self.is_connected or not self.websocket:
                raise LiveAPIError("Not connected to Live API")
            
            logger.info("👂 LIVE_API [RECEIVE] Listening for responses...")
            
            async for raw_message in self.websocket:
                try:
                    message = json.loads(raw_message) if isinstance(raw_message, str) else raw_message
                    
                    # Process different types of Live API responses
                    response = self._process_live_response(message)
                    
                    if response:
                        logger.info(f"📨 LIVE_API [RECEIVE] Received response: {response.text[:50] if response.text else 'Audio data'}")
                        yield response
                        
                        # Break if this is a complete response
                        if response.is_complete:
                            break
                            
                except json.JSONDecodeError as e:
                    logger.error(f"❌ LIVE_API [RECEIVE] JSON decode error: {str(e)}")
                    yield LiveResponse(error=f"Invalid JSON response: {str(e)}")
                except Exception as e:
                    logger.error(f"❌ LIVE_API [RECEIVE] Processing error: {str(e)}")
                    yield LiveResponse(error=f"Response processing error: {str(e)}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("⚠️ LIVE_API [RECEIVE] WebSocket connection closed")
            self.is_connected = False
            yield LiveResponse(error="Connection closed", is_complete=True)
        except Exception as e:
            logger.error(f"❌ LIVE_API [RECEIVE] Error: {str(e)}")
            yield LiveResponse(error=str(e), is_complete=True)
    
    async def disconnect(self) -> None:
        """Disconnect from Live API"""
        try:
            if self.websocket:
                logger.info("🔌 LIVE_API [DISCONNECT] Closing connection...")
                await self.websocket.close()
                self.websocket = None
                
            self.is_connected = False
            self.session_id = None
            logger.info("✅ LIVE_API [DISCONNECT] Disconnected successfully")
            
        except Exception as e:
            logger.error(f"❌ LIVE_API [DISCONNECT] Error: {str(e)}")
    
    def _build_websocket_url(self) -> str:
        """Build WebSocket URL for Live API"""
        base_url = f"wss://{self.region}-aiplatform.googleapis.com"
        endpoint = f"/{self.api_version}/projects/{self.project_id}/locations/{self.region}/publishers/google/models/{self.model_name}:streamGenerateContent"
        
        # Add query parameters
        params = {
            "alt": "sse"  # Server-sent events for streaming
        }
        query_string = urlencode(params)
        
        return f"{base_url}{endpoint}?{query_string}"
    
    async def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for Live API"""
        # For simplicity, using API key authentication
        # In production, you might want to use service account tokens
        headers = {
            "Authorization": f"Bearer {await self._get_access_token()}",
            "Content-Type": "application/json"
        }
        return headers
    
    async def _get_access_token(self) -> str:
        """Get access token for authentication using Google Application Default Credentials"""
        try:
            from google.auth import default
            from google.auth.transport.requests import Request
            
            # Get default credentials (will use the same credentials as Vertex AI)
            credentials, project = default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
            
            # Refresh the credentials if needed
            if not credentials.valid:
                credentials.refresh(Request())
            
            token = credentials.token
            logger.info("🔑 LIVE_API [AUTH] Successfully obtained access token")
            return token
            
        except Exception as e:
            logger.error(f"❌ LIVE_API [AUTH] Failed to get access token: {str(e)}")
            # Fallback to placeholder for testing
            logger.warning("⚠️ LIVE_API [AUTH] Using placeholder token for testing")
            return "placeholder_token"
    
    def _build_setup_message(self, session_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build setup message for Live API session"""
        setup_msg = {
            "setup": {
                "model": f"projects/{self.project_id}/locations/{self.region}/publishers/google/models/{self.model_name}",
                "generation_config": {
                    "response_modalities": session_config.get("response_modalities", ["AUDIO"]),
                    "speech_config": session_config.get("speech_config", {
                        "voice_config": {
                            "prebuilt_voice_config": {
                                "voice_name": "Kore"  # Default voice
                            }
                        }
                    })
                },
                "system_instruction": session_config.get("system_instruction", "You are a helpful AI trainer.")
            }
        }
        
        # Add context if provided
        if "context" in session_config:
            setup_msg["setup"]["tools"] = [{
                "function_declarations": [{
                    "name": "get_context",
                    "description": "Get current slide and learner context",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "slide_content": {"type": "string"},
                            "learner_profile": {"type": "object"}
                        }
                    }
                }]
            }]
        
        return setup_msg
    
    async def _send_message(self, message: Dict[str, Any]) -> None:
        """Send message to WebSocket"""
        if not self.websocket:
            raise LiveAPIError("WebSocket not connected")
        
        json_message = json.dumps(message)
        await self.websocket.send(json_message)
        logger.debug(f"📤 LIVE_API [SEND] Message sent: {json_message[:100]}...")
    
    async def _receive_message(self) -> Dict[str, Any]:
        """Receive single message from WebSocket"""
        if not self.websocket:
            raise LiveAPIError("WebSocket not connected")
        
        raw_message = await self.websocket.recv()
        message = json.loads(raw_message) if isinstance(raw_message, str) else raw_message
        logger.debug(f"📥 LIVE_API [RECEIVE] Message received: {str(message)[:100]}...")
        return message
    
    def _process_live_response(self, message: Dict[str, Any]) -> Optional[LiveResponse]:
        """Process Live API response message into LiveResponse object"""
        try:
            # Handle different Live API message types
            if "server_content" in message:
                server_content = message["server_content"]
                
                # Text response
                if "model_turn" in server_content:
                    model_turn = server_content["model_turn"]
                    if "parts" in model_turn:
                        for part in model_turn["parts"]:
                            if "text" in part:
                                return LiveResponse(
                                    text=part["text"],
                                    metadata={"type": "text_response"},
                                    is_complete=server_content.get("turn_complete", False)
                                )
                
                # Audio response  
                if "audio" in server_content:
                    audio_hex = server_content["audio"]
                    audio_bytes = bytes.fromhex(audio_hex) if isinstance(audio_hex, str) else audio_hex
                    return LiveResponse(
                        audio_data=audio_bytes,
                        metadata={"type": "audio_response", "sample_rate": 24000},
                        is_complete=server_content.get("turn_complete", False)
                    )
            
            # Setup confirmation
            elif "setup_complete" in message:
                return LiveResponse(
                    metadata={"type": "setup_complete", "session_id": message.get("session_id")},
                    is_complete=False
                )
            
            # Error messages
            elif "error" in message:
                return LiveResponse(
                    error=message["error"].get("message", "Unknown error"),
                    is_complete=True
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ LIVE_API [PROCESS] Error processing response: {str(e)}")
            return LiveResponse(error=f"Response processing error: {str(e)}")
    
    def is_connected_status(self) -> bool:
        """Check if client is connected"""
        return self.is_connected and self.websocket is not None
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information"""
        return {
            "connected": self.is_connected,
            "session_id": self.session_id,
            "model": self.model_name,
            "project": self.project_id,
            "region": self.region
        }