from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    sentinelx_control_id = Column(
        Integer,
        ForeignKey("sentinelx_controls.id"),
        nullable=False,
    )

    evidence_type = Column(
        String(100),
        nullable=False,
    )

    source = Column(
        String(255),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    reference = Column(
        String(255),
        nullable=True,
    )

    evidence_status = Column(
        String(50),
        nullable=False,
        default="AVAILABLE",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    sentinelx_control = relationship(
        "SentinelXControl",
    )