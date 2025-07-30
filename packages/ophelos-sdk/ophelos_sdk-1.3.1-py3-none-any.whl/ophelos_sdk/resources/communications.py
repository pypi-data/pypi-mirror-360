"""
Communications resource manager for Ophelos API.
"""

from typing import Any, List, Optional

from ..models import Communication, PaginatedResponse
from .base import BaseResource


class CommunicationsResource(BaseResource):
    """Resource manager for communication operations."""

    def list(
        self,
        limit: Optional[int] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        expand: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> PaginatedResponse:
        """
        List communications.

        Args:
            limit: Maximum number of results to return
            after: Cursor for pagination (after this ID)
            before: Cursor for pagination (before this ID)
            expand: List of fields to expand
            **kwargs: Additional query parameters

        Returns:
            Paginated response with communication data
        """
        params = self._build_list_params(limit, after, before, expand, **kwargs)
        response_tuple = self.http_client.get("communications", params=params, return_response=True)
        return self._parse_list_response(response_tuple, Communication)
