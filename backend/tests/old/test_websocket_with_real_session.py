#!/usr/bin/env python3
"""
Test WebSocket with real learner session
"""

import asyncio
import websockets
import json
import sys
from uuid import UUID

async def test_real_websocket():
    """Test WebSocket with real learner session"""
    
    # Use the real learner session ID that exists in DB
    real_learner_session_id = '177fadf3-4744-40e0-811f-71f2621ccfee'
    websocket_url = f"ws://localhost:8000/ws/live/{real_learner_session_id}"
    
    print(f"🔗 Testing WebSocket with real session: {websocket_url}")
    
    try:
        # Connect without timeout parameter
        async with websockets.connect(websocket_url) as websocket:
            print("✅ WebSocket connection established!")
            
            # Wait for initial message
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                message = json.loads(response)
                print(f"📥 Received: {message}")
                
                if message.get("type") == "session_started":
                    print("🎉 Live session started successfully!")
                    print(f"   Live Session ID: {message.get('live_session_id')}")
                    print(f"   Status: {message.get('status')}")
                    
                    # Check slide context
                    if 'slide_context' in message:
                        context = message['slide_context']
                        print(f"   Slide: {context.get('title')} (#{context.get('slide_number')})")
                    
                elif message.get("type") == "error":
                    print(f"❌ Error from server: {message.get('message')}")
                    return False
                    
            except asyncio.TimeoutError:
                print("⚠️ No initial message received")
                return False
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON: {e}")
                return False
            
            # Test ping-pong
            ping_message = {"type": "ping"}
            await websocket.send(json.dumps(ping_message))
            print("📤 Sent ping")
            
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                message = json.loads(response)
                if message.get("type") == "pong":
                    print("✅ Pong received - communication working!")
                else:
                    print(f"📥 Unexpected response: {message}")
            except asyncio.TimeoutError:
                print("⚠️ No pong received")
            
            # Send close
            close_message = {"type": "close"}
            await websocket.send(json.dumps(close_message))
            print("📤 Sent close message")
            
            return True
            
    except ConnectionRefusedError:
        print("❌ Connection refused - is the server running?")
        return False
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Invalid status code: {e.status_code}")
        if e.status_code == 404:
            print("   This indicates the WebSocket endpoint is not found")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def main():
    print("🚀 Testing WebSocket with real learner session...")
    
    success = await test_real_websocket()
    
    if success:
        print("\n✅ WebSocket test with real session successful!")
        print("🎉 Live API is ready for frontend testing!")
    else:
        print("\n❌ WebSocket test failed")
        print("📋 Make sure the FastAPI server is running")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)