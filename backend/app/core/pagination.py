"""Standardized offset pagination for list endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil

from sqlalchemy.orm import Query

MAX_PAGE_SIZE = 200
DEFAULT_PAGE_SIZE = 20


@dataclass
class Page:
    items: list
    page: int
    page_size: int
    total: int
    pages: int


def paginate(query: Query, page: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> Page:
    """Apply offset pagination to a SQLAlchemy query and return a Page.

    Clamps page >= 1 and page_size to [1, MAX_PAGE_SIZE].
    """
    page = max(1, page)
    page_size = max(1, min(page_size, MAX_PAGE_SIZE))

    total = query.order_by(None).count()
    pages = ceil(total / page_size) if total else 0

    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return Page(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        pages=pages,
    )
