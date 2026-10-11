
from sqlalchemy.orm import Session

from app.models.security_test import SecurityTestScenario
from app.schemas.security_test import SecurityTestScenarioCreate


def create_security_test_scenario(
    db: Session,
    scenario_data: SecurityTestScenarioCreate,
    owner_id: int,
) -> SecurityTestScenario:
    scenario = SecurityTestScenario(
        owner_id=owner_id,
        name=scenario_data.name,
        category=scenario_data.category,
        description=scenario_data.description,
        attack_input=scenario_data.attack_input,
        agent_id=scenario_data.agent_id,
        tool_name=scenario_data.tool_name,
        action=scenario_data.action,
        resource=scenario_data.resource,
        expected_decision=scenario_data.expected_decision,
        enabled=scenario_data.enabled,
    )

    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    return scenario


def get_security_test_scenario(
    db: Session,
    scenario_id: int,
) -> SecurityTestScenario | None:
    return (
        db.query(SecurityTestScenario)
        .filter(SecurityTestScenario.id == scenario_id)
        .first()
    )


def get_security_test_scenarios(
    db: Session,
    enabled_only: bool = False,
    owner_id: int | None = None,
) -> list[SecurityTestScenario]:
    query = db.query(SecurityTestScenario)

    if owner_id is not None:
        query = query.filter(
            SecurityTestScenario.owner_id == owner_id
        )

    if enabled_only:
        query = query.filter(
            SecurityTestScenario.enabled.is_(True)
        )

    return query.order_by(SecurityTestScenario.id.asc()).all()
