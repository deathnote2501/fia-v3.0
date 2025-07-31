"""Add is_ai_generated column to trainings table

Revision ID: 010_add_is_ai_generated_to_trainings
Revises: 009_add_slide_generated_image
Create Date: 2025-07-31 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '010_ai_training'
down_revision: Union[str, Sequence[str], None] = '009_add_slide_generated_image'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add is_ai_generated column to trainings table."""
    op.add_column('trainings', sa.Column('is_ai_generated', sa.Boolean(), nullable=False, server_default=sa.text('false')))


def downgrade() -> None:
    """Remove is_ai_generated column from trainings table."""
    op.drop_column('trainings', 'is_ai_generated')