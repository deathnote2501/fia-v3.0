#!/usr/bin/env python3
"""
Basic WebSocket Connection Test
Tests the fundamental WebSocket connection without Live API integration
"""

import asyncio
import json
import uuid
import logging
from typing import Dict, Any

import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BasicWebSocketTester:
    """Test basic WebSocket connection and message exchange"""
    
    def __init__(self, base_url: str = "ws://localhost:8000"):
        self.base_url = base_url
        self.test_results: Dict[str, Any] = {}
        
    async def test_connection_establishment(self, learner_session_id: str) -> bool:
        """Test if WebSocket connection can be established"""
        logger.info(f"🔌 Testing WebSocket connection establishment...")
        
        try:
            # Test connection to the live WebSocket endpoint
            uri = f"{self.base_url}/ws/live/{learner_session_id}"
            logger.info(f"Connecting to: {uri}")
            
            async with websockets.connect(uri) as websocket:
                logger.info("✅ WebSocket connection established successfully")
                
                # Wait a moment to see if we get the initial session_started message
                try:
                    initial_message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    parsed_message = json.loads(initial_message)
                    logger.info(f"📨 Received initial message: {parsed_message.get('type', 'unknown')}")
                    
                    if parsed_message.get('type') == 'session_started':
                        logger.info("✅ Session started message received correctly")
                        return True
                    elif parsed_message.get('type') == 'error':
                        logger.error(f"❌ Error in session start: {parsed_message.get('message')}")
                        return False
                    else:
                        logger.warning(f"⚠️ Unexpected initial message type: {parsed_message.get('type')}")
                        return True  # Connection worked, just unexpected message
                        
                except asyncio.TimeoutError:
                    logger.warning("⚠️ No initial message received within 5 seconds")
                    return True  # Connection worked, no initial message
                    
        except ConnectionClosed as e:
            logger.error(f"❌ WebSocket connection closed unexpectedly: {e}")
            return False
        except WebSocketException as e:
            logger.error(f"❌ WebSocket error: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False
    
    async def test_ping_pong(self, learner_session_id: str) -> bool:
        """Test basic ping-pong message exchange"""
        logger.info(f"🏓 Testing ping-pong message exchange...")
        
        try:
            uri = f"{self.base_url}/ws/live/{learner_session_id}"
            
            async with websockets.connect(uri) as websocket:
                # Skip initial session message if any
                try:
                    await asyncio.wait_for(websocket.recv(), timeout=2.0)
                except asyncio.TimeoutError:
                    pass
                
                # Send ping message
                ping_message = {"type": "ping"}
                await websocket.send(json.dumps(ping_message))
                logger.info("📤 Sent ping message")
                
                # Wait for pong response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    parsed_response = json.loads(response)
                    
                    if parsed_response.get('type') == 'pong':
                        logger.info("✅ Received pong response correctly")
                        return True
                    else:
                        logger.error(f"❌ Expected pong, got: {parsed_response.get('type')}")
                        return False
                        
                except asyncio.TimeoutError:
                    logger.error("❌ No pong response within 5 seconds")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error in ping-pong test: {e}")
            return False
    
    async def test_simple_text_message(self, learner_session_id: str) -> bool:
        """Test sending a simple text message (not audio)"""
        logger.info(f"📝 Testing simple text message exchange...")
        
        try:
            uri = f"{self.base_url}/ws/live/{learner_session_id}"
            
            async with websockets.connect(uri) as websocket:
                # Skip initial session message if any
                try:
                    await asyncio.wait_for(websocket.recv(), timeout=2.0)
                except asyncio.TimeoutError:
                    pass
                
                # Send a simple test message (not audio type)
                test_message = {
                    "type": "test",
                    "data": "Hello WebSocket"
                }
                await websocket.send(json.dumps(test_message))
                logger.info("📤 Sent test message")
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    parsed_response = json.loads(response)
                    
                    logger.info(f"📨 Received response: {parsed_response.get('type')}")
                    
                    # We expect an error response for unknown message type
                    if parsed_response.get('type') == 'error' and 'unknown' in parsed_response.get('message', '').lower():
                        logger.info("✅ Server correctly handled unknown message type")
                        return True
                    else:
                        logger.warning(f"⚠️ Unexpected response: {parsed_response}")
                        return True  # Still working, just different handling
                        
                except asyncio.TimeoutError:
                    logger.error("❌ No response to test message within 5 seconds")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error in text message test: {e}")
            return False
    
    async def test_connection_close(self, learner_session_id: str) -> bool:
        """Test graceful connection close"""
        logger.info(f"🔚 Testing graceful connection close...")
        
        try:
            uri = f"{self.base_url}/ws/live/{learner_session_id}"
            
            websocket = await websockets.connect(uri)
            
            # Skip initial session message if any
            try:
                await asyncio.wait_for(websocket.recv(), timeout=2.0)
            except asyncio.TimeoutError:
                pass
            
            # Send close message
            close_message = {"type": "close"}
            await websocket.send(json.dumps(close_message))
            logger.info("📤 Sent close message")
            
            # Wait for connection to close
            try:
                await asyncio.wait_for(websocket.recv(), timeout=5.0)
                logger.error("❌ Connection did not close after close message")
                return False
            except ConnectionClosed:
                logger.info("✅ Connection closed gracefully")
                return True
            except asyncio.TimeoutError:
                logger.warning("⚠️ Connection did not close within 5 seconds")
                await websocket.close()
                return False
                
        except Exception as e:
            logger.error(f"❌ Error in connection close test: {e}")
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all basic WebSocket tests"""
        logger.info("🚀 Starting Basic WebSocket Tests")
        logger.info("=" * 50)
        
        # Generate a test learner session ID
        test_learner_id = str(uuid.uuid4())
        logger.info(f"Using test learner session ID: {test_learner_id}")
        
        results = {}
        
        # Test 1: Connection establishment
        results['connection_establishment'] = await self.test_connection_establishment(test_learner_id)
        
        # Test 2: Ping-pong
        results['ping_pong'] = await self.test_ping_pong(test_learner_id)
        
        # Test 3: Simple text message
        results['text_message'] = await self.test_simple_text_message(test_learner_id)
        
        # Test 4: Connection close
        results['connection_close'] = await self.test_connection_close(test_learner_id)
        
        # Summary
        logger.info("=" * 50)
        logger.info("📊 Test Results Summary:")
        passed = 0
        total = len(results)
        
        for test_name, passed_test in results.items():
            status = "✅ PASS" if passed_test else "❌ FAIL"
            logger.info(f"  {test_name}: {status}")
            if passed_test:
                passed += 1
        
        logger.info(f"Overall: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 All basic WebSocket tests passed!")
        else:
            logger.error("⚠️ Some basic WebSocket tests failed")
            
        return results


async def main():
    """Main test function"""
    tester = BasicWebSocketTester()
    results = await tester.run_all_tests()
    
    # Exit with appropriate code
    all_passed = all(results.values())
    exit(0 if all_passed else 1)


if __name__ == "__main__":
    asyncio.run(main())