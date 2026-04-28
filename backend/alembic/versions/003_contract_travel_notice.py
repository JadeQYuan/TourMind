"""contract travel_notice column

Revision ID: 003_contract_travel_notice
Revises: 002_itinerary_travelers_string
Create Date: 2026-04-27

Changes:
- contracts.travel_notice: new nullable Text column (出行提示)
"""
from alembic import op
import sqlalchemy as sa

revision = '003_contract_travel_notice'
down_revision = '002_itinerary_travelers_string'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('contracts', sa.Column('travel_notice', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('contracts', 'travel_notice')
