"""add_strategic_performance_indexes

Revision ID: 011_strategic_indexes
Revises: 64d4179d4572
Create Date: 2025-08-02 15:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '011_strategic_indexes'
down_revision: Union[str, Sequence[str], None] = '64d4179d4572'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add strategic performance indexes for Plan 1 optimization."""
    
    # 1. Index composites pour jointures critiques
    op.create_index(
        'idx_trainings_trainer_ai', 
        'trainings', 
        ['trainer_id', 'is_ai_generated']
    )
    
    op.create_index(
        'idx_training_sessions_training_active', 
        'training_sessions', 
        ['training_id', 'is_active']
    )
    
    op.create_index(
        'idx_learner_sessions_email_time', 
        'learner_sessions', 
        ['email', 'total_time_spent']
    )
    
    # 2. Index partiels pour données actives (optimisation WHERE clauses)
    op.execute("""
        CREATE INDEX idx_active_sessions 
        ON training_sessions(training_id) 
        WHERE is_active = true
    """)
    
    op.execute("""
        CREATE INDEX idx_active_trainers 
        ON trainers(id) 
        WHERE is_active = true
    """)
    
    # 3. Index JSONB pour profils enrichis (recherche dans JSONB)
    op.create_index(
        'idx_enriched_profile_gin', 
        'learner_sessions', 
        ['enriched_profile'],
        postgresql_using='gin'
    )
    
    # 4. Index pour requêtes dashboard admin (GROUP BY optimization)
    op.create_index(
        'idx_learner_sessions_training_email', 
        'learner_sessions', 
        ['training_session_id', 'email']
    )
    
    op.create_index(
        'idx_chat_messages_session_created', 
        'chat_messages', 
        ['learner_session_id', 'created_at']
    )


def downgrade() -> None:
    """Remove strategic performance indexes."""
    
    # Drop indexes in reverse order
    op.drop_index('idx_chat_messages_session_created', table_name='chat_messages')
    op.drop_index('idx_learner_sessions_training_email', table_name='learner_sessions')
    op.drop_index('idx_enriched_profile_gin', table_name='learner_sessions')
    op.drop_index('idx_active_trainers', table_name='trainers')
    op.drop_index('idx_active_sessions', table_name='training_sessions')
    op.drop_index('idx_learner_sessions_email_time', table_name='learner_sessions')
    op.drop_index('idx_training_sessions_training_active', table_name='training_sessions')
    op.drop_index('idx_trainings_trainer_ai', table_name='trainings')