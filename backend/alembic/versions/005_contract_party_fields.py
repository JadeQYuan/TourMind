"""
Add party_a, party_a_phone, party_b, party_b_phone to contracts
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005_contract_party_fields'
down_revision = '004_contract_status_revoked'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('contracts', sa.Column('party_a', sa.String(length=100), nullable=True))
    op.add_column('contracts', sa.Column('party_a_phone', sa.String(length=20), nullable=True))
    op.add_column('contracts', sa.Column('party_b', sa.String(length=100), nullable=True))
    op.add_column('contracts', sa.Column('party_b_phone', sa.String(length=20), nullable=True))

def downgrade():
    op.drop_column('contracts', 'party_a')
    op.drop_column('contracts', 'party_a_phone')
    op.drop_column('contracts', 'party_b')
    op.drop_column('contracts', 'party_b_phone')
