
"""Add unique constraint for security event alerts."""

from typing import Sequence, Union

from alembic import op

# Revision identifiers, used by Alembic.
revision: str = "61959de99a91"
down_revision: Union[str, Sequence[str], None] = "131ceb4b6ea7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Prevent duplicate alert types for the same security event."""
    op.create_unique_constraint(
        "uq_security_alerts_event_alert_type",
        "security_alerts",
        ["security_event_id", "alert_type"],
    )


def downgrade() -> None:
    """Remove the event/alert-type uniqueness constraint."""
    op.drop_constraint(
        "uq_security_alerts_event_alert_type",
        "security_alerts",
        type_="unique",
    )
