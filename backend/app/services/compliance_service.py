from sqlalchemy.orm import Session

from app.models.control_mapping import ControlMapping
from app.models.evidence import Evidence
from app.models.framework import Framework, FrameworkControl
from app.models.sentinelx_control import SentinelXControl

STATUS_WEIGHTS = {
    "IMPLEMENTED": 1.0,
    "PARTIALLY_IMPLEMENTED": 0.5,
    "GAP_IDENTIFIED": 0.0,
    "NOT_IMPLEMENTED": 0.0,
}


def get_framework_coverage(
    db: Session,
    framework_id: int,
) -> dict:
    framework = (
        db.query(Framework)
        .filter(Framework.id == framework_id)
        .first()
    )

    if framework is None:
        return {
            "framework_id": framework_id,
            "framework_name": None,
            "error": "Framework not found",
        }

    framework_controls = (
        db.query(FrameworkControl)
        .filter(
            FrameworkControl.framework_id == framework_id
        )
        .order_by(FrameworkControl.id)
        .all()
    )

    total_controls = len(framework_controls)

    mapped_controls = 0
    evidence_backed_controls = 0

    implemented = 0
    partially_implemented = 0
    gap_identified = 0
    not_implemented = 0
    not_applicable = 0

    implementation_score = 0.0
    implementation_denominator = 0

    control_details = []

    for framework_control in framework_controls:
        mappings = (
            db.query(ControlMapping)
            .filter(
                ControlMapping.framework_control_id
                == framework_control.id
            )
            .all()
        )

        if mappings:
            mapped_controls += 1

        control_has_evidence = False
        mapping_statuses = []

        for mapping in mappings:
            mapping_status = mapping.mapping_status
            mapping_statuses.append(mapping_status)

            evidence = (
                db.query(Evidence)
                .filter(
                    Evidence.sentinelx_control_id
                    == mapping.sentinelx_control_id,
                    Evidence.evidence_status
                    == "AVAILABLE",
                )
                .first()
            )

            if evidence:
                control_has_evidence = True

            if mapping_status == "IMPLEMENTED":
                implemented += 1
            elif mapping_status == "PARTIALLY_IMPLEMENTED":
                partially_implemented += 1
            elif mapping_status == "GAP_IDENTIFIED":
                gap_identified += 1
            elif mapping_status == "NOT_IMPLEMENTED":
                not_implemented += 1
            elif mapping_status == "NOT_APPLICABLE":
                not_applicable += 1

            if mapping_status == "NOT_APPLICABLE":
                continue

            if mapping_status in STATUS_WEIGHTS:
                implementation_score += STATUS_WEIGHTS[
                    mapping_status
                ]
                implementation_denominator += 1

        if control_has_evidence:
            evidence_backed_controls += 1

        control_details.append(
            {
                "framework_control_id": framework_control.id,
                "control_id": framework_control.control_id,
                "title": framework_control.title,
                "function": framework_control.function,
                "category": framework_control.category,
                "reference": framework_control.reference,
                "mapped": bool(mappings),
                "evidence_available": control_has_evidence,
                "mapping_statuses": mapping_statuses,
            }
        )

    mapped_percentage = (
        round(
            (mapped_controls / total_controls) * 100,
            2,
        )
        if total_controls > 0
        else 0
    )

    evidence_coverage_percentage = (
        round(
            (evidence_backed_controls / total_controls) * 100,
            2,
        )
        if total_controls > 0
        else 0
    )

    implementation_coverage_percentage = (
        round(
            (
                implementation_score
                / implementation_denominator
            )
            * 100,
            2,
        )
        if implementation_denominator > 0
        else 0
    )

    return {
        "framework_id": framework.id,
        "framework_name": framework.name,
        "framework_version": framework.version,
        "total_controls": total_controls,
        "mapped_controls": mapped_controls,
        "mapped_percentage": mapped_percentage,
        "evidence_backed_controls": evidence_backed_controls,
        "evidence_coverage_percentage": (
            evidence_coverage_percentage
        ),
        "implementation_coverage_percentage": (
            implementation_coverage_percentage
        ),
        "status_counts": {
            "IMPLEMENTED": implemented,
            "PARTIALLY_IMPLEMENTED": partially_implemented,
            "GAP_IDENTIFIED": gap_identified,
            "NOT_IMPLEMENTED": not_implemented,
            "NOT_APPLICABLE": not_applicable,
        },
        "controls": control_details,
    }


def get_all_framework_coverage(
    db: Session,
) -> list[dict]:
    frameworks = (
        db.query(Framework)
        .filter(Framework.enabled == True)
        .order_by(Framework.id)
        .all()
    )

    return [
        get_framework_coverage(
            db=db,
            framework_id=framework.id,
        )
        for framework in frameworks
    ]