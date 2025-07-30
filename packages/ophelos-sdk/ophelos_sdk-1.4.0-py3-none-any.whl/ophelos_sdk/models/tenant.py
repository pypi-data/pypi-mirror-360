"""
Tenant-related models for Ophelos SDK.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from .base import BaseOphelosModel


class Tenant(BaseOphelosModel):
    """Tenant model."""

    id: Optional[str] = None
    object: Optional[str] = "tenant"
    name: Optional[str] = None
    description: Optional[str] = None
    configurations: Dict[str, Any] = {}
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
