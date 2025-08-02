"""add_language_column_to_trainers

Revision ID: 64d4179d4572
Revises: b3b741b9e509
Create Date: 2025-08-02 14:15:16.962755

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '64d4179d4572'
down_revision: Union[str, Sequence[str], None] = 'b3b741b9e509'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add language column to trainers table with default value 'fr'
    op.add_column('trainers', sa.Column('language', sa.String(length=10), nullable=False, server_default='fr'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove language column from trainers table
    op.drop_column('trainers', 'language')
