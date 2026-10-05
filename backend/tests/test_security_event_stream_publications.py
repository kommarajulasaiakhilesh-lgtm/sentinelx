import asyncio
import uuid

from app.main import app
from app.db.database import SessionLocal
from app.models.agent import Agent
from app.models.security_event import SecurityEvent
from app.services.event_stream_service import security_event_stream
from app.services.security_alert_service import create_security_alert
from app.services.incident_correlation_service import correlate_security_alert


def get_test_agent():
    db = SessionLocal()
    try:
        return (
            db.query(Agent)
            .filter(Agent.owner_id == 4)
            .first()
        )
    finally:
        db.close()


def test_security_alert_publication_to_owner():
    agent = get_test_agent()
    assert agent is not None

    async def run_test():
        queue = await security_event_stream.subscribe(agent.owner_id)

        db = SessionLocal()
        try:
            event = SecurityEvent(
                agent_id=agent.id,
                event_type="TOOL_ACTION",
                action="READ_FILE",
                decision="BLOCK",
                reason="Test stream alert",
                event_metadata=None,
            )
            db.add(event)
            db.commit()
            db.refresh(event)

            alert_type = f"TEST_STREAM_ALERT_{uuid.uuid4().hex[:8]}"

            alert = create_security_alert(
                db=db,
                security_event=event,
                alert_type=alert_type,
                severity="HIGH",
                title="Test stream alert",
                description="Test alert publication",
            )

            payload = await asyncio.wait_for(
                queue.get(),
                timeout=2,
            )

            assert payload["event"] == "ALERT_CREATED"
            assert payload["data"]["id"] == alert.id
            assert payload["data"]["agent_id"] == agent.id
            assert payload["data"]["alert_type"] == alert_type

        finally:
            security_event_stream.unsubscribe(
                agent.owner_id,
                queue,
            )
            db.close()

    asyncio.run(run_test())


def test_incident_publication_to_owner():
    agent = get_test_agent()
    assert agent is not None

    async def run_test():
        queue = await security_event_stream.subscribe(agent.owner_id)

        db = SessionLocal()
        try:
            event = SecurityEvent(
                agent_id=agent.id,
                event_type="TOOL_ACTION",
                action="BLOCKED_TEST_ACTION",
                decision="BLOCK",
                reason="Test incident stream",
                event_metadata=None,
            )
            db.add(event)
            db.commit()
            db.refresh(event)

            alert_type = f"TEST_INC_{uuid.uuid4().hex[:8]}"

            alert = create_security_alert(
                db=db,
                security_event=event,
                alert_type=alert_type,
                severity="HIGH",
                title="Test incident stream",
                description="Test incident publication",
            )

            alert_payload = await asyncio.wait_for(
                queue.get(),
                timeout=2,
            )

            assert alert_payload["event"] == "ALERT_CREATED"
            assert alert_payload["data"]["id"] == alert.id

            incident = correlate_security_alert(
                db=db,
                alert=alert,
            )

            incident_payload = await asyncio.wait_for(
                queue.get(),
                timeout=2,
            )

            assert incident_payload["event"] == "INCIDENT_CREATED"
            assert incident_payload["data"]["id"] == incident.id
            assert incident_payload["data"]["agent_id"] == agent.id

        finally:
            security_event_stream.unsubscribe(
                agent.owner_id,
                queue,
            )
            db.close()

    asyncio.run(run_test())


def test_correlated_alert_does_not_create_duplicate_incident_event():
    agent = get_test_agent()
    assert agent is not None

    async def run_test():
        queue = await security_event_stream.subscribe(agent.owner_id)

        db = SessionLocal()
        try:
            alert_type = f"TEST_CORR_{uuid.uuid4().hex[:8]}"

            event_one = SecurityEvent(
                agent_id=agent.id,
                event_type="TOOL_ACTION",
                action="CORRELATION_TEST_ONE",
                decision="BLOCK",
                reason="Correlation stream test",
                event_metadata=None,
            )
            db.add(event_one)
            db.commit()
            db.refresh(event_one)

            alert_one = create_security_alert(
                db=db,
                security_event=event_one,
                alert_type=alert_type,
                severity="HIGH",
                title="Correlation stream test",
                description="First correlation alert",
            )

            first_alert_payload = await asyncio.wait_for(
                queue.get(),
                timeout=2,
            )

            assert first_alert_payload["event"] == "ALERT_CREATED"
            assert first_alert_payload["data"]["id"] == alert_one.id

            incident_one = correlate_security_alert(
                db=db,
                alert=alert_one,
            )

            first_incident_payload = await asyncio.wait_for(
                queue.get(),
                timeout=2,
            )

            assert first_incident_payload["event"] == "INCIDENT_CREATED"
            assert first_incident_payload["data"]["id"] == incident_one.id

            event_two = SecurityEvent(
                agent_id=agent.id,
                event_type="TOOL_ACTION",
                action="CORRELATION_TEST_TWO",
                decision="BLOCK",
                reason="Correlation stream test",
                event_metadata=None,
            )
            db.add(event_two)
            db.commit()
            db.refresh(event_two)

            alert_two = create_security_alert(
                db=db,
                security_event=event_two,
                alert_type=alert_type,
                severity="HIGH",
                title="Correlation stream test",
                description="Second correlation alert",
            )

            second_alert_payload = await asyncio.wait_for(
                queue.get(),
                timeout=2,
            )

            assert second_alert_payload["event"] == "ALERT_CREATED"
            assert second_alert_payload["data"]["id"] == alert_two.id

            incident_two = correlate_security_alert(
                db=db,
                alert=alert_two,
            )

            assert incident_two.id == incident_one.id

            try:
                await asyncio.wait_for(
                    queue.get(),
                    timeout=0.5,
                )
                assert False, (
                    "A duplicate INCIDENT_CREATED event was published"
                )
            except asyncio.TimeoutError:
                pass

        finally:
            security_event_stream.unsubscribe(
                agent.owner_id,
                queue,
            )
            db.close()

    asyncio.run(run_test())


def test_security_alert_publication_is_isolated_between_users():
    agent = get_test_agent()
    assert agent is not None

    async def run_test():
        owner_queue = await security_event_stream.subscribe(
            agent.owner_id
        )

        other_user_id = 999999
        other_queue = await security_event_stream.subscribe(
            other_user_id
        )

        db = SessionLocal()
        try:
            event = SecurityEvent(
                agent_id=agent.id,
                event_type="TOOL_ACTION",
                action="ISOLATION_TEST",
                decision="BLOCK",
                reason="Stream isolation test",
                event_metadata=None,
            )
            db.add(event)
            db.commit()
            db.refresh(event)

            alert_type = f"TEST_ISO_{uuid.uuid4().hex[:8]}"

            alert = create_security_alert(
                db=db,
                security_event=event,
                alert_type=alert_type,
                severity="HIGH",
                title="Stream isolation test",
                description="Test user isolation",
            )

            owner_payload = await asyncio.wait_for(
                owner_queue.get(),
                timeout=2,
            )

            assert owner_payload["event"] == "ALERT_CREATED"
            assert owner_payload["data"]["id"] == alert.id

            try:
                await asyncio.wait_for(
                    other_queue.get(),
                    timeout=0.5,
                )
                assert False, (
                    "Alert was incorrectly published to another user"
                )
            except asyncio.TimeoutError:
                pass

        finally:
            security_event_stream.unsubscribe(
                agent.owner_id,
                owner_queue,
            )
            security_event_stream.unsubscribe(
                other_user_id,
                other_queue,
            )
            db.close()

    asyncio.run(run_test())