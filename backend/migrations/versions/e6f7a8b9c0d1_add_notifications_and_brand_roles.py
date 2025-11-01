"""add_notifications_and_brand_roles

Revision ID: e6f7a8b9c0d1
Revises: d4e5f6a7b8c9
Create Date: 2025-01-17 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e6f7a8b9c0d1'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add brand_role column to users table
    op.add_column(
        'users',
        sa.Column('brand_role', sa.String(length=50), nullable=False, server_default='brand_user')
    )
    op.create_index(op.f('ix_users_brand_role'), 'users', ['brand_role'], unique=False)
    
    # Update existing users
    # admin@opalsafecode.com → super_admin
    op.execute(
        "UPDATE users SET brand_role = 'super_admin' WHERE email = 'admin@opalsafecode.com'"
    )
    # user@vans.com → brand_user (already default, but explicit)
    op.execute(
        "UPDATE users SET brand_role = 'brand_user' WHERE email = 'user@vans.com'"
    )
    
    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('generated_code_id', sa.Integer(), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['generated_code_id'], ['generated_code.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for notifications
    op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'], unique=False)
    op.create_index(op.f('ix_notifications_read'), 'notifications', ['read'], unique=False)
    op.create_index(op.f('ix_notifications_created_at'), 'notifications', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop notifications table and indexes
    op.drop_index(op.f('ix_notifications_created_at'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_read'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_user_id'), table_name='notifications')
    op.drop_table('notifications')
    
    # Drop brand_role column from users
    op.drop_index(op.f('ix_users_brand_role'), table_name='users')
    op.drop_column('users', 'brand_role')

