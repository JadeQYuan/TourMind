"""itinerary travelers column: JSONB → Text

Revision ID: 002_itinerary_travelers_string
Revises: 001_full_system
Create Date: 2026-04-27

Changes:
- itineraries.travelers: JSONB → Text
  Existing JSONB array data (list of {name, id_no}) is migrated by
  extracting the 'name' field from each element and joining with ', '.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '002_itinerary_travelers_string'
down_revision = '001_full_system'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add a temporary text column
    op.add_column('itineraries', sa.Column('travelers_text', sa.Text(), nullable=True))

    # Migrate JSONB array → comma-separated names string
    op.execute("""
        UPDATE itineraries
        SET travelers_text = (
            SELECT string_agg(elem->>'name', ', ')
            FROM jsonb_array_elements(
                CASE
                    WHEN travelers IS NULL THEN '[]'::jsonb
                    WHEN jsonb_typeof(travelers) = 'array' THEN travelers
                    ELSE '[]'::jsonb
                END
            ) AS elem
            WHERE elem->>'name' IS NOT NULL AND elem->>'name' != ''
        )
        WHERE travelers IS NOT NULL
    """)

    # Drop old JSONB column
    op.drop_column('itineraries', 'travelers')

    # Rename new column to travelers
    op.alter_column('itineraries', 'travelers_text', new_column_name='travelers')


def downgrade() -> None:
    # Add back a JSONB column
    op.add_column('itineraries', sa.Column('travelers_jsonb', postgresql.JSONB(), nullable=True))

    # Convert text back to JSONB array of {name: ...} objects
    op.execute("""
        UPDATE itineraries
        SET travelers_jsonb = (
            SELECT jsonb_agg(jsonb_build_object('name', trim(name_val)))
            FROM regexp_split_to_table(travelers, ',\s*') AS name_val
            WHERE trim(name_val) != ''
        )
        WHERE travelers IS NOT NULL AND travelers != ''
    """)

    # Drop text column and rename JSONB column
    op.drop_column('itineraries', 'travelers')
    op.alter_column('itineraries', 'travelers_jsonb', new_column_name='travelers')
