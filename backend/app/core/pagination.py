"""Pagination utilities with enforced limits."""

from fastapi import Query
from typing import Optional

from app.core.config import settings

# Maximum page size to prevent abuse
MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 20


def pagination_params(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Items per page"),
) -> tuple[int, int]:
    """Standard pagination parameters with enforced limits.

    Returns:
        Tuple of (page, page_size)
    """
    return page, min(page_size, MAX_PAGE_SIZE)


def paginate(query, page: int, page_size: int):
    """Apply pagination to a SQLAlchemy query.

    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        page_size: Items per page

    Returns:
        tuple of (items, total_count, total_pages)
    """
    total = query.count()
    total_pages = max(1, (total + page_size - 1) // page_size)
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()
    return items, total, total_pages
