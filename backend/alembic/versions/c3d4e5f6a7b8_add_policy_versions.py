"""Add policy_versions history table."""

from alembic import op
import sqlalchemy as sa


revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "policy_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("policy_id", sa.Integer(), sa.ForeignKey("policies.id"), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("policy_type", sa.String(length=50), nullable=False),
        sa.Column("action", sa.String(length=20), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("condition", sa.Text(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("change_note", sa.String(length=255), nullable=False),
        sa.Column("changed_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_policy_versions_id", "policy_versions", ["id"])
    op.create_index("ix_policy_versions_policy_id", "policy_versions", ["policy_id"])


def downgrade() -> None:
    op.drop_index("ix_policy_versions_policy_id", table_name="policy_versions")
    op.drop_index("ix_policy_versions_id", table_name="policy_versions")
    op.drop_table("policy_versions")
