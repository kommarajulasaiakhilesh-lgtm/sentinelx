"""seed default risk scoring configuration

Revision ID: 5845815a4eea
Revises: 62ca4acb55d8
Create Date: 2026-10-05
"""

from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "5845815a4eea"
down_revision = "62ca4acb55d8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    risk_scoring_configurations = sa.table(
        "risk_scoring_configurations",
        sa.column("owner_id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("enabled", sa.Boolean),
        sa.column("blocked_event_weight", sa.Integer),
        sa.column("suspicious_event_weight", sa.Integer),
        sa.column("policy_violation_weight", sa.Integer),
        sa.column("score_cap", sa.Integer),
        sa.column("low_max", sa.Integer),
        sa.column("medium_max", sa.Integer),
        sa.column("high_max", sa.Integer),
        sa.column("critical_max", sa.Integer),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )

    now = datetime.now(timezone.utc)

    op.bulk_insert(
        risk_scoring_configurations,
        [
            {
                "owner_id": None,
                "name": "Default Risk Scoring",
                "enabled": True,
                "blocked_event_weight": 10,
                "suspicious_event_weight": 20,
                "policy_violation_weight": 15,
                "score_cap": 100,
                "low_max": 19,
                "medium_max": 49,
                "high_max": 79,
                "critical_max": 100,
                "created_at": now,
                "updated_at": now,
            }
        ],
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            DELETE FROM risk_scoring_configurations
            WHERE owner_id IS NULL
              AND name = 'Default Risk Scoring'
            """
        )
    )