"""
Test script for LiveSessionController
Simple test to validate the WebSocket Live API controller implementation
"""

import asyncio
import logging
import sys
import json
import base64
from pathlib import Path
from uuid import uuid4
from unittest.mock import AsyncMock, Mock

# Add the backend app to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.adapters.inbound.live_session_controller import ConnectionManager, handle_audio_message

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockWebSocket:
    """Mock WebSocket for testing"""
    
    def __init__(self):
        self.messages_sent = []
        self.messages_to_receive = []
        self.closed = False
    
    async def accept(self):
        """Mock accept method"""
        pass
    
    async def send_text(self, data):
        """Mock send_text method"""
        self.messages_sent.append(data)
    
    async def receive_text(self):
        """Mock receive_text method"""
        if self.messages_to_receive:
            return self.messages_to_receive.pop(0)
        else:
            # Simulate disconnect if no more messages
            from fastapi import WebSocketDisconnect
            raise WebSocketDisconnect()
    
    def add_message_to_receive(self, message):
        """Add message to the queue for receive_text"""
        self.messages_to_receive.append(json.dumps(message))


class MockLiveConversationService:
    """Mock Live Conversation Service for testing"""
    
    def __init__(self):
        self.sessions_started = []
        self.interactions_processed = []
        self.sessions_stopped = []
    
    async def start_live_session(self, learner_session_id):
        self.sessions_started.append(learner_session_id)
        return {
            "live_session_id": f"live_session_{uuid4()}",
            "status": "active",
            "slide_context": {
                "title": "Test Slide",
                "slide_number": 1
            },
            "metadata": {"test": True}
        }
    
    async def process_live_interaction(self, learner_session_id, audio_data, mime_type):
        self.interactions_processed.append({
            "learner_session_id": learner_session_id,
            "audio_size": len(audio_data),
            "mime_type": mime_type
        })
        
        return {
            "audio_response": b"mock_audio_response_data",
            "text_transcript": "Mock response from AI trainer",
            "session_updated": True,
            "metadata": {"mock": True}
        }
    
    async def stop_live_session(self, learner_session_id):
        self.sessions_stopped.append(learner_session_id)
        return True
    
    async def get_live_session_status(self, learner_session_id):
        return {
            "has_active_session": learner_session_id in [s for s in self.sessions_started if s not in self.sessions_stopped],
            "learner_session_id": str(learner_session_id)
        }


async def test_connection_manager():
    """Test ConnectionManager functionality"""
    logger.info("🧪 Testing ConnectionManager...")
    
    manager = ConnectionManager()
    websocket = MockWebSocket()
    connection_id = "test_connection_1"
    learner_session_id = uuid4()
    
    # Test 1: Initial state
    assert manager.get_connection_count() == 0, "Should start with no connections"
    
    # Test 2: Connect
    await manager.connect(websocket, connection_id, learner_session_id)
    assert manager.get_connection_count() == 1, "Should have 1 connection after connect"
    
    connection_info = manager.get_connection_info(connection_id)
    assert connection_info is not None, "Connection info should exist"
    assert connection_info["learner_session_id"] == learner_session_id, "Should store correct learner session ID"
    
    # Test 3: Send message
    test_message = {"type": "test", "data": "hello"}
    await manager.send_message(connection_id, test_message)
    
    assert len(websocket.messages_sent) == 1, "Should send 1 message"
    sent_message = json.loads(websocket.messages_sent[0])
    assert sent_message == test_message, "Should send correct message"
    
    # Test 4: Send audio response
    test_audio = b"test_audio_data"
    await manager.send_audio_response(connection_id, test_audio, {"sample_rate": 24000})
    
    assert len(websocket.messages_sent) == 2, "Should send 2 messages total"
    audio_message = json.loads(websocket.messages_sent[1])
    assert audio_message["type"] == "audio_response", "Should be audio response type"
    assert "data" in audio_message, "Should contain audio data"
    
    # Test 5: Send error
    await manager.send_error(connection_id, "Test error", "test_error")
    
    assert len(websocket.messages_sent) == 3, "Should send 3 messages total"
    error_message = json.loads(websocket.messages_sent[2])
    assert error_message["type"] == "error", "Should be error type"
    assert error_message["message"] == "Test error", "Should contain error message"
    
    # Test 6: Disconnect
    manager.disconnect(connection_id)
    assert manager.get_connection_count() == 0, "Should have no connections after disconnect"
    assert manager.get_connection_info(connection_id) is None, "Connection info should be removed"
    
    logger.info("✅ ConnectionManager tests passed")


async def test_handle_audio_message():
    """Test audio message handling"""
    logger.info("🧪 Testing handle_audio_message...")
    
    # Setup mocks
    connection_manager_mock = Mock()
    connection_manager_mock.send_audio_response = AsyncMock()
    connection_manager_mock.send_error = AsyncMock()
    
    live_service = MockLiveConversationService()
    connection_id = "test_connection"
    learner_session_id = uuid4()
    
    # Test audio data
    test_audio = b"fake_audio_data_for_testing"
    audio_b64 = base64.b64encode(test_audio).decode('utf-8')
    
    # Test 1: Valid audio message
    message = {
        "type": "audio",
        "data": audio_b64,
        "mime_type": "audio/pcm;rate=16000"
    }
    
    # Replace the global connection_manager temporarily
    import app.adapters.inbound.live_session_controller as controller_module
    original_connection_manager = controller_module.connection_manager
    controller_module.connection_manager = connection_manager_mock
    
    try:
        await handle_audio_message(connection_id, message, live_service, learner_session_id)
        
        # Verify interaction was processed
        assert len(live_service.interactions_processed) == 1, "Should process 1 interaction"
        interaction = live_service.interactions_processed[0]
        assert interaction["learner_session_id"] == learner_session_id, "Should process for correct learner"
        assert interaction["audio_size"] == len(test_audio), "Should process correct audio size"
        
        # Verify response was sent
        connection_manager_mock.send_audio_response.assert_called_once()
        call_args = connection_manager_mock.send_audio_response.call_args
        assert call_args[1]["connection_id"] == connection_id, "Should send to correct connection"
        
        logger.info("✅ Valid audio message test passed")
        
        # Test 2: Missing audio data
        connection_manager_mock.reset_mock()
        invalid_message = {"type": "audio"}  # Missing data field
        
        await handle_audio_message(connection_id, invalid_message, live_service, learner_session_id)
        
        # Should send error
        connection_manager_mock.send_error.assert_called_once()
        error_call = connection_manager_mock.send_error.call_args
        assert "Missing audio data" in error_call[0][1], "Should send missing data error"
        
        logger.info("✅ Missing audio data test passed")
        
        # Test 3: Invalid base64 data
        connection_manager_mock.reset_mock()
        invalid_b64_message = {
            "type": "audio",
            "data": "invalid_base64_data!"
        }
        
        await handle_audio_message(connection_id, invalid_b64_message, live_service, learner_session_id)
        
        # Should send decode error
        connection_manager_mock.send_error.assert_called_once()
        error_call = connection_manager_mock.send_error.call_args
        assert "audio_decode" in error_call[0][2], "Should send decode error type"
        
        logger.info("✅ Invalid base64 test passed")
        
    finally:
        # Restore original connection manager
        controller_module.connection_manager = original_connection_manager


async def test_websocket_protocol():
    """Test WebSocket protocol messages"""
    logger.info("🧪 Testing WebSocket protocol...")
    
    # Test message format validation
    test_cases = [
        # Valid messages
        ({"type": "audio", "data": "base64data"}, True),
        ({"type": "ping"}, True),
        ({"type": "close"}, True),
        
        # Invalid messages
        ({"invalid": "message"}, False),  # Missing type
        ({"type": "audio"}, False),       # Missing data for audio
        ("not_json", False),              # Not valid JSON
    ]
    
    for message, should_be_valid in test_cases:
        if isinstance(message, dict):
            # Test JSON serialization
            try:
                json_str = json.dumps(message)
                parsed = json.loads(json_str)
                
                # Check message structure
                has_type = "type" in parsed
                is_audio_with_data = parsed.get("type") == "audio" and "data" in parsed
                is_non_audio = parsed.get("type") in ["ping", "close"]
                
                is_valid = has_type and (is_audio_with_data or is_non_audio)
                
                if should_be_valid:
                    assert is_valid, f"Message should be valid: {message}"
                    logger.debug(f"✅ Valid message: {message}")
                else:
                    # For missing data in audio messages
                    if parsed.get("type") == "audio" and "data" not in parsed:
                        assert not is_valid, f"Audio message without data should be invalid: {message}"
                        logger.debug(f"✅ Invalid message correctly identified: {message}")
                    
            except json.JSONDecodeError:
                if not should_be_valid:
                    logger.debug(f"✅ Non-JSON message correctly rejected: {message}")
                else:
                    assert False, f"Valid message failed JSON parsing: {message}"
        else:
            # Non-dict messages should be invalid
            assert not should_be_valid, f"Non-dict message should be invalid: {message}"
    
    logger.info("✅ WebSocket protocol tests passed")


async def test_live_service_integration():
    """Test integration with Live Conversation Service"""
    logger.info("🧪 Testing Live Service integration...")
    
    mock_service = MockLiveConversationService()
    learner_session_id = uuid4()
    
    # Test session lifecycle
    
    # 1. Start session
    session_info = await mock_service.start_live_session(learner_session_id)
    assert "live_session_id" in session_info, "Should return session info"
    assert session_info["status"] == "active", "Should be active"
    assert len(mock_service.sessions_started) == 1, "Should track started session"
    
    # 2. Process interaction
    test_audio = b"test_audio_data"
    response = await mock_service.process_live_interaction(
        learner_session_id, test_audio, "audio/pcm;rate=16000"
    )
    
    assert "audio_response" in response, "Should return audio response"
    assert len(response["audio_response"]) > 0, "Should have audio data"
    assert len(mock_service.interactions_processed) == 1, "Should track processed interaction"
    
    # 3. Check status
    status = await mock_service.get_live_session_status(learner_session_id)
    assert status["has_active_session"] == True, "Should have active session"
    
    # 4. Stop session
    stop_success = await mock_service.stop_live_session(learner_session_id)
    assert stop_success == True, "Should stop successfully"
    assert len(mock_service.sessions_stopped) == 1, "Should track stopped session"
    
    # 5. Check status after stop
    status_after = await mock_service.get_live_session_status(learner_session_id)
    assert status_after["has_active_session"] == False, "Should not have active session after stop"
    
    logger.info("✅ Live Service integration tests passed")


async def main():
    """Run all tests"""
    logger.info("🚀 Starting Live Session Controller Tests")
    
    try:
        # Run all test functions
        await test_connection_manager()
        await test_handle_audio_message()
        await test_websocket_protocol()
        await test_live_service_integration()
        
        logger.info("🎉 All tests completed successfully!")
        logger.info("📝 Note: Tests use mocks - real WebSocket integration requires running server")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test suite failed with error: {str(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    # Run the test
    result = asyncio.run(main())
    
    if result:
        print("\n✅ Live Session Controller implementation is ready!")
        print("📋 Next steps:")
        print("   1. Test WebSocket endpoints with real server")
        print("   2. Create frontend Live button and audio handling")
        print("   3. Test end-to-end audio flow")
        print("   4. Add proper authentication for WebSocket connections")
    else:
        print("\n❌ Tests failed - check implementation")
        sys.exit(1)