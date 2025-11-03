"""add relationships column to dom_selectors

Revision ID: 20251103152818
Revises: 058ac8857924
Create Date: 2025-11-03 15:28:18.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '20251103152818'
down_revision: Union[str, None] = '058ac8857924'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add relationships column to dom_selectors table
    op.add_column(
        'dom_selectors',
        sa.Column('relationships', JSONB, nullable=True, server_default='{}')
    )


def downgrade() -> None:
    # Drop relationships column
    op.drop_column('dom_selectors', 'relationships')

