from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.control_mapping import (
    ControlMappingCreate,
    ControlMappingResponse,
)
from app.services.control_mapping_service import (
    create_control_mapping,
    get_control_mappings,
    get_control_mappings_by_framework_control,
    get_control_mappings_by_sentinelx_control,
)


router = APIRouter(
    prefix="/api/control-mappings",
    tags=["Control Mappings"],
)


@router.get(
    "",
    response_model=list[ControlMappingResponse],
)
def list_control_mappings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_control_mappings(db)


@router.get(
    "/framework-control/{framework_control_id}",
    response_model=list[ControlMappingResponse],
)
def list_framework_control_mappings(
    framework_control_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_control_mappings_by_framework_control(
        db=db,
        framework_control_id=framework_control_id,
    )


@router.get(
    "/sentinelx-control/{sentinelx_control_id}",
    response_model=list[ControlMappingResponse],
)
def list_sentinelx_control_mappings(
    sentinelx_control_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_control_mappings_by_sentinelx_control(
        db=db,
        sentinelx_control_id=sentinelx_control_id,
    )


@router.post(
    "",
    response_model=ControlMappingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_control_mapping_endpoint(
    mapping_data: ControlMappingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_control_mapping(
        db=db,
        framework_control_id=mapping_data.framework_control_id,
        sentinelx_control_id=mapping_data.sentinelx_control_id,
        mapping_status=mapping_data.mapping_status,
        rationale=mapping_data.rationale,
    )