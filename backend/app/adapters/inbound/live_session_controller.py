"""
FIA v3.0 - Live Session WebSocket Controller
FastAPI WebSocket endpoints for Live API conversation service
"""

import logging
import json
import base64
from typing import Dict, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from starlette.websockets import WebSocketState
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4
import asyncio
import time

from app.infrastructure.database import get_database_session
from app.domain.services.live_conversation_service import LiveConversationService, LiveConversationError
from app.adapters.outbound.live_api_adapter import LiveAPIAdapter
from app.adapters.repositories.learner_session_repository import LearnerSessionRepository
from app.adapters.repositories.slide_repository import SlideRepository
from app.adapters.repositories.training_session_repository import TrainingSessionRepository
from app.adapters.repositories.chat_message_repository import ChatMessageRepository

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["live-api"])


class ConnectionManager:
    """Manager for WebSocket connections to Live API sessions"""
    
    def __init__(self):
        # Track active WebSocket connections
        self.active_connections: Dict[str, WebSocket] = {}
        # Track connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        
    async def connect(self, websocket: WebSocket, connection_id: str, learner_session_id: UUID):
        """Accept WebSocket connection and store metadata"""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        self.connection_metadata[connection_id] = {
            "learner_session_id": learner_session_id,
            "connected_at": asyncio.get_event_loop().time(),
            "messages_sent": 0,
            "messages_received": 0
        }
        logger.info(f"🔗 LIVE_WS [CONNECT] WebSocket connected: {connection_id} for learner: {learner_session_id}")
    
    def disconnect(self, connection_id: str):
        """Remove WebSocket connection and cleanup metadata"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        if connection_id in self.connection_metadata:
            metadata = self.connection_metadata[connection_id]
            logger.info(f"🔌 LIVE_WS [DISCONNECT] WebSocket disconnected: {connection_id} "
                       f"(sent: {metadata['messages_sent']}, received: {metadata['messages_received']})")
            del self.connection_metadata[connection_id]
    
    async def send_message(self, connection_id: str, message: Dict[str, Any]):
        """Send message to specific WebSocket connection"""
        if connection_id not in self.active_connections:
            logger.warning(f"⚠️ LIVE_WS [SEND] Connection {connection_id} not found in active connections")
            return
            
        websocket = self.active_connections[connection_id]
        try:
            # Check WebSocket state before sending
            if websocket.client_state != WebSocketState.CONNECTED:
                logger.warning(f"⚠️ LIVE_WS [SEND] WebSocket {connection_id} not connected (state: {websocket.client_state})")
                self.disconnect(connection_id)
                return
                
            await websocket.send_text(json.dumps(message))
            if connection_id in self.connection_metadata:
                self.connection_metadata[connection_id]["messages_sent"] += 1
            logger.debug(f"📤 LIVE_WS [SEND] Message sent to {connection_id}")
        except Exception as e:
            logger.error(f"❌ LIVE_WS [SEND] Error sending message to {connection_id}: {str(e)}")
            # Connection might be stale, remove it
            self.disconnect(connection_id)
            # Don't re-raise exception to prevent further loops
            logger.debug(f"🔇 LIVE_WS [SEND] Silently ignoring send error for {connection_id}")
    
    async def send_audio_response(self, connection_id: str, audio_data: bytes, metadata: Dict[str, Any] = None):
        """Send audio response to WebSocket connection"""
        # Encode audio data as base64 for JSON transport
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        
        message = {
            "type": "audio_response",
            "data": audio_b64,
            "metadata": metadata or {}
        }
        
        await self.send_message(connection_id, message)
    
    async def send_error(self, connection_id: str, error_message: str, error_type: str = "general"):
        """Send error message to WebSocket connection"""
        message = {
            "type": "error",
            "error_type": error_type,
            "message": error_message
        }
        
        await self.send_message(connection_id, message)
    
    def get_connection_count(self) -> int:
        """Get count of active connections"""
        return len(self.active_connections)
    
    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get connection metadata"""
        return self.connection_metadata.get(connection_id)


# Global connection manager instance
connection_manager = ConnectionManager()

# Global Live API adapter instance (singleton for throttling state)
_live_api_adapter_instance = None


async def get_live_conversation_service(db: AsyncSession = Depends(get_database_session)) -> LiveConversationService:
    """Dependency to get Live Conversation Service with all dependencies injected"""
    # Initialize adapters and repositories
    global _live_api_adapter_instance
    if _live_api_adapter_instance is None:
        _live_api_adapter_instance = LiveAPIAdapter()
        logger.info("🔧 [LIVE_WS] Created singleton LiveAPIAdapter instance")
    
    live_api_adapter = _live_api_adapter_instance
    learner_session_repo = LearnerSessionRepository(db)
    slide_repo = SlideRepository(db)
    training_session_repo = TrainingSessionRepository(db)
    chat_message_repo = ChatMessageRepository(db)
    
    # Create and return service
    return LiveConversationService(
        live_api_adapter=live_api_adapter,
        learner_session_repository=learner_session_repo,
        slide_repository=slide_repo,
        training_session_repository=training_session_repo,
        chat_message_repository=chat_message_repo
    )


@router.websocket("/ws/live/{learner_session_id}")
async def live_session_websocket(
    websocket: WebSocket,
    learner_session_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """
    WebSocket endpoint for Live API conversation sessions
    
    Protocol:
    - Client connects to /ws/live/{learner_session_id}
    - Server starts Live API session automatically
    - Client sends audio data in JSON format: {"type": "audio", "data": "base64_audio_data"}
    - Server responds with: {"type": "audio_response", "data": "base64_audio_data", "metadata": {...}}
    - Either side can send: {"type": "error", "message": "error description"}
    - Client sends: {"type": "close"} to end session
    """
    
    # Generate unique connection ID
    connection_id = f"live_{learner_session_id}_{uuid4().hex[:8]}"
    live_service = None
    live_session_id = None
    
    try:
        logger.info(f"🎙️ LIVE_WS [NEW] New Live WebSocket connection request for learner: {learner_session_id}")
        
        # Initialize Live Conversation Service
        live_service = await get_live_conversation_service(db)
        
        # Accept WebSocket connection
        await connection_manager.connect(websocket, connection_id, learner_session_id)
        
        # Start Live API session
        try:
            session_info = await live_service.start_live_session(learner_session_id)
            live_session_id = session_info["live_session_id"]
            
            # Send session started confirmation
            await connection_manager.send_message(connection_id, {
                "type": "session_started",
                "live_session_id": live_session_id,
                "status": session_info["status"],
                "slide_context": {
                    "title": session_info["slide_context"]["title"],
                    "slide_number": session_info["slide_context"]["slide_number"]
                },
                "metadata": session_info["metadata"]
            })
            
            logger.info(f"✅ LIVE_WS [SESSION_STARTED] Live session started: {live_session_id} for connection: {connection_id}")
            
        except LiveConversationError as e:
            logger.error(f"❌ LIVE_WS [SESSION_ERROR] Failed to start Live session: {str(e)}")
            await connection_manager.send_error(connection_id, f"Failed to start Live session: {str(e)}", "session_start")
            return
        
        # Main message handling loop
        while True:
            try:
                # Check connection state before receiving
                if websocket.client_state != WebSocketState.CONNECTED:
                    logger.info(f"🔌 LIVE_WS [STATE_CHECK] WebSocket not connected: {connection_id}")
                    break
                    
                # Receive message from client with timeout
                import asyncio
                try:
                    raw_message = await asyncio.wait_for(
                        websocket.receive_text(), 
                        timeout=30.0
                    )
                except asyncio.TimeoutError:
                    # Send ping to check if connection is alive
                    try:
                        await connection_manager.send_message(connection_id, {"type": "ping"})
                        continue
                    except Exception:
                        logger.info(f"🔌 LIVE_WS [TIMEOUT] Connection timeout: {connection_id}")
                        break
                
                connection_manager.connection_metadata[connection_id]["messages_received"] += 1
                
                try:
                    message = json.loads(raw_message)
                except json.JSONDecodeError as e:
                    logger.error(f"❌ LIVE_WS [JSON_ERROR] Invalid JSON from {connection_id}: {str(e)}")
                    await connection_manager.send_error(connection_id, "Invalid JSON format", "json_error")
                    continue
                
                message_type = message.get("type")
                logger.debug(f"📥 LIVE_WS [RECEIVE] Message type '{message_type}' from {connection_id}")
                
                # Handle different message types
                if message_type == "audio":
                    await handle_audio_message(connection_id, message, live_service, learner_session_id)
                
                elif message_type == "ping":
                    # Respond to ping with pong
                    await connection_manager.send_message(connection_id, {"type": "pong"})
                
                elif message_type == "close":
                    logger.info(f"🔚 LIVE_WS [CLOSE_REQUEST] Client requested close for {connection_id}")
                    break
                
                else:
                    logger.warning(f"⚠️ LIVE_WS [UNKNOWN_TYPE] Unknown message type '{message_type}' from {connection_id}")
                    await connection_manager.send_error(connection_id, f"Unknown message type: {message_type}", "unknown_type")
                
            except WebSocketDisconnect:
                logger.info(f"🔌 LIVE_WS [DISCONNECT] WebSocket disconnected: {connection_id}")
                break
            
            except Exception as e:
                logger.error(f"❌ LIVE_WS [MESSAGE_ERROR] Error processing message from {connection_id}: {str(e)}")
                # Don't try to send error message if WebSocket is in bad state
                # Just break out of the loop to prevent infinite errors
                logger.info(f"🛑 LIVE_WS [BREAK] Breaking message loop due to error: {connection_id}")
                break
    
    except Exception as e:
        logger.error(f"❌ LIVE_WS [FATAL_ERROR] Fatal error in WebSocket handler for {connection_id}: {str(e)}")
    
    finally:
        # Cleanup
        logger.info(f"🧹 LIVE_WS [CLEANUP] Cleaning up connection: {connection_id}")
        
        # Stop Live API session if it was started
        if live_service and live_session_id:
            try:
                await live_service.stop_live_session(learner_session_id)
                logger.info(f"✅ LIVE_WS [CLEANUP] Live session stopped: {live_session_id}")
            except Exception as e:
                logger.error(f"❌ LIVE_WS [CLEANUP] Error stopping Live session: {str(e)}")
        
        # Disconnect WebSocket
        connection_manager.disconnect(connection_id)
        logger.info(f"✅ LIVE_WS [CLEANUP] Connection cleanup completed: {connection_id}")


async def handle_audio_message(
    connection_id: str,
    message: Dict[str, Any],
    live_service: LiveConversationService,
    learner_session_id: UUID
):
    """Handle audio message from WebSocket client"""
    try:
        # Check if connection still exists before processing
        if connection_id not in connection_manager.active_connections:
            logger.info(f"🔌 LIVE_WS [AUDIO] Connection {connection_id} no longer active, skipping audio processing")
            return
        
        # Extract and decode audio data
        audio_b64 = message.get("data")
        if not audio_b64:
            await connection_manager.send_error(connection_id, "Missing audio data", "audio_missing")
            return
        
        try:
            audio_data = base64.b64decode(audio_b64)
        except Exception as e:
            logger.error(f"❌ LIVE_WS [AUDIO_DECODE] Error decoding audio from {connection_id}: {str(e)}")
            await connection_manager.send_error(connection_id, "Invalid audio data encoding", "audio_decode")
            return
        
        logger.info(f"🎙️ LIVE_WS [AUDIO] Processing {len(audio_data)} bytes of audio from {connection_id}")
        
        # Get MIME type from message or use default
        mime_type = message.get("mime_type", "audio/pcm;rate=16000")
        
        # Validate and normalize MIME type
        supported_types = [
            "audio/webm", "audio/webm;codecs=opus", "audio/webm;codecs=pcm",
            "audio/ogg", "audio/ogg;codecs=opus", 
            "audio/pcm", "audio/pcm;rate=16000",
            "audio/wav", "audio/mp4"
        ]
        
        if mime_type not in supported_types:
            logger.warning(f"⚠️ LIVE_WS [AUDIO] Unsupported MIME type {mime_type}, using default")
            mime_type = "audio/webm"
        
        logger.debug(f"🎙️ LIVE_WS [AUDIO] Using MIME type: {mime_type}")
        
        # Process audio through Live Conversation Service
        response = await live_service.process_live_interaction(
            learner_session_id=learner_session_id,
            audio_data=audio_data,
            mime_type=mime_type
        )
        
        # Send response back to client (audio or text-only)
        # Check if we have either audio data OR text transcript OR if it's throttled
        has_audio = response["audio_response"] and len(response["audio_response"]) > 0
        has_text = response.get("text_transcript") and len(response.get("text_transcript", "").strip()) > 0
        
        # Check for throttled in the correct metadata location
        processing_metadata = response.get("metadata", {}).get("processing_metadata", {})
        is_throttled = processing_metadata.get("throttled", False)
        is_mock_mode = processing_metadata.get("mock", False)
        
        if has_audio or has_text or is_throttled:
            # Double-check connection is still active before sending response
            if connection_id not in connection_manager.active_connections:
                logger.info(f"🔌 LIVE_WS [AUDIO_RESPONSE] Connection {connection_id} closed during processing, skipping response")
                return
            
            await connection_manager.send_audio_response(
                connection_id=connection_id,
                audio_data=response["audio_response"],
                metadata={
                    "text_transcript": response.get("text_transcript", ""),
                    "session_updated": response.get("session_updated", False),
                    "processing_metadata": response.get("metadata", {})
                }
            )
            if has_audio:
                logger.info(f"🔊 LIVE_WS [AUDIO_RESPONSE] Sent {len(response['audio_response'])} bytes audio response to {connection_id}")
            elif is_throttled:
                logger.info(f"⏸️ LIVE_WS [THROTTLED_RESPONSE] Sent throttled response to {connection_id}")
            else:
                logger.info(f"📝 LIVE_WS [TEXT_RESPONSE] Sent text-only response to {connection_id} (mock mode: {is_mock_mode})")
        else:
            # Send error only if we have neither audio nor text and it's not throttled
            logger.warning(f"⚠️ LIVE_WS [NO_RESPONSE] No audio or text response generated for {connection_id}")
            # Check connection is still active before sending error
            if connection_id in connection_manager.active_connections:
                await connection_manager.send_error(connection_id, "No response generated", "no_response")
            else:
                logger.info(f"🔌 LIVE_WS [NO_RESPONSE] Connection {connection_id} closed, skipping error message")
    
    except LiveConversationError as e:
        logger.error(f"❌ LIVE_WS [AUDIO_PROCESSING] Live conversation error for {connection_id}: {str(e)}")
        if connection_id in connection_manager.active_connections:
            await connection_manager.send_error(connection_id, f"Live conversation error: {str(e)}", "live_conversation")
    
    except Exception as e:
        logger.error(f"❌ LIVE_WS [AUDIO_ERROR] Unexpected error processing audio from {connection_id}: {str(e)}")
        if connection_id in connection_manager.active_connections:
            await connection_manager.send_error(connection_id, "Error processing audio", "audio_processing")


# ============================================================================
# REST API ENDPOINTS FOR LIVE SESSION MANAGEMENT
# ============================================================================

@router.get("/api/live/status/{learner_session_id}", status_code=status.HTTP_200_OK)
async def get_live_session_status(
    learner_session_id: UUID,
    live_service: LiveConversationService = Depends(get_live_conversation_service)
):
    """
    Get status of Live API session for a learner
    
    Returns information about whether the learner has an active Live session,
    and if so, provides session details.
    """
    try:
        logger.info(f"📊 LIVE_API [STATUS] Getting Live session status for learner: {learner_session_id}")
        
        status_info = await live_service.get_live_session_status(learner_session_id)
        
        # Add WebSocket connection info
        active_connections = [
            conn_id for conn_id, metadata in connection_manager.connection_metadata.items()
            if metadata["learner_session_id"] == learner_session_id
        ]
        
        status_info["websocket_connections"] = len(active_connections)
        status_info["connection_ids"] = active_connections
        
        logger.info(f"✅ LIVE_API [STATUS] Retrieved status for learner: {learner_session_id}")
        return status_info
        
    except Exception as e:
        logger.error(f"❌ LIVE_API [STATUS] Error getting status for {learner_session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get Live session status"
        )


@router.post("/api/live/stop/{learner_session_id}", status_code=status.HTTP_200_OK)
async def stop_live_session(
    learner_session_id: UUID,
    live_service: LiveConversationService = Depends(get_live_conversation_service)
):
    """
    Manually stop Live API session for a learner
    
    This endpoint allows manual termination of a Live session, useful for
    administrative purposes or error recovery.
    """
    try:
        logger.info(f"🛑 LIVE_API [STOP] Manually stopping Live session for learner: {learner_session_id}")
        
        success = await live_service.stop_live_session(learner_session_id)
        
        if success:
            logger.info(f"✅ LIVE_API [STOP] Successfully stopped Live session for learner: {learner_session_id}")
            return {"status": "stopped", "learner_session_id": str(learner_session_id)}
        else:
            logger.warning(f"⚠️ LIVE_API [STOP] Live session stop had issues for learner: {learner_session_id}")
            return {"status": "error", "learner_session_id": str(learner_session_id), "message": "Stop operation had issues"}
        
    except Exception as e:
        logger.error(f"❌ LIVE_API [STOP] Error stopping Live session for {learner_session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop Live session"
        )


@router.get("/api/live/connections", status_code=status.HTTP_200_OK)
async def get_active_connections():
    """
    Get information about active WebSocket connections
    
    This endpoint provides admin/debug information about current Live API
    WebSocket connections.
    """
    try:
        logger.info("📊 LIVE_API [CONNECTIONS] Getting active connections info")
        
        connections_info = []
        for conn_id, metadata in connection_manager.connection_metadata.items():
            connections_info.append({
                "connection_id": conn_id,
                "learner_session_id": str(metadata["learner_session_id"]),
                "connected_at": metadata["connected_at"],
                "messages_sent": metadata["messages_sent"],
                "messages_received": metadata["messages_received"]
            })
        
        return {
            "total_connections": connection_manager.get_connection_count(),
            "connections": connections_info
        }
        
    except Exception as e:
        logger.error(f"❌ LIVE_API [CONNECTIONS] Error getting connections info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get connections information"
        )


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/api/live/health", status_code=status.HTTP_200_OK)
async def live_api_health_check():
    """Health check for Live API service"""
    try:
        # Test Live API adapter availability
        live_adapter = LiveAPIAdapter()
        
        return {
            "status": "healthy",
            "service": "live_api",
            "version": "1.0",
            "active_connections": connection_manager.get_connection_count(),
            "active_live_sessions": live_adapter.get_session_count()
        }
    except Exception as e:
        logger.error(f"❌ LIVE_API [HEALTH] Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "live_api",
            "version": "1.0",
            "active_connections": connection_manager.get_connection_count(),
            "error": str(e)
        }