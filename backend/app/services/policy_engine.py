
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
        .order_by(
            Policy.priority,
            Policy.id
        )
        .all()
    )

    normalized_input = input_text.lower()

    for policy in policies:

        if policy.policy_type == "PROMPT_INJECTION":

            # If a custom condition exists,
            # use it instead of the default patterns.
            if policy.condition:

                if policy.condition.lower() in normalized_input:

                    return {
                        "decision": policy.action,
                        "reason": "Policy condition matched",
                        "policy_type": policy.policy_type
                    }

            else:

                suspicious_patterns = [
                    "ignore previous instructions",
                    "ignore all previous instructions",
                    "reveal system prompt",
                    "show system prompt",
                    "disregard previous instructions",
                    "bypass your instructions"
                ]

                for pattern in suspicious_patterns:

                    if pattern in normalized_input:

                        return {
                            "decision": policy.action,
                            "reason": "Prompt injection detected",
                            "policy_type": policy.policy_type
                        }

    return {
        "decision": "ALLOW",
        "reason": "No active security policy violation detected",
        "policy_type": None
    }
