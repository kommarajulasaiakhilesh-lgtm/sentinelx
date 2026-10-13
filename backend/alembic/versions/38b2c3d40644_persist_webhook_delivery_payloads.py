
"""Persist webhook delivery payloads."""

from alembic import op
import sqlalchemy as sa


revision = "38b2c3d40644"
down_revision = "a18f3c9d7b21"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "webhook_deliveries",
        sa.Column(
            "payload",
            sa.JSON(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "webhook_deliveries",
        "payload",
    )
