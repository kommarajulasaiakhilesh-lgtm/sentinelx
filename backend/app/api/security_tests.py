from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.security_test import (
    SecurityTestScenarioCreate,
    SecurityTestScenarioResponse,
    SecurityTestRunResponse,
)
from app.services.attack_simulation_service import simulate_security_test
from app.services.security_test_service import (
    create_security_test_scenario,
    get_security_test_scenario,
    get_security_test_scenarios,
)


router = APIRouter(
    prefix="/api/security-tests",
    tags=["Security Testing"],
)


@router.post(
    "/scenarios",
    response_model=SecurityTestScenarioResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_scenario(
    scenario_data: SecurityTestScenarioCreate,
    db: Session = Depends(get_db),
):
    return create_security_test_scenario(
        db=db,
        scenario_data=scenario_data,
    )


@router.get(
    "/scenarios",
    response_model=list[SecurityTestScenarioResponse],
)
def list_scenarios(
    enabled_only: bool = False,
    db: Session = Depends(get_db),
):
    return get_security_test_scenarios(
        db=db,
        enabled_only=enabled_only,
    )


@router.get(
    "/scenarios/{scenario_id}",
    response_model=SecurityTestScenarioResponse,
)
def get_scenario(
    scenario_id: int,
    db: Session = Depends(get_db),
):
    scenario = get_security_test_scenario(
        db=db,
        scenario_id=scenario_id,
    )

    if scenario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Security test scenario not found",
        )

    return scenario


@router.post(
    "/scenarios/{scenario_id}/run",
    response_model=SecurityTestRunResponse,
)
def run_scenario(
    scenario_id: int,
    db: Session = Depends(get_db),
):
    try:
        return simulate_security_test(
            db=db,
            scenario_id=scenario_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )