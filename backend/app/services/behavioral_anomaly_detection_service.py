
from datetime import datetime

from sqlalchemy.orm import Session

from app.services.behavioral_baseline_service import (
    calculate_behavioral_baseline,
)


def _compare_metric(
    metric_name: str,
    baseline_rate: float,
    observed_rate: float,
    threshold_percent: int,
) -> dict:
    """Compare an observed metric against its historical baseline."""

    if baseline_rate == 0:
        if observed_rate == 0:
            deviation_percent = 0.0
        else:
            # A transition from zero to nonzero activity represents
            # a new activity pattern, rather than a finite percentage.
            deviation_percent = None
    else:
        deviation_percent = (
            (observed_rate - baseline_rate)
            / baseline_rate
        ) * 100

    is_anomaly = (
        observed_rate > baseline_rate
        and (
            baseline_rate == 0
            or deviation_percent > threshold_percent
        )
    )

    return {
        "metric": metric_name,
        "baseline_rate": baseline_rate,
        "observed_rate": observed_rate,
        "deviation_percent": deviation_percent,
        "threshold_percent": threshold_percent,
        "is_anomaly": is_anomaly,
        "reason": (
            f"{metric_name} exceeded its configured behavioral threshold."
            if is_anomaly
            else None
        ),
    }


def detect_behavioral_anomalies(
    db: Session,
    agent_id: int,
    owner_id: int | None = None,
    reference_time: datetime | None = None,
) -> dict:
    """
    Detect explainable increases in an agent's behavioral activity.

    All time windows, minimum observation requirements, and deviation
    thresholds come from the effective database configuration.
    """

    baseline_result = calculate_behavioral_baseline(
        db=db,
        agent_id=agent_id,
        owner_id=owner_id,
        reference_time=reference_time,
    )

    baseline = baseline_result["baseline"]
    observation = baseline_result["observation"]

    metrics = [
        (
            "activity_rate",
            baseline["activity_rate"],
            observation["activity_rate"],
        ),
        (
            "tool_action_rate",
            baseline["tool_action_rate"],
            observation["tool_action_rate"],
        ),
        (
            "blocked_event_rate",
            baseline["blocked_event_rate"],
            observation["blocked_event_rate"],
        ),
    ]

    comparisons = [
        _compare_metric(
            metric_name=metric_name,
            baseline_rate=baseline_rate,
            observed_rate=observed_rate,
            threshold_percent=baseline_result[
                "deviation_threshold_percent"
            ],
        )
        for metric_name, baseline_rate, observed_rate in metrics
    ]

    if not baseline_result["sufficient_observations"]:
        for comparison in comparisons:
            comparison["is_anomaly"] = False
            comparison["reason"] = None

    anomalies = [
        comparison
        for comparison in comparisons
        if comparison["is_anomaly"]
    ]

    return {
        "agent_id": agent_id,
        "configuration_id": baseline_result["configuration_id"],
        "configuration_name": baseline_result["configuration_name"],
        "sufficient_observations": baseline_result[
            "sufficient_observations"
        ],
        "minimum_observations": baseline_result["minimum_observations"],
        "deviation_threshold_percent": baseline_result[
            "deviation_threshold_percent"
        ],
        "baseline_window": {
            "start_time": baseline["start_time"],
            "end_time": baseline["end_time"],
        },
        "observation_window": {
            "start_time": observation["start_time"],
            "end_time": observation["end_time"],
        },
        "comparisons": comparisons,
        "anomalies": anomalies,
        "anomaly_detected": bool(anomalies),
    }
