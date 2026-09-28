from sqlalchemy.orm import Session

from app.models.sentinelx_control import SentinelXControl


def create_sentinelx_control(
    db: Session,
    control_id: str,
    name: str,
    description: str | None = None,
    category: str | None = None,
    implementation_status: str = "IMPLEMENTED",
) -> SentinelXControl:
    control = SentinelXControl(
        control_id=control_id,
        name=name,
        description=description,
        category=category,
        implementation_status=implementation_status,
        enabled=True,
    )

    db.add(control)
    db.commit()
    db.refresh(control)

    return control


def get_sentinelx_controls(
    db: Session,
) -> list[SentinelXControl]:
    return (
        db.query(SentinelXControl)
        .order_by(SentinelXControl.id)
        .all()
    )


def get_sentinelx_control(
    db: Session,
    control_id: str,
) -> SentinelXControl | None:
    return (
        db.query(SentinelXControl)
        .filter(
            SentinelXControl.control_id == control_id
        )
        .first()
    )