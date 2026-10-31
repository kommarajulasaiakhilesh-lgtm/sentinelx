from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class AuditLog(Base):
    """Append-only record of security-relevant actions.

    Entries are written by the application whenever a governed action occurs
    (agent lifecycle, policy changes, authentication). They are never updated
    or deleted through the API, providing a governance evidence trail scoped
    to the acting operator.
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    actor_user_id: Mapped[int | None] = mapped_column(
        Integer,
        index=True,
        nullable=True,
    )

    actor_username: Mapped[str] = mapped_column(String(50), nullable=False)

    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    resource_type: Mapped[str] = mapped_column(String(40), nullable=False)

    resource_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    summary: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
