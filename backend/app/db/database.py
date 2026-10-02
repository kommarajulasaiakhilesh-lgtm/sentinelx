import os

from dotenv import load_dotenv

from sqlalchemy import create_engine

from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker
)


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")


if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured"
    )


# ============================================================
# DATABASE DRIVER CONFIGURATION
# ============================================================

# SentinelX uses psycopg 3.
# Convert a generic PostgreSQL URL to SQLAlchemy's
# explicit psycopg 3 dialect when necessary.

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1
    )


# ============================================================
# SQL LOGGING CONFIGURATION
# ============================================================

SQL_ECHO = os.getenv(
    "SQL_ECHO",
    "false"
).strip().lower() == "true"


# ============================================================
# DATABASE BASE
# ============================================================

class Base(DeclarativeBase):
    pass


# ============================================================
# DATABASE ENGINE
# ============================================================

engine = create_engine(
    DATABASE_URL,
    echo=SQL_ECHO
)


# ============================================================
# DATABASE SESSION
# ============================================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# ============================================================
# DATABASE DEPENDENCY
# ============================================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()