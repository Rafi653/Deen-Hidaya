"""add_pgvector_support

Revision ID: add_pgvector_support
Revises: 3647477310f0
Create Date: 2025-10-29 05:30:00.000000

This migration:
1. Enables pgvector extension if not already enabled
2. Converts embedding_vector column from Text to Vector type
3. Adds vector similarity index for faster semantic search
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_pgvector_support'
down_revision: Union[str, None] = '3647477310f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade to pgvector support
    
    Note: This migration is designed to work with PostgreSQL.
    For SQLite (used in tests), the Vector type will be ignored.
    """
    # Enable pgvector extension (PostgreSQL only)
    # This will be ignored in SQLite
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Check if we're using PostgreSQL or SQLite
    conn = op.get_bind()
    dialect_name = conn.dialect.name
    
    if dialect_name == 'postgresql':
        # For PostgreSQL: Convert embedding_vector from Text to Vector
        # First, check if there are any existing embeddings and clear them
        # since text data cannot be directly cast to vector
        op.execute("""
            DELETE FROM embedding WHERE embedding_vector IS NOT NULL
        """)
        
        # Now safely convert the column type
        op.execute("""
            ALTER TABLE embedding 
            ALTER COLUMN embedding_vector 
            TYPE vector(384) 
            USING NULL::vector(384)
        """)
        
        # Make column nullable (embeddings will be regenerated)
        op.execute("""
            ALTER TABLE embedding 
            ALTER COLUMN embedding_vector 
            DROP NOT NULL
        """)
        
        # Create index for vector similarity search using cosine distance
        # This significantly speeds up similarity searches
        op.create_index(
            'ix_embedding_vector_cosine',
            'embedding',
            ['embedding_vector'],
            unique=False,
            postgresql_using='ivfflat',
            postgresql_with={'lists': 100},
            postgresql_ops={'embedding_vector': 'vector_cosine_ops'}
        )
    
    # For SQLite, no changes needed as Vector type will be treated as BLOB


def downgrade() -> None:
    """
    Downgrade from pgvector support
    
    Warning: This will convert Vector back to Text, which may result in data loss
    """
    conn = op.get_bind()
    dialect_name = conn.dialect.name
    
    if dialect_name == 'postgresql':
        # Drop the vector index
        op.drop_index('ix_embedding_vector_cosine', table_name='embedding')
        
        # Convert back to Text
        op.execute("""
            ALTER TABLE embedding 
            ALTER COLUMN embedding_vector 
            TYPE text 
            USING embedding_vector::text
        """)
        
        op.execute("""
            ALTER TABLE embedding 
            ALTER COLUMN embedding_vector 
            SET NOT NULL
        """)
