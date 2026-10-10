
from sqlalchemy.orm import Session

from app.services.risk_scoring_configuration_service import (
    get_risk_scoring_configuration,
)


def _validate_risk_scoring_configuration(configuration) -> None:
    """Reject invalid risk-scoring settings before calculating a score."""

    weights = {
        "blocked_event_weight": configuration.blocked_event_weight,
        "suspicious_event_weight": configuration.suspicious_event_weight,
        "policy_violation_weight": configuration.policy_violation_weight,
    }

    for name, value in weights.items():
        if value < 0:
            raise ValueError(
                f"Risk scoring configuration has invalid {name}: "
                "weights cannot be negative"
            )

    if configuration.score_cap <= 0:
        raise ValueError(
            "Risk scoring configuration score_cap must be positive"
        )

    low_max = configuration.low_max
    medium_max = configuration.medium_max
    high_max = configuration.high_max
    critical_max = configuration.critical_max
    score_cap = configuration.score_cap

    if not (
        0 <= low_max < medium_max < high_max
        < critical_max
    ):
        raise ValueError(
            "Risk scoring thresholds must satisfy "
            "0 <= low_max < medium_max < high_max < critical_max"
        )

    if critical_max != score_cap:
        raise ValueError(
            "Risk scoring configuration critical_max must equal score_cap"
        )


def calculate_risk_score(
    db: Session,
    owner_id: int | None,
    blocked_events: int,
    suspicious_events: int,
    policy_violations: int,
):
    configuration = get_risk_scoring_configuration(
        db=db,
        owner_id=owner_id,
    )

    if configuration is None:
        raise ValueError(
            "No enabled risk scoring configuration is available"
        )

    _validate_risk_scoring_configuration(configuration)

    event_counts = {
        "blocked_events": blocked_events,
        "suspicious_events": suspicious_events,
        "policy_violations": policy_violations,
    }

    for name, value in event_counts.items():
        if value < 0:
            raise ValueError(
                f"{name} cannot be negative"
            )

    score = (
        blocked_events * configuration.blocked_event_weight
        + suspicious_events * configuration.suspicious_event_weight
        + policy_violations * configuration.policy_violation_weight
    )

    score = min(score, configuration.score_cap)

    if score <= configuration.low_max:
        risk_level = "LOW"
    elif score <= configuration.medium_max:
        risk_level = "MEDIUM"
    elif score <= configuration.high_max:
        risk_level = "HIGH"
    elif score <= configuration.critical_max:
        risk_level = "CRITICAL"
    else:
        # Defensive guard: a valid configuration should make this unreachable.
        raise ValueError(
            "Calculated risk score exceeds all configured risk thresholds"
        )

    return score, risk_level
