from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class RiskScoringConfiguration(Base):
    __tablename__ = "risk_scoring_configurations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )

    blocked_event_weight: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    suspicious_event_weight: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    policy_violation_weight: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    score_cap: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    low_max: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    medium_max: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    high_max: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    critical_max: Mapped[int] = mapped_column(
        Integer,
        nullable=False
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