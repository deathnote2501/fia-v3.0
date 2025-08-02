"""add_admin_dashboard_performance_indexes

Revision ID: b3b741b9e509
Revises: 010_ai_training
Create Date: 2025-08-01 20:01:28.374339

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3b741b9e509'
down_revision: Union[str, Sequence[str], None] = '010_ai_training'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add basic performance indexes for admin dashboard queries."""
    
    # Only add indexes for tables we know exist and are needed
    # Index on trainers.is_active for filtering active trainers
    op.create_index(
        'idx_trainers_is_active', 
        'trainers', 
        ['is_active']
    )
    
    # Index on trainers.is_superuser for filtering superuser trainers  
    op.create_index(
        'idx_trainers_is_superuser', 
        'trainers', 
        ['is_superuser']
    )


def downgrade() -> None:
    """Remove basic performance indexes."""
    
    # Drop indexes in reverse order
    op.drop_index('idx_trainers_is_superuser', table_name='trainers')
    op.drop_index('idx_trainers_is_active', table_name='trainers')
