from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from .base import BaseOphelosModel

if TYPE_CHECKING:
    from .debt import Debt


class ContactDetailType(str, Enum):
    """Contact detail type enumeration."""

    EMAIL = "email"
    PHONE_NUMBER = "phone_number"
    MOBILE_NUMBER = "mobile_number"
    FAX_NUMBER = "fax_number"
    ADDRESS = "address"


class ContactDetailUsage(str, Enum):
    """Contact detail usage enumeration."""

    PERMANENT = "permanent"
    WORK = "work"
    SUPPLY_ADDRESS = "supply_address"
    DELIVERY_ADDRESS = "delivery_address"
    TEMPORARY = "temporary"


class ContactDetailSource(str, Enum):
    """Contact detail source enumeration."""

    CLIENT = "client"
    CUSTOMER = "customer"
    SUPPORT_AGENT = "support_agent"
    OTHER = "other"


class ContactDetailStatus(str, Enum):
    """Contact detail status enumeration."""

    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    UNDELIVERABLE = "undeliverable"
    DELETED = "deleted"


class ContactDetail(BaseOphelosModel):
    """Contact detail model."""

    id: Optional[str] = None
    object: Optional[str] = "contact_detail"
    type: ContactDetailType
    value: Union[str, Dict[str, Any]]
    primary: Optional[bool] = None
    usage: Optional[ContactDetailUsage] = None
    source: Optional[ContactDetailSource] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    # Define which fields can be sent in API create/update requests
    __api_body_fields__ = {"type", "value", "primary", "usage", "source", "status", "metadata"}


class Customer(BaseOphelosModel):
    """Customer model."""

    id: Optional[str] = None
    object: Optional[str] = "customer"
    kind: Optional[str] = None
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    preferred_locale: Optional[str] = None
    date_of_birth: Optional[date] = None
    contact_details: Optional[List[Union[str, ContactDetail]]] = None  # Can be IDs or objects
    debts: Optional[List[Union[str, "Debt"]]] = None  # Can be IDs or objects
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    # Define which fields can be sent in API create/update requests
    __api_body_fields__ = {
        "kind",
        "full_name",
        "first_name",
        "last_name",
        "preferred_locale",
        "date_of_birth",
        "contact_details",
        "metadata",
    }
