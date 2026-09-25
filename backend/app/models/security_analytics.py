from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class SecurityAnalytics(Base):
    __tablename__ = "security_analytics"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    agent_id: Mapped[int] = mapped_column(
        ForeignKey("agents.id"),
        nullable=False,
        index=True
    )

    period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    total_events: Mapped[int] = mapped_column(
        nullable=False,
        default=0
    )

    allowed_events: Mapped[int] = mapped_column(
        nullable=False,
        default=0
    )

    blocked_events: Mapped[int] = mapped_column(
        nullable=False,
        default=0
    )

    suspicious_events: Mapped[int] = mapped_column(
        nullable=False,
        default=0
    )

    policy_violations: Mapped[int] = mapped_column(
        nullable=False,
        default=0
    )

    risk_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    risk_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="LOW"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    agent = relationship(
        "Agent",
        back_populates="security_analytics"
    )
