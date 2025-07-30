"""
Contact details resource manager for Ophelos API.
"""

from typing import Any, Dict, List, Optional, Union, cast

from ..models import ContactDetail, PaginatedResponse
from .base import BaseResource


class ContactDetailsResource(BaseResource):
    """Resource manager for contact detail operations."""

    def create(
        self, customer_id: str, data: Union[Dict[str, Any], ContactDetail], expand: Optional[List[str]] = None
    ) -> ContactDetail:
        """
        Create a new contact detail for a customer.

        Creates a new contact detail for a customer. The system automatically checks for duplicates
        and handles deduplication. Contact details are never permanently deleted to prevent
        re-adding invalid or opted-out contact information.

        Args:
            customer_id: Customer ID
            data: Contact detail data (dictionary) or ContactDetail model instance
            expand: List of fields to expand

        Returns:
            Created contact detail instance
        """
        # Prepare data (handles both dict and model instances)
        if hasattr(data, "to_api_body"):
            api_data = data.to_api_body()
        else:
            api_data = data

        if expand:
            params = self._build_expand_params(expand)
            response_tuple = self.http_client.post(
                f"customers/{customer_id}/contact_details", data=api_data, params=params, return_response=True
            )
        else:
            response_tuple = self.http_client.post(
                f"customers/{customer_id}/contact_details", data=api_data, return_response=True
            )
        result = self._parse_response(response_tuple, ContactDetail)
        return cast(ContactDetail, result)

    def update(
        self,
        customer_id: str,
        contact_detail_id: str,
        data: Union[Dict[str, Any], ContactDetail],
        expand: Optional[List[str]] = None,
    ) -> ContactDetail:
        """
        Update an existing contact detail.

        Updates an existing contact detail. When the contact value (email, phone, etc.) is changed,
        the system creates a new contact detail record and marks the previous one as deleted.
        This maintains a complete audit trail and prevents accidental reactivation of invalid
        contact information. Other attributes (status, usage, primary flag) can be updated
        without creating a new record.

        Args:
            customer_id: Customer ID
            contact_detail_id: Contact detail ID
            data: Updated contact detail data (dictionary) or ContactDetail model instance
            expand: List of fields to expand

        Returns:
            Updated contact detail instance
        """
        # Prepare data (handles both dict and model instances)
        if hasattr(data, "to_api_body"):
            api_data = data.to_api_body()
        else:
            api_data = data

        if expand:
            params = self._build_expand_params(expand)
            response_tuple = self.http_client.put(
                f"customers/{customer_id}/contact_details/{contact_detail_id}",
                data=api_data,
                params=params,
                return_response=True,
            )
        else:
            response_tuple = self.http_client.put(
                f"customers/{customer_id}/contact_details/{contact_detail_id}", data=api_data, return_response=True
            )
        result = self._parse_response(response_tuple, ContactDetail)
        return cast(ContactDetail, result)

    def get(self, customer_id: str, contact_detail_id: str, expand: Optional[List[str]] = None) -> ContactDetail:
        """
        Retrieve a specific contact detail by ID.

        Retrieves a single contact detail by ID, regardless of its status. This includes
        contact details marked as deleted, which are retained for audit and deduplication purposes.

        Args:
            customer_id: Customer ID
            contact_detail_id: Contact detail ID
            expand: List of fields to expand

        Returns:
            Contact detail instance
        """
        params = self._build_expand_params(expand)
        response_tuple = self.http_client.get(
            f"customers/{customer_id}/contact_details/{contact_detail_id}", params=params, return_response=True
        )
        result = self._parse_response(response_tuple, ContactDetail)
        return cast(ContactDetail, result)

    def delete(self, customer_id: str, contact_detail_id: str) -> ContactDetail:
        """
        Mark a contact detail as deleted.

        Marks a contact detail as deleted by setting its status to "deleted". This is a soft
        delete operation - the contact detail remains in the database for:

        - Audit and compliance purposes
        - Prevention of re-adding invalid contact information
        - Legal obligation to retain financial records
        - Legitimate interests in debt recovery

        Note: Under GDPR Article 17(3), the right to erasure does not apply where processing
        is necessary for compliance with legal obligations or for the establishment, exercise,
        or defence of legal claims.

        Args:
            customer_id: Customer ID
            contact_detail_id: Contact detail ID

        Returns:
            Updated contact detail instance (with status "deleted")
        """
        response_tuple = self.http_client.delete(
            f"customers/{customer_id}/contact_details/{contact_detail_id}", return_response=True
        )
        result = self._parse_response(response_tuple, ContactDetail)
        return cast(ContactDetail, result)

    def list(
        self,
        customer_id: str,
        limit: Optional[int] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        expand: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> PaginatedResponse:
        """
        List all contact details for a customer.

        Returns a list of all contact details associated with a specific customer, including
        those marked as deleted. Contact details are never permanently removed from the system
        to maintain audit trails and prevent re-addition of invalid contact information.

        Args:
            customer_id: Customer ID
            limit: Maximum number of results to return
            after: Cursor for pagination (after this ID)
            before: Cursor for pagination (before this ID)
            expand: List of fields to expand
            **kwargs: Additional query parameters

        Returns:
            Paginated response with contact detail data
        """
        params = self._build_list_params(limit, after, before, expand, **kwargs)
        response_tuple = self.http_client.get(
            f"customers/{customer_id}/contact_details", params=params, return_response=True
        )
        return self._parse_list_response(response_tuple, ContactDetail)
