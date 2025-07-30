"""
Webhook-related models for Ophelos SDK.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .base import BaseOphelosModel


class Webhook(BaseOphelosModel):
    """Webhook model."""

    id: Optional[str] = None
    object: Optional[str] = "webhook"
    url: str
    enabled: Optional[bool] = None
    signing_key: Optional[str] = None
    enabled_events: Optional[List[str]] = None
    version: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class WebhookEvent(BaseOphelosModel):
    """Webhook event model."""

    id: Optional[str] = None
    object: Optional[str] = "event"
    type: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    livemode: Optional[bool] = None
