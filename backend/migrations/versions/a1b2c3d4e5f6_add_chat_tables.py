"""add_chat_tables

Revision ID: a1b2c3d4e5f6
Revises: 8cae0c760c0f
Create Date: 2025-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '8cae0c760c0f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('brand_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['brand_id'], ['brands.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_user_id'), 'conversations', ['user_id'], unique=False)
    op.create_index(op.f('ix_conversations_status'), 'conversations', ['status'], unique=False)
    
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('generated_code_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['generated_code_id'], ['generated_code.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_conversation_id'), 'messages', ['conversation_id'], unique=False)
    
    # Alter generated_code table to add conversation_id and user_id
    op.add_column('generated_code', sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('generated_code', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_generated_code_conversation', 'generated_code', 'conversations', ['conversation_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_generated_code_user', 'generated_code', 'users', ['user_id'], ['id'], ondelete='SET NULL')
    op.create_index(op.f('ix_generated_code_conversation_id'), 'generated_code', ['conversation_id'], unique=False)


def downgrade() -> None:
    # Drop indexes and foreign keys from generated_code
    op.drop_index(op.f('ix_generated_code_conversation_id'), table_name='generated_code')
    op.drop_constraint('fk_generated_code_user', 'generated_code', type_='foreignkey')
    op.drop_constraint('fk_generated_code_conversation', 'generated_code', type_='foreignkey')
    op.drop_column('generated_code', 'user_id')
    op.drop_column('generated_code', 'conversation_id')
    
    # Drop messages table
    op.drop_index(op.f('ix_messages_conversation_id'), table_name='messages')
    op.drop_table('messages')
    
    # Drop conversations table
    op.drop_index(op.f('ix_conversations_status'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_user_id'), table_name='conversations')
    op.drop_table('conversations')
    
    # Note: We don't drop the UUID extension as it might be used elsewhere

