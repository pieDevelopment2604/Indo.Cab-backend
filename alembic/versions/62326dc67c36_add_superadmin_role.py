"""Add SUPERADMIN role

Revision ID: 62326dc67c36
Revises: 7d93aa68679e
Create Date: 2026-08-11 11:49:33.882051

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '62326dc67c36'
down_revision: Union[str, None] = '7d93aa68679e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Cannot be run inside a transaction in older Postgres, but Postgres 12+ supports it.
    # We use IF NOT EXISTS just to be safe if it was already created manually.
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'SUPERADMIN'")


def downgrade() -> None:
    pass
