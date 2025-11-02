"""merge migration heads

Revision ID: 395f6bc701e6
Revises: 20251101144417, f7g8h9i0j1k2
Create Date: 2025-11-02 13:13:28.387679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '395f6bc701e6'
down_revision: Union[str, None] = ('20251101144417', 'f7g8h9i0j1k2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
