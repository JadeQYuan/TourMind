"""rename password_hash to password

Revision ID: a1b2c3d4e5f6
Revises: df342ea35b49
Create Date: 2026-05-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'df342ea35b49'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('users', 'password_hash',
                    new_column_name='password',
                    existing_type=sa.String(length=255),
                    existing_nullable=False)
    op.alter_column('users', 'password',
                    type_=sa.String(length=64),
                    existing_nullable=False)


def downgrade() -> None:
    op.alter_column('users', 'password',
                    new_column_name='password_hash',
                    existing_type=sa.String(length=64),
                    existing_nullable=False)
    op.alter_column('users', 'password_hash',
                    type_=sa.String(length=255),
                    existing_nullable=False)
