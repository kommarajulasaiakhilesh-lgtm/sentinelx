from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.db.database import Base


class SentinelXControl(Base):
    __tablename__ = "sentinelx_controls"

    id = Column(Integer, primary_key=True, index=True)

    control_id = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    name = Column(
        String(150),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    category = Column(
        String(100),
        nullable=True,
    )

    implementation_status = Column(
        String(50),
        nullable=False,
        default="IMPLEMENTED",
    )

    enabled = Column(
        Boolean,
        nullable=False,
        default=True,
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