"""
Ophelos SDK Models Package

This package contains all Pydantic models for Ophelos API data structures.
Models are organized by domain for better maintainability.
"""

# Import all models for backward compatibility
from .base import BaseOphelosModel, Currency
from .communication import Communication, CommunicationTemplate
from .customer import (
    ContactDetail,
    ContactDetailSource,
    ContactDetailStatus,
    ContactDetailType,
    ContactDetailUsage,
    Customer,
)
from .debt import Debt, DebtStatus, DebtSummary, StatusObject, SummaryBreakdown
from .invoice import Invoice, LineItem, LineItemKind
from .organisation import Organisation, PaymentOptionsConfiguration
from .pagination import PaginatedResponse
from .payment import Payment, PaymentPlan, PaymentStatus
from .payout import Payout
from .tenant import Tenant
from .webhook import Webhook, WebhookEvent

# Rebuild models to resolve forward references
Customer.model_rebuild()
Debt.model_rebuild()
Payment.model_rebuild()
PaymentPlan.model_rebuild()
Invoice.model_rebuild()
Communication.model_rebuild()
Organisation.model_rebuild()

# Export all models
__all__ = [
    # Base
    "BaseOphelosModel",
    "Currency",
    # Customer
    "Customer",
    "ContactDetail",
    "ContactDetailType",
    "ContactDetailUsage",
    "ContactDetailSource",
    "ContactDetailStatus",
    # Debt
    "Debt",
    "DebtStatus",
    "StatusObject",
    "DebtSummary",
    "SummaryBreakdown",
    # Payment
    "Payment",
    "PaymentPlan",
    "PaymentStatus",
    # Invoice
    "Invoice",
    "LineItem",
    "LineItemKind",
    # Communication
    "Communication",
    "CommunicationTemplate",
    # Webhook
    "Webhook",
    "WebhookEvent",
    # Organisation
    "Organisation",
    "PaymentOptionsConfiguration",
    # Tenant
    "Tenant",
    # Payout
    "Payout",
    # Pagination
    "PaginatedResponse",
]
