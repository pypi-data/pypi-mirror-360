"""
Resource managers for Ophelos API endpoints.
"""

from .base import BaseResource
from .communications import CommunicationsResource
from .contact_details import ContactDetailsResource
from .customers import CustomersResource
from .debts import DebtsResource
from .invoices import InvoicesResource
from .line_items import LineItemsResource
from .organisations import OrganisationsResource
from .payment_plans import PaymentPlansResource
from .payments import PaymentsResource
from .payouts import PayoutsResource
from .tenants import TenantsResource
from .webhooks import WebhooksResource

__all__ = [
    "BaseResource",
    "DebtsResource",
    "CustomersResource",
    "ContactDetailsResource",
    "OrganisationsResource",
    "PaymentsResource",
    "InvoicesResource",
    "LineItemsResource",
    "WebhooksResource",
    "PaymentPlansResource",
    "CommunicationsResource",
    "PayoutsResource",
    "TenantsResource",
]
