from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class IncidentResponseAction(Base):
    __tablename__ = "incident_response_actions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    incident_id: Mapped[int] = mapped_column(
        ForeignKey("incidents.id"),
        nullable=False,
        index=True
    )

    action_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    agent_id: Mapped[int] = mapped_column(
        ForeignKey("agents.id"),
        nullable=False,
        index=True
    )

    tool_id: Mapped[int | None] = mapped_column(
        ForeignKey("tools.id"),
        nullable=True,
        index=True
    )

    api_key_id: Mapped[int | None] = mapped_column(
        ForeignKey("agent_api_keys.id"),
        nullable=True,
        index=True
    )

    authorized_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    result: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    incident = relationship(
        "Incident",
        back_populates="response_actions"
    )

    agent = relationship(
        "Agent"
    )

    tool = relationship(
        "Tool"
    )

    api_key = relationship(
        "AgentAPIKey"
    )

    authorized_by_user = relationship(
        "User"
    )
