"""add name generator tables

Revision ID: add_name_generator
Revises: 3647477310f0
Create Date: 2025-11-03 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_name_generator'
down_revision = '3647477310f0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create name_entity table
    op.create_table(
        'name_entity',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('subtype', sa.String(length=100), nullable=True),
        sa.Column('gender', sa.String(length=20), nullable=True),
        sa.Column('meaning', sa.Text(), nullable=True),
        sa.Column('origin', sa.String(length=100), nullable=True),
        sa.Column('phonetic', sa.String(length=255), nullable=True),
        sa.Column('themes', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('associated_traits', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('popularity_score', sa.Float(), nullable=True, server_default='0.5'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for name_entity
    op.create_index('ix_name_entity_id', 'name_entity', ['id'])
    op.create_index('ix_name_entity_name', 'name_entity', ['name'])
    op.create_index('ix_name_entity_entity_type', 'name_entity', ['entity_type'])
    op.create_index('ix_name_entity_subtype', 'name_entity', ['subtype'])
    op.create_index('ix_name_entity_gender', 'name_entity', ['gender'])
    op.create_index('ix_name_entity_origin', 'name_entity', ['origin'])
    op.create_index('ix_name_entity_type_subtype', 'name_entity', ['entity_type', 'subtype'])
    op.create_index('ix_name_entity_gender_origin', 'name_entity', ['gender', 'origin'])
    
    # Create name_favorite table
    op.create_table(
        'name_favorite',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name_entity_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['name_entity_id'], ['name_entity.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for name_favorite
    op.create_index('ix_name_favorite_id', 'name_favorite', ['id'])
    op.create_index('ix_name_favorite_name_entity_id', 'name_favorite', ['name_entity_id'])
    op.create_index('ix_name_favorite_user_id', 'name_favorite', ['user_id'])
    op.create_index('ix_name_favorite_user_name', 'name_favorite', ['user_id', 'name_entity_id'], unique=True)


def downgrade() -> None:
    # Drop indexes and tables
    op.drop_index('ix_name_favorite_user_name', table_name='name_favorite')
    op.drop_index('ix_name_favorite_user_id', table_name='name_favorite')
    op.drop_index('ix_name_favorite_name_entity_id', table_name='name_favorite')
    op.drop_index('ix_name_favorite_id', table_name='name_favorite')
    op.drop_table('name_favorite')
    
    op.drop_index('ix_name_entity_gender_origin', table_name='name_entity')
    op.drop_index('ix_name_entity_type_subtype', table_name='name_entity')
    op.drop_index('ix_name_entity_origin', table_name='name_entity')
    op.drop_index('ix_name_entity_gender', table_name='name_entity')
    op.drop_index('ix_name_entity_subtype', table_name='name_entity')
    op.drop_index('ix_name_entity_entity_type', table_name='name_entity')
    op.drop_index('ix_name_entity_name', table_name='name_entity')
    op.drop_index('ix_name_entity_id', table_name='name_entity')
    op.drop_table('name_entity')
