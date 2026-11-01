"""Add entry_hash to audit_logs for tamper-evidence."""

from alembic import op
import sqlalchemy as sa


revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "audit_logs",
        sa.Column("entry_hash", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("audit_logs", "entry_hash")
