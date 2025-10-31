"""Initial migration

Revision ID: 0fb23199b410
Revises: 
Create Date: 2025-10-31 09:55:03.233417

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0fb23199b410'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create brands table
    op.create_table(
        'brands',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_brands_id'), 'brands', ['id'], unique=False)
    op.create_index(op.f('ix_brands_name'), 'brands', ['name'], unique=True)
    
    # Create templates table
    op.create_table(
        'templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('brand_id', sa.Integer(), nullable=False),
        sa.Column('test_type', sa.String(length=50), nullable=False),
        sa.Column('template_code', sa.Text(), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['brand_id'], ['brands.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_templates_id'), 'templates', ['id'], unique=False)
    op.create_index(op.f('ix_templates_brand_id'), 'templates', ['brand_id'], unique=False)
    op.create_index(op.f('ix_templates_is_active'), 'templates', ['is_active'], unique=False)
    # Partial index for active templates by brand and type
    op.execute("""
        CREATE INDEX idx_templates_brand_type 
        ON templates(brand_id, test_type) 
        WHERE is_active = TRUE
    """)
    
    # Create dom_selectors table
    op.create_table(
        'dom_selectors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('brand_id', sa.Integer(), nullable=False),
        sa.Column('page_type', sa.String(length=50), nullable=False),
        sa.Column('selector', sa.Text(), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['brand_id'], ['brands.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dom_selectors_id'), 'dom_selectors', ['id'], unique=False)
    op.create_index(op.f('ix_dom_selectors_brand_id'), 'dom_selectors', ['brand_id'], unique=False)
    op.create_index(op.f('ix_dom_selectors_status'), 'dom_selectors', ['status'], unique=False)
    # Partial index for active selectors by brand and page type
    op.execute("""
        CREATE INDEX idx_selectors_brand_page 
        ON dom_selectors(brand_id, page_type) 
        WHERE status = 'active'
    """)
    
    # Create code_rules table
    op.create_table(
        'code_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('brand_id', sa.Integer(), nullable=False),
        sa.Column('rule_type', sa.String(length=50), nullable=False),
        sa.Column('rule_content', sa.Text(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['brand_id'], ['brands.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_code_rules_id'), 'code_rules', ['id'], unique=False)
    op.create_index(op.f('ix_code_rules_brand_id'), 'code_rules', ['brand_id'], unique=False)
    
    # Create generated_code table
    op.create_table(
        'generated_code',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('brand_id', sa.Integer(), nullable=False),
        sa.Column('request_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('generated_code', sa.Text(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('validation_status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('user_feedback', sa.Text(), nullable=True),
        sa.Column('deployment_status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('error_logs', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['brand_id'], ['brands.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_generated_code_id'), 'generated_code', ['id'], unique=False)
    op.create_index(op.f('ix_generated_code_brand_id'), 'generated_code', ['brand_id'], unique=False)
    op.create_index(op.f('ix_generated_code_validation_status'), 'generated_code', ['validation_status'], unique=False)
    op.create_index(op.f('ix_generated_code_created_at'), 'generated_code', ['created_at'], unique=False)
    # Index on validation_status and created_at
    op.execute("""
        CREATE INDEX idx_generated_status 
        ON generated_code(validation_status, created_at)
    """)


def downgrade() -> None:
    # Drop indexes
    op.execute("DROP INDEX IF EXISTS idx_generated_status")
    op.execute("DROP INDEX IF EXISTS idx_selectors_brand_page")
    op.execute("DROP INDEX IF EXISTS idx_templates_brand_type")
    
    # Drop tables in reverse order
    op.drop_table('generated_code')
    op.drop_table('code_rules')
    op.drop_table('dom_selectors')
    op.drop_table('templates')
    op.drop_table('brands')
    
    # No enum types to drop (using VARCHAR instead)