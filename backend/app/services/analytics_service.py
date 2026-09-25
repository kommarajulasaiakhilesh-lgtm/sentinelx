from datetime import datetime

from sqlalchemy.orm import Session

from app.models.security_event import SecurityEvent
from app.models.security_analytics import SecurityAnalytics
from app.services.risk_scoring_service import calculate_risk_score


def generate_agent_analytics(
    db: Session,
    agent_id: int,
    period_start: datetime,
    period_end: datetime
):
    events = (
        db.query(SecurityEvent)
        .filter(
            SecurityEvent.agent_id == agent_id,
            SecurityEvent.created_at >= period_start,
            SecurityEvent.created_at <= period_end
        )
        .all()
    )

    total_events = len(events)

    allowed_events = sum(
        1 for event in events
        if event.action == "ALLOW"
    )

    blocked_events = sum(
        1 for event in events
        if event.action == "BLOCK"
    )

    suspicious_events = sum(
        1 for event in events
        if event.event_type == "SUSPICIOUS"
    )

    policy_violations = sum(
        1 for event in events
        if event.decision == "BLOCK"
    )

    risk_score, risk_level = calculate_risk_score(
        blocked_events,
        suspicious_events,
        policy_violations
    )

    analytics = (
        db.query(SecurityAnalytics)
        .filter(
            SecurityAnalytics.agent_id == agent_id,
            SecurityAnalytics.period_start == period_start,
            SecurityAnalytics.period_end == period_end
        )
        .first()
    )

    if analytics:
        analytics.total_events = total_events
        analytics.allowed_events = allowed_events
        analytics.blocked_events = blocked_events
        analytics.suspicious_events = suspicious_events
        analytics.policy_violations = policy_violations
        analytics.risk_score = risk_score
        analytics.risk_level = risk_level

    else:
        analytics = SecurityAnalytics(
            agent_id=agent_id,
            period_start=period_start,
            period_end=period_end,
            total_events=total_events,
            allowed_events=allowed_events,
            blocked_events=blocked_events,
            suspicious_events=suspicious_events,
            policy_violations=policy_violations,
            risk_score=risk_score,
            risk_level=risk_level
        )

        db.add(analytics)

    db.commit()
    db.refresh(analytics)

    return analytics
