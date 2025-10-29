"""Initial database schema

Revision ID: a3bbf0720c9b
Revises: 
Create Date: 2025-10-29 01:56:26.551968

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY


# revision identifiers, used by Alembic.
revision: str = 'a3bbf0720c9b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create surah table
    op.create_table(
        'surah',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('number', sa.Integer(), nullable=False),
        sa.Column('name_arabic', sa.String(length=255), nullable=False),
        sa.Column('name_english', sa.String(length=255), nullable=False),
        sa.Column('name_transliteration', sa.String(length=255), nullable=True),
        sa.Column('revelation_place', sa.String(length=50), nullable=True),
        sa.Column('total_verses', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('number')
    )
    op.create_index(op.f('ix_surah_id'), 'surah', ['id'], unique=False)
    op.create_index(op.f('ix_surah_number'), 'surah', ['number'], unique=False)

    # Create verse table
    op.create_table(
        'verse',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('surah_id', sa.Integer(), nullable=False),
        sa.Column('verse_number', sa.Integer(), nullable=False),
        sa.Column('text_arabic', sa.Text(), nullable=False),
        sa.Column('text_simple', sa.Text(), nullable=True),
        sa.Column('juz_number', sa.Integer(), nullable=True),
        sa.Column('hizb_number', sa.Integer(), nullable=True),
        sa.Column('rub_number', sa.Integer(), nullable=True),
        sa.Column('sajda', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['surah_id'], ['surah.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_verse_id'), 'verse', ['id'], unique=False)
    op.create_index(op.f('ix_verse_juz_number'), 'verse', ['juz_number'], unique=False)
    op.create_index(op.f('ix_verse_surah_id'), 'verse', ['surah_id'], unique=False)
    op.create_index(op.f('ix_verse_verse_number'), 'verse', ['verse_number'], unique=False)
    op.create_index('ix_verse_surah_number', 'verse', ['surah_id', 'verse_number'], unique=True)

    # Create translation table
    op.create_table(
        'translation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('verse_id', sa.Integer(), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('translator', sa.String(length=255), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['verse_id'], ['verse.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_translation_id'), 'translation', ['id'], unique=False)
    op.create_index(op.f('ix_translation_language'), 'translation', ['language'], unique=False)
    op.create_index(op.f('ix_translation_verse_id'), 'translation', ['verse_id'], unique=False)
    op.create_index('ix_translation_verse_language', 'translation', ['verse_id', 'language', 'translator'], unique=False)

    # Create audio_track table
    op.create_table(
        'audio_track',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('verse_id', sa.Integer(), nullable=False),
        sa.Column('reciter', sa.String(length=255), nullable=False),
        sa.Column('reciter_arabic', sa.String(length=255), nullable=True),
        sa.Column('audio_url', sa.String(length=512), nullable=False),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('format', sa.String(length=10), nullable=True),
        sa.Column('quality', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['verse_id'], ['verse.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audio_track_id'), 'audio_track', ['id'], unique=False)
    op.create_index(op.f('ix_audio_track_reciter'), 'audio_track', ['reciter'], unique=False)
    op.create_index(op.f('ix_audio_track_verse_id'), 'audio_track', ['verse_id'], unique=False)
    op.create_index('ix_audio_verse_reciter', 'audio_track', ['verse_id', 'reciter'], unique=False)

    # Create tag table
    op.create_table(
        'tag',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_tag_category'), 'tag', ['category'], unique=False)
    op.create_index(op.f('ix_tag_id'), 'tag', ['id'], unique=False)
    op.create_index(op.f('ix_tag_name'), 'tag', ['name'], unique=False)

    # Create verse_tag table
    op.create_table(
        'verse_tag',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('verse_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.Column('relevance_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['verse_id'], ['verse.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_verse_tag_id'), 'verse_tag', ['id'], unique=False)
    op.create_index(op.f('ix_verse_tag_tag_id'), 'verse_tag', ['tag_id'], unique=False)
    op.create_index(op.f('ix_verse_tag_verse_id'), 'verse_tag', ['verse_id'], unique=False)
    op.create_index('ix_verse_tag_unique', 'verse_tag', ['verse_id', 'tag_id'], unique=True)

    # Create entity table
    op.create_table(
        'entity',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('name_arabic', sa.String(length=255), nullable=True),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('verse_references', ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_entity_entity_type'), 'entity', ['entity_type'], unique=False)
    op.create_index(op.f('ix_entity_id'), 'entity', ['id'], unique=False)
    op.create_index(op.f('ix_entity_name'), 'entity', ['name'], unique=False)

    # Create embedding table
    op.create_table(
        'embedding',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('verse_id', sa.Integer(), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('embedding_vector', sa.Text(), nullable=False),
        sa.Column('dimension', sa.Integer(), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['verse_id'], ['verse.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_embedding_id'), 'embedding', ['id'], unique=False)
    op.create_index(op.f('ix_embedding_language'), 'embedding', ['language'], unique=False)
    op.create_index(op.f('ix_embedding_model'), 'embedding', ['model'], unique=False)
    op.create_index(op.f('ix_embedding_verse_id'), 'embedding', ['verse_id'], unique=False)
    op.create_index('ix_embedding_verse_model', 'embedding', ['verse_id', 'model', 'language'], unique=False)

    # Create bookmark table
    op.create_table(
        'bookmark',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('verse_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['verse_id'], ['verse.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bookmark_id'), 'bookmark', ['id'], unique=False)
    op.create_index(op.f('ix_bookmark_user_id'), 'bookmark', ['user_id'], unique=False)
    op.create_index(op.f('ix_bookmark_verse_id'), 'bookmark', ['verse_id'], unique=False)
    op.create_index('ix_bookmark_user_verse', 'bookmark', ['user_id', 'verse_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_bookmark_user_verse', table_name='bookmark')
    op.drop_index(op.f('ix_bookmark_verse_id'), table_name='bookmark')
    op.drop_index(op.f('ix_bookmark_user_id'), table_name='bookmark')
    op.drop_index(op.f('ix_bookmark_id'), table_name='bookmark')
    op.drop_table('bookmark')
    
    op.drop_index('ix_embedding_verse_model', table_name='embedding')
    op.drop_index(op.f('ix_embedding_verse_id'), table_name='embedding')
    op.drop_index(op.f('ix_embedding_model'), table_name='embedding')
    op.drop_index(op.f('ix_embedding_language'), table_name='embedding')
    op.drop_index(op.f('ix_embedding_id'), table_name='embedding')
    op.drop_table('embedding')
    
    op.drop_index(op.f('ix_entity_name'), table_name='entity')
    op.drop_index(op.f('ix_entity_id'), table_name='entity')
    op.drop_index(op.f('ix_entity_entity_type'), table_name='entity')
    op.drop_table('entity')
    
    op.drop_index('ix_verse_tag_unique', table_name='verse_tag')
    op.drop_index(op.f('ix_verse_tag_verse_id'), table_name='verse_tag')
    op.drop_index(op.f('ix_verse_tag_tag_id'), table_name='verse_tag')
    op.drop_index(op.f('ix_verse_tag_id'), table_name='verse_tag')
    op.drop_table('verse_tag')
    
    op.drop_index(op.f('ix_tag_name'), table_name='tag')
    op.drop_index(op.f('ix_tag_id'), table_name='tag')
    op.drop_index(op.f('ix_tag_category'), table_name='tag')
    op.drop_table('tag')
    
    op.drop_index('ix_audio_verse_reciter', table_name='audio_track')
    op.drop_index(op.f('ix_audio_track_verse_id'), table_name='audio_track')
    op.drop_index(op.f('ix_audio_track_reciter'), table_name='audio_track')
    op.drop_index(op.f('ix_audio_track_id'), table_name='audio_track')
    op.drop_table('audio_track')
    
    op.drop_index('ix_translation_verse_language', table_name='translation')
    op.drop_index(op.f('ix_translation_verse_id'), table_name='translation')
    op.drop_index(op.f('ix_translation_language'), table_name='translation')
    op.drop_index(op.f('ix_translation_id'), table_name='translation')
    op.drop_table('translation')
    
    op.drop_index('ix_verse_surah_number', table_name='verse')
    op.drop_index(op.f('ix_verse_verse_number'), table_name='verse')
    op.drop_index(op.f('ix_verse_surah_id'), table_name='verse')
    op.drop_index(op.f('ix_verse_juz_number'), table_name='verse')
    op.drop_index(op.f('ix_verse_id'), table_name='verse')
    op.drop_table('verse')
    
    op.drop_index(op.f('ix_surah_number'), table_name='surah')
    op.drop_index(op.f('ix_surah_id'), table_name='surah')
    op.drop_table('surah')

