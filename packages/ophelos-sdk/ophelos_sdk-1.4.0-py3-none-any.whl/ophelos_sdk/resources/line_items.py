"""
Line Items resource manager for Ophelos API.
"""

from typing import Any, Dict, List, Optional, cast

from ..models import LineItem, PaginatedResponse
from .base import BaseResource


class LineItemsResource(BaseResource):
    """Resource manager for line item operations."""

    def list(
        self,
        debt_id: str,
        limit: Optional[int] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        expand: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> PaginatedResponse:
        """
        List all line items for a debt.

        Args:
            debt_id: Debt ID
            limit: Maximum number of results to return
            after: Cursor for pagination (after this ID)
            before: Cursor for pagination (before this ID)
            expand: List of fields to expand
            **kwargs: Additional query parameters

        Returns:
            Paginated response with line item data
        """
        params = self._build_list_params(limit, after, before, expand, **kwargs)
        response_tuple = self.http_client.get(f"debts/{debt_id}/line_items", params=params, return_response=True)
        return self._parse_list_response(response_tuple, LineItem)

    def create(self, debt_id: str, data: Dict[str, Any]) -> LineItem:
        """
        Create a new line item for a debt.

        Args:
            debt_id: Debt ID
            data: Line item data

        Returns:
            Created line item instance
        """
        response_tuple = self.http_client.post(f"debts/{debt_id}/line_items", data=data, return_response=True)
        return cast(LineItem, self._parse_response(response_tuple, LineItem))
