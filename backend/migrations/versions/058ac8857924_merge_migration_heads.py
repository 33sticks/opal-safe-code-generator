"""merge migration heads

Revision ID: 058ac8857924
Revises: a8b9c0d1e2f3, 2833d4be0fb6
Create Date: 2025-11-03 10:10:03.388053

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '058ac8857924'
down_revision: Union[str, None] = ('a8b9c0d1e2f3', '2833d4be0fb6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
