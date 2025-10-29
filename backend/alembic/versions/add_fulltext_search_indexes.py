"""add fulltext search indexes

Revision ID: add_fts_indexes
Revises: add_pgvector_support
Create Date: 2024-10-29

Adds PostgreSQL full-text search indexes for improved search performance
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_fts_indexes'
down_revision = 'add_pgvector_support'
branch_labels = None
depends_on = None


def upgrade():
    """
    Add full-text search indexes to verses and translations tables
    
    These indexes enable fast text search using PostgreSQL's built-in
    full-text search capabilities with to_tsvector and to_tsquery.
    """
    # Enable pg_trgm extension if not already enabled (for trigram similarity)
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    
    # Create GIN index on verses.text_simple for Arabic search
    # Uses 'simple' configuration to avoid language-specific stemming
    op.execute("""
        CREATE INDEX IF NOT EXISTS verses_text_simple_fts_idx 
        ON verses USING GIN(to_tsvector('simple', COALESCE(text_simple, '')))
    """)
    
    # Create GIN index on verses.text_arabic for Arabic search with full diacritics
    op.execute("""
        CREATE INDEX IF NOT EXISTS verses_text_arabic_fts_idx 
        ON verses USING GIN(to_tsvector('simple', COALESCE(text_arabic, '')))
    """)
    
    # Create GIN index on translations.text for English/Telugu translations
    # Uses 'english' configuration for better stemming and stop word handling
    op.execute("""
        CREATE INDEX IF NOT EXISTS translations_text_fts_idx 
        ON translations USING GIN(to_tsvector('english', COALESCE(text, '')))
    """)
    
    # Create trigram index for fuzzy search fallback
    op.execute("""
        CREATE INDEX IF NOT EXISTS verses_text_simple_trgm_idx 
        ON verses USING GIN(text_simple gin_trgm_ops)
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS translations_text_trgm_idx 
        ON translations USING GIN(text gin_trgm_ops)
    """)


def downgrade():
    """Remove full-text search indexes"""
    op.execute("DROP INDEX IF EXISTS verses_text_simple_fts_idx")
    op.execute("DROP INDEX IF EXISTS verses_text_arabic_fts_idx")
    op.execute("DROP INDEX IF EXISTS translations_text_fts_idx")
    op.execute("DROP INDEX IF EXISTS verses_text_simple_trgm_idx")
    op.execute("DROP INDEX IF EXISTS translations_text_trgm_idx")
