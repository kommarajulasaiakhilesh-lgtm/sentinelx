from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    agent_id: Mapped[int] = mapped_column(
        ForeignKey("agents.id"),
        nullable=False,
        index=True
    )

    policy_id: Mapped[int | None] = mapped_column(
        ForeignKey("policies.id"),
        nullable=True,
        index=True
    )

    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    action: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    decision: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    event_metadata: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    agent = relationship(
        "Agent",
        back_populates="security_events"
    )

    policy = relationship(
        "Policy",
        back_populates="security_events"
    )