from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from .base import BaseOphelosModel

if TYPE_CHECKING:
    from .customer import ContactDetail
    from .debt import Debt


class CommunicationTemplate(BaseOphelosModel):
    """Communication template model."""

    id: str
    object: str = "communication_template"
    name: str
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None


class Communication(BaseOphelosModel):
    """Communication model."""

    id: str
    object: str = "communication"
    debt: Union[str, "Debt"]
    template: Optional[Union[str, CommunicationTemplate]] = None
    status: str
    provider: Optional[str] = None
    provider_reference: Optional[str] = None
    direction: str = "outbound"
    delivery_method: Optional[str] = None
    contact_detail: Optional[Union[str, "ContactDetail"]] = None
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None
