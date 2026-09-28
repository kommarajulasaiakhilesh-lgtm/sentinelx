from sqlalchemy.orm import Session

from app.models.evidence import Evidence


def create_evidence(
    db: Session,
    sentinelx_control_id: int,
    evidence_type: str,
    source: str,
    description: str | None = None,
    reference: str | None = None,
    evidence_status: str = "AVAILABLE",
) -> Evidence:
    evidence = Evidence(
        sentinelx_control_id=sentinelx_control_id,
        evidence_type=evidence_type,
        source=source,
        description=description,
        reference=reference,
        evidence_status=evidence_status,
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    return evidence


def get_evidence(
    db: Session,
) -> list[Evidence]:
    return (
        db.query(Evidence)
        .order_by(Evidence.id)
        .all()
    )


def get_evidence_by_control(
    db: Session,
    sentinelx_control_id: int,
) -> list[Evidence]:
    return (
        db.query(Evidence)
        .filter(
            Evidence.sentinelx_control_id
            == sentinelx_control_id
        )
        .order_by(Evidence.id)
        .all()
    )