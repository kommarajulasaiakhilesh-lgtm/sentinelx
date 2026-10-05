from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("webhook_endpoints.id"),
        nullable=False,
        index=True
    )

    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )

    attempt_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    response_status: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    response_body: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    endpoint = relationship(
        "WebhookEndpoint",
        back_populates="deliveries"
    )
