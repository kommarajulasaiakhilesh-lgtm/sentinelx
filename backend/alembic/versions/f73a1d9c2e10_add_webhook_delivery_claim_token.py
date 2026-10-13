"""Add ownership tokens to webhook delivery leases."""

from alembic import op
import sqlalchemy as sa


revision = "f73a1d9c2e10"
down_revision = "c4c7c9ba5ebf"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "webhook_deliveries",
        sa.Column("claim_token", sa.String(length=36), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("webhook_deliveries", "claim_token")
