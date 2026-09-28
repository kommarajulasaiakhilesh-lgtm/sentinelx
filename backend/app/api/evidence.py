from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.evidence import (
    EvidenceCreate,
    EvidenceResponse,
)
from app.services.evidence_service import (
    create_evidence,
    get_evidence,
    get_evidence_by_control,
)


router = APIRouter(
    prefix="/api/evidence",
    tags=["Evidence"],
)


@router.get(
    "",
    response_model=list[EvidenceResponse],
)
def list_evidence(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_evidence(db)


@router.get(
    "/control/{sentinelx_control_id}",
    response_model=list[EvidenceResponse],
)
def list_control_evidence(
    sentinelx_control_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_evidence_by_control(
        db=db,
        sentinelx_control_id=sentinelx_control_id,
    )


@router.post(
    "",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_evidence_endpoint(
    evidence_data: EvidenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_evidence(
        db=db,
        sentinelx_control_id=evidence_data.sentinelx_control_id,
        evidence_type=evidence_data.evidence_type,
        source=evidence_data.source,
        description=evidence_data.description,
        reference=evidence_data.reference,
        evidence_status=evidence_data.evidence_status,
    )