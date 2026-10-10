from app.main import app  # noqa: F401

import pytest

from app.db.database import SessionLocal
from app.models.risk_scoring_configuration import (
    RiskScoringConfiguration,
)
from app.services.risk_scoring_service import calculate_risk_score


def test_default_configuration_scores_and_classifies_risk():
    db = SessionLocal()

    try:
        test_cases = [
            (0, 0, 0, 0, "LOW"),
            (2, 0, 0, 20, "MEDIUM"),
            (5, 0, 0, 50, "HIGH"),
            (8, 0, 0, 80, "CRITICAL"),
            (20, 0, 0, 100, "CRITICAL"),
        ]

        for blocked, suspicious, violations, expected_score, expected_level in test_cases:
            score, level = calculate_risk_score(
                db=db,
                owner_id=None,
                blocked_events=blocked,
                suspicious_events=suspicious,
                policy_violations=violations,
            )

            assert score == expected_score
            assert level == expected_level

    finally:
        db.close()


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("blocked_event_weight", -1, "weights cannot be negative"),
        ("suspicious_event_weight", -1, "weights cannot be negative"),
        ("policy_violation_weight", -1, "weights cannot be negative"),
        ("score_cap", 0, "score_cap must be positive"),
        ("low_max", 49, "Risk scoring thresholds"),
        ("critical_max", 99, "critical_max must equal score_cap"),
    ],
)
def test_invalid_configuration_is_rejected(field, value, message):
    db = SessionLocal()
    configuration = None

    try:
        configuration = RiskScoringConfiguration(
            owner_id=None,
            name=f"Invalid Scoring Test {field}",
            enabled=True,
            blocked_event_weight=10,
            suspicious_event_weight=20,
            policy_violation_weight=15,
            score_cap=100,
            low_max=19,
            medium_max=49,
            high_max=79,
            critical_max=100,
        )

        setattr(configuration, field, value)
        db.add(configuration)
        db.commit()

        with pytest.raises(ValueError, match=message):
            calculate_risk_score(
                db=db,
                owner_id=None,
                blocked_events=1,
                suspicious_events=0,
                policy_violations=0,
            )

    finally:
        if configuration is not None and configuration.id is not None:
            db.delete(configuration)
            db.commit()

        db.close()


@pytest.mark.parametrize(
    ("blocked", "suspicious", "violations"),
    [
        (-1, 0, 0),
        (0, -1, 0),
        (0, 0, -1),
    ],
)
def test_negative_event_counts_are_rejected(blocked, suspicious, violations):
    db = SessionLocal()

    try:
        with pytest.raises(ValueError, match="cannot be negative"):
            calculate_risk_score(
                db=db,
                owner_id=None,
                blocked_events=blocked,
                suspicious_events=suspicious,
                policy_violations=violations,
            )

    finally:
        db.close()
