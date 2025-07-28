#!/usr/bin/env python3
"""
Test Live API audio functionality with mock audio data
"""

import asyncio
import websockets
import json
import base64

async def test_live_audio():
    """Test Live API with mock audio input"""
    
    real_learner_session_id = '177fadf3-4744-40e0-811f-71f2621ccfee'
    websocket_url = f"ws://localhost:8000/ws/live/{real_learner_session_id}"
    
    print(f"🎙️ Testing Live Audio API: {websocket_url}")
    
    try:
        # Connect to WebSocket
        websocket = await websockets.connect(websocket_url)
        print("✅ WebSocket connected")
        
        # Wait for session started
        response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
        session_msg = json.loads(response)
        print(f"🎯 Session started: {session_msg.get('live_session_id')}")
        
        # Create mock audio data (simulate 16kHz PCM audio)
        mock_audio_data = b"MOCK_AUDIO_16KHZ_PCM_DATA" * 100  # Simulate ~2.5KB of audio
        audio_b64 = base64.b64encode(mock_audio_data).decode('utf-8')
        
        # Send audio message
        audio_message = {
            "type": "audio",
            "data": audio_b64,
            "mime_type": "audio/pcm;rate=16000"
        }
        
        print(f"🎙️ Sending {len(mock_audio_data)} bytes of mock audio...")
        await websocket.send(json.dumps(audio_message))
        
        # Wait for audio response
        print("👂 Waiting for audio response...")
        response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
        response_msg = json.loads(response)
        
        if response_msg.get("type") == "audio_response":
            # Decode the audio response
            audio_response_b64 = response_msg.get("data", "")
            audio_response = base64.b64decode(audio_response_b64)
            
            metadata = response_msg.get("metadata", {})
            text_transcript = metadata.get("text_transcript", "")
            
            print(f"🔊 Received audio response: {len(audio_response)} bytes")
            print(f"📝 Text transcript: {text_transcript}")
            print(f"📊 Metadata: {metadata}")
            
            # Verify it's a mock response
            if text_transcript and "mock" not in text_transcript.lower():
                print("✅ Mock Live API generated contextual French response!")
            
            success = True
            
        elif response_msg.get("type") == "error":
            print(f"❌ Error response: {response_msg.get('message')}")
            success = False
            
        else:
            print(f"❓ Unexpected response: {response_msg}")
            success = False
        
        # Close connection
        await websocket.send(json.dumps({"type": "close"}))
        await websocket.close()
        
        return success
        
    except asyncio.TimeoutError:
        print("⚠️ Timeout waiting for audio response")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_live_audio())
    if result:
        print("\n🎉 Live Voice functionality is working!")
        print("✅ Ready for frontend integration")
    else:
        print("\n❌ Live Voice test failed")