"""add_transliteration_and_translation_license

Revision ID: 3647477310f0
Revises: a3bbf0720c9b
Create Date: 2025-10-29 03:03:34.458081

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3647477310f0'
down_revision: Union[str, None] = 'a3bbf0720c9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add text_transliteration column to verse table
    op.add_column('verse', sa.Column('text_transliteration', sa.Text(), nullable=True))
    
    # Add license and source columns to translation table
    op.add_column('translation', sa.Column('license', sa.String(length=255), nullable=True))
    op.add_column('translation', sa.Column('source', sa.String(length=255), nullable=True))


def downgrade() -> None:
    # Remove license and source columns from translation table
    op.drop_column('translation', 'source')
    op.drop_column('translation', 'license')
    
    # Remove text_transliteration column from verse table
    op.drop_column('verse', 'text_transliteration')
