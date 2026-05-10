"""add_orders_table

Revision ID: add_orders_table
Revises: init_core_tables
Create Date: 2026-05-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'add_orders_table'
down_revision: Union[str, None] = 'init_core_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_no', sa.String(length=20), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('customer_name', sa.String(length=100), nullable=False),
        sa.Column('customer_phone', sa.String(length=20), nullable=True),
        sa.Column('travel_date', sa.Date(), nullable=True),
        sa.Column('days', sa.SmallInteger(), nullable=True),
        sa.Column('people_count', sa.SmallInteger(), nullable=False),
        sa.Column('price', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('deposit', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('deposit_due_date', sa.Date(), nullable=True, comment='定金到账日期'),
        sa.Column('balance_amount', sa.Numeric(precision=12, scale=2), nullable=True, comment='尾款金额'),
        sa.Column('balance_due_date', sa.Date(), nullable=True, comment='尾款到账日期'),
        sa.Column('supplier_id', sa.Integer(), nullable=True),
        sa.Column('cost', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('profit', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_no'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    )


def downgrade() -> None:
    op.drop_table('orders')