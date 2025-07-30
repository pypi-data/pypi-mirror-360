"""
Unit tests for Ophelos SDK HTTP client.
"""

from unittest.mock import Mock, patch

import pytest
from urllib3.util.retry import Retry

from ophelos_sdk.auth import OAuth2Authenticator
from ophelos_sdk.exceptions import (
    AuthenticationError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    OphelosAPIError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError,
)
from ophelos_sdk.http_client import HTTPClient, JitteredRetry


class TestHTTPClient:
    """Test cases for HTTP client."""

    @pytest.fixture
    def mock_authenticator(self):
        """Mock authenticator for testing."""
        auth = Mock(spec=OAuth2Authenticator)
        auth.get_auth_headers.return_value = {"Authorization": "Bearer test_token"}
        return auth

    @pytest.fixture
    def http_client(self, mock_authenticator):
        """Create HTTP client for testing."""
        return HTTPClient(
            authenticator=mock_authenticator,
            base_url="https://api.test.com",
            timeout=30,
            max_retries=3,
        )

    def test_http_client_initialization(self, http_client, mock_authenticator):
        """Test HTTP client initialization."""
        assert http_client.authenticator == mock_authenticator
        assert http_client.base_url == "https://api.test.com"
        assert http_client.timeout == 30

    def test_prepare_headers(self, http_client):
        """Test header preparation."""
        headers = http_client._prepare_headers()

        expected_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "ophelos-python-sdk/1.4.1",
            "Authorization": "Bearer test_token",
        }

        assert headers == expected_headers

    def test_prepare_headers_with_custom_headers(self, http_client):
        """Test header preparation with custom headers."""
        custom_headers = {"X-Custom-Header": "custom_value"}
        headers = http_client._prepare_headers(custom_headers)

        assert headers["X-Custom-Header"] == "custom_value"
        assert headers["Authorization"] == "Bearer test_token"
        assert headers["Content-Type"] == "application/json"

    @patch("requests.Session.request")
    def test_successful_get_request(self, mock_request, http_client):
        """Test successful GET request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test_123", "status": "success"}
        mock_response.content = b'{"test": "data"}'
        mock_request.return_value = mock_response

        result = http_client.get("/test/endpoint", params={"limit": 10})

        assert result == {"id": "test_123", "status": "success"}
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[0][0] == "GET"
        assert call_args[0][1] == "https://api.test.com/test/endpoint"
        assert call_args[1]["params"] == {"limit": 10}

    @patch("requests.Session.request")
    def test_successful_post_request(self, mock_request, http_client):
        """Test successful POST request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "new_123", "created": True}
        mock_response.content = b'{"test": "data"}'
        mock_request.return_value = mock_response

        data = {"name": "Test Object"}
        result = http_client.post("/test/endpoint", data=data)

        assert result == {"id": "new_123", "created": True}
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[0][0] == "POST"
        assert call_args[1]["json"] == data

    @patch("requests.Session.request")
    def test_successful_put_request(self, mock_request, http_client):
        """Test successful PUT request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test_123", "updated": True}
        mock_response.content = b'{"test": "data"}'
        mock_request.return_value = mock_response

        data = {"name": "Updated Object"}
        result = http_client.put("/test/endpoint/123", data=data)

        assert result == {"id": "test_123", "updated": True}

    @patch("requests.Session.request")
    def test_successful_patch_request(self, mock_request, http_client):
        """Test successful PATCH request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test_123", "patched": True}
        mock_response.content = b'{"test": "data"}'
        mock_request.return_value = mock_response

        data = {"status": "updated"}
        result = http_client.patch("/test/endpoint/123", data=data)

        assert result == {"id": "test_123", "patched": True}

    @patch("requests.Session.request")
    def test_successful_delete_request(self, mock_request, http_client):
        """Test successful DELETE request."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.json.return_value = {}
        mock_response.content = b""
        mock_request.return_value = mock_response

        result = http_client.delete("/test/endpoint/123")

        assert result == {}

    def test_error_handling_401_authentication_error(self, http_client, mock_authenticator):
        """Test handling of 401 authentication errors."""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"message": "Unauthorized"}
            mock_response.content = b'{"message": "Unauthorized"}'
            mock_request.return_value = mock_response

            with pytest.raises(AuthenticationError) as exc_info:
                http_client.get("/test/endpoint")

            assert "Unauthorized" in str(exc_info.value)
            # Should invalidate token on 401
            mock_authenticator.invalidate_token.assert_called_once()

    def test_error_handling_403_forbidden_error(self, http_client):
        """Test handling of 403 forbidden errors."""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 403
            mock_response.json.return_value = {"message": "Forbidden"}
            mock_response.content = b'{"message": "Forbidden"}'
            mock_request.return_value = mock_response

            with pytest.raises(ForbiddenError) as exc_info:
                http_client.get("/test/endpoint")

            assert "Forbidden" in str(exc_info.value)

    def test_error_handling_404_not_found_error(self, http_client):
        """Test handling of 404 not found errors."""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.json.return_value = {"message": "Not Found"}
            mock_response.content = b'{"message": "Not Found"}'
            mock_request.return_value = mock_response

            with pytest.raises(NotFoundError) as exc_info:
                http_client.get("/test/endpoint")

            assert "Not Found" in str(exc_info.value)
            assert exc_info.value.response_raw is mock_response

    def test_error_handling_409_conflict_error(self, http_client):
        """Test handling of 409 conflict errors."""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 409
            mock_response.json.return_value = {"message": "Conflict"}
            mock_response.content = b'{"message": "Conflict"}'
            mock_request.return_value = mock_response

            with pytest.raises(ConflictError) as exc_info:
                http_client.post("/test/endpoint", data={})

            assert "Conflict" in str(exc_info.value)

    def test_error_handling_422_validation_error(self, http_client):
        """Test handling of 422 validation errors."""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 422
            mock_response.json.return_value = {
                "message": "Validation failed",
                "errors": {"field": ["is required"]},
            }
            mock_response.content = b'{"message": "Validation failed"}'
            mock_request.return_value = mock_response

            with pytest.raises(ValidationError) as exc_info:
                http_client.post("/test/endpoint", data={})

            assert "Validation failed" in str(exc_info.value)

    def test_error_handling_429_rate_limit_error(self, http_client):
        """Test handling of 429 rate limit errors."""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.json.return_value = {"message": "Too Many Requests"}
            mock_response.content = b'{"message": "Too Many Requests"}'
            mock_request.return_value = mock_response

            with pytest.raises(RateLimitError) as exc_info:
                http_client.get("/test/endpoint")

            assert "Too Many Requests" in str(exc_info.value)

    def test_error_handling_500_server_error(self, http_client):
        """Test handling of 500 server errors."""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.json.return_value = {"message": "Internal Server Error"}
            mock_response.content = b'{"message": "Internal Server Error"}'
            mock_request.return_value = mock_response

            with pytest.raises(ServerError) as exc_info:
                http_client.get("/test/endpoint")

            assert "Internal Server Error" in str(exc_info.value)
            assert exc_info.value.status_code == 500

    def test_error_handling_generic_4xx_error(self, http_client):
        """Test handling of generic 4xx errors."""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 418  # I'm a teapot
            mock_response.json.return_value = {"message": "I'm a teapot"}
            mock_response.content = b'{"message": "I\'m a teapot"}'
            mock_request.return_value = mock_response

            with pytest.raises(OphelosAPIError) as exc_info:
                http_client.get("/test/endpoint")

            assert "I'm a teapot" in str(exc_info.value)
            assert exc_info.value.status_code == 418

    def test_response_without_json_content(self, http_client):
        """Test handling of responses without JSON content."""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b""  # No content
            mock_response.json.return_value = {}
            mock_request.return_value = mock_response

            result = http_client.get("/test/endpoint")
            assert result == {}

    def test_response_with_invalid_json(self, http_client):
        """Test handling of responses with invalid JSON."""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_response.text = "Invalid response text"
            mock_response.content = b"invalid json"
            mock_request.return_value = mock_response

            with pytest.raises(OphelosAPIError) as exc_info:
                http_client.get("/test/endpoint")

            # Should use response text as message
            assert "Invalid response text" in str(exc_info.value)

    def test_base_url_path_handling(self, http_client):
        """Test proper handling of base URL and path combinations."""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            mock_response.content = b"{}"
            mock_request.return_value = mock_response

            # Test various path formats
            test_cases = [
                ("/test/endpoint", "https://api.test.com/test/endpoint"),
                ("test/endpoint", "https://api.test.com/test/endpoint"),
                ("/test/endpoint/", "https://api.test.com/test/endpoint/"),
                ("test/endpoint/", "https://api.test.com/test/endpoint/"),
            ]

            for path, expected_url in test_cases:
                http_client.get(path)
                call_args = mock_request.call_args
                # Should result in proper URL
                assert call_args[0][1] == expected_url

    def test_timeout_configuration(self, mock_authenticator):
        """Test timeout configuration."""
        client = HTTPClient(authenticator=mock_authenticator, base_url="https://api.test.com", timeout=60)

        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            mock_response.content = b"{}"
            mock_request.return_value = mock_response

            client.get("/test")

            call_args = mock_request.call_args
            assert call_args[1]["timeout"] == 60

    def test_tenant_id_header(self, mock_authenticator):
        """Test that OPHELOS_TENANT_ID header is added when tenant_id is set."""
        tenant_id = "test-tenant-123"
        client = HTTPClient(authenticator=mock_authenticator, base_url="https://api.test.com", tenant_id=tenant_id)

        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            mock_response.content = b"{}"
            mock_request.return_value = mock_response

            client.get("/test")

            call_args = mock_request.call_args
            headers = call_args[1]["headers"]
            assert "OPHELOS_TENANT_ID" in headers
            assert headers["OPHELOS_TENANT_ID"] == tenant_id

    def test_no_tenant_id_header_when_not_set(self, mock_authenticator):
        """Test that OPHELOS_TENANT_ID header is not added when tenant_id is None."""
        client = HTTPClient(authenticator=mock_authenticator, base_url="https://api.test.com", tenant_id=None)

        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            mock_response.content = b"{}"
            mock_request.return_value = mock_response

            client.get("/test")

            call_args = mock_request.call_args
            headers = call_args[1]["headers"]
            assert "OPHELOS_TENANT_ID" not in headers

    def test_tenant_id_header_with_post_request(self, mock_authenticator):
        """Test that OPHELOS_TENANT_ID header is added for POST requests."""
        tenant_id = "test-tenant-456"
        client = HTTPClient(authenticator=mock_authenticator, base_url="https://api.test.com", tenant_id=tenant_id)

        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"id": "123"}
            mock_response.content = b'{"id": "123"}'
            mock_request.return_value = mock_response

            client.post("/test", data={"name": "test"})

            call_args = mock_request.call_args
            headers = call_args[1]["headers"]
            assert "OPHELOS_TENANT_ID" in headers
            assert headers["OPHELOS_TENANT_ID"] == tenant_id

    def test_version_header_with_default_version(self, mock_authenticator):
        """Test that Ophelos-Version header is added when version is set."""
        version = "2025-04-01"
        client = HTTPClient(authenticator=mock_authenticator, base_url="https://api.test.com", version=version)

        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            mock_response.content = b"{}"
            mock_request.return_value = mock_response

            client.get("/test")

            call_args = mock_request.call_args
            headers = call_args[1]["headers"]
            assert "Ophelos-Version" in headers
            assert headers["Ophelos-Version"] == version

    def test_version_header_with_custom_version(self, mock_authenticator):
        """Test that Ophelos-Version header uses custom version when specified."""
        custom_version = "2024-12-01"
        client = HTTPClient(authenticator=mock_authenticator, base_url="https://api.test.com", version=custom_version)

        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"id": "123"}
            mock_response.content = b'{"id": "123"}'
            mock_request.return_value = mock_response

            client.post("/test", data={"name": "test"})

            call_args = mock_request.call_args
            headers = call_args[1]["headers"]
            assert "Ophelos-Version" in headers
            assert headers["Ophelos-Version"] == custom_version

    def test_no_version_header_when_not_set(self, mock_authenticator):
        """Test that Ophelos-Version header is not added when version is None."""
        client = HTTPClient(authenticator=mock_authenticator, base_url="https://api.test.com", version=None)

        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            mock_response.content = b"{}"
            mock_request.return_value = mock_response

            client.get("/test")

            call_args = mock_request.call_args
            headers = call_args[1]["headers"]
            assert "Ophelos-Version" not in headers

    def test_pagination_headers_with_next_page(self, http_client):
        """Test that pagination information is extracted from headers when next page exists."""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b'{"object": "list", "data": [{"id": "test_1"}]}'
            mock_response.json.return_value = {"object": "list", "data": [{"id": "test_1"}]}
            # Headers indicating there are more pages
            mock_response.headers = {
                "Link": '<https://api.ophelos.com/debts?after=deb_123&limit=10>; rel="next", <https://api.ophelos.com/debts?before=deb_456&limit=10>; rel="prev"',
                "X-Total-Count": "50",
                "X-Page-Items": "10",
            }
            mock_request.return_value = mock_response

            result = http_client.get("/debts", params={"limit": 10})

            assert result["object"] == "list"
            assert result["has_more"] is True
            assert result["total_count"] == 50
            assert len(result["data"]) == 1

    def test_pagination_headers_without_next_page(self, http_client):
        """Test that pagination information is extracted from headers when no next page exists."""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b'{"object": "list", "data": [{"id": "test_1"}]}'
            mock_response.json.return_value = {"object": "list", "data": [{"id": "test_1"}]}
            # Headers indicating no more pages (no "next" rel)
            mock_response.headers = {
                "Link": '<https://api.ophelos.com/debts?before=deb_456&limit=10>; rel="prev"',
                "X-Total-Count": "1",
                "X-Page-Items": "1",
            }
            mock_request.return_value = mock_response

            result = http_client.get("/debts", params={"limit": 10})

            assert result["object"] == "list"
            assert result["has_more"] is False
            assert result["total_count"] == 1

    def test_pagination_headers_with_empty_link_header(self, http_client):
        """Test that pagination works correctly with empty Link header."""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b'{"object": "list", "data": []}'
            mock_response.json.return_value = {"object": "list", "data": []}
            # No Link header or empty Link header
            mock_response.headers = {"X-Total-Count": "0", "X-Page-Items": "0"}
            mock_request.return_value = mock_response

            result = http_client.get("/debts")

            assert result["object"] == "list"
            assert result["has_more"] is False
            assert result["total_count"] == 0
            assert len(result["data"]) == 0

    def test_pagination_headers_with_invalid_total_count(self, http_client):
        """Test that pagination handles invalid X-Total-Count gracefully."""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b'{"object": "list", "data": [{"id": "test_1"}]}'
            mock_response.json.return_value = {"object": "list", "data": [{"id": "test_1"}]}
            # Invalid X-Total-Count header
            mock_response.headers = {
                "Link": '<https://api.ophelos.com/debts?after=deb_123&limit=10>; rel="next"',
                "X-Total-Count": "invalid_number",
                "X-Page-Items": "1",
            }
            mock_request.return_value = mock_response

            result = http_client.get("/debts")

            assert result["object"] == "list"
            assert result["has_more"] is True
            assert result.get("total_count") is None  # Should be None for invalid count

    def test_no_pagination_headers_for_non_list_responses(self, http_client):
        """Test that pagination headers are not processed for non-list responses."""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b'{"id": "single_item", "name": "Test"}'
            mock_response.json.return_value = {"id": "single_item", "name": "Test"}
            # Headers that would indicate pagination (but shouldn't be processed)
            mock_response.headers = {
                "Link": '<https://api.ophelos.com/debts?after=deb_123&limit=10>; rel="next"',
                "X-Total-Count": "50",
            }
            mock_request.return_value = mock_response

            result = http_client.get("/debts/single_item")

            # Should not have pagination fields added
            assert "has_more" not in result
            assert "total_count" not in result
            assert result["id"] == "single_item"
            assert result["name"] == "Test"

    def test_link_header_parsing_comprehensive(self, http_client):
        """Test comprehensive Link header parsing with all relations."""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b'{"object": "list", "data": [{"id": "test_1"}]}'
            mock_response.json.return_value = {"object": "list", "data": [{"id": "test_1"}]}
            # Complex Link header with multiple relations
            mock_response.headers = {
                "Link": '<https://api.ophelos.com/debts?after=deb_first&limit=10>; rel="first", <https://api.ophelos.com/debts?after=deb_next&limit=10>; rel="next", <https://api.ophelos.com/debts?before=deb_prev&limit=10>; rel="prev"',
                "X-Total-Count": "100",
            }
            mock_request.return_value = mock_response

            result = http_client.get("/debts")

            assert result["has_more"] is True
            assert result["total_count"] == 100
            assert "pagination" in result

            pagination = result["pagination"]

            # Check next relation
            assert "next" in pagination
            assert pagination["next"]["after"] == "deb_next"
            assert pagination["next"]["limit"] == 10
            assert "debts?after=deb_next" in pagination["next"]["url"]

            # Check prev relation
            assert "prev" in pagination
            assert pagination["prev"]["before"] == "deb_prev"
            assert pagination["prev"]["limit"] == 10
            assert "debts?before=deb_prev" in pagination["prev"]["url"]

            # Check first relation
            assert "first" in pagination
            assert pagination["first"]["after"] == "deb_first"
            assert pagination["first"]["limit"] == 10
            assert "debts?after=deb_first" in pagination["first"]["url"]

    def test_link_header_parsing_malformed(self, http_client):
        """Test Link header parsing with malformed header."""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b'{"object": "list", "data": []}'
            mock_response.json.return_value = {"object": "list", "data": []}
            # Malformed Link header
            mock_response.headers = {"Link": "malformed link header without proper format", "X-Total-Count": "0"}
            mock_request.return_value = mock_response

            result = http_client.get("/debts")

            assert result["has_more"] is False
            assert result["total_count"] == 0
            # Should not have pagination field for malformed header
            assert result.get("pagination") is None

    def test_link_header_parsing_mixed_parameters(self, http_client):
        """Test Link header parsing with mixed query parameters."""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b'{"object": "list", "data": [{"id": "test_1"}]}'
            mock_response.json.return_value = {"object": "list", "data": [{"id": "test_1"}]}
            # Link header with mixed parameters including expand, status, etc.
            mock_response.headers = {
                "Link": '<https://api.ophelos.com/debts?after=deb_123&limit=5&expand=customer&status=active>; rel="next"',
                "X-Total-Count": "25",
            }
            mock_request.return_value = mock_response

            result = http_client.get("/debts")

            assert result["has_more"] is True
            pagination = result["pagination"]

            # Should extract cursor and limit, ignore other parameters
            assert pagination["next"]["after"] == "deb_123"
            assert pagination["next"]["limit"] == 5
            assert "expand=customer" in pagination["next"]["url"]
            assert "status=active" in pagination["next"]["url"]

    def test_error_debugging_interface(self, http_client):
        """Test that exceptions provide request/response debugging info."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Not Found"}
        mock_response.content = b'{"message": "Not Found"}'
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.url = "https://api.test.com/test/endpoint"
        mock_response.reason = "Not Found"
        mock_response.encoding = "utf-8"
        mock_response.elapsed = Mock()
        mock_response.elapsed.total_seconds.return_value = 0.5

        # Mock request object
        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.url = "https://api.test.com/test/endpoint"
        mock_request.headers = {"Authorization": "Bearer test"}
        mock_request.body = None
        mock_response.request = mock_request

        with patch("requests.Session.request") as mock_request_method:
            mock_request_method.return_value = mock_response

            with pytest.raises(NotFoundError) as exc_info:
                http_client.get("/test/endpoint")

            error = exc_info.value
            assert error.request_info is not None
            assert error.request_info["method"] == "GET"
            assert error.request_info["url"] == "https://api.test.com/test/endpoint"

            assert error.response_info is not None
            assert error.response_info["status_code"] == 404
            assert error.response_info["elapsed_ms"] == 500.0

            assert error.response_raw is mock_response

    def test_timeout_error_with_request_info(self, http_client):
        """Test that timeout errors provide request debugging info."""
        from requests.exceptions import ConnectTimeout

        with patch("ophelos_sdk.http_client.HTTPClient._get_session") as mock_get_session:
            mock_session = Mock()
            mock_session.request.side_effect = ConnectTimeout("Connection timed out")
            mock_get_session.return_value = mock_session

            with pytest.raises(TimeoutError) as exc_info:
                http_client.post("/test", data={"test": "value"}, params={"limit": 5})

            error = exc_info.value
            assert error.request_info is not None
            assert error.request_info["method"] == "POST"
            assert error.request_info["url"] == "https://api.test.com/test"
            assert error.request_info["body"] == '{"test": "value"}'
            assert error.request_info["params"] == {"limit": 5}

            assert error.response_info is None
            assert error.response_raw is None

    def test_timeout_error_detection(self, http_client):
        """Test that various timeout errors are properly detected."""
        from requests.exceptions import ConnectionError, ReadTimeout

        with patch("ophelos_sdk.http_client.HTTPClient._get_session") as mock_get_session:
            mock_session = Mock()
            mock_get_session.return_value = mock_session

            # Test ReadTimeout
            mock_session.request.side_effect = ReadTimeout("Read timed out")
            with pytest.raises(TimeoutError):
                http_client.get("/test")

            # Test ConnectionError with timeout message
            mock_session.request.side_effect = ConnectionError("HTTPConnectionPool: Read timed out")
            with pytest.raises(TimeoutError):
                http_client.get("/test")


class TestJitteredRetry:
    """Test cases for JitteredRetry functionality."""

    def _create_mock_response(self, status=500):
        """Create a mock response object for retry history."""
        response = Mock()
        response.redirect_location = None
        response.status = status
        return response

    def test_jittered_retry_initialization(self):
        """Test JitteredRetry can be initialized properly."""
        retry = JitteredRetry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1,
        )

        assert retry.total == 3
        assert retry.status_forcelist == [429, 500, 502, 503, 504]
        assert retry.allowed_methods == ["HEAD", "GET", "OPTIONS"]
        assert retry.backoff_factor == 1

    def test_jittered_retry_inherits_from_retry(self):
        """Test JitteredRetry properly inherits from urllib3 Retry."""
        retry = JitteredRetry(total=3)
        assert isinstance(retry, Retry)
        assert isinstance(retry, JitteredRetry)

    def test_jittered_backoff_adds_randomness(self):
        """Test that jittered retry adds 0-1.5 seconds to base backoff."""
        jittered_retry = JitteredRetry(total=3, backoff_factor=1)

        # Test first retry (base: 0s, should be 0)
        jittered_retry.history = [self._create_mock_response()]
        jitter_time_1 = jittered_retry.get_backoff_time()

        assert jitter_time_1 == 0, f"Expected 0 for first retry, got {jitter_time_1}"

        # Test second retry (base: 2.0s, should be 2.0-3.5s)
        jittered_retry.history = [self._create_mock_response(), self._create_mock_response()]
        jitter_time_2 = jittered_retry.get_backoff_time()

        assert 2.0 <= jitter_time_2 <= 3.5, f"Expected 2.0-3.5, got {jitter_time_2}"

        # Test third retry (base: 4.0s, should be 4.0-5.5s)
        jittered_retry.history = [
            self._create_mock_response(),
            self._create_mock_response(),
            self._create_mock_response(),
        ]
        jitter_time_3 = jittered_retry.get_backoff_time()

        assert 4.0 <= jitter_time_3 <= 5.5, f"Expected 4.0-5.5, got {jitter_time_3}"

    def test_jitter_randomness_variation(self):
        """Test that jitter actually produces different values."""
        jittered_retry = JitteredRetry(total=3, backoff_factor=1)

        # Use second retry attempt (history length 2) which has non-zero base backoff
        times = []
        for _ in range(10):
            # Set history for second retry (base: 2.0s, should be 2.0-3.5s)
            jittered_retry.history = [self._create_mock_response(), self._create_mock_response()]
            time = jittered_retry.get_backoff_time()
            times.append(time)

        # All times should be in valid range for second retry
        for time in times:
            assert 2.0 <= time <= 3.5, f"Time {time} outside expected range 2.0-3.5"

        # Should have some variation (not all the same)
        unique_times = set(times)
        assert len(unique_times) > 1, "Jitter should produce varying times, got all same values"

        # Check that we're getting reasonable spread
        min_time = min(times)
        max_time = max(times)
        time_range = max_time - min_time
        assert time_range > 0.1, f"Expected more variation, got range: {time_range}"

    def test_zero_backoff_handling(self):
        """Test handling of zero or negative backoff times."""
        jittered_retry = JitteredRetry(total=3, backoff_factor=0)

        # With backoff_factor=0, base backoff should be 0
        jittered_retry.history = [self._create_mock_response()]
        backoff_time = jittered_retry.get_backoff_time()

        # Should return 0 when base backoff is 0
        assert backoff_time == 0

    def test_http_client_uses_jittered_retry(self, mock_authenticator):
        """Test that HTTPClient uses JitteredRetry by default."""
        client = HTTPClient(authenticator=mock_authenticator, base_url="https://api.test.com", max_retries=3)

        # Get the thread-local session (this will create it)
        session = client._get_session()

        # Check that the session has the adapter with JitteredRetry
        assert hasattr(session, "adapters")

        # Get the adapter (should be for both http and https)
        adapters = session.adapters
        assert len(adapters) >= 2  # Should have http:// and https:// adapters

        # Check one of the adapters
        adapter = next(iter(adapters.values()))
        assert hasattr(adapter, "max_retries")
        assert isinstance(adapter.max_retries, JitteredRetry)

    def test_jitter_preserves_retry_configuration(self):
        """Test that jitter doesn't interfere with other retry settings."""
        jittered_retry = JitteredRetry(
            total=5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=2,  # Different backoff factor
        )

        # Verify all settings are preserved
        assert jittered_retry.total == 5
        assert jittered_retry.status_forcelist == [429, 500, 502, 503, 504]
        assert jittered_retry.allowed_methods == ["HEAD", "GET", "OPTIONS"]
        assert jittered_retry.backoff_factor == 2

        # Test backoff with different factor (use second retry which has base 4.0)
        jittered_retry.history = [self._create_mock_response(), self._create_mock_response()]
        backoff_time = jittered_retry.get_backoff_time()

        # With backoff_factor=2, second retry base is 4.0, so jittered should be 4.0-5.5
        assert 4.0 <= backoff_time <= 5.5, f"Expected 4.0-5.5 with backoff_factor=2, got {backoff_time}"

    def test_thread_local_sessions(self, mock_authenticator):
        """Test that each thread gets its own session instance."""
        import threading

        client = HTTPClient(authenticator=mock_authenticator, base_url="https://api.test.com", max_retries=3)

        # Store sessions from different threads
        sessions = {}

        def get_session_in_thread(thread_id):
            sessions[thread_id] = client._get_session()

        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=get_session_in_thread, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Get session from main thread
        main_session = client._get_session()

        # Each thread should have its own session instance
        assert len(sessions) == 3
        for thread_id, session in sessions.items():
            assert session is not None
            assert hasattr(session, "adapters")
            # Sessions from different threads should be different instances
            for other_id, other_session in sessions.items():
                if thread_id != other_id:
                    assert session is not other_session

        # Main thread session should be different from all thread sessions
        for session in sessions.values():
            assert main_session is not session
