"""create OrderEvent table

Revision ID: 0001
Revises:
Create Date: 2024-06-01 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "orderevent",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.String(), nullable=False),
        sa.Column("order_id", sa.String(), nullable=False),
        sa.Column("payload", sa.String(), nullable=False),
    )
    op.create_index("ix_orderevent_event_id", "orderevent", ["event_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_orderevent_event_id", table_name="orderevent")
    op.drop_table("orderevent")
