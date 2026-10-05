import asyncio

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.security_event import SecurityEvent
from app.models.user import User
from app.schemas.security_event import SecurityEventListResponse
from app.services.event_stream_service import (
    format_sse_message,
    security_event_stream,
)


router = APIRouter(
    prefix="/api/security-events",
    tags=["Security Events"]
)


@router.get(
    "",
    response_model=SecurityEventListResponse
)
def get_security_events(
    agent_id: int | None = None,
    event_type: str | None = None,
    action: str | None = None,
    decision: str | None = None,
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if page < 1:
        page = 1

    if page_size < 1:
        page_size = 10

    if page_size > 100:
        page_size = 100

    query = (
        db.query(SecurityEvent)
        .join(SecurityEvent.agent)
        .filter(
            SecurityEvent.agent.has(
                owner_id=current_user.id
            )
        )
    )

    if agent_id is not None:
        query = query.filter(
            SecurityEvent.agent_id == agent_id
        )

    if event_type is not None:
        query = query.filter(
            SecurityEvent.event_type == event_type
        )

    if action is not None:
        query = query.filter(
            SecurityEvent.action == action
        )

    if decision is not None:
        query = query.filter(
            SecurityEvent.decision == decision
        )

    total = query.count()

    events = (
        query
        .order_by(
            SecurityEvent.created_at.desc()
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    pages = (total + page_size - 1) // page_size

    return {
        "items": events,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": pages
    }


@router.get(
    "/stream"
)
async def security_event_stream_endpoint(
    current_user: User = Depends(get_current_user)
):
    queue = await security_event_stream.subscribe(
        current_user.id
    )

    async def event_generator():
        try:
            yield ": connected\n\n"

            while True:
                try:
                    payload = await asyncio.wait_for(
                        queue.get(),
                        timeout=15
                    )

                    yield format_sse_message(
                        event_type=payload["event"],
                        data=payload["data"]
                    )

                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"

        except asyncio.CancelledError:
            raise

        finally:
            security_event_stream.unsubscribe(
                current_user.id,
                queue
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )