"""add_requires_review_to_generated_code

Revision ID: f7g8h9i0j1k2
Revises: e6f7a8b9c0d1
Create Date: 2025-01-18 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7g8h9i0j1k2'
down_revision: Union[str, None] = 'e6f7a8b9c0d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add requires_review column to generated_code table
    op.add_column(
        'generated_code',
        sa.Column('requires_review', sa.Boolean(), nullable=False, server_default='false')
    )
    
    # Create index for filtering
    op.create_index(
        op.f('ix_generated_code_requires_review'),
        'generated_code',
        ['requires_review'],
        unique=False
    )


def downgrade() -> None:
    # Drop index
    op.drop_index(op.f('ix_generated_code_requires_review'), table_name='generated_code')
    
    # Drop column
    op.drop_column('generated_code', 'requires_review')

