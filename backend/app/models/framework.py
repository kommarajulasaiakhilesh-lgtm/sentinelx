from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Framework(Base):
    __tablename__ = "frameworks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    version = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    controls = relationship(
        "FrameworkControl",
        back_populates="framework",
        cascade="all, delete-orphan",
    )


class FrameworkControl(Base):
    __tablename__ = "framework_controls"

    id = Column(Integer, primary_key=True, index=True)
    framework_id = Column(
        Integer,
        ForeignKey("frameworks.id"),
        nullable=False,
    )

    control_id = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    function = Column(String(50), nullable=True)
    category = Column(String(100), nullable=True)
    reference = Column(String(255), nullable=True)

    enabled = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    framework = relationship(
        "Framework",
        back_populates="controls",
    )