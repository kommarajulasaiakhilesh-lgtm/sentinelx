from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.framework import (
    FrameworkControlCreate,
    FrameworkControlResponse,
    FrameworkCreate,
    FrameworkResponse,
)
from app.services.framework_service import (
    create_framework,
    create_framework_control,
    get_framework_controls,
    get_frameworks,
)


router = APIRouter(
    prefix="/api/frameworks",
    tags=["Frameworks"],
)


@router.get(
    "",
    response_model=list[FrameworkResponse],
)
def list_frameworks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_frameworks(db)


@router.post(
    "",
    response_model=FrameworkResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_framework_endpoint(
    framework_data: FrameworkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_framework(
        db=db,
        name=framework_data.name,
        version=framework_data.version,
        description=framework_data.description,
    )


@router.get(
    "/{framework_id}/controls",
    response_model=list[FrameworkControlResponse],
)
def list_framework_controls(
    framework_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_framework_controls(
        db=db,
        framework_id=framework_id,
    )


@router.post(
    "/{framework_id}/controls",
    response_model=FrameworkControlResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_framework_control_endpoint(
    framework_id: int,
    control_data: FrameworkControlCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_framework_control(
        db=db,
        framework_id=framework_id,
        control_id=control_data.control_id,
        title=control_data.title,
        description=control_data.description,
        function=control_data.function,
        category=control_data.category,
        reference=control_data.reference,
    )