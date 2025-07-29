"""add_objectives_and_training_duration_to_learner_sessions

Revision ID: 4ec93e9be28b
Revises: 008_add_slide_type
Create Date: 2025-07-29 16:06:11.925505

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4ec93e9be28b'
down_revision: Union[str, Sequence[str], None] = '008_add_slide_type'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add objectives and training_duration columns to learner_sessions table."""
    # Add objectives column for learner's expectations/objectives
    op.add_column('learner_sessions', sa.Column('objectives', sa.Text(), nullable=True))
    
    # Add training_duration column for desired training duration  
    op.add_column('learner_sessions', sa.Column('training_duration', sa.String(20), nullable=True))


def downgrade() -> None:
    """Remove objectives and training_duration columns from learner_sessions table."""
    # Remove the added columns
    op.drop_column('learner_sessions', 'training_duration')
    op.drop_column('learner_sessions', 'objectives')
