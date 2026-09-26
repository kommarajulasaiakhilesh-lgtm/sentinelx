from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.services.runtime_guardrail_service import (
    is_tool_action_rate_limited,
    has_repeated_blocked_actions
)

from app.schemas.security_event import SecurityEventCreate
from app.services.security_event_service import create_security_event

from app.models.tool import Tool
from app.schemas.tool_action import ToolActionRequest

from app.api.dependencies import get_current_agent
from app.db.database import get_db
from app.models.agent import Agent

from app.schemas.enforcement import (
    EnforcementRequest,
    EnforcementResponse
)

from app.services.policy_engine import evaluate_policy


router = APIRouter(
    prefix="/api/enforcement",
    tags=["Enforcement"]
)


# ============================================================
# NORMAL POLICY ENFORCEMENT
# ============================================================

@router.post(
    "/evaluate",
    response_model=EnforcementResponse
)
def evaluate_request(
    request: EnforcementRequest,
    current_agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):

    if request.agent_id != current_agent.id:
        raise HTTPException(
            status_code=403,
            detail="Agent ID does not match authenticated agent"
        )

    result = evaluate_policy(
        agent=current_agent,
        input_text=request.input_text,
        db=db
    )

    create_security_event(
        event_data=SecurityEventCreate(
            agent_id=current_agent.id,
            policy_id=result["policy_id"],
            event_type="POLICY_CHECK",
            action=result["decision"],
            decision=result["decision"],
            reason=result["reason"]
        ),
        db=db
    )

    return {
        "agent_id": current_agent.id,
        "decision": result["decision"],
        "reason": result["reason"],
        "policy_type": result["policy_type"]
    }


# ============================================================
# TOOL ACTION ENFORCEMENT
# ============================================================

@router.post(
    "/tool-action",
    response_model=EnforcementResponse
)
def evaluate_tool_action(
    request: ToolActionRequest,
    current_agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # 1. Verify Agent ID
    # --------------------------------------------------------

    if request.agent_id != current_agent.id:
        raise HTTPException(
            status_code=403,
            detail="Agent ID does not match authenticated agent"
        )

    # --------------------------------------------------------
    # 2. Find the requested tool
    # --------------------------------------------------------

    tool = (
        db.query(Tool)
        .filter(
            Tool.agent_id == current_agent.id,
            Tool.name == request.tool_name,
            Tool.enabled == True
        )
        .first()
    )

    if tool is None:
        raise HTTPException(
            status_code=404,
            detail="Tool not found or disabled"
        )

    # --------------------------------------------------------
    # 3. Build canonical tool action
    # --------------------------------------------------------

    tool_action = (
        f"{tool.tool_type.lower()}."
        f"{request.action.lower()}"
    )

    # --------------------------------------------------------
    # 4. Add resource to tool action
    # --------------------------------------------------------

    tool_action_with_resource = (
        f"{tool_action}:{request.resource.lower()}"
    )

    # --------------------------------------------------------
    # 5. Evaluate security policy
    # --------------------------------------------------------

    result = evaluate_policy(
        agent=current_agent,
        input_text=tool_action_with_resource,
        db=db
    )

    # --------------------------------------------------------
    # 6. Apply runtime tool-action rate-limit guardrail
    # --------------------------------------------------------

    rate_limited = is_tool_action_rate_limited(
        db=db,
        agent_id=current_agent.id
    )

    if rate_limited:

        create_security_event(
            event_data=SecurityEventCreate(
                agent_id=current_agent.id,
                policy_id=None,
                event_type="TOOL_ACTION",
                action=request.action,
                decision="BLOCK",
                reason="Runtime tool action rate limit exceeded",
                event_metadata=(
                    "max_actions=10;"
                    "time_window_seconds=60"
                )
            ),
            db=db
        )

        return {
            "agent_id": current_agent.id,
            "decision": "BLOCK",
            "reason": "Runtime tool action rate limit exceeded",
            "policy_type": None
        }

    # --------------------------------------------------------
    # 7. Detect repeated blocked tool actions
    # --------------------------------------------------------

    repeated_blocked_actions = has_repeated_blocked_actions(
        db=db,
        agent_id=current_agent.id
    )

    if repeated_blocked_actions:

        create_security_event(
            event_data=SecurityEventCreate(
                agent_id=current_agent.id,
                policy_id=None,
                event_type="TOOL_ACTION",
                action=request.action,
                decision="BLOCK",
                reason="Repeated blocked tool actions detected",
                event_metadata=(
                    "max_blocked_actions=5;"
                    "time_window_seconds=60"
                )
            ),
            db=db
        )

        return {
            "agent_id": current_agent.id,
            "decision": "BLOCK",
            "reason": "Repeated blocked tool actions detected",
            "policy_type": None
        }

    # --------------------------------------------------------
    # 8. Record normal security event
    # --------------------------------------------------------

    create_security_event(
        event_data=SecurityEventCreate(
            agent_id=current_agent.id,
            policy_id=result["policy_id"],
            event_type="TOOL_ACTION",
            action=request.action,
            decision=result["decision"],
            reason=result["reason"]
        ),
        db=db
    )

    # --------------------------------------------------------
    # 9. Return enforcement result
    # --------------------------------------------------------

    return {
        "agent_id": current_agent.id,
        "decision": result["decision"],
        "reason": result["reason"],
        "policy_type": result["policy_type"]
    }