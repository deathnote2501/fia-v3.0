"""Add slide_type column to training_slides table

This migration adds a slide_type column to support different types of slides:
- plan: Overview slide showing the complete training plan
- stage: Introduction slide for each training stage  
- module: Introduction slide for each training module
- content: Regular content slide (existing behavior, default value)
- quiz: Quiz slide for evaluation (end of submodule/module/stage)

Revision ID: 008_add_slide_type
Revises: 007_rename_personalized_plan
Create Date: 2025-01-29 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '008_add_slide_type'
down_revision: str = '007_rename_personalized_plan'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add slide_type column to training_slides table."""
    # Add slide_type column with default value 'content'
    op.add_column(
        'training_slides',
        sa.Column(
            'slide_type', 
            sa.String(20), 
            nullable=False, 
            server_default='content'
        )
    )


def downgrade() -> None:
    """Remove slide_type column from training_slides table."""
    op.drop_column('training_slides', 'slide_type')