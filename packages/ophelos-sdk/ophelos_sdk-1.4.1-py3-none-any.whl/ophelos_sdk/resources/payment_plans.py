"""
Payment Plans resource manager for Ophelos API.
"""

from typing import Any, Dict, List, Optional, cast

from ..models import PaginatedResponse, PaymentPlan
from .base import BaseResource


class PaymentPlansResource(BaseResource):
    """Resource manager for payment plan operations."""

    def list(
        self,
        limit: Optional[int] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        expand: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> PaginatedResponse:
        """
        List payment plans.

        Args:
            limit: Maximum number of results to return
            after: Cursor for pagination (after this ID)
            before: Cursor for pagination (before this ID)
            expand: List of fields to expand
            **kwargs: Additional query parameters

        Returns:
            Paginated response with payment plan data
        """
        params = self._build_list_params(limit, after, before, expand, **kwargs)
        response_tuple = self.http_client.get("payment_plans", params=params, return_response=True)
        return self._parse_list_response(response_tuple, PaymentPlan)

    def reschedule(self, plan_id: str, data: Dict[str, Any]) -> PaymentPlan:
        """
        Reschedule a payment plan.

        Args:
            plan_id: Payment plan ID
            data: Reschedule data (e.g., new dates, amounts)

        Returns:
            Updated payment plan instance
        """
        response_tuple = self.http_client.patch(f"payment_plans/{plan_id}/reschedule", data=data, return_response=True)
        return cast(PaymentPlan, self._parse_response(response_tuple, PaymentPlan))

    def delay(self, plan_id: str, data: Dict[str, Any]) -> PaymentPlan:
        """
        Delay a payment plan.

        Args:
            plan_id: Payment plan ID
            data: Delay data (e.g., delay period, reason)

        Returns:
            Updated payment plan instance
        """
        response_tuple = self.http_client.patch(f"payment_plans/{plan_id}/delay", data=data, return_response=True)
        return cast(PaymentPlan, self._parse_response(response_tuple, PaymentPlan))

    def get(self, plan_id: str, expand: Optional[List[str]] = None) -> PaymentPlan:
        """
        Get a specific payment plan by ID.

        Args:
            plan_id: Payment plan ID
            expand: List of fields to expand

        Returns:
            Payment plan instance
        """
        params = self._build_expand_params(expand)
        response_tuple = self.http_client.get(f"payment-plans/{plan_id}", params=params, return_response=True)
        return cast(PaymentPlan, self._parse_response(response_tuple, PaymentPlan))

    def create(self, data: Dict[str, Any], expand: Optional[List[str]] = None) -> PaymentPlan:
        """
        Create a new payment plan.

        Args:
            data: Payment plan data
            expand: List of fields to expand

        Returns:
            Created payment plan instance
        """
        params = self._build_expand_params(expand)
        response_tuple = self.http_client.post("payment-plans", data=data, params=params, return_response=True)
        return cast(PaymentPlan, self._parse_response(response_tuple, PaymentPlan))
