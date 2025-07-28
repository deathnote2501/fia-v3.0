#!/usr/bin/env python3
"""
Throttling Fix Validation Test
Tests that the throttling fix works correctly
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


class ThrottlingFixTester:
    """Test throttling fix validation"""
    
    def __init__(self, base_url: str = "ws://localhost:8000"):
        self.base_url = base_url
        self.engine = create_async_engine(settings.database_url)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def create_test_data(self) -> Dict[str, Any]:
        """Create test data in database"""
        logger.info("🗄️ Creating test data...")
        
        async with self.async_session() as session:
            try:
                trainer = TrainerModel(
                    email=f"test_trainer_{uuid.uuid4().hex[:8]}@test.com",
                    hashed_password="fake_hash",
                    first_name="Test",
                    last_name="Trainer",
                    is_verified=True
                )
                session.add(trainer)
                await session.flush()
                
                training = TrainingModel(
                    name="Test Training",
                    description="Test Description",
                    file_type="pdf",
                    file_path="/tmp/test.pdf",
                    trainer_id=trainer.id
                )
                session.add(training)
                await session.flush()
                
                training_session = TrainingSessionModel(
                    name="Test Session",
                    training_id=training.id,
                    session_token=f"test_token_{uuid.uuid4().hex[:8]}"
                )
                session.add(training_session)
                await session.flush()
                
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
                
                return {"learner_session_id": learner_session.id}
                
            except Exception as e:
                await session.rollback()
                raise
    
    async def cleanup_test_data(self, test_data: Dict[str, Any]):
        """Clean up test data"""
        async with self.async_session() as session:
            try:
                if "learner_session_id" in test_data:
                    learner = await session.get(LearnerSessionModel, test_data["learner_session_id"])
                    if learner:
                        training_session = await session.get(TrainingSessionModel, learner.training_session_id)
                        if training_session:
                            training = await session.get(TrainingModel, training_session.training_id)
                            if training:
                                trainer = await session.get(TrainerModel, training.trainer_id)
                                
                                await session.delete(learner)
                                await session.delete(training_session)
                                await session.delete(training)
                                if trainer:
                                    await session.delete(trainer)
                
                await session.commit()
                logger.info("✅ Test data cleaned up")
                
            except Exception as e:
                await session.rollback()
                logger.error(f"❌ Error cleaning up: {e}")
    
    async def test_aggressive_throttling(self, learner_session_id: str) -> bool:
        """Test very aggressive audio sending to trigger throttling"""
        logger.info("🔥 Testing aggressive throttling (10 chunks immediately)...")
        
        try:
            uri = f"{self.base_url}/ws/live/{learner_session_id}"
            
            async with websockets.connect(uri) as websocket:
                # Skip initial message
                await asyncio.wait_for(websocket.recv(), timeout=5.0)
                
                # Send 10 audio chunks as fast as possible
                chunk_count = 10
                for i in range(chunk_count):
                    fake_audio = f"AGGRESSIVE_CHUNK_{i}".encode() + b"_DATA" * 100
                    audio_b64 = base64.b64encode(fake_audio).decode('utf-8')
                    
                    audio_message = {
                        "type": "audio",
                        "data": audio_b64,
                        "mime_type": "audio/webm"
                    }
                    
                    await websocket.send(json.dumps(audio_message))
                    logger.info(f"📤 Aggressive chunk {i+1}/{chunk_count}")
                
                # Collect all responses
                responses_received = 0
                throttled_responses = 0
                processed_responses = 0
                error_responses = 0
                
                for i in range(chunk_count):
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        parsed_response = json.loads(response)
                        responses_received += 1
                        
                        if parsed_response.get('type') == 'audio_response':
                            metadata = parsed_response.get('metadata', {})
                            processing_metadata = metadata.get('processing_metadata', {})
                            
                            if processing_metadata.get('throttled'):
                                throttled_responses += 1
                                logger.info(f"⏸️ Response {i+1} throttled")
                            else:
                                processed_responses += 1
                                logger.info(f"✅ Response {i+1} processed")
                        elif parsed_response.get('type') == 'error':
                            error_responses += 1
                            logger.info(f"❌ Response {i+1} error: {parsed_response.get('message')}")
                        
                    except asyncio.TimeoutError:
                        logger.warning(f"⏰ Response {i+1} timeout")
                        break
                
                logger.info(f"📊 Aggressive test results:")
                logger.info(f"  Total responses: {responses_received}/{chunk_count}")
                logger.info(f"  Processed: {processed_responses}")
                logger.info(f"  Throttled: {throttled_responses}")
                logger.info(f"  Errors: {error_responses}")
                
                # Success criteria:
                # 1. All chunks get responses (no "No response generated" errors)
                # 2. At least some responses are throttled (shows throttling works)
                # 3. No error responses
                success = (
                    responses_received == chunk_count and  # All responses received
                    error_responses == 0 and  # No errors
                    throttled_responses > 0  # Some throttling occurred
                )
                
                if success:
                    logger.info("✅ Aggressive throttling test PASSED")
                else:
                    logger.error("❌ Aggressive throttling test FAILED")
                
                return success
                
        except Exception as e:
            logger.error(f"❌ Aggressive throttling test failed: {e}")
            return False
    
    async def test_throttling_recovery(self, learner_session_id: str) -> bool:
        """Test that throttling recovers after cooldown period"""
        logger.info("🔄 Testing throttling recovery...")
        
        try:
            uri = f"{self.base_url}/ws/live/{learner_session_id}"
            
            async with websockets.connect(uri) as websocket:
                # Skip initial message
                await asyncio.wait_for(websocket.recv(), timeout=5.0)
                
                # Send first chunk
                fake_audio = b"RECOVERY_TEST_CHUNK_1" + b"_DATA" * 50
                audio_b64 = base64.b64encode(fake_audio).decode('utf-8')
                
                audio_message = {
                    "type": "audio",
                    "data": audio_b64,
                    "mime_type": "audio/webm"
                }
                
                await websocket.send(json.dumps(audio_message))
                logger.info("📤 Sent first chunk")
                
                # Get response
                response1 = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                parsed_response1 = json.loads(response1)
                
                # Send immediate second chunk (should be throttled)
                fake_audio2 = b"RECOVERY_TEST_CHUNK_2" + b"_DATA" * 50
                audio_b64_2 = base64.b64encode(fake_audio2).decode('utf-8')
                
                audio_message2 = {
                    "type": "audio",
                    "data": audio_b64_2,
                    "mime_type": "audio/webm"
                }
                
                await websocket.send(json.dumps(audio_message2))
                logger.info("📤 Sent immediate second chunk")
                
                # Get response (should be throttled)
                response2 = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                parsed_response2 = json.loads(response2)
                
                # Wait for cooldown period (2 seconds + buffer)
                logger.info("⏰ Waiting for throttling cooldown (3 seconds)...")
                await asyncio.sleep(3)
                
                # Send third chunk (should work normally)
                fake_audio3 = b"RECOVERY_TEST_CHUNK_3" + b"_DATA" * 50
                audio_b64_3 = base64.b64encode(fake_audio3).decode('utf-8')
                
                audio_message3 = {
                    "type": "audio",
                    "data": audio_b64_3,
                    "mime_type": "audio/webm"
                }
                
                await websocket.send(json.dumps(audio_message3))
                logger.info("📤 Sent third chunk after cooldown")
                
                # Get response (should be processed normally)
                response3 = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                parsed_response3 = json.loads(response3)
                
                # Analyze responses
                r1_throttled = parsed_response1.get('metadata', {}).get('processing_metadata', {}).get('throttled', False)
                r2_throttled = parsed_response2.get('metadata', {}).get('processing_metadata', {}).get('throttled', False)
                r3_throttled = parsed_response3.get('metadata', {}).get('processing_metadata', {}).get('throttled', False)
                
                logger.info(f"Response 1 throttled: {r1_throttled}")
                logger.info(f"Response 2 throttled: {r2_throttled}")
                logger.info(f"Response 3 throttled: {r3_throttled}")
                
                # Success criteria:
                # 1. First response not throttled
                # 2. Second response throttled
                # 3. Third response not throttled (recovered)
                success = (
                    not r1_throttled and  # First normal
                    r2_throttled and     # Second throttled
                    not r3_throttled     # Third recovered
                )
                
                if success:
                    logger.info("✅ Throttling recovery test PASSED")
                else:
                    logger.error("❌ Throttling recovery test FAILED")
                
                return success
                
        except Exception as e:
            logger.error(f"❌ Throttling recovery test failed: {e}")
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all throttling fix tests"""
        logger.info("🚀 Starting Throttling Fix Validation Tests")
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
            # Test 1: Aggressive throttling
            results['aggressive_throttling'] = await self.test_aggressive_throttling(learner_session_id)
            
            # Test 2: Throttling recovery
            results['throttling_recovery'] = await self.test_throttling_recovery(learner_session_id)
            
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
            logger.info("🎉 All throttling fix tests passed!")
        else:
            logger.error("⚠️ Some throttling fix tests failed")
        
        return results


async def main():
    """Main test function"""
    tester = ThrottlingFixTester()
    results = await tester.run_all_tests()
    
    # Exit with appropriate code
    all_passed = all(results.values())
    exit(0 if all_passed else 1)


if __name__ == "__main__":
    asyncio.run(main())