from datetime import datetime

from pydantic import BaseModel


class SecurityMetricsResponse(BaseModel):
    agent_id: int

    period_start: datetime
    period_end: datetime

    total_events: int
    allowed_events: int
    blocked_events: int
    suspicious_events: int
    policy_violations: int

    risk_score: int
    risk_level: str

    block_rate: float
    violation_rate: float