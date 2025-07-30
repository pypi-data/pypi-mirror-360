from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from .base import BaseOphelosModel, Currency
from .customer import Customer
from .organisation import Organisation

if TYPE_CHECKING:
    from .invoice import Invoice, LineItem
    from .payment import Payment, PaymentPlan


class DebtStatus(str, Enum):
    """Debt status enumeration."""

    # Client flow
    INITIALIZING = "initializing"  # Debt is being created
    PREPARED = "prepared"  # Client informs us that the debt is ready to process
    PAUSED = "paused"  # Client requests to pause the debt
    WITHDRAWN = "withdrawn"  # Client withdraws the debt
    DELETED = "deleted"  # Debt is deleted before being processed

    # Ophelos Flow
    ANALYSING = "analysing"  # Debt is being analysed by Data
    RESUMED = "resumed"  # Debt is resumed after being paused
    CONTACTED = "contacted"  # Communication has been sent to the customer regarding this debt
    CONTACT_ESTABLISHED = "contact_established"  # Communication has been established with the customer
    CONTACT_FAILED = "contact_failed"  # Communication with the customer has failed
    ENRICHING = "enriching"  # Debt is being enriched by Data
    RETURNED = "returned"  # Debt is returned to the client
    DISCHARGED = "discharged"  # Debt is discharged/written-off

    # Customer Flow
    ARRANGING = "arranging"  # Customer is arranging payment
    PAYING = "paying"  # Customer is paying
    SETTLED = "settled"  # Debt is settled (POSITIVE END)
    PAID = "paid"  # Debt is fully paid (POSITIVE END)

    # Action Required
    QUERIED = "queried"  # Customer has queried the debt
    DISPUTED = "disputed"  # Customer has disputed the debt
    DEFAULTED = "defaulted"  # Customer has defaulted on the debt
    FOLLOW_UP_REQUIRED = "follow_up_required"  # Follow up is required
    ADJUSTED = "adjusted"  # Client has adjusted the debt

    # Customer Operations
    ASSESSING = "assessing"  # Debt is being assessed by Customer Operations
    RECOVERING = "recovering"  # Customer has been given options to recover paying
    PROCESS_EXHAUSTED = "process_exhausted"  # Debt is closed due to process exhaustion

    # Legal flow
    LEGAL_PROTECTION = "legal_protection"  # Debt is under legal protection (e.g., DRO, bankruptcy, sequestration)

    # Legacy
    CLOSED = "closed"  # Debt is closed as paid in full
    OPEN = "open"  # DO NOT USE Legacy support


class StatusObject(BaseOphelosModel):
    """Status object with metadata."""

    value: DebtStatus
    whodunnit: Optional[str] = None
    context: Optional[str] = None
    reason: Optional[str] = None
    updated_at: datetime


class SummaryBreakdown(BaseOphelosModel):
    """Summary breakdown object."""

    principal: Optional[int] = None
    interest: Optional[int] = None
    fees: Optional[int] = None
    discounts: Optional[int] = None
    charges: Optional[int] = None
    value_added_tax: Optional[int] = None
    miscellaneous: Optional[int] = None
    refunds: Optional[int] = None


class DebtSummary(BaseOphelosModel):
    """Debt summary object."""

    amount_total: Optional[int] = None
    amount_paid: Optional[int] = None
    amount_remaining: Optional[int] = None
    breakdown: Optional[SummaryBreakdown] = None
    history: Optional[List[Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Debt(BaseOphelosModel):
    """Debt model."""

    id: Optional[str] = None
    object: Optional[str] = "debt"
    status: Optional[StatusObject] = None
    kind: Optional[str] = None
    account_number: Optional[str] = None
    customer: Optional[Union[str, "Customer"]] = None  # Can be customer ID or expanded customer object
    customer_id: Optional[str] = None  # Used for API POST or PUT requests
    organisation: Optional[Union[str, "Organisation"]] = None  # Can be organisation ID or expanded organisation object
    organisation_id: Optional[str] = None  # Used for API POST or PUT requests
    originator: Optional[Union[str, Any]] = None  # Can be originator ID, expanded object, or None
    currency: Optional[Currency] = None
    summary: Optional[DebtSummary] = None
    invoices: Optional[List[Union[str, "Invoice"]]] = None  # Can be invoice IDs or expanded invoice objects
    line_items: Optional[List[Union[str, "LineItem"]]] = None  # Can be line_item IDs or expanded objects
    payments: Optional[List[Union[str, "Payment"]]] = None  # Can be payment IDs or expanded payment objects
    payment_plans: Optional[List[Union[str, "PaymentPlan"]]] = None  # Can be payment_plan IDs or expanded objects
    tags: Optional[List[str]] = None
    configurations: Optional[Dict[str, Any]] = None
    calculated_configurations: Optional[Dict[str, Any]] = None
    start_at: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    # Define which fields can be sent in API create/update requests
    __api_body_fields__ = {
        "kind",
        "account_number",
        "customer",
        "customer_id",
        "organisation",
        "organisation_id",
        "originator",
        "currency",
        "invoices",
        "line_items",
        "payments",
        "tags",
        "configurations",
        "start_at",
        "metadata",
    }

    @property
    def balance_amount(self) -> int:
        """Get the remaining balance amount."""
        if self.summary is None:
            return 0
        return self.summary.amount_remaining or 0

    def to_api_body(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert debt model to API body with customer/organisation ID conversion."""
        api_data = super().to_api_body(exclude_none=exclude_none)

        # Convert customer to customer_id
        customer_value = getattr(self, "customer", None)
        if customer_value:
            customer_id = None
            if isinstance(customer_value, str):
                customer_id = customer_value
            elif (
                isinstance(customer_value, Customer) and customer_value.id and not customer_value.id.startswith("temp")
            ):
                customer_id = customer_value.id

            if customer_id:
                api_data["customer_id"] = customer_id
                api_data.pop("customer", None)

        # Convert organisation to organisation_id
        organisation_value = getattr(self, "organisation", None)
        if organisation_value:
            organisation_id = None
            if isinstance(organisation_value, str):
                organisation_id = organisation_value
            elif (
                isinstance(organisation_value, Organisation)
                and organisation_value.id
                and not organisation_value.id.startswith("temp")
            ):
                organisation_id = organisation_value.id

            if organisation_id:
                api_data["organisation_id"] = organisation_id
                api_data.pop("organisation", None)

        return api_data
