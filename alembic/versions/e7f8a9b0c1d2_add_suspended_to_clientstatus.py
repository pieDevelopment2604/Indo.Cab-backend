"""Add SUSPENDED to clientstatus enum

Revision ID: e7f8a9b0c1d2
Revises: 6b552d29ad6f
Create Date: 2026-08-14 15:52:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7f8a9b0c1d2'
down_revision: Union[str, None] = '6b552d29ad6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE clientstatus ADD VALUE IF NOT EXISTS 'SUSPENDED'")


def downgrade() -> None:
    pass
