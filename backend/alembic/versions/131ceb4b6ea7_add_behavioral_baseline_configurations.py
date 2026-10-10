from alembic import op
import sqlalchemy as sa


revision = "131ceb4b6ea7"
down_revision = "5845815a4eea"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "behavioral_baseline_configurations",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),
        sa.Column(
            "owner_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column(
            "name",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "baseline_window_seconds",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "observation_window_seconds",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "minimum_observations",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "deviation_threshold_percent",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_behavioral_baseline_configurations_id",
        "behavioral_baseline_configurations",
        ["id"],
    )

    op.create_index(
        "ix_behavioral_baseline_configurations_owner_id",
        "behavioral_baseline_configurations",
        ["owner_id"],
    )

    op.create_index(
        "ix_behavioral_baseline_configurations_enabled",
        "behavioral_baseline_configurations",
        ["enabled"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_behavioral_baseline_configurations_enabled",
        table_name="behavioral_baseline_configurations",
    )

    op.drop_index(
        "ix_behavioral_baseline_configurations_owner_id",
        table_name="behavioral_baseline_configurations",
    )

    op.drop_index(
        "ix_behavioral_baseline_configurations_id",
        table_name="behavioral_baseline_configurations",
    )

    op.drop_table("behavioral_baseline_configurations")