from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.sentinelx_control import (
    SentinelXControlCreate,
    SentinelXControlResponse,
)
from app.services.sentinelx_control_service import (
    create_sentinelx_control,
    get_sentinelx_controls,
)


router = APIRouter(
    prefix="/api/sentinelx-controls",
    tags=["SentinelX Controls"],
)


@router.get(
    "",
    response_model=list[SentinelXControlResponse],
)
def list_sentinelx_controls(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_sentinelx_controls(db)


@router.post(
    "",
    response_model=SentinelXControlResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sentinelx_control_endpoint(
    control_data: SentinelXControlCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_sentinelx_control(
        db=db,
        control_id=control_data.control_id,
        name=control_data.name,
        description=control_data.description,
        category=control_data.category,
        implementation_status=control_data.implementation_status,
    )