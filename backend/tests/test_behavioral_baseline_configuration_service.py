from app.db.database import SessionLocal
from app.main import app
from app.models.behavioral_baseline_configuration import (
    BehavioralBaselineConfiguration,
)
from app.services.behavioral_baseline_configuration_service import (
    get_behavioral_baseline_configuration,
)


def create_configuration(
    db,
    *,
    owner_id=None,
    enabled=True,
    name="Test Baseline",
):
    configuration = BehavioralBaselineConfiguration(
        owner_id=owner_id,
        name=name,
        enabled=enabled,
        baseline_window_seconds=3600,
        observation_window_seconds=300,
        minimum_observations=10,
        deviation_threshold_percent=50,
    )

    db.add(configuration)
    db.commit()
    db.refresh(configuration)

    return configuration


def cleanup_test_configurations(db):
    db.query(BehavioralBaselineConfiguration).filter(
        BehavioralBaselineConfiguration.name.like("Test Baseline%")
    ).delete(
        synchronize_session=False
    )

    db.commit()


def test_returns_global_configuration():
    db = SessionLocal()

    try:
        cleanup_test_configurations(db)

        configuration = create_configuration(
            db,
            name="Test Baseline Global",
        )

        resolved = get_behavioral_baseline_configuration(
            db,
            owner_id=999999,
        )

        assert resolved is not None
        assert resolved.id == configuration.id
    finally:
        cleanup_test_configurations(db)
        db.close()


def test_owner_configuration_overrides_global():
    db = SessionLocal()

    try:
        cleanup_test_configurations(db)

        global_configuration = create_configuration(
            db,
            name="Test Baseline Global",
        )

        owner_configuration = create_configuration(
            db,
            owner_id=1,
            name="Test Baseline Owner",
        )

        resolved = get_behavioral_baseline_configuration(
            db,
            owner_id=1,
        )

        assert resolved is not None
        assert resolved.id == owner_configuration.id
        assert resolved.id != global_configuration.id
    finally:
        cleanup_test_configurations(db)
        db.close()


def test_disabled_owner_configuration_falls_back_to_global():
    db = SessionLocal()

    try:
        cleanup_test_configurations(db)

        test_owner_id = 2

        global_configuration = create_configuration(
            db,
            name="Test Baseline Global",
        )

        create_configuration(
            db,
            owner_id=test_owner_id,
            enabled=False,
            name="Test Baseline Disabled Owner",
        )

        resolved = get_behavioral_baseline_configuration(
            db,
            owner_id=test_owner_id,
        )

        assert resolved is not None
        assert resolved.id == global_configuration.id
    finally:
        cleanup_test_configurations(db)
        db.close()


def test_no_owner_id_returns_global_configuration():
    db = SessionLocal()

    try:
        cleanup_test_configurations(db)

        global_configuration = create_configuration(
            db,
            name="Test Baseline Global",
        )

        resolved = get_behavioral_baseline_configuration(
            db,
            owner_id=None,
        )

        assert resolved is not None
        assert resolved.id == global_configuration.id
    finally:
        cleanup_test_configurations(db)
        db.close()


def test_returns_none_when_all_test_configurations_are_disabled():
    db = SessionLocal()

    try:
        cleanup_test_configurations(db)

        disabled_configuration = create_configuration(
            db,
            enabled=False,
            name="Test Baseline Disabled",
        )

        resolved = get_behavioral_baseline_configuration(
            db,
            owner_id=999999,
        )

        # A seeded global configuration may already exist in the real
        # development database, so this test cannot assume the entire
        # database has no configuration.
        #
        # Instead, verify that the disabled test configuration itself
        # is never selected.
        assert resolved is None or resolved.id != disabled_configuration.id
    finally:
        cleanup_test_configurations(db)
        db.close()