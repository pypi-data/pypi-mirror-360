"""
Unit tests for Ophelos SDK authentication module.
"""

import time
from unittest.mock import Mock, patch

import pytest
import requests

from ophelos_sdk.auth import OAuth2Authenticator, StaticTokenAuthenticator
from ophelos_sdk.exceptions import AuthenticationError


class TestOAuth2Authenticator:
    """Test cases for OAuth2 authentication."""

    @pytest.fixture
    def auth_config(self):
        """Authentication configuration for testing."""
        return {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "audience": "test_audience",
            "environment": "development",
        }

    @pytest.fixture
    def authenticator(self, auth_config):
        """Create authenticator instance for testing."""
        return OAuth2Authenticator(**auth_config)

    def test_authenticator_initialization(self, authenticator):
        """Test authenticator initialization."""
        assert authenticator.client_id == "test_client_id"
        assert authenticator.client_secret == "test_client_secret"
        assert authenticator.audience == "test_audience"
        assert authenticator.environment == "development"
        assert "ophelos-dev" in authenticator.token_url

    def test_production_environment_url(self):
        """Test production environment uses correct URL."""
        auth = OAuth2Authenticator(client_id="test", client_secret="test", audience="test", environment="production")
        assert "ophelos.eu.auth0.com" in auth.token_url

    @patch("requests.post")
    def test_successful_token_fetch(self, mock_post, authenticator, mock_auth_response):
        """Test successful token fetch."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = mock_auth_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        token = authenticator.get_access_token()

        assert token == mock_auth_response["access_token"]
        assert authenticator._access_token == token
        assert authenticator._token_expires_at is not None

        # Verify the request was made with correct parameters
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["data"]["grant_type"] == "client_credentials"
        assert call_args[1]["data"]["client_id"] == "test_client_id"
        assert call_args[1]["data"]["client_secret"] == "test_client_secret"
        assert call_args[1]["data"]["audience"] == "test_audience"

    @patch("requests.post")
    def test_token_reuse_when_valid(self, mock_post, authenticator, mock_auth_response):
        """Test that valid tokens are reused."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = mock_auth_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # First call
        token1 = authenticator.get_access_token()

        # Second call should reuse token
        token2 = authenticator.get_access_token()

        assert token1 == token2
        # Should only call the API once
        assert mock_post.call_count == 1

    @patch("requests.post")
    def test_token_refresh_when_expired(self, mock_post, authenticator, mock_auth_response):
        """Test token refresh when expired."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = mock_auth_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Get initial token
        token1 = authenticator.get_access_token()

        # Simulate token expiration
        authenticator._token_expires_at = time.time() - 100

        # Second call should refresh token
        token2 = authenticator.get_access_token()

        assert token1 == token2  # Same token value, but refreshed
        # Should call the API twice
        assert mock_post.call_count == 2

    @patch("requests.post")
    def test_http_error_handling(self, mock_post, authenticator):
        """Test handling of HTTP errors."""
        # Mock HTTP error
        mock_post.side_effect = requests.RequestException("Network error")

        with pytest.raises(AuthenticationError) as exc_info:
            authenticator.get_access_token()

        assert "Failed to request access token" in str(exc_info.value)
        assert "Network error" in str(exc_info.value)

    @patch("requests.post")
    def test_invalid_json_response(self, mock_post, authenticator):
        """Test handling of invalid JSON response."""
        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Invalid response"
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        with pytest.raises(AuthenticationError) as exc_info:
            authenticator.get_access_token()

        assert "Invalid token response format" in str(exc_info.value)

    @patch("requests.post")
    def test_missing_access_token_in_response(self, mock_post, authenticator):
        """Test handling of response without access token."""
        # Mock response without access_token
        mock_response = Mock()
        mock_response.json.return_value = {"token_type": "Bearer"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        with pytest.raises(AuthenticationError) as exc_info:
            authenticator.get_access_token()

        assert "Missing access_token in response" in str(exc_info.value)

    def test_get_auth_headers(self, authenticator, mock_auth_response):
        """Test getting authentication headers."""
        with patch.object(authenticator, "get_access_token", return_value=mock_auth_response["access_token"]):
            headers = authenticator.get_auth_headers()

        expected_header = f"Bearer {mock_auth_response['access_token']}"
        assert headers["Authorization"] == expected_header

    def test_invalidate_token(self, authenticator):
        """Test token invalidation."""
        # Set some token data
        authenticator._access_token = "some_token"
        authenticator._token_expires_at = time.time() + 3600

        # Invalidate
        authenticator.invalidate_token()

        assert authenticator._access_token is None
        assert authenticator._token_expires_at is None

    def test_token_expiry_buffer(self, authenticator):
        """Test that token expiry includes buffer time."""
        # Set token to expire in 30 seconds (less than 60 second buffer)
        authenticator._access_token = "test_token"
        authenticator._token_expires_at = time.time() + 30

        # Should be considered expired due to buffer
        assert not authenticator._is_token_valid()

        # Set token to expire in 120 seconds (more than 60 second buffer)
        authenticator._token_expires_at = time.time() + 120

        # Should be considered valid
        assert authenticator._is_token_valid()

    @patch("requests.post")
    def test_default_expires_in_handling(self, mock_post, authenticator):
        """Test handling of missing expires_in in response."""
        # Mock response without expires_in
        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "test_token",
            "token_type": "Bearer",
            # Missing expires_in
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        token = authenticator.get_access_token()

        assert token == "test_token"
        # Should default to 1 hour (3600 seconds)
        expected_expiry = time.time() + 3600
        assert abs(authenticator._token_expires_at - expected_expiry) < 10


class TestStaticTokenAuthenticator:
    """Test cases for StaticTokenAuthenticator."""

    def test_static_token_initialization(self):
        """Test StaticTokenAuthenticator initialization."""
        access_token = "test_static_token_123"
        authenticator = StaticTokenAuthenticator(access_token=access_token)

        assert authenticator.access_token == access_token

    def test_get_access_token(self):
        """Test getting access token from static authenticator."""
        access_token = "test_static_token_123"
        authenticator = StaticTokenAuthenticator(access_token=access_token)

        token = authenticator.get_access_token()
        assert token == access_token

    def test_get_auth_headers(self):
        """Test getting authentication headers from static authenticator."""
        access_token = "test_static_token_123"
        authenticator = StaticTokenAuthenticator(access_token=access_token)

        headers = authenticator.get_auth_headers()
        assert headers["Authorization"] == f"Bearer {access_token}"

    def test_invalidate_token_no_op(self):
        """Test that invalidate_token is a no-op for static authenticator."""
        access_token = "test_static_token_123"
        authenticator = StaticTokenAuthenticator(access_token=access_token)

        # Should not raise any errors
        authenticator.invalidate_token()

        # Token should still be available
        assert authenticator.get_access_token() == access_token
