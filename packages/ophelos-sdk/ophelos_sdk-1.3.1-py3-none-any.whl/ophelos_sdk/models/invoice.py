from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from .base import BaseOphelosModel, Currency

if TYPE_CHECKING:
    from .debt import Debt


class LineItemKind(str, Enum):
    """Line item kind enumeration."""

    DEBT = "debt"
    INTEREST = "interest"
    FEE = "fee"
    VAT = "vat"
    CREDIT = "credit"  # Amount must be negative
    DISCOUNT = "discount"  # Amount must be negative
    REFUND = "refund"
    CREDITOR_REFUND = "creditor_refund"


class LineItem(BaseOphelosModel):
    """Line item model."""

    id: Optional[str] = None
    object: Optional[str] = "line_item"
    debt_id: Optional[str] = None
    invoice_id: Optional[str] = None
    kind: LineItemKind
    description: Optional[str] = None
    amount: int
    currency: Optional[Currency] = None
    transaction_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    # Define which fields can be sent in API create/update requests
    __api_body_fields__ = {
        "description",
        "kind",
        "amount",
        "currency",
        "transaction_at",
        "metadata",
    }


class Invoice(BaseOphelosModel):
    """Invoice model."""

    id: Optional[str] = None
    object: Optional[str] = "invoice"
    debt: Optional[Union[str, "Debt"]] = None  # Can be debt ID or expanded debt object
    currency: Optional[Currency] = None
    reference: Optional[str] = None
    status: Optional[str] = None
    invoiced_on: Optional[date] = None
    due_on: Optional[date] = None
    description: Optional[str] = None
    line_items: Optional[List[Union[str, LineItem]]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    # Define which fields can be sent in API create/update requests
    __api_body_fields__ = {
        "description",
        "reference",
        "status",
        "invoiced_on",
        "due_on",
        "line_items",
        "metadata",
    }
