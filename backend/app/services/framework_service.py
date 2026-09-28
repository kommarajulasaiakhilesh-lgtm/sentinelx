from sqlalchemy.orm import Session

from app.models.framework import Framework, FrameworkControl


def create_framework(
    db: Session,
    name: str,
    version: str | None = None,
    description: str | None = None,
) -> Framework:
    framework = Framework(
        name=name,
        version=version,
        description=description,
        enabled=True,
    )

    db.add(framework)
    db.commit()
    db.refresh(framework)

    return framework


def get_frameworks(
    db: Session,
) -> list[Framework]:
    return (
        db.query(Framework)
        .order_by(Framework.id)
        .all()
    )


def create_framework_control(
    db: Session,
    framework_id: int,
    control_id: str,
    title: str,
    description: str | None = None,
    function: str | None = None,
    category: str | None = None,
    reference: str | None = None,
) -> FrameworkControl:
    control = FrameworkControl(
        framework_id=framework_id,
        control_id=control_id,
        title=title,
        description=description,
        function=function,
        category=category,
        reference=reference,
        enabled=True,
    )

    db.add(control)
    db.commit()
    db.refresh(control)

    return control


def get_framework_controls(
    db: Session,
    framework_id: int,
) -> list[FrameworkControl]:
    return (
        db.query(FrameworkControl)
        .filter(
            FrameworkControl.framework_id == framework_id
        )
        .order_by(FrameworkControl.id)
        .all()
    )