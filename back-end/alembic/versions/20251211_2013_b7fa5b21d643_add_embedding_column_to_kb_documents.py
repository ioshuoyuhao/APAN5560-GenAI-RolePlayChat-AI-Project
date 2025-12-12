"""add_embedding_column_to_kb_documents

Revision ID: b7fa5b21d643
Revises: 1c0db4e8a004
Create Date: 2025-12-11 20:13:52.316380

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = 'b7fa5b21d643'
down_revision: Union[str, None] = '1c0db4e8a004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Ensure pgvector extension is enabled
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    
    # Add embedding column with pgvector Vector type
    op.add_column('kb_documents', sa.Column('embedding', Vector(1536), nullable=True))


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_column('kb_documents', 'embedding')
