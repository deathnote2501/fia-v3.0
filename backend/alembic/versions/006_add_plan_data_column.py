"""Add plan_data column to learner_training_plans

Revision ID: 006_add_plan_data
Revises: 8b74fa16b171
Create Date: 2025-07-27 12:49:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = '006_add_plan_data'
down_revision: Union[str, Sequence[str], None] = '8b74fa16b171'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add plan_data column to learner_training_plans table."""
    
    # Add the missing columns to learner_training_plans
    op.add_column('learner_training_plans', 
        sa.Column('plan_data', JSONB, nullable=True)
    )
    op.add_column('learner_training_plans', 
        sa.Column('generation_method', sa.String(), nullable=True)
    )
    op.add_column('learner_training_plans', 
        sa.Column('tokens_used', sa.Integer(), nullable=True)
    )
    op.add_column('learner_training_plans', 
        sa.Column('generation_time_seconds', sa.Integer(), nullable=True)
    )


def downgrade() -> None:
    """Remove plan_data column from learner_training_plans table."""
    
    # Remove the columns
    op.drop_column('learner_training_plans', 'generation_time_seconds')
    op.drop_column('learner_training_plans', 'tokens_used')
    op.drop_column('learner_training_plans', 'generation_method')
    op.drop_column('learner_training_plans', 'plan_data')