from pydantic import BaseModel


class EnforcementRequest(BaseModel):
    agent_id: int
    input_text: str


class EnforcementResponse(BaseModel):
    agent_id: int
    decision: str
    reason: str
    policy_type: str | None = None