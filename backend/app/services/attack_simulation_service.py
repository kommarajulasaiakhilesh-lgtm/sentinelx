from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.security_event import SecurityEvent
from app.models.security_test import (
    SecurityTestRun,
    SecurityTestScenario,
)
from app.models.tool import Tool
from app.services.policy_engine import evaluate_policy
from app.services.runtime_guardrail_service import (
    has_repeated_blocked_actions,
    is_tool_action_rate_limited,
)
from app.services.security_test_service import get_security_test_scenario


def simulate_security_test(
    db: Session,
    scenario_id: int,
) -> SecurityTestRun:

    scenario = get_security_test_scenario(
        db,
        scenario_id,
    )

    if scenario is None:
        raise ValueError("Security test scenario not found")

    if not scenario.enabled:
        raise ValueError("Security test scenario is disabled")

    actual_decision = _simulate_attack(
        db=db,
        scenario=scenario,
    )

    result = (
        "PASSED"
        if actual_decision == scenario.expected_decision
        else "FAILED"
    )

    details = (
        f"Scenario: {scenario.name}; "
        f"Category: {scenario.category}; "
        f"Expected: {scenario.expected_decision}; "
        f"Actual: {actual_decision}"
    )

    test_run = SecurityTestRun(
        scenario_id=scenario.id,
        actual_decision=actual_decision,
        expected_decision=scenario.expected_decision,
        result=result,
        details=details,
    )

    db.add(test_run)
    db.commit()
    db.refresh(test_run)

    return test_run


def _simulate_attack(
    db: Session,
    scenario: SecurityTestScenario,
) -> str:

    normalized_category = scenario.category.upper()

    if scenario.agent_id is None:
        raise ValueError(
            "Security test scenario requires an agent_id"
        )

    agent = (
        db.query(Agent)
        .filter(Agent.id == scenario.agent_id)
        .first()
    )

    if agent is None:
        raise ValueError(
            "Security test scenario agent not found"
        )

    if normalized_category == "PROMPT_INJECTION":
        return _simulate_prompt_injection(
            db=db,
            agent=agent,
            attack_input=scenario.attack_input,
        )

    if normalized_category == "UNAUTHORIZED_TOOL":
        return _simulate_unauthorized_tool(
            db=db,
            agent=agent,
            scenario=scenario,
        )

    if normalized_category == "POLICY_BYPASS":
        return _simulate_policy_bypass(
            db=db,
            agent=agent,
            scenario=scenario,
        )

    if normalized_category == "RATE_LIMIT":
        return _simulate_rate_limit(
            db=db,
            agent=agent,
            scenario=scenario,
        )

    if normalized_category == "REPEATED_BLOCK":
        return _simulate_repeated_block(
            db=db,
            agent=agent,
            scenario=scenario,
        )

    if normalized_category == "SUSPICIOUS_ACTION":
        return _simulate_suspicious_action(
            db=db,
            agent=agent,
            scenario=scenario,
        )

    return "ALLOW"


def _build_tool_action(
    db: Session,
    agent: Agent,
    scenario: SecurityTestScenario,
) -> str:

    if not scenario.tool_name:
        raise ValueError(
            "Security test scenario requires a tool_name"
        )

    if not scenario.action:
        raise ValueError(
            "Security test scenario requires an action"
        )

    if not scenario.resource:
        raise ValueError(
            "Security test scenario requires a resource"
        )

    tool = (
        db.query(Tool)
        .filter(
            Tool.agent_id == agent.id,
            Tool.name == scenario.tool_name,
            Tool.enabled.is_(True),
        )
        .first()
    )

    if tool is None:
        raise ValueError(
            "Security test scenario tool not found or disabled"
        )

    return (
        f"{tool.tool_type.lower()}."
        f"{scenario.action.lower()}:"
        f"{scenario.resource.lower()}"
    )

def _simulate_prompt_injection(
    db: Session,
    agent: Agent,
    attack_input: str | None,
) -> str:

    if not attack_input:
        return "ALLOW"

    result = evaluate_policy(
        agent=agent,
        input_text=attack_input,
        db=db,
    )

    return result["decision"]


def _simulate_unauthorized_tool(
    db: Session,
    agent: Agent,
    scenario: SecurityTestScenario,
) -> str:

    tool_action = _build_tool_action(
        db=db,
        agent=agent,
        scenario=scenario,
    )

    result = evaluate_policy(
        agent=agent,
        input_text=tool_action,
        db=db,
    )

    if result["decision"] != "ALLOW":
        return result["decision"]

    return "BLOCK"


def _simulate_policy_bypass(
    db: Session,
    agent: Agent,
    scenario: SecurityTestScenario,
) -> str:

    tool_action = _build_tool_action(
        db=db,
        agent=agent,
        scenario=scenario,
    )

    result = evaluate_policy(
        agent=agent,
        input_text=tool_action,
        db=db,
    )

    return result["decision"]


def _simulate_rate_limit(
    db: Session,
    agent: Agent,
    scenario: SecurityTestScenario,
) -> str:

    for _ in range(10):
        db.add(
            SecurityEvent(
                agent_id=agent.id,
                policy_id=None,
                event_type="TOOL_ACTION",
                action=scenario.action,
                decision="ALLOW",
                reason="Security test rate-limit simulation",
            )
        )

    db.commit()

    if is_tool_action_rate_limited(
        db=db,
        agent_id=agent.id,
    ):
        return "BLOCK"

    return "ALLOW"

def _simulate_repeated_block(
    db: Session,
    agent: Agent,
    scenario: SecurityTestScenario,
) -> str:

    for _ in range(5):
        db.add(
            SecurityEvent(
                agent_id=agent.id,
                policy_id=None,
                event_type="TOOL_ACTION",
                action=scenario.action,
                decision="BLOCK",
                reason="Security test repeated-block simulation",
            )
        )

    db.commit()

    if has_repeated_blocked_actions(
        db=db,
        agent_id=agent.id,
    ):
        return "BLOCK"

    return "ALLOW"


def _simulate_suspicious_action(
    db: Session,
    agent: Agent,
    scenario: SecurityTestScenario,
) -> str:

    result = evaluate_policy(
        agent=agent,
        input_text=scenario.attack_input or "",
        db=db,
    )

    if result["decision"] != "ALLOW":
        return result["decision"]

    return "WARN"