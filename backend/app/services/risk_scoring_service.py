def calculate_risk_score(
    blocked_events: int,
    suspicious_events: int,
    policy_violations: int
):
    score = (
        blocked_events * 10
        + suspicious_events * 20
        + policy_violations * 15
    )

    score = min(score, 100)

    if score >= 80:
        risk_level = "CRITICAL"
    elif score >= 50:
        risk_level = "HIGH"
    elif score >= 20:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return score, risk_level