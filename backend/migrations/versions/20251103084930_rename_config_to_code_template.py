"""rename config to code_template

Revision ID: 14ba839b015c
Revises: f7g8h9i0j1k2
Create Date: 2025-11-03 08:49:30.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '14ba839b015c'
down_revision: Union[str, None] = 'f7g8h9i0j1k2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename brands.config column to brands.code_template
    op.alter_column('brands', 'config', new_column_name='code_template')


def downgrade() -> None:
    # Revert rename: brands.code_template back to brands.config
    op.alter_column('brands', 'code_template', new_column_name='config')

