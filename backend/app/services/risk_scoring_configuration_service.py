from sqlalchemy.orm import Session

from app.models.risk_scoring_configuration import (
    RiskScoringConfiguration,
)


def get_risk_scoring_configuration(
    db: Session,
    owner_id: int | None = None,
) -> RiskScoringConfiguration | None:
    """
    Resolve the effective risk-scoring configuration.

    Resolution order:
    1. Enabled owner-specific configuration
    2. Enabled global configuration
    3. None if no configuration exists
    """

    if owner_id is not None:
        owner_configuration = (
            db.query(RiskScoringConfiguration)
            .filter(
                RiskScoringConfiguration.owner_id == owner_id,
                RiskScoringConfiguration.enabled.is_(True),
            )
            .order_by(
                RiskScoringConfiguration.id.desc()
            )
            .first()
        )

        if owner_configuration is not None:
            return owner_configuration

    global_configuration = (
        db.query(RiskScoringConfiguration)
        .filter(
            RiskScoringConfiguration.owner_id.is_(None),
            RiskScoringConfiguration.enabled.is_(True),
        )
        .order_by(
            RiskScoringConfiguration.id.desc()
        )
        .first()
    )

    return global_configuration
