"""
Pagination-related models for Ophelos SDK.
"""

from typing import Any, Dict, List, Optional, Union

from .base import BaseOphelosModel


class PaginatedResponse(BaseOphelosModel):
    """Paginated response model."""

    object: str = "list"
    data: List[Union[Dict[str, Any], BaseOphelosModel]]
    has_more: bool = False
    total_count: Optional[int] = None
    pagination: Optional[Dict[str, Dict[str, Any]]] = None
