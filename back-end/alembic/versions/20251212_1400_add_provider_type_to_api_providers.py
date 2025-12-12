"""Add provider_type column to api_providers table

Revision ID: add_provider_type
Revises: a07523f0207c
Create Date: 2025-12-12 14:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "add_provider_type"
down_revision: Union[str, None] = "a07523f0207c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add provider_type column with default value 'openai'."""
    op.add_column(
        "api_providers",
        sa.Column(
            "provider_type",
            sa.String(50),
            nullable=False,
            server_default="openai",
        ),
    )


def downgrade() -> None:
    """Remove provider_type column."""
    op.drop_column("api_providers", "provider_type")
