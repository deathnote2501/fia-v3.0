#!/usr/bin/env python3
"""
WebSocket Test with Database Integration
Tests WebSocket with actual database entries
"""

import asyncio
import json
import logging
from typing import Dict, Any
import uuid

import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.infrastructure.settings import settings
from app.infrastructure.models.trainer_model import TrainerModel
from app.infrastructure.models.training_model import TrainingModel
from app.infrastructure.models.training_session_model import TrainingSessionModel
from app.infrastructure.models.learner_session_model import LearnerSessionModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebSocketDBTester:
    """Test WebSocket with database integration"""
    
    def __init__(self, base_url: str = "ws://localhost:8000"):
        self.base_url = base_url
        self.test_results: Dict[str, Any] = {}
        
        # Create async engine for database operations
        self.engine = create_async_engine(settings.database_url)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def create_test_data(self) -> Dict[str, Any]:
        """Create test data in database"""
        logger.info("🗄️ Creating test data in database...")
        
        async with self.async_session() as session:
            try:
                # Create trainer
                trainer = TrainerModel(
                    email=f"test_trainer_{uuid.uuid4().hex[:8]}@test.com",
                    hashed_password="fake_hash",
                    first_name="Test",
                    last_name="Trainer",
                    is_verified=True
                )
                session.add(trainer)
                await session.flush()
                
                # Create training
                training = TrainingModel(
                    name="Test Training",
                    description="Test Description",
                    file_type="pdf",
                    file_path="/tmp/test.pdf",
                    trainer_id=trainer.id
                )
                session.add(training)
                await session.flush()
                
                # Create training session
                training_session = TrainingSessionModel(
                    name="Test Session",
                    training_id=training.id,
                    session_token=f"test_token_{uuid.uuid4().hex[:8]}"
                )
                session.add(training_session)
                await session.flush()
                
                # Create learner session
                learner_session = LearnerSessionModel(
                    email="test_learner@test.com",
                    training_session_id=training_session.id,
                    experience_level="beginner",
                    learning_style="visual",
                    job_position="developer",
                    activity_sector="tech",
                    country="France",
                    language="fr",
                    current_slide_number=1,
                    total_time_spent=0,
                    enriched_profile={"test": "data"}
                )
                session.add(learner_session)
                await session.flush()
                
                await session.commit()
                
                test_data = {
                    "trainer_id": trainer.id,
                    "training_id": training.id, 
                    "training_session_id": training_session.id,
                    "learner_session_id": learner_session.id
                }
                
                logger.info(f"✅ Test data created: learner_session_id = {learner_session.id}")
                return test_data
                
            except Exception as e:
                await session.rollback()
                logger.error(f"❌ Error creating test data: {e}")
                raise
    
    async def cleanup_test_data(self, test_data: Dict[str, Any]):
        """Clean up test data"""
        logger.info("🧹 Cleaning up test data...")
        
        async with self.async_session() as session:
            try:
                # Delete in reverse order of dependencies
                if "learner_session_id" in test_data:
                    learner = await session.get(LearnerSessionModel, test_data["learner_session_id"])
                    if learner:
                        await session.delete(learner)
                
                if "training_session_id" in test_data:
                    training_session = await session.get(TrainingSessionModel, test_data["training_session_id"])
                    if training_session:
                        await session.delete(training_session)
                
                if "training_id" in test_data:
                    training = await session.get(TrainingModel, test_data["training_id"])
                    if training:
                        await session.delete(training)
                
                if "trainer_id" in test_data:
                    trainer = await session.get(TrainerModel, test_data["trainer_id"])
                    if trainer:
                        await session.delete(trainer)
                
                await session.commit()
                logger.info("✅ Test data cleaned up")
                
            except Exception as e:
                await session.rollback()
                logger.error(f"❌ Error cleaning up: {e}")
    
    async def test_websocket_with_valid_session(self, learner_session_id: str) -> bool:
        """Test WebSocket with valid learner session"""
        logger.info(f"🔌 Testing WebSocket with valid session: {learner_session_id}")
        
        try:
            uri = f"{self.base_url}/ws/live/{learner_session_id}"
            logger.info(f"Connecting to: {uri}")
            
            async with websockets.connect(uri) as websocket:
                logger.info("✅ WebSocket connection established")
                
                # Wait for initial session_started message
                try:
                    initial_message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    parsed_message = json.loads(initial_message)
                    logger.info(f"📨 Received initial message: {parsed_message.get('type')}")
                    
                    if parsed_message.get('type') == 'session_started':
                        logger.info("✅ Session started message received correctly")
                        logger.info(f"Live session ID: {parsed_message.get('live_session_id')}")
                        return True
                    elif parsed_message.get('type') == 'error':
                        logger.error(f"❌ Error starting session: {parsed_message.get('message')}")
                        return False
                    else:
                        logger.warning(f"⚠️ Unexpected message type: {parsed_message.get('type')}")
                        return False
                        
                except asyncio.TimeoutError:
                    logger.error("❌ No initial message received within 10 seconds")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ WebSocket test failed: {e}")
            return False
    
    async def test_ping_pong_with_valid_session(self, learner_session_id: str) -> bool:
        """Test ping-pong with valid session"""
        logger.info(f"🏓 Testing ping-pong with valid session")
        
        try:
            uri = f"{self.base_url}/ws/live/{learner_session_id}"
            
            async with websockets.connect(uri) as websocket:
                # Skip initial message
                try:
                    await asyncio.wait_for(websocket.recv(), timeout=5.0)
                except asyncio.TimeoutError:
                    pass
                
                # Send ping
                ping_message = {"type": "ping"}
                await websocket.send(json.dumps(ping_message))
                logger.info("📤 Sent ping message")
                
                # Wait for pong
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
            logger.error(f"❌ Ping-pong test failed: {e}")
            return False
    
    async def test_audio_message_with_valid_session(self, learner_session_id: str) -> bool:
        """Test audio message processing with valid session"""
        logger.info(f"🎙️ Testing audio message with valid session")
        
        try:
            uri = f"{self.base_url}/ws/live/{learner_session_id}"
            
            async with websockets.connect(uri) as websocket:
                # Skip initial message
                try:
                    await asyncio.wait_for(websocket.recv(), timeout=5.0)
                except asyncio.TimeoutError:
                    pass
                
                # Send fake audio message
                import base64
                fake_audio = b"FAKE_AUDIO_DATA_FOR_TESTING"
                audio_b64 = base64.b64encode(fake_audio).decode('utf-8')
                
                audio_message = {
                    "type": "audio",
                    "data": audio_b64,
                    "mime_type": "audio/webm"
                }
                await websocket.send(json.dumps(audio_message))
                logger.info("📤 Sent audio message")
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    parsed_response = json.loads(response)
                    
                    if parsed_response.get('type') == 'audio_response':
                        logger.info("✅ Received audio response")
                        metadata = parsed_response.get('metadata', {})
                        text_transcript = metadata.get('text_transcript', '')
                        logger.info(f"Text transcript: {text_transcript[:50]}...")
                        return True
                    elif parsed_response.get('type') == 'error':
                        logger.error(f"❌ Error processing audio: {parsed_response.get('message')}")
                        return False
                    else:
                        logger.warning(f"⚠️ Unexpected response type: {parsed_response.get('type')}")
                        return False
                        
                except asyncio.TimeoutError:
                    logger.error("❌ No audio response within 10 seconds")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Audio message test failed: {e}")
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all WebSocket tests with database"""
        logger.info("🚀 Starting WebSocket Tests with Database")
        logger.info("=" * 50)
        
        # Create test data
        try:
            test_data = await self.create_test_data()
            learner_session_id = str(test_data["learner_session_id"])
        except Exception as e:
            logger.error(f"❌ Failed to create test data: {e}")
            return {"setup_failed": False}
        
        results = {}
        
        try:
            # Test 1: WebSocket connection with valid session
            results['websocket_connection'] = await self.test_websocket_with_valid_session(learner_session_id)
            
            # Test 2: Ping-pong with valid session
            results['ping_pong'] = await self.test_ping_pong_with_valid_session(learner_session_id)
            
            # Test 3: Audio message processing
            results['audio_processing'] = await self.test_audio_message_with_valid_session(learner_session_id)
            
        finally:
            # Clean up test data
            await self.cleanup_test_data(test_data)
        
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
            logger.info("🎉 All WebSocket database tests passed!")
        else:
            logger.error("⚠️ Some WebSocket database tests failed")
        
        return results


async def main():
    """Main test function"""
    tester = WebSocketDBTester()
    results = await tester.run_all_tests()
    
    # Exit with appropriate code
    all_passed = all(results.values())
    exit(0 if all_passed else 1)


if __name__ == "__main__":
    asyncio.run(main())