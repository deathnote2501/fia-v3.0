"""Rename personalized_plan to enriched_profile in learner_sessions

This migration renames the personalized_plan column to enriched_profile to better reflect 
its new purpose of storing enriched learner profile data rather than plan data.

Revision ID: 007_rename_personalized_plan
Revises: 8b74fa16b171
Create Date: 2025-01-28 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '007_rename_personalized_plan'
down_revision: str = '006_add_plan_data'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Rename personalized_plan column to enriched_profile in learner_sessions table."""
    # Rename column from personalized_plan to enriched_profile
    op.alter_column(
        'learner_sessions',
        'personalized_plan',
        new_column_name='enriched_profile'
    )


def downgrade() -> None:
    """Rename enriched_profile column back to personalized_plan in learner_sessions table."""
    # Rename column back from enriched_profile to personalized_plan
    op.alter_column(
        'learner_sessions',
        'enriched_profile',
        new_column_name='personalized_plan'
    )