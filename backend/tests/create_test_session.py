#!/usr/bin/env python3
"""
Create a test learner session for Live API testing
"""

import asyncio
from uuid import UUID
from app.infrastructure.database import get_database_session
from app.domain.entities.learner_session import LearnerSession
from app.adapters.repositories.learner_session_repository import LearnerSessionRepository
from app.adapters.repositories.training_session_repository import TrainingSessionRepository
from app.domain.entities.training_session import TrainingSession
from datetime import datetime, timezone

async def create_test_session():
    """Create a test learner session that can be used with Live API"""
    
    # Use the ID from the URL token that was failing
    test_learner_session_id = UUID('177fadf3-4744-40e0-811f-71f2621ccfee')
    
    async for db in get_database_session():
        try:
            learner_repo = LearnerSessionRepository(db)
            training_repo = TrainingSessionRepository(db)
            
            # Check if session already exists
            existing_session = await learner_repo.get_by_id(test_learner_session_id)
            if existing_session:
                print(f"✅ Session {test_learner_session_id} already exists")
                print(f"   Email: {existing_session.email}")
                print(f"   Language: {existing_session.language}")
                return existing_session
            
            # Try to find the training session that was referenced in the error
            training_session_id = UUID('0ee2a51a-921c-4acb-afdc-461332e8c44e')
            training_session = await training_repo.get_by_id(training_session_id)
            
            if not training_session:
                print(f"⚠️ Training session {training_session_id} not found, creating a mock one")
                # Create a mock training session
                training_session = TrainingSession(
                    id=training_session_id,
                    training_id=UUID('550e8400-e29b-41d4-a716-446655440000'),  # Mock training ID
                    name="Test Training Session",
                    description="Mock training session for Live API testing",
                    session_token="test_token",
                    is_active=True,
                    created_at=datetime.now(timezone.utc),
                    expires_at=datetime.now(timezone.utc).replace(year=2025, month=12)
                )
                await training_repo.create(training_session)
                print(f"✅ Created mock training session {training_session_id}")
            
            # Create learner session
            learner_session = LearnerSession(
                id=test_learner_session_id,
                training_session_id=training_session_id,
                email="test@example.com",
                experience_level="intermediate",
                learning_style="visual",
                job_position="Software Developer",
                activity_sector="Technology",
                country="France",
                language="fr",
                current_slide_number=1,
                total_time_spent=0,
                started_at=datetime.now(timezone.utc),
                last_activity_at=datetime.now(timezone.utc)
            )
            
            created_session = await learner_repo.create(learner_session)
            print(f"✅ Created test learner session {test_learner_session_id}")
            print(f"   Email: {created_session.email}")
            print(f"   Language: {created_session.language}")
            print(f"   Training: {created_session.training_session_id}")
            
            return created_session
            
        except Exception as e:
            print(f"❌ Error creating test session: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            break

if __name__ == "__main__":
    result = asyncio.run(create_test_session())
    if result:
        print(f"\n🎉 Test session ready! You can now test Live API with:")
        print(f"   Learner Session ID: {result.id}")
        print(f"   URL: http://localhost:8000/frontend/public/training.html?token=YOUR_TOKEN")
    else:
        print("\n❌ Failed to create test session")