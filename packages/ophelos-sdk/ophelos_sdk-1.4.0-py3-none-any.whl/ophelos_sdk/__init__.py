"""
Ophelos Python SDK

Python SDK for the Ophelos API - a comprehensive debt management platform.
"""

from .client import OphelosClient
from .exceptions import (
    AuthenticationError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    OphelosAPIError,
    OphelosError,
    ParseError,
    RateLimitError,
    ServerError,
    TimeoutError,
    UnexpectedError,
    ValidationError,
)
from .webhooks import WebhookHandler, construct_event

__version__ = "1.4.0"
__author__ = "Ophelos"
__email__ = "support@ophelos.com"

__all__ = [
    # Core client
    "OphelosClient",
    # Exceptions
    "OphelosError",
    "OphelosAPIError",
    "AuthenticationError",
    "ValidationError",
    "NotFoundError",
    "RateLimitError",
    "ConflictError",
    "ForbiddenError",
    "ServerError",
    "TimeoutError",
    "UnexpectedError",
    "ParseError",
    # Webhook handling
    "WebhookHandler",
    "construct_event",
]
