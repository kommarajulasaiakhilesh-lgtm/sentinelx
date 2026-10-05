from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    agent_id: Mapped[int] = mapped_column(
        ForeignKey("agents.id"),
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="OPEN",
        index=True
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
        back_populates="incidents"
    )

    incident_alerts = relationship(
        "IncidentAlert",
        back_populates="incident",
        cascade="all, delete-orphan"
    )

    timeline_entries = relationship(
        "IncidentTimelineEntry",
        back_populates="incident",
        cascade="all, delete-orphan"
    )

    response_actions = relationship(
        "IncidentResponseAction",
        back_populates="incident",
        cascade="all, delete-orphan"
    )
