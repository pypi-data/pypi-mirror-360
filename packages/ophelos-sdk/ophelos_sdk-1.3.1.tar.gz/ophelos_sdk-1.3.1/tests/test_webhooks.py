"""
Unit tests for Ophelos SDK webhook handling.
"""

import hashlib
import hmac
import json
import time
from unittest.mock import patch

import pytest

from ophelos_sdk.exceptions import OphelosError
from ophelos_sdk.models import WebhookEvent
from ophelos_sdk.webhooks import WebhookHandler, construct_event


class TestWebhookHandler:
    """Test cases for webhook handling."""

    @pytest.fixture
    def webhook_secret(self):
        """Webhook secret for testing."""
        return "test_webhook_secret_12345"

    @pytest.fixture
    def webhook_handler(self, webhook_secret):
        """Create webhook handler for testing."""
        return WebhookHandler(webhook_secret)

    @pytest.fixture
    def sample_payload(self, sample_webhook_event):
        """Sample webhook payload as JSON string."""
        return json.dumps(sample_webhook_event)

    def create_signature(self, payload: str, secret: str, timestamp: int = None) -> str:
        """Create a valid webhook signature for testing."""
        if timestamp is None:
            timestamp = int(time.time())

        signed_payload = f"{timestamp}.{payload}"
        signature = hmac.new(secret.encode("utf-8"), signed_payload.encode("utf-8"), hashlib.sha256).hexdigest()

        return f"t={timestamp},v1={signature}"

    def test_webhook_handler_initialization(self, webhook_handler, webhook_secret):
        """Test webhook handler initialization."""
        assert webhook_handler.webhook_secret == webhook_secret

    def test_valid_signature_verification(self, webhook_handler, sample_payload, webhook_secret):
        """Test verification of valid signature."""
        signature_header = self.create_signature(sample_payload, webhook_secret)

        is_valid = webhook_handler.verify_signature(sample_payload, signature_header)
        assert is_valid is True

    def test_invalid_signature_verification(self, webhook_handler, sample_payload):
        """Test verification of invalid signature."""
        # Create signature with wrong secret
        signature_header = self.create_signature(sample_payload, "wrong_secret")

        is_valid = webhook_handler.verify_signature(sample_payload, signature_header)
        assert is_valid is False

    def test_malformed_signature_header(self, webhook_handler, sample_payload):
        """Test handling of malformed signature header."""
        malformed_headers = [
            "invalid_format",
            "t=timestamp",  # Missing signature
            "v1=signature",  # Missing timestamp
            "t=,v1=sig",  # Empty timestamp
            "t=123,v1=",  # Empty signature
        ]

        for header in malformed_headers:
            with pytest.raises(OphelosError) as exc_info:
                webhook_handler.verify_signature(sample_payload, header)
            # The error message can be either direct format error or wrapped error
            error_msg = str(exc_info.value)
            assert "Invalid signature header format" in error_msg or "Error verifying webhook signature" in error_msg

    def test_timestamp_tolerance(self, webhook_handler, sample_payload, webhook_secret):
        """Test timestamp tolerance for replay attack prevention."""
        # Create signature with old timestamp (beyond tolerance)
        old_timestamp = int(time.time()) - 400  # 400 seconds ago (> 300 default tolerance)
        signature_header = self.create_signature(sample_payload, webhook_secret, old_timestamp)

        with pytest.raises(OphelosError) as exc_info:
            webhook_handler.verify_signature(sample_payload, signature_header, tolerance=300)
        assert "Webhook timestamp too old" in str(exc_info.value)

    def test_custom_tolerance(self, webhook_handler, sample_payload, webhook_secret):
        """Test custom timestamp tolerance."""
        # Create signature with timestamp within custom tolerance
        old_timestamp = int(time.time()) - 100  # 100 seconds ago
        signature_header = self.create_signature(sample_payload, webhook_secret, old_timestamp)

        # Should pass with higher tolerance
        is_valid = webhook_handler.verify_signature(sample_payload, signature_header, tolerance=200)
        assert is_valid is True

        # Should fail with lower tolerance
        with pytest.raises(OphelosError):
            webhook_handler.verify_signature(sample_payload, signature_header, tolerance=50)

    def test_parse_valid_event(self, webhook_handler, sample_payload, sample_webhook_event):
        """Test parsing of valid webhook event."""
        event = webhook_handler.parse_event(sample_payload)

        assert isinstance(event, WebhookEvent)
        assert event.id == sample_webhook_event["id"]
        assert event.type == sample_webhook_event["type"]
        assert event.data == sample_webhook_event["data"]
        assert event.livemode == sample_webhook_event["livemode"]

    def test_parse_invalid_json(self, webhook_handler):
        """Test parsing of invalid JSON payload."""
        invalid_payloads = ["invalid json", '{"incomplete": json', "", "null"]

        for payload in invalid_payloads:
            with pytest.raises(OphelosError) as exc_info:
                webhook_handler.parse_event(payload)
            assert "Error parsing webhook payload" in str(exc_info.value)

    def test_verify_and_parse_success(self, webhook_handler, sample_payload, webhook_secret, sample_webhook_event):
        """Test successful verification and parsing in one step."""
        signature_header = self.create_signature(sample_payload, webhook_secret)

        event = webhook_handler.verify_and_parse(sample_payload, signature_header)

        assert isinstance(event, WebhookEvent)
        assert event.id == sample_webhook_event["id"]
        assert event.type == sample_webhook_event["type"]

    def test_verify_and_parse_invalid_signature(self, webhook_handler, sample_payload):
        """Test verification and parsing with invalid signature."""
        # Create a signature with valid timestamp but wrong signature
        current_time = int(time.time())
        invalid_signature = f"t={current_time},v1=invalid_signature"

        with pytest.raises(OphelosError) as exc_info:
            webhook_handler.verify_and_parse(sample_payload, invalid_signature)
        assert "Webhook signature verification failed" in str(exc_info.value)

    def test_construct_event_function(self, sample_payload, webhook_secret, sample_webhook_event):
        """Test the convenience construct_event function."""
        signature_header = self.create_signature(sample_payload, webhook_secret)

        event = construct_event(sample_payload, signature_header, webhook_secret)

        assert isinstance(event, WebhookEvent)
        assert event.id == sample_webhook_event["id"]
        assert event.type == sample_webhook_event["type"]

    def test_construct_event_with_custom_tolerance(self, sample_payload, webhook_secret):
        """Test construct_event with custom tolerance."""
        old_timestamp = int(time.time()) - 100
        signature_header = self.create_signature(sample_payload, webhook_secret, old_timestamp)

        # Should work with higher tolerance
        event = construct_event(sample_payload, signature_header, webhook_secret, tolerance=200)
        assert isinstance(event, WebhookEvent)

        # Should fail with lower tolerance
        with pytest.raises(OphelosError):
            construct_event(sample_payload, signature_header, webhook_secret, tolerance=50)

    def test_webhook_event_types(self, webhook_handler):
        """Test parsing different webhook event types."""
        event_types = [
            "debt.created",
            "debt.updated",
            "debt.closed",
            "debt.withdrawn",
            "payment.succeeded",
            "payment.failed",
            "customer.created",
            "customer.updated",
        ]

        for event_type in event_types:
            event_data = {
                "id": f"evt_{event_type.replace('.', '_')}",
                "object": "event",
                "type": event_type,
                "created_at": "2024-01-15T10:00:00Z",
                "livemode": False,
                "data": {"id": "test_123", "object": event_type.split(".")[0]},
            }

            payload = json.dumps(event_data)
            event = webhook_handler.parse_event(payload)

            assert event.type == event_type
            assert event.id == event_data["id"]

    def test_signature_header_parsing_edge_cases(self, webhook_handler, sample_payload):
        """Test edge cases in signature header parsing."""
        edge_case_headers = [
            "t=123,v1=sig,extra=value",  # Extra parameters (should be ignored)
            " t=123 , v1=signature ",  # Whitespace
            "v1=signature,t=123",  # Different order
        ]

        # These should not raise errors during parsing, but may fail verification
        for header in edge_case_headers:
            try:
                webhook_handler.verify_signature(sample_payload, header)
            except OphelosError as e:
                # Expected to fail verification, but should parse header correctly
                assert "Invalid signature header format" not in str(e)

    def test_constant_time_comparison(self, webhook_handler, sample_payload, webhook_secret):
        """Test that signature comparison uses constant-time comparison."""
        signature_header = self.create_signature(sample_payload, webhook_secret)

        # This test mainly ensures the function completes without timing attacks
        # The actual constant-time behavior is provided by hmac.compare_digest
        with patch("hmac.compare_digest", return_value=True) as mock_compare:
            result = webhook_handler.verify_signature(sample_payload, signature_header)
            assert result is True
            mock_compare.assert_called_once()

    def test_empty_payload_handling(self, webhook_handler, webhook_secret):
        """Test handling of empty payload."""
        empty_payload = ""
        signature_header = self.create_signature(empty_payload, webhook_secret)

        # Signature verification should work for empty payload
        is_valid = webhook_handler.verify_signature(empty_payload, signature_header)
        assert is_valid is True

        # But parsing should fail
        with pytest.raises(OphelosError):
            webhook_handler.parse_event(empty_payload)
