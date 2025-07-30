"""add document intelligence config type

Revision ID: 4443fbd4c9b
Revises: 1997c3ff664e
Create Date: 2025-01-25 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '4443fbd4c9b'
down_revision: Union[str, None] = '1997c3ff664e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add DOCUMENT_INTELLIGENCE to the configtype enum
    op.execute("ALTER TYPE configtype ADD VALUE 'DOCUMENT_INTELLIGENCE'")


def downgrade() -> None:
    # Note: PostgreSQL doesn't support removing enum values directly
    # You would need to recreate the enum type without the value
    # For now, we'll leave this as a no-op since removing enum values
    # is complex and rarely needed in practice
    pass