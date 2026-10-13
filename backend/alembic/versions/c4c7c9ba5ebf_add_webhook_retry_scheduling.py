
"""Add webhook retry scheduling."""

from alembic import op
import sqlalchemy as sa


revision = "c4c7c9ba5ebf"
down_revision = "38b2c3d40644"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "webhook_deliveries",
        sa.Column(
            "next_attempt_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "webhook_deliveries",
        sa.Column(
            "last_attempt_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "webhook_deliveries",
        sa.Column(
            "locked_until",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_webhook_deliveries_next_attempt_at",
        "webhook_deliveries",
        ["next_attempt_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_webhook_deliveries_next_attempt_at",
        table_name="webhook_deliveries",
    )
    op.drop_column("webhook_deliveries", "locked_until")
    op.drop_column("webhook_deliveries", "last_attempt_at")
    op.drop_column("webhook_deliveries", "next_attempt_at")
