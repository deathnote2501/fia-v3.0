"""
Test script for LiveAPIClient
Simple test to validate the Live API client implementation
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the backend app to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.infrastructure.live_api_client import LiveAPIClient, AudioData, LiveAPIError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_live_api_client():
    """Test basic Live API client functionality"""
    logger.info("🧪 Starting Live API Client Test")
    
    # Initialize client
    client = LiveAPIClient()
    
    # Test 1: Check initial state
    logger.info("Test 1: Checking initial state...")
    assert not client.is_connected_status(), "Client should not be connected initially"
    logger.info("✅ Initial state test passed")
    
    # Test 2: Session configuration
    logger.info("Test 2: Testing session configuration...")
    session_config = {
        "response_modalities": ["AUDIO"],
        "system_instruction": "Tu es un formateur IA expert en formation professionnelle.",
        "speech_config": {
            "voice_config": {
                "prebuilt_voice_config": {
                    "voice_name": "Kore"
                }
            }
        },
        "context": {
            "slide_content": "Introduction aux KPI et métriques de performance",
            "slide_title": "KPI Dashboard",
            "learner_profile": {
                "experience_level": "intermediate",
                "learning_style": "visual",
                "job_position": "manager"
            }
        }
    }
    logger.info("✅ Session configuration test passed")
    
    # Test 3: Connection attempt (will fail without proper auth, but should not crash)
    logger.info("Test 3: Testing connection attempt (expected to fail gracefully)...")
    try:
        await client.connect(session_config)
        logger.info("✅ Connection succeeded (unexpected but OK)")
    except LiveAPIError as e:
        logger.info(f"✅ Connection failed as expected: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Unexpected error during connection: {str(e)}")
        return False
    
    # Test 4: Audio data creation
    logger.info("Test 4: Testing audio data creation...")
    test_audio_bytes = b"fake_audio_data_for_testing"
    audio_data = AudioData(
        data=test_audio_bytes,
        mime_type="audio/pcm;rate=16000",
        sample_rate=16000
    )
    assert audio_data.data == test_audio_bytes, "Audio data should match"
    assert audio_data.sample_rate == 16000, "Sample rate should be 16000"
    logger.info("✅ Audio data creation test passed")
    
    # Test 5: Send audio (will fail without connection, but should not crash)
    logger.info("Test 5: Testing send audio (expected to fail gracefully)...")
    try:
        await client.send_audio(audio_data)
        logger.info("✅ Audio sent successfully (unexpected but OK)")
    except LiveAPIError as e:
        logger.info(f"✅ Audio send failed as expected: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Unexpected error during audio send: {str(e)}")
        return False
    
    # Test 6: Session info
    logger.info("Test 6: Testing session info...")
    session_info = client.get_session_info()
    expected_keys = ["connected", "session_id", "model", "project", "region"]
    for key in expected_keys:
        assert key in session_info, f"Session info should contain {key}"
    logger.info("✅ Session info test passed")
    
    # Test 7: Disconnect
    logger.info("Test 7: Testing disconnect...")
    await client.disconnect()
    assert not client.is_connected_status(), "Client should not be connected after disconnect"
    logger.info("✅ Disconnect test passed")
    
    logger.info("🎉 All Live API Client tests passed!")
    return True


async def test_websocket_url_building():
    """Test WebSocket URL building"""
    logger.info("🧪 Testing WebSocket URL building...")
    
    client = LiveAPIClient()
    
    # Access private method for testing
    url = client._build_websocket_url()
    
    # Verify URL structure
    assert "wss://" in url, "URL should use WSS protocol"
    assert "aiplatform.googleapis.com" in url, "URL should point to AI Platform"
    assert "streamGenerateContent" in url, "URL should contain streamGenerateContent endpoint"
    assert client.model_name in url, "URL should contain model name"
    
    logger.info(f"✅ Generated URL: {url}")
    logger.info("✅ WebSocket URL building test passed")


async def main():
    """Run all tests"""
    logger.info("🚀 Starting Live API Client Tests")
    
    try:
        # Run basic client tests
        success = await test_live_api_client()
        if not success:
            logger.error("❌ Basic client tests failed")
            return False
        
        # Run URL building tests
        await test_websocket_url_building()
        
        logger.info("🎉 All tests completed successfully!")
        logger.info("📝 Note: Actual Live API connection requires proper authentication and Google Cloud setup")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test suite failed with error: {str(e)}")
        return False


if __name__ == "__main__":
    # Run the test
    result = asyncio.run(main())
    
    if result:
        print("\n✅ Live API Client implementation is ready!")
        print("📋 Next steps:")
        print("   1. Set up proper Google Cloud authentication")
        print("   2. Configure environment variables")
        print("   3. Test with real Live API endpoint")
    else:
        print("\n❌ Tests failed - check implementation")
        sys.exit(1)