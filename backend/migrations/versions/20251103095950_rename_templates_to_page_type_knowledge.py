"""rename templates to page_type_knowledge

Revision ID: a8b9c0d1e2f3
Revises: f7g8h9i0j1k2
Create Date: 2025-11-03 09:59:50.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8b9c0d1e2f3'
down_revision: Union[str, None] = 'f7g8h9i0j1k2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename table from templates to page_type_knowledge
    op.rename_table('templates', 'page_type_knowledge')


def downgrade() -> None:
    # Revert rename
    op.rename_table('page_type_knowledge', 'templates')

