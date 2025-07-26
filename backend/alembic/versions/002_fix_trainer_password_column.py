"""Fix trainer password column name for FastAPI-Users

Revision ID: 002_fix_password
Revises: 001_initial
Create Date: 2025-07-26 15:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_fix_password'
down_revision: Union[str, Sequence[str], None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename password_hash to hashed_password for FastAPI-Users compatibility
    op.alter_column('trainers', 'password_hash', new_column_name='hashed_password')
    
    # Add missing FastAPI-Users columns if they don't exist
    # Check if columns exist first
    op.add_column('trainers', sa.Column('is_superuser', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('trainers', sa.Column('is_verified', sa.Boolean(), nullable=True, server_default='false'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove FastAPI-Users specific columns
    op.drop_column('trainers', 'is_verified')
    op.drop_column('trainers', 'is_superuser')
    
    # Rename back to password_hash
    op.alter_column('trainers', 'hashed_password', new_column_name='password_hash')