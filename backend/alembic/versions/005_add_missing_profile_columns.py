"""add_missing_profile_columns

Revision ID: 005_add_missing_profile_columns
Revises: 004_fix_profile_columns
Create Date: 2025-07-26 18:26:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '005_add_missing_profile_columns'
down_revision: Union[str, Sequence[str], None] = '003_personalized_training'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing profile columns and update existing ones"""
    
    # Rename existing columns to match new schema
    op.alter_column('learner_sessions', 'level', new_column_name='experience_level')
    op.alter_column('learner_sessions', 'job', new_column_name='job_position')
    op.alter_column('learner_sessions', 'sector', new_column_name='activity_sector')
    op.alter_column('learner_sessions', 'current_slide_index', new_column_name='current_slide_number')
    
    # Add missing columns
    op.add_column('learner_sessions', sa.Column('personalized_plan', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    
    # Set default values
    op.execute("UPDATE learner_sessions SET current_slide_number = 1 WHERE current_slide_number IS NULL")
    op.execute("UPDATE learner_sessions SET total_time_spent = 0 WHERE total_time_spent IS NULL")
    
    # Make email NOT NULL
    op.alter_column('learner_sessions', 'email',
               existing_type=sa.VARCHAR(),
               nullable=False)
    
    # Remove session_token column and its index
    try:
        op.drop_index('ix_learner_sessions_session_token', table_name='learner_sessions')
    except Exception:
        pass
    
    try:
        op.drop_column('learner_sessions', 'session_token')
    except Exception:
        pass
    
    # Remove unused columns
    try:
        op.drop_column('learner_sessions', 'completed_at')
        op.drop_column('learner_sessions', 'engagement_level')
    except Exception:
        pass
    
    # Add unique constraint for training_session_id + email
    try:
        op.create_unique_constraint('_training_session_email_uc', 'learner_sessions', ['training_session_id', 'email'])
    except Exception:
        # Constraint might already exist
        pass


def downgrade() -> None:
    """Revert column changes"""
    
    # Drop unique constraint
    try:
        op.drop_constraint('_training_session_email_uc', 'learner_sessions', type_='unique')
    except Exception:
        pass
    
    # Revert column names
    op.alter_column('learner_sessions', 'experience_level', new_column_name='level')
    op.alter_column('learner_sessions', 'job_position', new_column_name='job')
    op.alter_column('learner_sessions', 'activity_sector', new_column_name='sector')
    op.alter_column('learner_sessions', 'current_slide_number', new_column_name='current_slide_index')
    
    # Drop added columns
    op.drop_column('learner_sessions', 'personalized_plan')
    
    # Add back removed columns
    op.add_column('learner_sessions', sa.Column('session_token', sa.VARCHAR(), nullable=False))
    op.add_column('learner_sessions', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('learner_sessions', sa.Column('engagement_level', sa.VARCHAR(), nullable=True))
    
    # Recreate session_token index
    op.create_index('ix_learner_sessions_session_token', 'learner_sessions', ['session_token'], unique=True)
    
    # Revert email nullable
    op.alter_column('learner_sessions', 'email',
               existing_type=sa.VARCHAR(),
               nullable=True)