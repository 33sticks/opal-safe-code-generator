"""add_code_review_fields

Revision ID: d4e5f6a7b8c9
Revises: a1b2c3d4e5f6
Create Date: 2025-01-16 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add review fields to generated_code table
    op.add_column('generated_code', sa.Column('status', sa.String(length=50), nullable=False, server_default='generated'))
    op.add_column('generated_code', sa.Column('reviewer_id', sa.Integer(), nullable=True))
    op.add_column('generated_code', sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('generated_code', sa.Column('reviewer_notes', sa.Text(), nullable=True))
    op.add_column('generated_code', sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('generated_code', sa.Column('rejection_reason', sa.Text(), nullable=True))
    
    # Create foreign key constraint for reviewer_id
    op.create_foreign_key(
        'fk_generated_code_reviewer',
        'generated_code',
        'users',
        ['reviewer_id'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Create indexes
    op.create_index(op.f('ix_generated_code_status'), 'generated_code', ['status'], unique=False)
    op.create_index(op.f('ix_generated_code_reviewer_id'), 'generated_code', ['reviewer_id'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_generated_code_reviewer_id'), table_name='generated_code')
    op.drop_index(op.f('ix_generated_code_status'), table_name='generated_code')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_generated_code_reviewer', 'generated_code', type_='foreignkey')
    
    # Drop columns
    op.drop_column('generated_code', 'rejection_reason')
    op.drop_column('generated_code', 'approved_at')
    op.drop_column('generated_code', 'reviewer_notes')
    op.drop_column('generated_code', 'reviewed_at')
    op.drop_column('generated_code', 'reviewer_id')
    op.drop_column('generated_code', 'status')

