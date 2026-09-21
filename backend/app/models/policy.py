from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    agent_id: Mapped[int] = mapped_column(
        ForeignKey("agents.id"),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    policy_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
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

    agent = relationship(
        "Agent",
        back_populates="policies"
    )