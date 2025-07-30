"""
Tenants resource manager for Ophelos API.
"""

from typing import Any, Dict, List, Optional, cast

from ..models import Tenant
from .base import BaseResource


class TenantsResource(BaseResource):
    """Resource manager for tenant operations."""

    def get_me(self, expand: Optional[List[str]] = None) -> Tenant:
        """
        Get current tenant information.

        Args:
            expand: List of fields to expand

        Returns:
            Current tenant instance
        """
        params = self._build_expand_params(expand)
        response_tuple = self.http_client.get("tenants/me", params=params, return_response=True)
        return cast(Tenant, self._parse_response(response_tuple, Tenant))

    def update_me(self, data: Dict[str, Any], expand: Optional[List[str]] = None) -> Tenant:
        """
        Update current tenant information.

        Args:
            data: Updated tenant data
            expand: List of fields to expand

        Returns:
            Updated tenant instance
        """
        params = self._build_expand_params(expand)
        response_tuple = self.http_client.patch("tenants/me", data=data, params=params, return_response=True)
        return cast(Tenant, self._parse_response(response_tuple, Tenant))
