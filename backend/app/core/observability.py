
import re
from uuid import uuid4


_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,128}$")


def get_request_id(incoming_request_id: str | None) -> str:
    """Return a validated request ID or generate a new one."""
    if (
        incoming_request_id is not None
        and _REQUEST_ID_PATTERN.fullmatch(incoming_request_id)
    ):
        return incoming_request_id

    return uuid4().hex
