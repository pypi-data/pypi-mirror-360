from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from .base import BaseOphelosModel

if TYPE_CHECKING:
    from .customer import ContactDetail


class PaymentOptionsConfiguration(BaseOphelosModel):
    """Payment options configuration model."""

    pay_later_permitted: Optional[bool] = None
    payment_plans_permitted: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class Organisation(BaseOphelosModel):
    """Organisation model."""

    id: Optional[str] = None
    object: Optional[str] = "organisation"
    name: Optional[str] = None
    internal_name: Optional[str] = None
    customer_facing_name: Optional[str] = None
    contact_details: Optional[List[Union[str, "ContactDetail"]]] = None
    configurations: Dict[str, Any] = {}
    deleted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    payment_options_configuration: Optional[PaymentOptionsConfiguration] = None

    # Define which fields can be sent in API create/update requests
    __api_body_fields__ = {
        "name",
        "internal_name",
        "customer_facing_name",
        "industry",
        "logo",
        "contact_details",
        "configurations",
        "metadata",
    }
