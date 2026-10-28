import asyncio
import json
from collections import defaultdict
# Subscribers are stored in process-local memory. With multiple backend
# workers, events published by one worker are not delivered to subscribers
# connected to another worker. Use shared pub/sub for multi-worker delivery.


MAX_SUBSCRIBERS_PER_USER = 5
MAX_QUEUED_EVENTS_PER_SUBSCRIBER = 100


class SubscriberLimitExceeded(Exception):
    pass


class SecurityEventStream:
    def __init__(self):
        self._subscribers: dict[
            int,
            set[tuple[asyncio.AbstractEventLoop, asyncio.Queue]]
        ] = defaultdict(set)

    async def subscribe(self, user_id: int) -> asyncio.Queue:
        subscribers = self._subscribers[user_id]
        if len(subscribers) >= MAX_SUBSCRIBERS_PER_USER:
            raise SubscriberLimitExceeded

        queue: asyncio.Queue = asyncio.Queue(
            maxsize=MAX_QUEUED_EVENTS_PER_SUBSCRIBER
        )
        loop = asyncio.get_running_loop()

        subscribers.add((loop, queue))

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
                self._enqueue_latest,
                queue,
                payload
            )

    @staticmethod
    def _enqueue_latest(queue: asyncio.Queue, payload: dict) -> None:
        if queue.full():
            try:
                while True:
                    queue.get_nowait()
            except asyncio.QueueEmpty:
                pass

            # The client consumes stream events as cache invalidations. Tell
            # it to refresh all relevant views after dropping queued events.
            payload = {"event": "STREAM_RESET", "data": {}}

        try:
            queue.put_nowait(payload)
        except asyncio.QueueFull:
            # Another queued callback may have filled the queue first.
            pass


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
