"""Initial migration with file storage

Revision ID: 001_initial
Revises: 
Create Date: 2025-07-26 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create trainers table
    op.create_table('trainers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trainers_email'), 'trainers', ['email'], unique=True)

    # Create trainings table with file storage fields
    op.create_table('trainings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('trainer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('file_path', sa.String(), nullable=True),
        sa.Column('file_name', sa.String(), nullable=True),
        sa.Column('file_type', sa.String(), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['trainer_id'], ['trainers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create training_sessions table
    op.create_table('training_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('training_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('session_token', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['training_id'], ['trainings.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_training_sessions_session_token'), 'training_sessions', ['session_token'], unique=True)

    # Create learner_sessions table
    op.create_table('learner_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('training_session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('level', sa.String(), nullable=True),
        sa.Column('learning_style', sa.String(), nullable=True),
        sa.Column('job', sa.String(), nullable=True),
        sa.Column('sector', sa.String(), nullable=True),
        sa.Column('country', sa.String(), nullable=True),
        sa.Column('language', sa.String(), nullable=True),
        sa.Column('session_token', sa.String(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('current_slide_index', sa.Integer(), nullable=True),
        sa.Column('total_time_spent', sa.Integer(), nullable=True),
        sa.Column('engagement_level', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['training_session_id'], ['training_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_learner_sessions_session_token'), 'learner_sessions', ['session_token'], unique=True)

    # Create slides table
    op.create_table('slides',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('learner_session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('slide_index', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('ai_context', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('viewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('time_spent', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['learner_session_id'], ['learner_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create chat_messages table
    op.create_table('chat_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('learner_session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('response', sa.Text(), nullable=True),
        sa.Column('message_type', sa.String(), nullable=False),
        sa.Column('ai_context', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['learner_session_id'], ['learner_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create api_logs table
    op.create_table('api_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('endpoint', sa.String(), nullable=False),
        sa.Column('method', sa.String(), nullable=False),
        sa.Column('request_data', sa.Text(), nullable=True),
        sa.Column('response_data', sa.Text(), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('execution_time', sa.Float(), nullable=False),
        sa.Column('gemini_tokens_used', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('api_logs')
    op.drop_table('chat_messages')
    op.drop_table('slides')
    op.drop_index(op.f('ix_learner_sessions_session_token'), table_name='learner_sessions')
    op.drop_table('learner_sessions')
    op.drop_index(op.f('ix_training_sessions_session_token'), table_name='training_sessions')
    op.drop_table('training_sessions')
    op.drop_table('trainings')
    op.drop_index(op.f('ix_trainers_email'), table_name='trainers')
    op.drop_table('trainers')