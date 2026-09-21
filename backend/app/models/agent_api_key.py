from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class AgentAPIKey(Base):
    __tablename__ = "agent_api_keys"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    agent_id: Mapped[int] = mapped_column(
        ForeignKey("agents.id"),
        nullable=False,
        index=True
    )

    key_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False
    )

    agent = relationship(
        "Agent",
        back_populates="api_keys"
    )