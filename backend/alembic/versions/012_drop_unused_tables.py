"""drop_unused_tables

Revision ID: 012_drop_unused
Revises: 011_strategic_indexes
Create Date: 2025-08-02 15:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '012_drop_unused'
down_revision: Union[str, Sequence[str], None] = '011_strategic_indexes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop unused tables to improve performance and simplify schema."""
    
    # Drop unused slides table (replaced by training_slides)
    op.drop_table('slides')
    
    # Drop unused api_logs table and its index (replaced by application logging)
    op.drop_index('idx_api_logs_created', table_name='api_logs')
    op.drop_table('api_logs')


def downgrade() -> None:
    """Recreate unused tables if needed (not recommended)."""
    
    # Recreate api_logs table
    op.create_table('api_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('service_name', sa.VARCHAR(), nullable=False),
        sa.Column('endpoint', sa.VARCHAR(), nullable=False),
        sa.Column('method', sa.VARCHAR(), nullable=False),
        sa.Column('request_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('response_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status_code', sa.INTEGER(), nullable=True),
        sa.Column('response_time_ms', sa.INTEGER(), nullable=True),
        sa.Column('tokens_used', sa.INTEGER(), nullable=True),
        sa.Column('cost_estimate', sa.VARCHAR(), nullable=True),
        sa.Column('learner_session_id', sa.UUID(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['learner_session_id'], ['learner_sessions.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_api_logs_created', 'api_logs', ['created_at'])
    
    # Recreate slides table
    op.create_table('slides',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('learner_session_id', sa.UUID(), nullable=False),
        sa.Column('slide_index', sa.INTEGER(), nullable=False),
        sa.Column('title', sa.VARCHAR(), nullable=False),
        sa.Column('content', sa.TEXT(), nullable=True),
        sa.Column('ai_context', sa.TEXT(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('viewed_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('time_spent', sa.INTEGER(), default=0, nullable=True),
        sa.ForeignKeyConstraint(['learner_session_id'], ['learner_sessions.id']),
        sa.PrimaryKeyConstraint('id')
    )