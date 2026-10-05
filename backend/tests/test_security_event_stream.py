import asyncio

from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user
from app.main import app
from app.services.event_stream_service import security_event_stream


client = TestClient(app)


def setup_user_override():
    app.dependency_overrides[get_current_user] = lambda: _get_test_user()


def teardown_user_override():
    app.dependency_overrides.clear()


def _get_test_user():
    from app.db.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()

    try:
        return (
            db.query(User)
            .filter(User.id == 4)
            .first()
        )
    finally:
        db.close()


def test_security_event_stream_subscribe_and_publish():
    async def test_stream():
        queue = await security_event_stream.subscribe(4)

        try:
            security_event_stream.publish(
                user_id=4,
                event_type="SECURITY_EVENT",
                data={
                    "id": 999999,
                    "agent_id": 1,
                    "event_type": "TEST_EVENT",
                    "decision": "BLOCK",
                },
            )

            payload = await asyncio.wait_for(
                queue.get(),
                timeout=1,
            )

            assert payload["event"] == "SECURITY_EVENT"
            assert payload["data"]["id"] == 999999
            assert payload["data"]["agent_id"] == 1
            assert payload["data"]["event_type"] == "TEST_EVENT"
            assert payload["data"]["decision"] == "BLOCK"

        finally:
            security_event_stream.unsubscribe(
                user_id=4,
                queue=queue,
            )

    asyncio.run(test_stream())


def test_security_event_stream_does_not_cross_users():
    async def test_isolation():
        user_one_queue = await security_event_stream.subscribe(4)
        user_two_queue = await security_event_stream.subscribe(999999)

        try:
            security_event_stream.publish(
                user_id=4,
                event_type="SECURITY_EVENT",
                data={
                    "id": 1000000,
                    "agent_id": 1,
                },
            )

            user_one_payload = await asyncio.wait_for(
                user_one_queue.get(),
                timeout=1,
            )

            assert user_one_payload["event"] == "SECURITY_EVENT"
            assert user_one_payload["data"]["id"] == 1000000

            assert user_two_queue.empty()

        finally:
            security_event_stream.unsubscribe(
                user_id=4,
                queue=user_one_queue,
            )

            security_event_stream.unsubscribe(
                user_id=999999,
                queue=user_two_queue,
            )

    asyncio.run(test_isolation())


def test_security_event_stream_unsubscribe():
    async def test_unsubscribe():
        queue = await security_event_stream.subscribe(4)

        security_event_stream.unsubscribe(
            user_id=4,
            queue=queue,
        )

        security_event_stream.publish(
            user_id=4,
            event_type="SECURITY_EVENT",
            data={
                "id": 1000001,
            },
        )

        assert queue.empty()

    asyncio.run(test_unsubscribe())


def test_security_event_stream_endpoint_requires_authentication():
    app.dependency_overrides.clear()

    response = client.get(
        "/api/security-events/stream",
        timeout=2,
    )

    assert response.status_code == 401


def test_security_event_stream_format():
    from app.services.event_stream_service import format_sse_message

    message = format_sse_message(
        event_type="SECURITY_EVENT",
        data={
            "id": 123,
            "decision": "BLOCK",
        },
    )

    assert message.startswith("event: SECURITY_EVENT\n")
    assert 'data: {"id": 123, "decision": "BLOCK"}' in message
    assert message.endswith("\n\n")