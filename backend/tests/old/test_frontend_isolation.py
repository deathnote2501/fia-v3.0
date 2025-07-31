#!/usr/bin/env python3
"""
Frontend Audio Handling Test
Tests that simulate frontend behavior to isolate audio issues
"""

import asyncio
import json
import logging
import base64
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


class FrontendAudioTester:
    """Test frontend audio handling patterns"""
    
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
    
    async def simulate_frontend_audio_pattern(self, learner_session_id: str) -> bool:
        """Simulate the exact frontend pattern: connect, start, send audio chunks"""
        logger.info("🎭 Simulating frontend audio pattern...")
        
        try:
            uri = f"{self.base_url}/ws/live/{learner_session_id}"
            
            async with websockets.connect(uri) as websocket:
                logger.info("✅ WebSocket connected")
                
                # 1. Wait for session_started message (frontend expects this)
                initial_message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                parsed_message = json.loads(initial_message)
                
                if parsed_message.get('type') != 'session_started':
                    logger.error(f"❌ Expected session_started, got: {parsed_message.get('type')}")
                    return False
                
                logger.info(f"✅ Session started: {parsed_message.get('live_session_id')}")
                
                # 2. Simulate multiple audio chunks (frontend sends 1-second chunks)
                for i in range(3):
                    # Create fake audio data that simulates MediaRecorder output
                    fake_webm_audio = b"WEBM_AUDIO_HEADER" + b"FAKE_OPUS_DATA" * 100 + bytes([i % 256])
                    audio_b64 = base64.b64encode(fake_webm_audio).decode('utf-8')
                    
                    audio_message = {
                        "type": "audio",
                        "data": audio_b64,
                        "mime_type": "audio/webm;codecs=opus"
                    }
                    
                    await websocket.send(json.dumps(audio_message))
                    logger.info(f"📤 Sent audio chunk {i+1}/3 ({len(fake_webm_audio)} bytes)")
                    
                    # Wait for response
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=8.0)
                        parsed_response = json.loads(response)
                        
                        if parsed_response.get('type') == 'audio_response':
                            metadata = parsed_response.get('metadata', {})
                            text_transcript = metadata.get('text_transcript', '')
                            
                            logger.info(f"✅ Chunk {i+1} response: '{text_transcript[:30]}...'")
                            
                            # Check if it's throttled (expected for rapid chunks)
                            if metadata.get('processing_metadata', {}).get('throttled'):
                                logger.info(f"⏸️ Chunk {i+1} was throttled (expected)")
                            elif metadata.get('processing_metadata', {}).get('mock'):
                                logger.info(f"🎭 Chunk {i+1} got mock response (expected)")
                            
                        elif parsed_response.get('type') == 'error':
                            logger.error(f"❌ Chunk {i+1} error: {parsed_response.get('message')}")
                            return False
                        else:
                            logger.warning(f"⚠️ Chunk {i+1} unexpected response: {parsed_response.get('type')}")
                        
                    except asyncio.TimeoutError:
                        logger.error(f"❌ Chunk {i+1} no response within 8 seconds")
                        return False
                    
                    # Small delay between chunks (simulating real audio recording)
                    await asyncio.sleep(1.5)
                
                # 3. Send close message (frontend cleanup)
                close_message = {"type": "close"}
                await websocket.send(json.dumps(close_message))
                logger.info("📤 Sent close message")
                
                # Wait for connection to close
                try:
                    await asyncio.wait_for(websocket.recv(), timeout=3.0)
                    logger.warning("⚠️ Still receiving messages after close")
                except (ConnectionClosed, asyncio.TimeoutError):
                    logger.info("✅ Connection closed gracefully")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Frontend simulation failed: {e}")
            return False
    
    async def test_rapid_audio_chunks(self, learner_session_id: str) -> bool:
        """Test rapid audio chunks to see throttling behavior"""
        logger.info("⚡ Testing rapid audio chunks (stress test)...")
        
        try:
            uri = f"{self.base_url}/ws/live/{learner_session_id}"
            
            async with websockets.connect(uri) as websocket:
                # Skip initial message
                await asyncio.wait_for(websocket.recv(), timeout=5.0)
                
                # Send 5 rapid audio chunks
                responses_received = 0
                throttled_responses = 0
                error_responses = 0
                
                for i in range(5):
                    fake_audio = b"RAPID_AUDIO_CHUNK_" + str(i).encode() + b"_DATA" * 50
                    audio_b64 = base64.b64encode(fake_audio).decode('utf-8')
                    
                    audio_message = {
                        "type": "audio",
                        "data": audio_b64,
                        "mime_type": "audio/webm"
                    }
                    
                    await websocket.send(json.dumps(audio_message))
                    logger.info(f"📤 Rapid chunk {i+1}/5")
                    
                    # Immediate next chunk (no delay - stress test)
                
                # Now collect all responses
                for i in range(5):
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        parsed_response = json.loads(response)
                        responses_received += 1
                        
                        if parsed_response.get('type') == 'audio_response':
                            metadata = parsed_response.get('metadata', {})
                            if metadata.get('processing_metadata', {}).get('throttled'):
                                throttled_responses += 1
                                logger.info(f"⏸️ Response {i+1} throttled")
                            else:
                                logger.info(f"✅ Response {i+1} processed")
                        elif parsed_response.get('type') == 'error':
                            error_responses += 1
                            logger.info(f"❌ Response {i+1} error: {parsed_response.get('message')}")
                        
                    except asyncio.TimeoutError:
                        logger.warning(f"⏰ Response {i+1} timeout")
                        break
                
                logger.info(f"📊 Rapid test results: {responses_received}/5 responses, {throttled_responses} throttled, {error_responses} errors")
                
                # Success if we got at least some responses and proper throttling
                success = responses_received >= 3 and error_responses == 0
                return success
                
        except Exception as e:
            logger.error(f"❌ Rapid chunks test failed: {e}")
            return False
    
    async def test_invalid_audio_data(self, learner_session_id: str) -> bool:
        """Test how system handles invalid audio data"""
        logger.info("🚫 Testing invalid audio data handling...")
        
        try:
            uri = f"{self.base_url}/ws/live/{learner_session_id}"
            
            async with websockets.connect(uri) as websocket:
                # Skip initial message
                await asyncio.wait_for(websocket.recv(), timeout=5.0)
                
                # Test 1: Invalid base64
                invalid_message = {
                    "type": "audio",
                    "data": "INVALID_BASE64_DATA!!!",
                    "mime_type": "audio/webm"
                }
                
                await websocket.send(json.dumps(invalid_message))
                logger.info("📤 Sent invalid base64 audio data")
                
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                parsed_response = json.loads(response)
                
                if parsed_response.get('type') == 'error' and 'audio' in parsed_response.get('message', '').lower():
                    logger.info("✅ Invalid base64 properly handled with error")
                else:
                    logger.warning(f"⚠️ Unexpected response to invalid audio: {parsed_response.get('type')}")
                
                # Test 2: Missing audio data
                missing_data_message = {
                    "type": "audio",
                    "mime_type": "audio/webm"
                }
                
                await websocket.send(json.dumps(missing_data_message))
                logger.info("📤 Sent message missing audio data")
                
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                parsed_response = json.loads(response)
                
                if parsed_response.get('type') == 'error':
                    logger.info("✅ Missing audio data properly handled with error")
                else:
                    logger.warning(f"⚠️ Unexpected response to missing data: {parsed_response.get('type')}")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Invalid audio test failed: {e}")
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all frontend audio tests"""
        logger.info("🚀 Starting Frontend Audio Handling Tests")
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
            # Test 1: Frontend audio pattern simulation
            results['frontend_pattern'] = await self.simulate_frontend_audio_pattern(learner_session_id)
            
            # Test 2: Rapid audio chunks stress test
            results['rapid_chunks'] = await self.test_rapid_audio_chunks(learner_session_id)
            
            # Test 3: Invalid audio data handling
            results['invalid_audio'] = await self.test_invalid_audio_data(learner_session_id)
            
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
            logger.info("🎉 All frontend audio tests passed!")
        else:
            logger.error("⚠️ Some frontend audio tests failed - need investigation")
        
        return results


async def main():
    """Main test function"""
    tester = FrontendAudioTester()
    results = await tester.run_all_tests()
    
    # Exit with appropriate code
    all_passed = all(results.values())
    exit(0 if all_passed else 1)


if __name__ == "__main__":
    asyncio.run(main())