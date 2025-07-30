from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from .base import BaseOphelosModel, Currency

if TYPE_CHECKING:
    from .debt import Debt


class PaymentStatus(str, Enum):
    """Payment status enumeration."""

    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    DISPUTED = "disputed"
    REFUNDED = "refunded"
    SCHEDULED = "scheduled"
    CANCELED = "canceled"


class Payment(BaseOphelosModel):
    """Payment model."""

    id: Optional[str] = None
    object: Optional[str] = "payment"
    debt: Optional[Union[str, "Debt"]] = None  # Can be debt ID or expanded debt object
    status: Optional[PaymentStatus] = None
    transaction_at: datetime
    transaction_ref: str
    amount: int  # Amount in cents
    currency: Optional[Currency] = None
    payment_provider: Optional[str] = None
    payment_plan: Optional[Union[str, "PaymentPlan"]] = None  # Can be payment_plan ID or expanded object
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    # Define which fields can be sent in API create/update requests
    __api_body_fields__ = {"transaction_at", "transaction_ref", "amount", "currency", "metadata"}


class PaymentPlan(BaseOphelosModel):
    """Payment plan model."""

    id: Optional[str] = None
    object: Optional[str] = "payment_plan"
    debt: Optional[Union[str, "Debt"]] = None  # Can be debt ID or expanded debt object (from jbuilder)
    status: Optional[str] = None  # From item.status in jbuilder
    schedule: Optional[List[Union[str, Any]]] = None  # Can be schedule IDs or expanded objects (from jbuilder)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
