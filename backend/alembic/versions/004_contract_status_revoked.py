"""contract status simplify: remove in_progress/completed, rename cancelled to revoked

Revision ID: 004_contract_status_revoked
Revises: 003_contract_travel_notice
Create Date: 2026-04-27

Changes:
- contracts.status: rename 'cancelled' -> 'revoked'
- contracts.status: migrate 'in_progress'/'completed' -> 'signed'
"""
from alembic import op

revision = '004_contract_status_revoked'
down_revision = '003_contract_travel_notice'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE contracts SET status = 'revoked' WHERE status = 'cancelled'")
    op.execute("UPDATE contracts SET status = 'signed' WHERE status IN ('in_progress', 'completed')")


def downgrade() -> None:
    op.execute("UPDATE contracts SET status = 'cancelled' WHERE status = 'revoked'")
