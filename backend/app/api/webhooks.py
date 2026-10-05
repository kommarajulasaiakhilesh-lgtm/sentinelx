from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.webhook import (
    WebhookEndpointCreate,
    WebhookEndpointResponse,
    WebhookEndpointUpdate,
)
from app.services.webhook_service import (
    create_webhook_endpoint,
    delete_webhook_endpoint,
    get_owned_endpoint,
    list_owned_endpoints,
    update_webhook_endpoint,
)


router = APIRouter(
    prefix="/api/webhooks",
    tags=["Webhooks"]
)


@router.post(
    "",
    response_model=WebhookEndpointResponse,
    status_code=201
)
def create_webhook(
    request: WebhookEndpointCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_webhook_endpoint(
        db=db,
        owner_id=current_user.id,
        name=request.name,
        url=str(request.url),
        secret=request.secret
    )


@router.get(
    "",
    response_model=list[WebhookEndpointResponse]
)
def get_webhooks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return list_owned_endpoints(
        db=db,
        owner_id=current_user.id
    )


@router.get(
    "/{endpoint_id}",
    response_model=WebhookEndpointResponse
)
def get_webhook(
    endpoint_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    endpoint = get_owned_endpoint(
        db=db,
        endpoint_id=endpoint_id,
        owner_id=current_user.id
    )

    if endpoint is None:
        raise HTTPException(
            status_code=404,
            detail="Webhook endpoint not found"
        )

    return endpoint


@router.patch(
    "/{endpoint_id}",
    response_model=WebhookEndpointResponse
)
def update_webhook(
    endpoint_id: int,
    request: WebhookEndpointUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    endpoint = get_owned_endpoint(
        db=db,
        endpoint_id=endpoint_id,
        owner_id=current_user.id
    )

    if endpoint is None:
        raise HTTPException(
            status_code=404,
            detail="Webhook endpoint not found"
        )

    return update_webhook_endpoint(
        db=db,
        endpoint=endpoint,
        name=request.name,
        url=str(request.url) if request.url else None,
        secret=request.secret,
        enabled=request.enabled
    )


@router.delete(
    "/{endpoint_id}",
    status_code=204
)
def delete_webhook(
    endpoint_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    endpoint = get_owned_endpoint(
        db=db,
        endpoint_id=endpoint_id,
        owner_id=current_user.id
    )

    if endpoint is None:
        raise HTTPException(
            status_code=404,
            detail="Webhook endpoint not found"
        )

    delete_webhook_endpoint(
        db=db,
        endpoint=endpoint
    )

    return None