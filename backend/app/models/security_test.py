from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.db.database import Base


class SecurityTestScenario(Base):
    __tablename__ = "security_test_scenarios"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(150),
        nullable=False,
    )

    category = Column(
        String(50),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    attack_input = Column(
        Text,
        nullable=True,
    )

    agent_id = Column(
        Integer,
        nullable=True,
    )

    tool_name = Column(
        String(100),
        nullable=True,
    )

    action = Column(
        String(100),
        nullable=True,
    )

    resource = Column(
        String(255),
        nullable=True,
    )

    expected_decision = Column(
        String(50),
        nullable=False,
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


class SecurityTestRun(Base):
    __tablename__ = "security_test_runs"

    id = Column(Integer, primary_key=True, index=True)

    scenario_id = Column(
        Integer,
        nullable=False,
    )

    actual_decision = Column(
        String(50),
        nullable=True,
    )

    expected_decision = Column(
        String(50),
        nullable=False,
    )

    result = Column(
        String(20),
        nullable=False,
    )

    details = Column(
        Text,
        nullable=True,
    )

    executed_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )