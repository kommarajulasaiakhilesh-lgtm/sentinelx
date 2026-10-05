import asyncio
import json
from collections import defaultdict


class SecurityEventStream:
    def __init__(self):
        self._subscribers: dict[
            int,
            set[tuple[asyncio.AbstractEventLoop, asyncio.Queue]]
        ] = defaultdict(set)

    async def subscribe(self, user_id: int) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        loop = asyncio.get_running_loop()

        self._subscribers[user_id].add((loop, queue))

        return queue

    def unsubscribe(
        self,
        user_id: int,
        queue: asyncio.Queue
    ) -> None:
        subscribers = self._subscribers.get(user_id)

        if subscribers is None:
            return

        subscribers_to_remove = {
            subscriber
            for subscriber in subscribers
            if subscriber[1] is queue
        }

        subscribers.difference_update(subscribers_to_remove)

        if not subscribers:
            self._subscribers.pop(user_id, None)

    def publish(
        self,
        user_id: int,
        event_type: str,
        data: dict
    ) -> None:
        subscribers = self._subscribers.get(user_id)

        if not subscribers:
            return

        payload = {
            "event": event_type,
            "data": data
        }

        for loop, queue in list(subscribers):
            loop.call_soon_threadsafe(
                queue.put_nowait,
                payload
            )


security_event_stream = SecurityEventStream()


def serialize_security_event(event) -> dict:
    return {
        "id": event.id,
        "agent_id": event.agent_id,
        "policy_id": event.policy_id,
        "event_type": event.event_type,
        "action": event.action,
        "decision": event.decision,
        "reason": event.reason,
        "event_metadata": event.event_metadata,
        "created_at": event.created_at.isoformat(),
    }


def serialize_security_alert(alert) -> dict:
    return {
        "id": alert.id,
        "agent_id": alert.agent_id,
        "security_event_id": alert.security_event_id,
        "alert_type": alert.alert_type,
        "severity": alert.severity,
        "title": alert.title,
        "description": alert.description,
        "status": alert.status,
        "created_at": alert.created_at.isoformat(),
    }


def serialize_incident(incident) -> dict:
    return {
        "id": incident.id,
        "agent_id": incident.agent_id,
        "title": incident.title,
        "description": incident.description,
        "severity": incident.severity,
        "status": incident.status,
        "created_at": incident.created_at.isoformat(),
        "updated_at": incident.updated_at.isoformat(),
    }


def format_sse_message(event_type: str, data: dict) -> str:
    return (
        f"event: {event_type}\n"
        f"data: {json.dumps(data)}\n\n"
    )