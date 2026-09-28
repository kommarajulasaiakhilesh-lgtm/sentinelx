from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class ControlMapping(Base):
    __tablename__ = "control_mappings"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    framework_control_id = Column(
        Integer,
        ForeignKey("framework_controls.id"),
        nullable=False,
    )

    sentinelx_control_id = Column(
        Integer,
        ForeignKey("sentinelx_controls.id"),
        nullable=False,
    )

    mapping_status = Column(
        String(50),
        nullable=False,
        default="PARTIALLY_IMPLEMENTED",
    )

    rationale = Column(
        Text,
        nullable=True,
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

    framework_control = relationship(
        "FrameworkControl",
    )

    sentinelx_control = relationship(
        "SentinelXControl",
    )