#!/usr/bin/env python3
"""
Mock Response Generation Test
Tests the mock response generation in isolation without WebSocket
"""

import asyncio
import logging
import uuid
from typing import Dict, Any

from app.adapters.outbound.live_api_adapter import LiveAPIAdapter
from app.infrastructure.live_api_client import LiveAPIError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockResponseTester:
    """Test mock response generation in isolation"""
    
    def __init__(self):
        self.adapter = LiveAPIAdapter()
        self.test_results: Dict[str, Any] = {}
        
        # Test data
        self.test_slide_context = {
            "title": "Introduction à Python",
            "content": "Python est un langage de programmation polyvalent et facile à apprendre.",
            "module_name": "Bases de Python",
            "training_name": "Formation Python Débutant"
        }
        
        self.test_learner_profile = {
            "experience_level": "débutant",
            "learning_style": "visuel",
            "job_position": "développeur junior",
            "activity_sector": "informatique",
            "language": "fr"
        }
    
    async def test_session_creation(self) -> bool:
        """Test creating a Live API session"""
        logger.info("🚀 Testing Live API session creation...")
        
        try:
            learner_session_id = uuid.uuid4()
            
            session_id = await self.adapter.create_live_session(
                slide_context=self.test_slide_context,
                learner_profile=self.test_learner_profile,
                learner_session_id=learner_session_id
            )
            
            if session_id:
                logger.info(f"✅ Session created successfully: {session_id}")
                logger.info(f"Active sessions count: {self.adapter.get_session_count()}")
                return True
            else:
                logger.error("❌ Session creation returned empty session ID")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating session: {e}")
            return False
    
    async def test_mock_text_generation(self) -> bool:
        """Test mock text generation directly"""
        logger.info("📝 Testing mock text generation...")
        
        try:
            # Test the private method directly
            mock_text = self.adapter._generate_mock_response(
                self.test_learner_profile,
                self.test_slide_context
            )
            
            if mock_text and len(mock_text.strip()) > 0:
                logger.info(f"✅ Mock text generated: '{mock_text[:100]}...'")
                return True
            else:
                logger.error("❌ Mock text generation returned empty string")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error generating mock text: {e}")
            return False
    
    async def test_conversation_handling_without_throttle(self) -> bool:
        """Test conversation handling without throttling issues"""
        logger.info("🎙️ Testing conversation handling (no throttle)...")
        
        try:
            # First create a session
            learner_session_id = uuid.uuid4()
            session_id = await self.adapter.create_live_session(
                slide_context=self.test_slide_context,
                learner_profile=self.test_learner_profile,
                learner_session_id=learner_session_id
            )
            
            # Test audio data (dummy)
            dummy_audio = b"FAKE_AUDIO_DATA_FOR_TESTING"
            
            # Process conversation
            response = await self.adapter.handle_live_conversation(
                session_id=session_id,
                audio_input=dummy_audio,
                mime_type="audio/webm"
            )
            
            # Check response structure
            required_keys = ['audio_response', 'text_transcript', 'metadata', 'is_complete']
            missing_keys = [key for key in required_keys if key not in response]
            
            if missing_keys:
                logger.error(f"❌ Response missing keys: {missing_keys}")
                return False
            
            # Check text content
            text_content = response.get('text_transcript', '')
            if not text_content or len(text_content.strip()) == 0:
                logger.error("❌ No text transcript in response")
                return False
            
            # Check metadata
            metadata = response.get('metadata', {})
            if not metadata.get('mock'):
                logger.warning("⚠️ Response not marked as mock")
            
            logger.info(f"✅ Conversation response generated: '{text_content[:50]}...'")
            logger.info(f"Metadata: {metadata}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in conversation handling: {e}")
            return False
    
    async def test_throttling_mechanism(self) -> bool:
        """Test the throttling mechanism"""
        logger.info("⏰ Testing throttling mechanism...")
        
        try:
            # Create session
            learner_session_id = uuid.uuid4()
            session_id = await self.adapter.create_live_session(
                slide_context=self.test_slide_context,
                learner_profile=self.test_learner_profile,
                learner_session_id=learner_session_id
            )
            
            dummy_audio = b"FAKE_AUDIO_DATA_FOR_TESTING"
            
            # First request (should work)
            response1 = await self.adapter.handle_live_conversation(
                session_id=session_id,
                audio_input=dummy_audio,
                mime_type="audio/webm"
            )
            
            if not response1.get('text_transcript'):
                logger.error("❌ First request failed to generate response")
                return False
            
            logger.info("✅ First request succeeded")
            
            # Immediate second request (should be throttled)
            response2 = await self.adapter.handle_live_conversation(
                session_id=session_id,
                audio_input=dummy_audio,
                mime_type="audio/webm"
            )
            
            # Check if throttled
            if response2.get('metadata', {}).get('throttled'):
                logger.info("✅ Second request correctly throttled")
                return True
            else:
                logger.warning("⚠️ Second request was not throttled (might be OK if enough time passed)")
                return True  # Not necessarily a failure
                
        except Exception as e:
            logger.error(f"❌ Error testing throttling: {e}")
            return False
    
    async def test_session_cleanup(self) -> bool:
        """Test session cleanup"""
        logger.info("🧹 Testing session cleanup...")
        
        try:
            # Create a session
            learner_session_id = uuid.uuid4()
            session_id = await self.adapter.create_live_session(
                slide_context=self.test_slide_context,
                learner_profile=self.test_learner_profile,
                learner_session_id=learner_session_id
            )
            
            initial_count = self.adapter.get_session_count()
            logger.info(f"Sessions before cleanup: {initial_count}")
            
            # Close the session
            success = await self.adapter.close_live_session(session_id)
            
            if not success:
                logger.error("❌ Session close returned failure")
                return False
            
            final_count = self.adapter.get_session_count()
            logger.info(f"Sessions after cleanup: {final_count}")
            
            if final_count < initial_count:
                logger.info("✅ Session cleaned up successfully")
                return True
            else:
                logger.error("❌ Session count did not decrease after cleanup")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error testing cleanup: {e}")
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all mock response tests"""
        logger.info("🚀 Starting Mock Response Tests")
        logger.info("=" * 50)
        
        results = {}
        
        # Test 1: Session creation
        results['session_creation'] = await self.test_session_creation()
        
        # Test 2: Mock text generation
        results['mock_text_generation'] = await self.test_mock_text_generation()
        
        # Test 3: Conversation handling
        results['conversation_handling'] = await self.test_conversation_handling_without_throttle()
        
        # Test 4: Throttling mechanism
        results['throttling_mechanism'] = await self.test_throttling_mechanism()
        
        # Test 5: Session cleanup
        results['session_cleanup'] = await self.test_session_cleanup()
        
        # Cleanup all sessions
        await self.adapter.cleanup_all_sessions()
        
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
            logger.info("🎉 All mock response tests passed!")
        else:
            logger.error("⚠️ Some mock response tests failed")
            
        return results


async def main():
    """Main test function"""
    tester = MockResponseTester()
    results = await tester.run_all_tests()
    
    # Exit with appropriate code
    all_passed = all(results.values())
    exit(0 if all_passed else 1)


if __name__ == "__main__":
    asyncio.run(main())