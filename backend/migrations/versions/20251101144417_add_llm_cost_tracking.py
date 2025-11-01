"""add_llm_cost_tracking

Revision ID: 20251101144417
Revises: e6f7a8b9c0d1
Create Date: 2025-11-01 14:44:17.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '20251101144417'
down_revision: Union[str, None] = 'e6f7a8b9c0d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add LLM cost tracking fields to generated_code table
    op.add_column(
        'generated_code',
        sa.Column('prompt_tokens', sa.Integer(), nullable=True)
    )
    op.add_column(
        'generated_code',
        sa.Column('completion_tokens', sa.Integer(), nullable=True)
    )
    op.add_column(
        'generated_code',
        sa.Column('total_tokens', sa.Integer(), nullable=True)
    )
    op.add_column(
        'generated_code',
        sa.Column('llm_cost_usd', sa.Numeric(precision=10, scale=4), nullable=True)
    )


def downgrade() -> None:
    # Remove LLM cost tracking fields
    op.drop_column('generated_code', 'llm_cost_usd')
    op.drop_column('generated_code', 'total_tokens')
    op.drop_column('generated_code', 'completion_tokens')
    op.drop_column('generated_code', 'prompt_tokens')

