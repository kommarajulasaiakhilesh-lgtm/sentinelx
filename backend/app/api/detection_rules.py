import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.detection_rule import DetectionRule
from app.models.user import User
from app.schemas.detection_rule import (
    DetectionRuleCreate,
    DetectionRuleUpdate,
    DetectionRuleResponse,
)


router = APIRouter(
    prefix="/api/detection-rules",
    tags=["Detection Rules"]
)


# ============================================================
# CREATE DETECTION RULE
# ============================================================

@router.post(
    "",
    response_model=DetectionRuleResponse,
    status_code=status.HTTP_201_CREATED
)
def create_detection_rule(
    rule_data: DetectionRuleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rule = DetectionRule(
        owner_id=current_user.id,
        name=rule_data.name,
        description=rule_data.description,
        enabled=rule_data.enabled,
        severity=rule_data.severity,
        alert_type=rule_data.alert_type,
        title=rule_data.title,
        conditions=(
            json.dumps(rule_data.conditions)
            if rule_data.conditions is not None
            else None
        ),
        threshold=rule_data.threshold,
        window_seconds=rule_data.window_seconds,
    )

    db.add(rule)
    db.commit()
    db.refresh(rule)

    return rule


# ============================================================
# GET ALL DETECTION RULES
# ============================================================

@router.get(
    "",
    response_model=list[DetectionRuleResponse]
)
def get_detection_rules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(DetectionRule)
        .filter(
            DetectionRule.owner_id == current_user.id
        )
        .order_by(
            DetectionRule.id.asc()
        )
        .all()
    )


# ============================================================
# GET ONE DETECTION RULE
# ============================================================

@router.get(
    "/{rule_id}",
    response_model=DetectionRuleResponse
)
def get_detection_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rule = (
        db.query(DetectionRule)
        .filter(
            DetectionRule.id == rule_id,
            DetectionRule.owner_id == current_user.id
        )
        .first()
    )

    if rule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection rule not found"
        )

    return rule


# ============================================================
# UPDATE DETECTION RULE
# ============================================================

@router.patch(
    "/{rule_id}",
    response_model=DetectionRuleResponse
)
def update_detection_rule(
    rule_id: int,
    rule_data: DetectionRuleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rule = (
        db.query(DetectionRule)
        .filter(
            DetectionRule.id == rule_id,
            DetectionRule.owner_id == current_user.id
        )
        .first()
    )

    if rule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection rule not found"
        )

    update_data = rule_data.model_dump(
        exclude_unset=True
    )

    if "conditions" in update_data:
        conditions = update_data.pop("conditions")

        rule.conditions = (
            json.dumps(conditions)
            if conditions is not None
            else None
        )

    for field, value in update_data.items():
        setattr(rule, field, value)

    db.commit()
    db.refresh(rule)

    return rule


# ============================================================
# DELETE DETECTION RULE
# ============================================================

@router.delete(
    "/{rule_id}"
)
def delete_detection_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rule = (
        db.query(DetectionRule)
        .filter(
            DetectionRule.id == rule_id,
            DetectionRule.owner_id == current_user.id
        )
        .first()
    )

    if rule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection rule not found"
        )

    db.delete(rule)
    db.commit()

    return {
        "message": "Detection rule deleted successfully",
        "rule_id": rule_id
    }