"""Add generated image fields to training_slides table

This migration adds support for storing generated images for slides:
- generated_image_path: File path to the stored PNG image
- generated_image_metadata: JSON metadata about the generated image

Revision ID: 009_add_slide_generated_image
Revises: 008_add_slide_type
Create Date: 2025-01-30 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '009_add_slide_generated_image'
down_revision: str = '4ec93e9be28b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add generated image fields to training_slides table."""
    # Add generated_image_path column
    op.add_column(
        'training_slides',
        sa.Column(
            'generated_image_path', 
            sa.String(255), 
            nullable=True
        )
    )
    
    # Add generated_image_metadata column
    op.add_column(
        'training_slides',
        sa.Column(
            'generated_image_metadata', 
            sa.JSON(), 
            nullable=True
        )
    )


def downgrade() -> None:
    """Remove generated image fields from training_slides table."""
    op.drop_column('training_slides', 'generated_image_metadata')
    op.drop_column('training_slides', 'generated_image_path')