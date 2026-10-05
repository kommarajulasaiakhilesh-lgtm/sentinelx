from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class IncidentAlert(Base):
    __tablename__ = "incident_alerts"

    __table_args__ = (
        UniqueConstraint(
            "incident_id",
            "alert_id",
            name="uq_incident_alert",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    incident_id: Mapped[int] = mapped_column(
        ForeignKey("incidents.id"),
        nullable=False,
        index=True,
    )

    alert_id: Mapped[int] = mapped_column(
        ForeignKey("security_alerts.id"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    incident = relationship(
        "Incident",
        back_populates="incident_alerts",
    )

    alert = relationship(
        "SecurityAlert",
    )