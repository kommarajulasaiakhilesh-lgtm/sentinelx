from datetime import datetime, timezone
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f273c8016875"
down_revision: Union[str, Sequence[str], None] = "81b0f76c34f8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    detection_rules = sa.table(
        "detection_rules",
        sa.column("owner_id", sa.Integer()),
        sa.column("name", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("enabled", sa.Boolean()),
        sa.column("severity", sa.String()),
        sa.column("alert_type", sa.String()),
        sa.column("title", sa.String()),
        sa.column("conditions", sa.Text()),
        sa.column("threshold", sa.Integer()),
        sa.column("window_seconds", sa.Integer()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )

    now = datetime.now(timezone.utc)

    op.bulk_insert(
        detection_rules,
        [
            {
                "owner_id": None,
                "name": "Tool Action Rate Limit",
                "description": (
                    "Detects when an agent exceeds the configured "
                    "runtime tool action rate limit."
                ),
                "enabled": True,
                "severity": "HIGH",
                "alert_type": "TOOL_RATE_LIMIT",
                "title": "Tool action rate limit exceeded",
                "conditions": (
                    '{"event_type":"TOOL_ACTION",'
                    '"decision":"BLOCK",'
                    '"reason":"Runtime tool action rate limit exceeded"}'
                ),
                "threshold": 1,
                "window_seconds": 0,
                "created_at": now,
                "updated_at": now,
            },
            {
                "owner_id": None,
                "name": "Repeated Blocked Tool Actions",
                "description": (
                    "Detects when an agent generates repeated blocked "
                    "tool actions within the configured runtime window."
                ),
                "enabled": True,
                "severity": "HIGH",
                "alert_type": "REPEATED_BLOCKED_ACTIONS",
                "title": "Repeated blocked tool actions detected",
                "conditions": (
                    '{"event_type":"TOOL_ACTION",'
                    '"decision":"BLOCK",'
                    '"reason":"Repeated blocked tool actions detected"}'
                ),
                "threshold": 1,
                "window_seconds": 0,
                "created_at": now,
                "updated_at": now,
            },
        ],
    )


def downgrade() -> None:
    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
            DELETE FROM detection_rules
            WHERE owner_id IS NULL
              AND alert_type IN (
                  'TOOL_RATE_LIMIT',
                  'REPEATED_BLOCKED_ACTIONS'
              )
            """
        )
    )