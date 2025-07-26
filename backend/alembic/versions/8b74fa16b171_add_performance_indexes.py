"""add_performance_indexes

Revision ID: 8b74fa16b171
Revises: 005_add_missing_profile_columns
Create Date: 2025-07-26 20:42:43.158585

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b74fa16b171'
down_revision: Union[str, Sequence[str], None] = '005_add_missing_profile_columns'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes for frequently queried columns."""
    # Index for learner_sessions by training_session_id (foreign key queries)
    op.create_index(
        'idx_learner_sessions_training_session', 
        'learner_sessions', 
        ['training_session_id']
    )
    
    # Index for chat_messages by learner_session_id (foreign key queries)
    op.create_index(
        'idx_chat_messages_learner_session', 
        'chat_messages', 
        ['learner_session_id']
    )
    
    # Index for api_logs by created_at (time-based queries and cleanup)
    op.create_index(
        'idx_api_logs_created', 
        'api_logs', 
        ['created_at']
    )


def downgrade() -> None:
    """Remove performance indexes."""
    # Drop indexes in reverse order
    op.drop_index('idx_api_logs_created', table_name='api_logs')
    op.drop_index('idx_chat_messages_learner_session', table_name='chat_messages')
    op.drop_index('idx_learner_sessions_training_session', table_name='learner_sessions')
