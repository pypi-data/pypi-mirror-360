"""
Webhook validation and handling utilities.
"""

import hashlib
import hmac
import time

from .exceptions import OphelosError
from .models import WebhookEvent


class WebhookHandler:
    """Handler for validating and parsing Ophelos webhook events."""

    def __init__(self, webhook_secret: str):
        """
        Initialize webhook handler.

        Args:
            webhook_secret: Secret key for webhook signature validation
        """
        self.webhook_secret = webhook_secret

    def verify_signature(self, payload: str, signature_header: str, tolerance: int = 300) -> bool:
        """
        Verify webhook signature using HMAC-SHA256.

        Args:
            payload: Raw webhook payload as string
            signature_header: Value of Ophelos-Signature header
            tolerance: Maximum age of webhook in seconds (default: 5 minutes)

        Returns:
            True if signature is valid, False otherwise

        Raises:
            OphelosError: If signature format is invalid
        """
        try:
            # Parse signature header
            elements = signature_header.split(",")
            signature_dict = {}

            for element in elements:
                key, value = element.strip().split("=", 1)
                signature_dict[key] = value

            timestamp = signature_dict.get("t")
            signature = signature_dict.get("v1")

            if not timestamp or not signature:
                raise OphelosError("Invalid signature header format")

            # Check timestamp tolerance
            webhook_time = int(timestamp)
            current_time = int(time.time())

            if abs(current_time - webhook_time) > tolerance:
                raise OphelosError("Webhook timestamp too old")

            # Create signed payload
            signed_payload = f"{timestamp}.{payload}"

            # Calculate expected signature
            expected_signature = hmac.new(
                self.webhook_secret.encode("utf-8"), signed_payload.encode("utf-8"), hashlib.sha256
            ).hexdigest()

            # Compare signatures using constant-time comparison
            return hmac.compare_digest(signature, expected_signature)

        except (ValueError, KeyError) as e:
            raise OphelosError(f"Error verifying webhook signature: {str(e)}")

    def parse_event(self, payload: str) -> WebhookEvent:
        """
        Parse webhook payload into WebhookEvent object.

        Args:
            payload: JSON payload string

        Returns:
            WebhookEvent instance

        Raises:
            OphelosError: If payload parsing fails
        """
        try:
            import json

            data = json.loads(payload)
            return WebhookEvent(**data)
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            raise OphelosError(f"Error parsing webhook payload: {str(e)}")

    def verify_and_parse(self, payload: str, signature_header: str, tolerance: int = 300) -> WebhookEvent:
        """
        Verify signature and parse webhook event in one step.

        Args:
            payload: Raw webhook payload as string
            signature_header: Value of Ophelos-Signature header
            tolerance: Maximum age of webhook in seconds

        Returns:
            WebhookEvent instance

        Raises:
            OphelosError: If verification or parsing fails
        """
        if not self.verify_signature(payload, signature_header, tolerance):
            raise OphelosError("Webhook signature verification failed")

        return self.parse_event(payload)


def construct_event(payload: str, signature_header: str, webhook_secret: str, tolerance: int = 300) -> WebhookEvent:
    """
    Convenience function to verify and parse a webhook event.

    Args:
        payload: Raw webhook payload as string
        signature_header: Value of Ophelos-Signature header
        webhook_secret: Secret key for webhook signature validation
        tolerance: Maximum age of webhook in seconds

    Returns:
        WebhookEvent instance

    Raises:
        OphelosError: If verification or parsing fails
    """
    handler = WebhookHandler(webhook_secret)
    return handler.verify_and_parse(payload, signature_header, tolerance)
