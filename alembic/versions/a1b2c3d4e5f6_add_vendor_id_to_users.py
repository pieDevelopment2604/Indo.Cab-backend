"""Add vendor_id to users table for driver-vendor association

Revision ID: a1b2c3d4e5f6
Revises: 471bb4364f1b
Create Date: 2026-08-07

Adds a proper `vendor_id` foreign key column to the `users` table.
Previously, the vendor-driver relationship was incorrectly stored in
`created_by` (an audit field). This migration introduces a dedicated
`vendor_id` column so the relationship is semantically correct and queryable.

Only rows where `role = 'DRIVER'` will have a non-null `vendor_id`.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '471bb4364f1b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add vendor_id column to users table
    op.add_column(
        'users',
        sa.Column('vendor_id', sa.Integer(), nullable=True)
    )

    # Add foreign key constraint
    op.create_foreign_key(
        'fk_users_vendor_id_users',
        'users', 'users',
        ['vendor_id'], ['user_id'],
        ondelete='SET NULL'
    )

    # Index for efficient vendor -> driver lookups
    op.create_index(
        'ix_users_vendor_id',
        'users',
        ['vendor_id'],
        unique=False,
        postgresql_where=sa.text("is_deleted = FALSE")
    )


def downgrade() -> None:
    op.drop_index('ix_users_vendor_id', table_name='users')
    op.drop_constraint('fk_users_vendor_id_users', 'users', type_='foreignkey')
    op.drop_column('users', 'vendor_id')
