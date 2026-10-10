from sqlalchemy.orm import Session
from app.models.user import User
from app.models.behavioral_baseline_configuration import (
    BehavioralBaselineConfiguration,
)


def get_behavioral_baseline_configuration(
    db: Session,
    owner_id: int | None = None,
) -> BehavioralBaselineConfiguration | None:
    """
    Resolve the effective behavioral-baseline configuration.

    Resolution order:
    1. Enabled owner-specific configuration
    2. Enabled global configuration
    3. None if no configuration exists
    """

    if owner_id is not None:
        owner_configuration = (
            db.query(BehavioralBaselineConfiguration)
            .filter(
                BehavioralBaselineConfiguration.owner_id == owner_id,
                BehavioralBaselineConfiguration.enabled.is_(True),
            )
            .order_by(
                BehavioralBaselineConfiguration.id.desc()
            )
            .first()
        )

        if owner_configuration is not None:
            return owner_configuration

    global_configuration = (
        db.query(BehavioralBaselineConfiguration)
        .filter(
            BehavioralBaselineConfiguration.owner_id.is_(None),
            BehavioralBaselineConfiguration.enabled.is_(True),
        )
        .order_by(
            BehavioralBaselineConfiguration.id.desc()
        )
        .first()
    )

    return global_configuration