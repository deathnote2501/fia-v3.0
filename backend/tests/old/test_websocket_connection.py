#!/usr/bin/env python3
"""
Test script to verify WebSocket Live API endpoint connectivity
"""

import asyncio
import websockets
import json
import sys
from uuid import uuid4

async def test_websocket_connection():
    """Test basic WebSocket connection to Live API endpoint"""
    
    # Use a test learner session ID
    test_learner_session_id = str(uuid4())
    websocket_url = f"ws://localhost:8000/ws/live/{test_learner_session_id}"
    
    print(f"🔗 Testing WebSocket connection to: {websocket_url}")
    
    try:
        async with websockets.connect(websocket_url) as websocket:
            print("✅ WebSocket connection established successfully!")
            
            # Wait for session_started message
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                message = json.loads(response)
                print(f"📥 Received message: {message}")
                
                if message.get("type") == "session_started":
                    print("✅ Live session started successfully!")
                else:
                    print(f"⚠️ Unexpected message type: {message.get('type')}")
                    
            except asyncio.TimeoutError:
                print("⚠️ No session_started message received within 5 seconds")
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse response as JSON: {e}")
            
            # Send a ping message
            ping_message = {"type": "ping"}
            await websocket.send(json.dumps(ping_message))
            print("📤 Sent ping message")
            
            # Wait for pong response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                message = json.loads(response)
                if message.get("type") == "pong":
                    print("✅ Received pong response - WebSocket communication working!")
                else:
                    print(f"📥 Received: {message}")
            except asyncio.TimeoutError:
                print("⚠️ No pong response received within 3 seconds")
                
            # Send close message
            close_message = {"type": "close"}
            await websocket.send(json.dumps(close_message))
            print("📤 Sent close message")
            
    except websockets.exceptions.ConnectionRefused:
        print("❌ Connection refused - is the server running on localhost:8000?")
        return False
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ WebSocket connection failed with status code: {e.status_code}")
        print("This might indicate a 404 error or server configuration issue")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

async def main():
    print("🚀 Starting WebSocket Live API connection test...")
    
    success = await test_websocket_connection()
    
    if success:
        print("\n✅ WebSocket test completed successfully!")
        print("📋 Next steps:")
        print("   1. Test with real learner session ID")
        print("   2. Test audio message sending")
        print("   3. Test frontend integration")
        return True
    else:
        print("\n❌ WebSocket test failed!")
        print("📋 Troubleshooting:")
        print("   1. Make sure the FastAPI server is running")
        print("   2. Check that live_session_router is properly included")
        print("   3. Verify the WebSocket endpoint is accessible")
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)