
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

        # ====================================================
        # PROMPT INJECTION POLICY
        # ====================================================

        if policy.policy_type == "PROMPT_INJECTION":

            if policy.condition:

                if policy.condition.lower() in normalized_input:

                    return {
                        "decision": policy.action,
                        "reason": "Policy condition matched",
                        "policy_type": policy.policy_type,
                        "policy_id": policy.id
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
                            "policy_type": policy.policy_type,
                            "policy_id": policy.id
                        }

        # ====================================================
        # TOOL ACTION POLICY
        # ====================================================

        elif policy.policy_type == "TOOL_ACTION":

            if policy.condition:

                policy_condition = policy.condition.lower()

                # ------------------------------------------------
                # Exact resource match
                #
                # Example:
                # policy = file.read:secret.txt
                # request = file.read:secret.txt
                # ------------------------------------------------

                if policy_condition == normalized_input:

                    return {
                        "decision": policy.action,
                        "reason": "Tool action policy matched",
                        "policy_type": policy.policy_type,
                        "policy_id": policy.id
                    }

                # ------------------------------------------------
                # Broad tool-action match
                #
                # Example:
                # policy = file.read
                # request = file.read:test.txt
                #
                # This means the policy applies to ALL resources
                # used by that tool action.
                # ------------------------------------------------

                if ":" in normalized_input:

                    tool_action = normalized_input.split(
                        ":",
                        1
                    )[0]

                    if policy_condition == tool_action:

                        return {
                            "decision": policy.action,
                            "reason": "Tool action policy matched",
                            "policy_type": policy.policy_type,
                            "policy_id": policy.id
                        }

    return {
        "decision": "ALLOW",
        "reason": "No active security policy violation detected",
        "policy_type": None,
        "policy_id": None
    }