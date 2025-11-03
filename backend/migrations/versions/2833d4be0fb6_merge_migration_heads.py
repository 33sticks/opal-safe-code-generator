"""merge migration heads

Revision ID: 2833d4be0fb6
Revises: 14ba839b015c, 395f6bc701e6
Create Date: 2025-11-03 08:53:11.937558

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2833d4be0fb6'
down_revision: Union[str, None] = ('14ba839b015c', '395f6bc701e6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
