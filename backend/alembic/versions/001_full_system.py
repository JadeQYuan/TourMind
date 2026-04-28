"""Full system schema migration — TourMind 001-full-system-spec

Revision ID: 001_full_system
Revises: 
Create Date: 2026-04-22

Covers:
- D1: Add cancellation_policy, travel_notice, important_tips to products
- D3: Rename user role values (sales/finance/readonly → assistant)
- D4: Realign accounts — add description, user_id; drop bank_name, account_last4
- D7: Create customer_orders table
- D9: Create audit_logs table
- D11: Add customer_order_id FK to itineraries (UNIQUE) and contracts; update itinerary status values
       Add customer_order_id FK to bills
- Indexes: ix_customer_orders_travel_date, ix_bills_bill_date, ix_audit_logs_created_at, ix_audit_logs_user_id
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_full_system'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── D1: Add new text columns to products ─────────────────────────────
    op.add_column('products', sa.Column('cancellation_policy', sa.Text(), nullable=True))
    op.add_column('products', sa.Column('travel_notice', sa.Text(), nullable=True))
    op.add_column('products', sa.Column('important_tips', sa.Text(), nullable=True))
    # Make product_type and origin nullable (they were NOT NULL before)
    op.alter_column('products', 'product_type', existing_type=sa.String(30), nullable=True)
    op.alter_column('products', 'origin', existing_type=sa.String(100), nullable=True)

    # ── D3: Rename user role values ───────────────────────────────────────
    op.execute("""
        UPDATE users
        SET role = 'assistant'
        WHERE role IN ('sales', 'finance', 'readonly')
    """)
    # 'admin' stays 'admin'; 'system_admin' is new (created by application seed)
    op.alter_column('users', 'role',
                    existing_type=sa.String(20),
                    server_default='assistant',
                    existing_nullable=False)

    # ── D4: Realign accounts ──────────────────────────────────────────────
    op.add_column('accounts', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('accounts', sa.Column(
        'user_id',
        sa.Integer(),
        sa.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
    ))
    op.drop_column('accounts', 'bank_name')
    op.drop_column('accounts', 'account_last4')

    # ── D7: Create customer_orders table ──────────────────────────────────
    op.create_table(
        'customer_orders',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('order_no', sa.String(20), unique=True, nullable=False),
        sa.Column('product_id', sa.Integer(),
                  sa.ForeignKey('products.id', ondelete='SET NULL'), nullable=True),
        sa.Column('product_name', sa.String(200), nullable=False),
        sa.Column('customer_name', sa.String(100), nullable=False),
        sa.Column('customer_phone', sa.String(20), nullable=True),
        sa.Column('travel_date', sa.Date(), nullable=True),
        sa.Column('days', sa.SmallInteger(), nullable=True),
        sa.Column('people_count', sa.SmallInteger(), nullable=False, server_default='1'),
        sa.Column('price', sa.Numeric(12, 2), nullable=True),
        sa.Column('deposit', sa.Numeric(12, 2), nullable=True),
        sa.Column('supplier_id', sa.Integer(),
                  sa.ForeignKey('suppliers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('supplier_name', sa.String(200), nullable=True),
        sa.Column('cost', sa.Numeric(12, 2), nullable=True),
        sa.Column('profit', sa.Numeric(12, 2), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending_deposit'),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(),
                  sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_customer_orders_travel_date', 'customer_orders', ['travel_date'])

    # ── D9: Create audit_logs table ───────────────────────────────────────
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('user_id', sa.Integer(),
                  sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('user_name', sa.String(100), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=True),
        sa.Column('resource_id', sa.String(50), nullable=True),
        sa.Column('detail', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])

    # ── D11: Add customer_order_id to itineraries (UNIQUE) ────────────────
    op.add_column('itineraries', sa.Column(
        'customer_order_id',
        sa.Integer(),
        sa.ForeignKey('customer_orders.id', ondelete='SET NULL'),
        nullable=True,
    ))
    op.create_unique_constraint(
        'uq_itineraries_customer_order_id', 'itineraries', ['customer_order_id']
    )
    # Add share_token column to itineraries
    op.add_column('itineraries', sa.Column(
        'share_token', sa.String(64), unique=True, nullable=True
    ))
    # Update itinerary status values
    op.execute("""
        UPDATE itineraries
        SET status = CASE
            WHEN status IN ('draft', 'confirmed') THEN 'not_started'
            WHEN status = 'in_progress' THEN 'in_progress'
            WHEN status IN ('completed', 'cancelled') THEN 'completed'
            ELSE 'not_started'
        END
    """)

    # ── Add customer_order_id FK to contracts ─────────────────────────────
    op.add_column('contracts', sa.Column(
        'customer_order_id',
        sa.Integer(),
        sa.ForeignKey('customer_orders.id', ondelete='SET NULL'),
        nullable=True,
    ))

    # ── Add customer_order_id FK to bills ─────────────────────────────────
    op.add_column('bills', sa.Column(
        'customer_order_id',
        sa.Integer(),
        sa.ForeignKey('customer_orders.id', ondelete='SET NULL'),
        nullable=True,
    ))
    op.create_index('ix_bills_bill_date', 'bills', ['bill_date'])


def downgrade() -> None:
    # bills
    op.drop_index('ix_bills_bill_date', table_name='bills')
    op.drop_column('bills', 'customer_order_id')

    # contracts
    op.drop_column('contracts', 'customer_order_id')

    # itineraries
    op.drop_constraint('uq_itineraries_customer_order_id', 'itineraries', type_='unique')
    op.drop_column('itineraries', 'customer_order_id')
    op.drop_column('itineraries', 'share_token')
    op.execute("""
        UPDATE itineraries SET status = 'draft' WHERE status IN ('not_started', 'in_progress', 'completed')
    """)

    # audit_logs
    op.drop_index('ix_audit_logs_user_id', table_name='audit_logs')
    op.drop_index('ix_audit_logs_created_at', table_name='audit_logs')
    op.drop_table('audit_logs')

    # customer_orders
    op.drop_index('ix_customer_orders_travel_date', table_name='customer_orders')
    op.drop_table('customer_orders')

    # accounts
    op.add_column('accounts', sa.Column('bank_name', sa.String(100), nullable=True))
    op.add_column('accounts', sa.Column('account_last4', sa.String(4), nullable=True))
    op.drop_column('accounts', 'user_id')
    op.drop_column('accounts', 'description')

    # users
    op.execute("""
        UPDATE users SET role = 'sales' WHERE role = 'assistant'
    """)

    # products
    op.alter_column('products', 'product_type', existing_type=sa.String(30), nullable=False)
    op.alter_column('products', 'origin', existing_type=sa.String(100), nullable=False)
    op.drop_column('products', 'important_tips')
    op.drop_column('products', 'travel_notice')
    op.drop_column('products', 'cancellation_policy')
