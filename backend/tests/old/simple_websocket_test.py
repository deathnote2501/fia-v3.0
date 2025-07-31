#!/usr/bin/env python3
"""
Simple WebSocket connection test
"""

import asyncio
import websockets
import json

async def test_websocket():
    """Test basic WebSocket connection"""
    
    real_learner_session_id = '177fadf3-4744-40e0-811f-71f2621ccfee'
    websocket_url = f"ws://localhost:8000/ws/live/{real_learner_session_id}"
    
    print(f"🔗 Testing WebSocket connection to: {websocket_url}")
    
    try:
        # Simple connection test
        websocket = await websockets.connect(websocket_url)
        print("✅ WebSocket connection established!")
        
        # Wait for initial message with timeout
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"📥 Initial message: {response}")
            
            # Parse and display
            message = json.loads(response)
            print(f"📋 Message type: {message.get('type')}")
            print(f"🆔 Live session ID: {message.get('live_session_id')}")
            
            # Send ping
            ping_msg = json.dumps({"type": "ping"})
            await websocket.send(ping_msg)
            print("📤 Sent ping")
            
            # Wait for pong
            pong_response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
            pong_message = json.loads(pong_response)
            print(f"📥 Pong response: {pong_message.get('type')}")
            
            # Close gracefully
            close_msg = json.dumps({"type": "close"})
            await websocket.send(close_msg)
            print("📤 Sent close")
            
            await websocket.close()
            print("✅ WebSocket closed successfully")
            
            return True
            
        except asyncio.TimeoutError:
            print("⚠️ Timeout waiting for response")
            await websocket.close()
            return False
            
    except ConnectionRefusedError:
        print("❌ Connection refused - server not running?")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_websocket())
    print(f"🏁 Test result: {'✅ SUCCESS' if result else '❌ FAILED'}")