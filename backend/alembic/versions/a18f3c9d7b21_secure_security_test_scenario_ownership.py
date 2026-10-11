
"""Secure security test scenario ownership and relationships."""

from alembic import op
import sqlalchemy as sa


revision = "a18f3c9d7b21"
down_revision = "61959de99a91"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    # Validate existing data before changing the schema.
    invalid_scenario = bind.execute(
        sa.text(
            """
            SELECT s.id
            FROM security_test_scenarios AS s
            LEFT JOIN agents AS a ON a.id = s.agent_id
            LEFT JOIN users AS u ON u.id = a.owner_id
            WHERE s.agent_id IS NULL
               OR a.id IS NULL
               OR a.owner_id IS NULL
               OR u.id IS NULL
            LIMIT 1
            """
        )
    ).first()

    if invalid_scenario is not None:
        raise RuntimeError(
            "Migration stopped: security test scenario "
            f"{invalid_scenario[0]} has no valid agent owner. "
            "Repair the data before retrying."
        )

    orphaned_run = bind.execute(
        sa.text(
            """
            SELECT r.id
            FROM security_test_runs AS r
            LEFT JOIN security_test_scenarios AS s
                ON s.id = r.scenario_id
            WHERE s.id IS NULL
            LIMIT 1
            """
        )
    ).first()

    if orphaned_run is not None:
        raise RuntimeError(
            "Migration stopped: security test run "
            f"{orphaned_run[0]} references a missing scenario. "
            "Repair the data before retrying."
        )

    # Add ownership as nullable temporarily so existing rows can
    # be backfilled without losing any scenarios.
    op.add_column(
        "security_test_scenarios",
        sa.Column("owner_id", sa.Integer(), nullable=True),
    )

    op.execute(
        sa.text(
            """
            UPDATE security_test_scenarios AS s
            SET owner_id = a.owner_id
            FROM agents AS a
            WHERE s.agent_id = a.id
            """
        )
    )

    op.alter_column(
        "security_test_scenarios",
        "owner_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.alter_column(
        "security_test_scenarios",
        "agent_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.create_index(
        "ix_security_test_scenarios_owner_id",
        "security_test_scenarios",
        ["owner_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_security_test_scenarios_owner_id_users",
        "security_test_scenarios",
        "users",
        ["owner_id"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_security_test_scenarios_agent_id_agents",
        "security_test_scenarios",
        "agents",
        ["agent_id"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_security_test_runs_scenario_id_scenarios",
        "security_test_runs",
        "security_test_scenarios",
        ["scenario_id"],
        ["id"],
    )


def downgrade() -> None:
    # Remove only the schema additions made by this migration.
    # Existing scenarios and runs are retained.
    op.drop_constraint(
        "fk_security_test_runs_scenario_id_scenarios",
        "security_test_runs",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_security_test_scenarios_agent_id_agents",
        "security_test_scenarios",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_security_test_scenarios_owner_id_users",
        "security_test_scenarios",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_security_test_scenarios_owner_id",
        table_name="security_test_scenarios",
    )

    op.alter_column(
        "security_test_scenarios",
        "agent_id",
        existing_type=sa.Integer(),
        nullable=True,
    )

    op.drop_column("security_test_scenarios", "owner_id")
