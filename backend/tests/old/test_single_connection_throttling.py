#!/usr/bin/env python3
"""
Single Connection Throttling Test
Tests throttling on a single WebSocket connection (same session)
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


class SingleConnectionThrottlingTester:
    """Test throttling on single WebSocket connection"""
    
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
    
    async def test_same_connection_throttling(self, learner_session_id: str) -> bool:
        """Test throttling on the same WebSocket connection and Live session"""
        logger.info("🔥 Testing same connection throttling...")
        
        try:
            uri = f"{self.base_url}/ws/live/{learner_session_id}"
            
            async with websockets.connect(uri) as websocket:
                # Skip initial message and get session info
                initial_message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                parsed_initial = json.loads(initial_message)
                
                if parsed_initial.get('type') != 'session_started':
                    logger.error(f"❌ Expected session_started, got: {parsed_initial.get('type')}")
                    return False
                
                live_session_id = parsed_initial.get('live_session_id')
                logger.info(f"✅ Live session started: {live_session_id}")
                
                # Send first audio chunk
                fake_audio1 = b"THROTTLE_TEST_CHUNK_1" + b"_DATA" * 50
                audio_b64_1 = base64.b64encode(fake_audio1).decode('utf-8')
                
                audio_message1 = {
                    "type": "audio",
                    "data": audio_b64_1,
                    "mime_type": "audio/webm"
                }
                
                await websocket.send(json.dumps(audio_message1))
                logger.info("📤 Sent first audio chunk")
                
                # Get first response
                response1 = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                parsed_response1 = json.loads(response1)
                
                # IMMEDIATELY send second audio chunk (should be throttled)
                fake_audio2 = b"THROTTLE_TEST_CHUNK_2" + b"_DATA" * 50
                audio_b64_2 = base64.b64encode(fake_audio2).decode('utf-8')
                
                audio_message2 = {
                    "type": "audio",
                    "data": audio_b64_2,
                    "mime_type": "audio/webm"
                }
                
                await websocket.send(json.dumps(audio_message2))
                logger.info("📤 Sent IMMEDIATE second audio chunk")
                
                # Get second response (should be throttled)
                response2 = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                parsed_response2 = json.loads(response2)
                
                # IMMEDIATELY send third audio chunk (should also be throttled)
                fake_audio3 = b"THROTTLE_TEST_CHUNK_3" + b"_DATA" * 50
                audio_b64_3 = base64.b64encode(fake_audio3).decode('utf-8')
                
                audio_message3 = {
                    "type": "audio",
                    "data": audio_b64_3,
                    "mime_type": "audio/webm"
                }
                
                await websocket.send(json.dumps(audio_message3))
                logger.info("📤 Sent IMMEDIATE third audio chunk")
                
                # Get third response (should be throttled)
                response3 = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                parsed_response3 = json.loads(response3)
                
                # Analyze responses
                def is_throttled(response):
                    if response.get('type') == 'audio_response':
                        metadata = response.get('metadata', {})
                        processing_metadata = metadata.get('processing_metadata', {})
                        return processing_metadata.get('throttled', False)
                    return False
                
                r1_throttled = is_throttled(parsed_response1)
                r2_throttled = is_throttled(parsed_response2)
                r3_throttled = is_throttled(parsed_response3)
                
                logger.info(f"Response 1 throttled: {r1_throttled}")
                logger.info(f"Response 2 throttled: {r2_throttled}")
                logger.info(f"Response 3 throttled: {r3_throttled}")
                
                # Success criteria: At least some responses should be throttled
                throttled_count = sum([r1_throttled, r2_throttled, r3_throttled])
                logger.info(f"Throttled responses: {throttled_count}/3")
                
                # We expect at least the 2nd and 3rd to be throttled
                success = throttled_count >= 2
                
                if success:
                    logger.info("✅ Same connection throttling test PASSED")
                else:
                    logger.error("❌ Same connection throttling test FAILED - no throttling detected")
                
                return success
                
        except Exception as e:
            logger.error(f"❌ Same connection throttling test failed: {e}")
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all single connection throttling tests"""
        logger.info("🚀 Starting Single Connection Throttling Tests")
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
            # Test: Same connection throttling
            results['same_connection_throttling'] = await self.test_same_connection_throttling(learner_session_id)
            
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
            logger.info("🎉 All single connection throttling tests passed!")
        else:
            logger.error("⚠️ Some single connection throttling tests failed")
        
        return results


async def main():
    """Main test function"""
    tester = SingleConnectionThrottlingTester()
    results = await tester.run_all_tests()
    
    # Exit with appropriate code
    all_passed = all(results.values())
    exit(0 if all_passed else 1)


if __name__ == "__main__":
    asyncio.run(main())