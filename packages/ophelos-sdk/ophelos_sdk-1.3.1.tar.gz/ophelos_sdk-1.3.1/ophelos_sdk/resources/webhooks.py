"""
Webhooks resource manager for Ophelos API.
"""

from typing import Any, Dict, List, Optional, cast

from ..models import PaginatedResponse, Webhook
from .base import BaseResource


class WebhooksResource(BaseResource):
    """Resource manager for webhook operations."""

    def list(
        self,
        limit: Optional[int] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        expand: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> PaginatedResponse:
        """
        List webhooks.

        Args:
            limit: Maximum number of results to return
            after: Cursor for pagination (after this ID)
            before: Cursor for pagination (before this ID)
            expand: List of fields to expand
            **kwargs: Additional query parameters

        Returns:
            Paginated response with webhook data
        """
        params = self._build_list_params(limit, after, before, expand, **kwargs)
        response_tuple = self.http_client.get("webhooks", params=params, return_response=True)
        return self._parse_list_response(response_tuple, Webhook)

    def get(self, webhook_id: str, expand: Optional[List[str]] = None) -> Webhook:
        """
        Get a specific webhook.

        Args:
            webhook_id: Webhook ID
            expand: List of fields to expand

        Returns:
            Webhook instance
        """
        params = self._build_expand_params(expand)
        response_tuple = self.http_client.get(f"webhooks/{webhook_id}", params=params, return_response=True)
        return cast(Webhook, self._parse_response(response_tuple, Webhook))

    def create(self, data: Dict[str, Any], expand: Optional[List[str]] = None) -> Webhook:
        """
        Create a new webhook.

        Args:
            data: Webhook data (url, events, etc.)
            expand: List of fields to expand

        Returns:
            Created webhook instance
        """
        params = self._build_expand_params(expand)
        response_tuple = self.http_client.post("webhooks", data=data, params=params, return_response=True)
        return cast(Webhook, self._parse_response(response_tuple, Webhook))

    def update(self, webhook_id: str, data: Dict[str, Any], expand: Optional[List[str]] = None) -> Webhook:
        """
        Update a webhook.

        Args:
            webhook_id: Webhook ID
            data: Updated webhook data
            expand: List of fields to expand

        Returns:
            Updated webhook instance
        """
        params = self._build_expand_params(expand)
        response_tuple = self.http_client.patch(
            f"webhooks/{webhook_id}", data=data, params=params, return_response=True
        )
        return cast(Webhook, self._parse_response(response_tuple, Webhook))

    def delete(self, webhook_id: str) -> Dict[str, Any]:
        """
        Delete a webhook.

        Args:
            webhook_id: Webhook ID

        Returns:
            Deletion response
        """
        response_tuple = self.http_client.delete(f"webhooks/{webhook_id}", return_response=True)
        response_data, _ = response_tuple
        return cast(Dict[str, Any], response_data)
