"""
Invoices resource manager for Ophelos API.
"""

from typing import Any, Dict, List, Optional, cast

from ..models import Invoice, PaginatedResponse
from .base import BaseResource


class InvoicesResource(BaseResource):
    """Resource manager for invoice operations."""

    def get(self, debt_id: str, invoice_id: str, expand: Optional[List[str]] = None) -> Invoice:
        """
        Get a specific invoice for a debt.

        Args:
            debt_id: Debt ID
            invoice_id: Invoice ID
            expand: List of fields to expand (e.g., ["line_items"])

        Returns:
            Invoice instance
        """
        params = self._build_expand_params(expand)
        response_tuple = self.http_client.get(
            f"debts/{debt_id}/invoices/{invoice_id}", params=params, return_response=True
        )
        return cast(Invoice, self._parse_response(response_tuple, Invoice))

    def create(self, debt_id: str, data: Dict[str, Any]) -> Invoice:
        """
        Create a new invoice for a debt.

        Args:
            debt_id: Debt ID
            data: Invoice data

        Returns:
            Created invoice instance
        """
        response_tuple = self.http_client.post(f"debts/{debt_id}/invoices", data=data, return_response=True)
        return cast(Invoice, self._parse_response(response_tuple, Invoice))

    def update(self, debt_id: str, invoice_id: str, data: Dict[str, Any]) -> Invoice:
        """
        Update an invoice.

        Args:
            debt_id: Debt ID
            invoice_id: Invoice ID
            data: Updated invoice data

        Returns:
            Updated invoice instance
        """
        response_tuple = self.http_client.put(f"debts/{debt_id}/invoices/{invoice_id}", data=data, return_response=True)
        return cast(Invoice, self._parse_response(response_tuple, Invoice))

    def search(
        self,
        debt_id: str,
        query: str,
        limit: Optional[int] = None,
        expand: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> PaginatedResponse:
        """
        Search invoices for a debt.

        Args:
            debt_id: Debt ID
            query: Search query string (e.g., "status:paid")
            limit: Maximum number of results to return
            expand: List of fields to expand
            **kwargs: Additional query parameters

        Returns:
            Paginated response with invoice data
        """
        params = self._build_search_params(query, limit, expand, **kwargs)
        response_tuple = self.http_client.get(f"debts/{debt_id}/invoices/search", params=params, return_response=True)
        return self._parse_list_response(response_tuple, Invoice)
