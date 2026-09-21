from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.policy import Policy


def evaluate_policy(
    agent: Agent,
    input_text: str,
    db: Session
) -> dict:

    policies = (
        db.query(Policy)
        .filter(
            Policy.agent_id == agent.id,
            Policy.enabled == True
        )
        .all()
    )

    for policy in policies:

        if policy.policy_type == "PROMPT_INJECTION":

            suspicious_patterns = [
                "ignore previous instructions",
                "ignore all previous instructions",
                "reveal system prompt",
                "show system prompt",
                "disregard previous instructions",
                "bypass your instructions"
            ]

            normalized_input = input_text.lower()

            for pattern in suspicious_patterns:

                if pattern in normalized_input:
                    return {
                        "decision": "BLOCK",
                        "reason": "Prompt injection detected",
                        "policy_type": "PROMPT_INJECTION"
                    }

    return {
        "decision": "ALLOW",
        "reason": "No active security policy violation detected",
        "policy_type": None
    }