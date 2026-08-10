"""Add clients table for corporate client management

Revision ID: 471bb4364f1b
Revises: 34fc78256868
Create Date: 2026-08-06 15:53:39.450649

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '471bb4364f1b'
down_revision: Union[str, None] = '34fc78256868'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('clients',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('company_name', sa.String(length=255), nullable=False),
    sa.Column('contact_person', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('mobile_number', sa.String(length=15), nullable=False),
    sa.Column('gst_number', sa.String(length=15), nullable=True),
    sa.Column('pan_number', sa.String(length=10), nullable=True),
    sa.Column('address', sa.Text(), nullable=True),
    sa.Column('operating_cities', sa.JSON(), nullable=True),
    sa.Column('discount_percentage', sa.Float(), nullable=False),
    sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', name='clientstatus'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('updated_by', sa.Integer(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.user_id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.user_id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_clients_company_name'), 'clients', ['company_name'], unique=False)
    op.create_index(op.f('ix_clients_email'), 'clients', ['email'], unique=True)
    op.create_index(op.f('ix_clients_id'), 'clients', ['id'], unique=False)
    op.create_index(op.f('ix_clients_mobile_number'), 'clients', ['mobile_number'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_clients_mobile_number'), table_name='clients')
    op.drop_index(op.f('ix_clients_id'), table_name='clients')
    op.drop_index(op.f('ix_clients_email'), table_name='clients')
    op.drop_index(op.f('ix_clients_company_name'), table_name='clients')
    op.drop_table('clients')
