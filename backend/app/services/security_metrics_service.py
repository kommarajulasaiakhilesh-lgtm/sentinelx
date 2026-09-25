from sqlalchemy.orm import Session

from app.models.security_analytics import SecurityAnalytics


def calculate_security_metrics(
    db: Session,
    agent_id: int
):
    analytics = (
        db.query(SecurityAnalytics)
        .filter(
            SecurityAnalytics.agent_id == agent_id
        )
        .order_by(
            SecurityAnalytics.period_end.desc()
        )
        .first()
    )

    if not analytics:
        return None

    total_events = analytics.total_events

    if total_events > 0:
        block_rate = (
            analytics.blocked_events / total_events
        ) * 100

        violation_rate = (
            analytics.policy_violations / total_events
        ) * 100
    else:
        block_rate = 0
        violation_rate = 0

    return {
        "agent_id": agent_id,

        "period_start": analytics.period_start,
        "period_end": analytics.period_end,

        "total_events": total_events,
        "allowed_events": analytics.allowed_events,
        "blocked_events": analytics.blocked_events,
        "suspicious_events": analytics.suspicious_events,
        "policy_violations": analytics.policy_violations,

        "risk_score": analytics.risk_score,
        "risk_level": analytics.risk_level,

        "block_rate": round(block_rate, 2),
        "violation_rate": round(violation_rate, 2)
    }