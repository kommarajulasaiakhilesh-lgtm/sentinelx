from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from app.db.database import Base, DATABASE_URL

# Import all models so SQLAlchemy registers every table
from app.models.agent import Agent
from app.models.agent_api_key import AgentAPIKey
from app.models.policy import Policy
from app.models.security_event import SecurityEvent
from app.models.security_analytics import SecurityAnalytics
from app.models.security_alert import SecurityAlert
from app.models.tool import Tool
from app.models.user import User
from app.models.framework import Framework, FrameworkControl
from app.models.evidence import Evidence
from app.models.control_mapping import ControlMapping
from app.models.sentinelx_control import SentinelXControl
from app.models.security_test import SecurityTestScenario, SecurityTestRun
from app.models.incident import Incident
from app.models.incident_alert import IncidentAlert
from app.models.incident_timeline import IncidentTimelineEntry
from app.models.incident_response import IncidentResponseAction
from app.models.webhook_endpoint import WebhookEndpoint
from app.models.webhook_delivery import WebhookDelivery
from app.models.detection_rule import DetectionRule
from app.models.risk_scoring_configuration import RiskScoringConfiguration
from app.models.behavioral_baseline_configuration import (
    BehavioralBaselineConfiguration
)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use SentinelX's actual SQLAlchemy metadata.
target_metadata = Base.metadata

# Use the DATABASE_URL loaded by SentinelX's database module.
# This preserves the existing psycopg 3 configuration.
config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL.replace("%", "%%")
)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
