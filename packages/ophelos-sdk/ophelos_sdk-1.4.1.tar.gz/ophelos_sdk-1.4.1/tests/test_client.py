"""
Unit tests for Ophelos SDK client.
"""

from unittest.mock import Mock, patch

import pytest

from ophelos_sdk.auth import OAuth2Authenticator
from ophelos_sdk.client import OphelosClient
from ophelos_sdk.http_client import HTTPClient


class TestOphelosClient:
    """Test cases for OphelosClient."""

    @pytest.fixture
    def client_config(self):
        """Client configuration for testing."""
        return {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "audience": "test_audience",
            "environment": "staging",
        }

    @patch("ophelos_sdk.client.OAuth2Authenticator")
    @patch("ophelos_sdk.client.HTTPClient")
    def test_client_initialization_without_tenant_id(self, mock_http_client, mock_authenticator, client_config):
        """Test client initialization without tenant_id."""
        mock_auth_instance = Mock(spec=OAuth2Authenticator)
        mock_authenticator.return_value = mock_auth_instance

        mock_http_instance = Mock(spec=HTTPClient)
        mock_http_client.return_value = mock_http_instance

        client = OphelosClient(**client_config)

        # Verify authenticator was created correctly
        mock_authenticator.assert_called_once_with(
            client_id="test_client_id",
            client_secret="test_client_secret",
            audience="test_audience",
            environment="staging",
        )

        # Verify HTTP client was created without tenant_id
        mock_http_client.assert_called_once_with(
            authenticator=mock_auth_instance,
            base_url="https://api.ophelos.dev",  # staging environment
            timeout=30,
            max_retries=3,
            tenant_id=None,
            version="2025-04-01",
        )

        # Verify resource managers are initialized
        assert hasattr(client, "debts")
        assert hasattr(client, "customers")
        assert hasattr(client, "organisations")
        assert hasattr(client, "line_items")

    @patch("ophelos_sdk.client.OAuth2Authenticator")
    @patch("ophelos_sdk.client.HTTPClient")
    def test_client_initialization_with_tenant_id(self, mock_http_client, mock_authenticator, client_config):
        """Test client initialization with tenant_id."""
        mock_auth_instance = Mock(spec=OAuth2Authenticator)
        mock_authenticator.return_value = mock_auth_instance

        mock_http_instance = Mock(spec=HTTPClient)
        mock_http_client.return_value = mock_http_instance

        tenant_id = "test-tenant-123"
        client = OphelosClient(**client_config, tenant_id=tenant_id)

        # Verify HTTP client was created with tenant_id
        mock_http_client.assert_called_once_with(
            authenticator=mock_auth_instance,
            base_url="https://api.ophelos.dev",  # staging environment
            timeout=30,
            max_retries=3,
            tenant_id=tenant_id,
            version="2025-04-01",
        )

    @patch("ophelos_sdk.client.OAuth2Authenticator")
    @patch("ophelos_sdk.client.HTTPClient")
    def test_client_environment_urls(self, mock_http_client, mock_authenticator, client_config):
        """Test that different environments use correct URLs."""
        mock_auth_instance = Mock(spec=OAuth2Authenticator)
        mock_authenticator.return_value = mock_auth_instance

        mock_http_instance = Mock(spec=HTTPClient)
        mock_http_client.return_value = mock_http_instance

        # Test staging (default)
        client_config["environment"] = "staging"
        OphelosClient(**client_config)
        args, kwargs = mock_http_client.call_args
        assert kwargs["base_url"] == "https://api.ophelos.dev"

        # Test production
        mock_http_client.reset_mock()
        client_config["environment"] = "production"
        OphelosClient(**client_config)
        args, kwargs = mock_http_client.call_args
        assert kwargs["base_url"] == "https://api.ophelos.com"

        # Test development
        mock_http_client.reset_mock()
        client_config["environment"] = "development"
        OphelosClient(**client_config)
        args, kwargs = mock_http_client.call_args
        assert kwargs["base_url"] == "http://api.localhost:3000"

    @patch("ophelos_sdk.client.OAuth2Authenticator")
    @patch("ophelos_sdk.client.HTTPClient")
    def test_client_custom_timeout_and_retries(self, mock_http_client, mock_authenticator, client_config):
        """Test client with custom timeout and retry settings."""
        mock_auth_instance = Mock(spec=OAuth2Authenticator)
        mock_authenticator.return_value = mock_auth_instance

        mock_http_instance = Mock(spec=HTTPClient)
        mock_http_client.return_value = mock_http_instance

        OphelosClient(**client_config, timeout=60, max_retries=5, tenant_id="custom-tenant")

        # Verify HTTP client was created with custom settings
        mock_http_client.assert_called_once_with(
            authenticator=mock_auth_instance,
            base_url="https://api.ophelos.dev",
            timeout=60,
            max_retries=5,
            tenant_id="custom-tenant",
            version="2025-04-01",
        )

    @patch("ophelos_sdk.client.OAuth2Authenticator")
    @patch("ophelos_sdk.client.HTTPClient")
    def test_tenant_id_passed_to_all_requests(self, mock_http_client, mock_authenticator, client_config):
        """Test that tenant_id is passed through to HTTP client for all resource operations."""
        mock_auth_instance = Mock(spec=OAuth2Authenticator)
        mock_authenticator.return_value = mock_auth_instance

        mock_http_instance = Mock(spec=HTTPClient)
        mock_http_client.return_value = mock_http_instance

        tenant_id = "integration-tenant-456"
        client = OphelosClient(**client_config, tenant_id=tenant_id)

        # Verify that the HTTP client instance used by resources has the tenant_id
        # All resources should use the same http_client instance
        assert client.debts.http_client == mock_http_instance
        assert client.customers.http_client == mock_http_instance
        assert client.payments.http_client == mock_http_instance
        assert client.line_items.http_client == mock_http_instance

        # Verify the HTTP client was initialized with the tenant_id
        args, kwargs = mock_http_client.call_args
        assert kwargs["tenant_id"] == tenant_id

    def test_client_initialization_with_access_token(self):
        """Test client initialization with direct access token."""
        access_token = "test_access_token_123"
        client = OphelosClient(access_token=access_token, environment="development")

        # Verify StaticTokenAuthenticator is used
        from ophelos_sdk.auth import StaticTokenAuthenticator

        assert isinstance(client.authenticator, StaticTokenAuthenticator)
        assert client.authenticator.access_token == access_token

    def test_client_initialization_validation_error(self):
        """Test that client raises ValueError when neither access_token nor OAuth2 credentials are provided."""
        with pytest.raises(ValueError, match="client_id, client_secret, and audience are required"):
            OphelosClient()

    def test_client_initialization_with_access_token_and_tenant_id(self):
        """Test client initialization with access token and tenant ID."""
        access_token = "test_access_token_123"
        tenant_id = "test_tenant_456"
        client = OphelosClient(access_token=access_token, tenant_id=tenant_id, environment="development")

        # Verify both access token and tenant ID are set
        from ophelos_sdk.auth import StaticTokenAuthenticator

        assert isinstance(client.authenticator, StaticTokenAuthenticator)
        assert client.authenticator.access_token == access_token
        assert client.http_client.tenant_id == tenant_id

    def test_client_access_token_takes_precedence(self):
        """Test that access_token takes precedence over OAuth2 credentials when both are provided."""
        access_token = "test_access_token_123"
        client = OphelosClient(
            access_token=access_token,
            client_id="should_be_ignored",
            client_secret="should_be_ignored",
            audience="should_be_ignored",
            environment="development",
        )

        # Verify StaticTokenAuthenticator is used instead of OAuth2Authenticator
        from ophelos_sdk.auth import StaticTokenAuthenticator

        assert isinstance(client.authenticator, StaticTokenAuthenticator)
        assert client.authenticator.access_token == access_token

    @patch("ophelos_sdk.client.OAuth2Authenticator")
    @patch("ophelos_sdk.client.HTTPClient")
    def test_client_default_version(self, mock_http_client, mock_authenticator, client_config):
        """Test that client uses default version when none is specified."""
        mock_auth_instance = Mock(spec=OAuth2Authenticator)
        mock_authenticator.return_value = mock_auth_instance

        mock_http_instance = Mock(spec=HTTPClient)
        mock_http_client.return_value = mock_http_instance

        OphelosClient(**client_config)

        # Verify HTTP client was created with default version
        args, kwargs = mock_http_client.call_args
        assert kwargs["version"] == "2025-04-01"

    @patch("ophelos_sdk.client.OAuth2Authenticator")
    @patch("ophelos_sdk.client.HTTPClient")
    def test_client_custom_version(self, mock_http_client, mock_authenticator, client_config):
        """Test that client uses custom version when specified."""
        mock_auth_instance = Mock(spec=OAuth2Authenticator)
        mock_authenticator.return_value = mock_auth_instance

        mock_http_instance = Mock(spec=HTTPClient)
        mock_http_client.return_value = mock_http_instance

        custom_version = "2024-12-01"
        OphelosClient(**client_config, version=custom_version)

        # Verify HTTP client was created with custom version
        args, kwargs = mock_http_client.call_args
        assert kwargs["version"] == custom_version

    @patch("ophelos_sdk.client.OAuth2Authenticator")
    @patch("ophelos_sdk.client.HTTPClient")
    def test_client_no_version(self, mock_http_client, mock_authenticator, client_config):
        """Test that client uses None version when explicitly set to None."""
        mock_auth_instance = Mock(spec=OAuth2Authenticator)
        mock_authenticator.return_value = mock_auth_instance

        mock_http_instance = Mock(spec=HTTPClient)
        mock_http_client.return_value = mock_http_instance

        OphelosClient(**client_config, version=None)

        # Verify HTTP client was created with None version
        args, kwargs = mock_http_client.call_args
        assert kwargs["version"] is None
