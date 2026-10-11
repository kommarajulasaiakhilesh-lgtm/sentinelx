
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_role
from app.db.database import get_db
from app.models.risk_scoring_configuration import (
    RiskScoringConfiguration,
)
from app.models.user import User
from app.schemas.risk_scoring_configuration import (
    RiskScoringConfigurationResponse,
    RiskScoringConfigurationUpdate,
)
from app.services.risk_scoring_configuration_service import (
    get_risk_scoring_configuration,
)


router = APIRouter(
    prefix="/api/risk-configurations",
    tags=["Risk Configurations"],
)


def _get_owned_configuration(
    db: Session,
    owner_id: int,
) -> RiskScoringConfiguration | None:
    return (
        db.query(RiskScoringConfiguration)
        .filter(RiskScoringConfiguration.owner_id == owner_id)
        .order_by(RiskScoringConfiguration.id.desc())
        .first()
    )


def _get_global_configuration(
    db: Session,
) -> RiskScoringConfiguration | None:
    return (
        db.query(RiskScoringConfiguration)
        .filter(RiskScoringConfiguration.owner_id.is_(None))
        .order_by(RiskScoringConfiguration.id.desc())
        .first()
    )


def _apply_configuration(
    configuration: RiskScoringConfiguration,
    payload: RiskScoringConfigurationUpdate,
) -> RiskScoringConfiguration:
    for field, value in payload.model_dump().items():
        setattr(configuration, field, value)

    return configuration


@router.get(
    "/effective",
    response_model=RiskScoringConfigurationResponse,
)
def get_effective_configuration(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    configuration = get_risk_scoring_configuration(
        db,
        owner_id=current_user.id,
    )

    if configuration is None:
        raise HTTPException(
            status_code=404,
            detail="No enabled risk configuration is available",
        )

    return configuration


@router.get(
    "/mine",
    response_model=RiskScoringConfigurationResponse,
)
def get_my_configuration(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    configuration = _get_owned_configuration(
        db,
        owner_id=current_user.id,
    )

    if configuration is None:
        raise HTTPException(
            status_code=404,
            detail="You do not have a personal risk configuration",
        )

    return configuration


@router.put(
    "/mine",
    response_model=RiskScoringConfigurationResponse,
)
def upsert_my_configuration(
    payload: RiskScoringConfigurationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    configuration = _get_owned_configuration(
        db,
        owner_id=current_user.id,
    )

    if configuration is None:
        configuration = RiskScoringConfiguration(
            owner_id=current_user.id,
            **payload.model_dump(),
        )
        db.add(configuration)
    else:
        _apply_configuration(configuration, payload)

    try:
        db.commit()
        db.refresh(configuration)
    except Exception:
        db.rollback()
        raise

    return configuration


@router.get(
    "/global",
    response_model=RiskScoringConfigurationResponse,
)
def get_global_configuration(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    configuration = _get_global_configuration(db)

    if configuration is None:
        raise HTTPException(
            status_code=404,
            detail="Global risk configuration not found",
        )

    return configuration


@router.put(
    "/global",
    response_model=RiskScoringConfigurationResponse,
)
def upsert_global_configuration(
    payload: RiskScoringConfigurationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    configuration = _get_global_configuration(db)

    if configuration is None:
        configuration = RiskScoringConfiguration(
            owner_id=None,
            **payload.model_dump(),
        )
        db.add(configuration)
    else:
        _apply_configuration(configuration, payload)

    try:
        db.commit()
        db.refresh(configuration)
    except Exception:
        db.rollback()
        raise

    return configuration
