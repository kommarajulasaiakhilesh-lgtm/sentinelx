from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.services.compliance_service import (
    get_all_framework_coverage,
    get_framework_coverage,
)


router = APIRouter(
    prefix="/api/compliance",
    tags=["Compliance"],
)


@router.get("/coverage")
def get_compliance_coverage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_framework_coverage(db)


@router.get("/coverage/{framework_id}")
def get_framework_compliance_coverage(
    framework_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    coverage = get_framework_coverage(
        db=db,
        framework_id=framework_id,
    )

    if coverage.get("framework_name") is None:
        raise HTTPException(
            status_code=404,
            detail="Framework not found",
        )

    return coverage