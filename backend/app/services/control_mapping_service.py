from sqlalchemy.orm import Session

from app.models.control_mapping import ControlMapping


def create_control_mapping(
    db: Session,
    framework_control_id: int,
    sentinelx_control_id: int,
    mapping_status: str = "PARTIALLY_IMPLEMENTED",
    rationale: str | None = None,
) -> ControlMapping:
    mapping = ControlMapping(
        framework_control_id=framework_control_id,
        sentinelx_control_id=sentinelx_control_id,
        mapping_status=mapping_status,
        rationale=rationale,
    )

    db.add(mapping)
    db.commit()
    db.refresh(mapping)

    return mapping


def get_control_mappings(
    db: Session,
) -> list[ControlMapping]:
    return (
        db.query(ControlMapping)
        .order_by(ControlMapping.id)
        .all()
    )


def get_control_mappings_by_framework_control(
    db: Session,
    framework_control_id: int,
) -> list[ControlMapping]:
    return (
        db.query(ControlMapping)
        .filter(
            ControlMapping.framework_control_id
            == framework_control_id
        )
        .order_by(ControlMapping.id)
        .all()
    )


def get_control_mappings_by_sentinelx_control(
    db: Session,
    sentinelx_control_id: int,
) -> list[ControlMapping]:
    return (
        db.query(ControlMapping)
        .filter(
            ControlMapping.sentinelx_control_id
            == sentinelx_control_id
        )
        .order_by(ControlMapping.id)
        .all()
    )