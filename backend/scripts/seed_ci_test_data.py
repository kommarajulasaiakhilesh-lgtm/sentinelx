
"""Seed predictable records for a fresh, isolated CI test database."""

import app.main  # noqa: F401 — register all SQLAlchemy models

from sqlalchemy import text

from app.db.database import SessionLocal
from app.models.agent import Agent
from app.models.user import User


def seed_ci_test_data() -> None:
    db = SessionLocal()

    try:
        for user_id in range(1, 5):
            username = f"ci_user_{user_id}"
            email = f"ci_user_{user_id}@example.test"
            expected_role = "ADMIN" if user_id == 1 else "USER"

            user = db.get(User, user_id)

            if user is None:
                username_owner = (
                    db.query(User).filter(User.username == username).first()
                )
                email_owner = (
                    db.query(User).filter(User.email == email).first()
                )

                if username_owner or email_owner:
                    raise RuntimeError(
                        f"CI seed username/email already exists for user {user_id}"
                    )

                user = User(
                    id=user_id,
                    username=username,
                    email=email,
                    password_hash="ci-test-only-not-a-real-password-hash",
                    role=expected_role,
                    is_active=True,
                )
                db.add(user)
            elif (
                user.username != username
                or user.email != email
                or user.role != expected_role
                or not user.is_active
            ):
                raise RuntimeError(
                    f"Unexpected existing user at ID {user_id}; "
                    "refusing to modify existing data"
                )

        db.flush()

        agent = db.get(Agent, 1)

        if agent is None:
            agent = Agent(
                id=1,
                owner_id=4,
                name="CI Test Agent",
                description="Agent for automated integration tests",
                status="ACTIVE",
            )
            db.add(agent)
        elif agent.owner_id != 4:
            raise RuntimeError(
                "Unexpected existing agent at ID 1; "
                "refusing to modify existing data"
            )

        db.flush()

        # Explicit IDs must not leave PostgreSQL sequences behind.
        for table in ("users", "agents"):
            db.execute(
                text(
                    f"""
                    SELECT setval(
                        pg_get_serial_sequence('{table}', 'id'),
                        (SELECT MAX(id) FROM {table}),
                        true
                    )
                    """
                )
            )

        db.commit()
        print(
            "CI test data is ready: user 1 (ADMIN), "
            "users 2-4 (USER), and agent 1."
        )

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_ci_test_data()
