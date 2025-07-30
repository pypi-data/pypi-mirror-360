"""
HTTP client for making authenticated requests to the Ophelos API.
"""

import random
import threading
from typing import Any, Dict, Optional, Tuple, Union

import requests
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .auth import OAuth2Authenticator, StaticTokenAuthenticator
from .exceptions import (
    AuthenticationError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    OphelosAPIError,
    RateLimitError,
    ServerError,
    TimeoutError,
    UnexpectedError,
    ValidationError,
)


class JitteredRetry(Retry):
    """Custom retry class with exponential backoff and additive jitter."""

    def get_backoff_time(self) -> float:
        """
        Calculate backoff time with additive jitter.

        Uses standard exponential backoff plus random 0-1.5 seconds.
        This maintains predictable base timing while preventing thundering herd.
        """
        backoff_time = super().get_backoff_time()
        if backoff_time <= 0:
            return 0

        # Additive jitter: standard backoff + random 0-1.5 seconds
        jitter_amount = random.uniform(0, 1.5)
        return backoff_time + jitter_amount


class HTTPClient:
    """
    Thread-safe HTTP client for making authenticated requests to Ophelos API.

    Uses thread-local storage to ensure each thread gets its own requests.Session
    instance, making it safe for concurrent usage across multiple threads.
    """

    # Timeout-related exceptions to catch
    TIMEOUT_EXCEPTIONS = (
        requests.exceptions.Timeout,
        requests.exceptions.ConnectTimeout,
        requests.exceptions.ReadTimeout,
        requests.exceptions.ConnectionError,
    )

    def __init__(
        self,
        authenticator: Union[OAuth2Authenticator, StaticTokenAuthenticator],
        base_url: str,
        tenant_id: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        version: Optional[str] = None,
    ):
        """
        Initialize HTTP client.

        Args:
            authenticator: OAuth2 or StaticToken authenticator instance
            base_url: Base URL for API requests
            tenant_id: Optional tenant ID to include in all requests as OPHELOS_TENANT_ID header
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            version: Optional API version to include in Ophelos-Version header
        """
        self.authenticator = authenticator
        self.base_url = base_url.rstrip("/")
        self.tenant_id = tenant_id
        self.timeout = timeout
        self.version = version
        self.max_retries = max_retries

        # Thread-local storage for sessions (thread-safe)
        self._local = threading.local()

    def _get_session(self) -> Session:
        """
        Get thread-local session instance.

        Each thread gets its own requests.Session instance to ensure thread safety.
        Sessions are configured with jittered retry strategy and connection pooling.

        Returns:
            Thread-local requests.Session instance
        """
        if not hasattr(self._local, "session"):
            # Create new session for this thread
            self._local.session = requests.Session()

            # Configure session with jittered retry strategy
            retry_strategy = JitteredRetry(
                total=self.max_retries,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"],
                backoff_factor=1,
            )

            adapter = HTTPAdapter(max_retries=retry_strategy)
            self._local.session.mount("http://", adapter)
            self._local.session.mount("https://", adapter)

        session: Session = self._local.session
        return session

    def _prepare_headers(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Prepare headers for request including authentication."""
        request_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "ophelos-python-sdk/1.4.0",
        }

        request_headers.update(self.authenticator.get_auth_headers())

        if self.tenant_id:
            request_headers["OPHELOS_TENANT_ID"] = self.tenant_id

        if self.version:
            request_headers["Ophelos-Version"] = self.version

        if headers:
            request_headers.update(headers)

        return request_headers

    def _execute_request(self, method: str, url: str, headers: Dict[str, str], **kwargs: Any) -> requests.Response:
        """
        Execute HTTP request with comprehensive error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Request headers
            **kwargs: Additional arguments for the request

        Returns:
            requests.Response object

        Raises:
            TimeoutError: If request times out
            UnexpectedError: For unexpected errors during request processing
        """
        session = self._get_session()

        # Build request info for debugging (before making the request)
        body_data = kwargs.get("json") or kwargs.get("data")
        body: Optional[str] = None
        if body_data and kwargs.get("json"):
            # Serialize JSON data to string for debugging
            import json

            body = json.dumps(body_data)
        elif body_data is not None:
            body = str(body_data)

        request_info = {
            "method": method,
            "url": url,
            "headers": dict(headers),
            "body": body,
            "params": kwargs.get("params"),
        }

        try:
            response = session.request(method, url, headers=headers, timeout=self.timeout, **kwargs)
            return response
        except self.TIMEOUT_EXCEPTIONS as e:
            # Check if it's a timeout-related error (including those wrapped in ConnectionError/RetryError)
            if any(timeout_word in str(e).lower() for timeout_word in ["timeout", "timed out"]):
                raise TimeoutError(f"Request timed out after {self.timeout} seconds: {e}", request_info=request_info)
            else:
                # Re-raise non-timeout connection errors as UnexpectedError
                raise UnexpectedError(f"Connection error: {e}", original_error=e, request_info=request_info)
        except Exception as e:
            # Catch any other unexpected errors and wrap with debugging info
            raise UnexpectedError(f"Unexpected error during request: {e}", original_error=e, request_info=request_info)

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and raise appropriate exceptions for errors.

        Args:
            response: HTTP response object

        Returns:
            Parsed JSON response data with pagination info from headers

        Raises:
            OphelosAPIError: For various API errors
        """
        try:
            json_data = response.json() if response.content else {}
            response_data = json_data if isinstance(json_data, dict) else {"data": json_data}
        except ValueError:
            response_data = {"message": response.text}

        if response.status_code >= 400:
            message = response_data.get("message", f"HTTP {response.status_code}")

            if response.status_code == 401:
                self.authenticator.invalidate_token()
                raise AuthenticationError(message, response_data=response_data, response=response)
            elif response.status_code == 403:
                raise ForbiddenError(message, response_data=response_data, response=response)
            elif response.status_code == 404:
                raise NotFoundError(message, response_data=response_data, response=response)
            elif response.status_code == 409:
                raise ConflictError(message, response_data=response_data, response=response)
            elif response.status_code == 422:
                raise ValidationError(message, response_data=response_data, response=response)
            elif response.status_code == 429:
                raise RateLimitError(message, response_data=response_data, response=response)
            elif response.status_code >= 500:
                raise ServerError(
                    message, status_code=response.status_code, response_data=response_data, response=response
                )
            else:
                raise OphelosAPIError(
                    message, status_code=response.status_code, response_data=response_data, response=response
                )

        # Extract pagination information from headers for list responses
        if self._is_list_response(response_data):
            response_data = self._extract_pagination_from_headers(response, response_data)

        return response_data

    def _is_list_response(self, response_data: Dict[str, Any]) -> bool:
        """
        Check if this is a list response that should have pagination information.

        Args:
            response_data: Response data dictionary

        Returns:
            True if this appears to be a list response
        """
        return isinstance(response_data, dict) and response_data.get("object") == "list" and "data" in response_data

    def _extract_pagination_from_headers(
        self, response: requests.Response, response_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract pagination information from response headers and add to response data.

        Args:
            response: HTTP response object
            response_data: Response data dictionary

        Returns:
            Updated response data with pagination information
        """
        headers = response.headers

        # Parse Link header to extract pagination cursors
        link_header = headers.get("Link", "")
        pagination_info = self._parse_link_header(link_header)

        # Determine if there are more pages
        has_more = "next" in pagination_info

        # Get total count from X-Total-Count header
        total_count = None
        if "X-Total-Count" in headers:
            try:
                total_count = int(headers["X-Total-Count"])
            except (ValueError, TypeError):
                total_count = None

        # Update response data with pagination info
        response_data["has_more"] = has_more
        if total_count is not None:
            response_data["total_count"] = total_count

        # Add pagination cursors for easy navigation
        if pagination_info:
            response_data["pagination"] = pagination_info

        return response_data

    def _parse_link_header(self, link_header: str) -> Dict[str, Dict[str, Any]]:
        """
        Parse Link header to extract pagination URLs and cursors.

        Args:
            link_header: Raw Link header value

        Returns:
            Dictionary with pagination info for each relation (next, prev, first)

        Example return:
            {
                "next": {"after": "deb_123", "url": "https://..."},
                "prev": {"before": "deb_456", "url": "https://..."},
                "first": {"after": "deb_789", "url": "https://..."}
            }
        """
        import re
        from urllib.parse import parse_qs, urlparse

        pagination_info: Dict[str, Dict[str, Any]] = {}

        if not link_header:
            return pagination_info

        # Parse Link header format: <url>; rel="relation", <url>; rel="relation"
        link_pattern = r'<([^>]+)>;\s*rel="([^"]+)"'
        matches = re.findall(link_pattern, link_header)

        for url, relation in matches:
            if relation in ["next", "prev", "first"]:
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)

                # Extract cursor parameters
                cursor_info = {"url": url}

                if "after" in query_params:
                    cursor_info["after"] = query_params["after"][0]

                if "before" in query_params:
                    cursor_info["before"] = query_params["before"][0]

                if "limit" in query_params:
                    try:
                        cursor_info["limit"] = int(query_params["limit"][0])
                    except (ValueError, TypeError):
                        pass

                pagination_info[relation] = cursor_info

        return pagination_info

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        return_response: bool = False,
    ) -> Union[Dict[str, Any], Tuple[Dict[str, Any], requests.Response]]:
        """
        Make GET request.

        Args:
            path: API endpoint path
            params: Query parameters
            headers: Additional headers
            return_response: If True, return (data, response) tuple

        Returns:
            Response data or (data, response) tuple
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        request_headers = self._prepare_headers(headers)

        response = self._execute_request("GET", url, request_headers, params=params)

        try:
            response_data = self._handle_response(response)
        except Exception as e:
            # Catch response processing errors and wrap with debugging info
            if not isinstance(e, (OphelosAPIError, TimeoutError, UnexpectedError)):
                raise UnexpectedError(f"Error processing response: {e}", original_error=e, response=response)
            raise

        if return_response:
            return response_data, response
        return response_data

    def post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        return_response: bool = False,
    ) -> Union[Dict[str, Any], Tuple[Dict[str, Any], requests.Response]]:
        """
        Make POST request.

        Args:
            path: API endpoint path
            data: Request body data
            params: Query parameters
            headers: Additional headers
            return_response: If True, return (data, response) tuple

        Returns:
            Response data or (data, response) tuple
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        request_headers = self._prepare_headers(headers)

        response = self._execute_request("POST", url, request_headers, json=data, params=params)

        try:
            response_data = self._handle_response(response)
        except Exception as e:
            # Catch response processing errors and wrap with debugging info
            if not isinstance(e, (OphelosAPIError, TimeoutError, UnexpectedError)):
                raise UnexpectedError(f"Error processing response: {e}", original_error=e, response=response)
            raise

        if return_response:
            return response_data, response
        return response_data

    def put(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        return_response: bool = False,
    ) -> Union[Dict[str, Any], Tuple[Dict[str, Any], requests.Response]]:
        """
        Make PUT request.

        Args:
            path: API endpoint path
            data: Request body data
            params: Query parameters
            headers: Additional headers
            return_response: If True, return (data, response) tuple

        Returns:
            Response data or (data, response) tuple
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        request_headers = self._prepare_headers(headers)

        response = self._execute_request("PUT", url, request_headers, json=data, params=params)

        try:
            response_data = self._handle_response(response)
        except Exception as e:
            # Catch response processing errors and wrap with debugging info
            if not isinstance(e, (OphelosAPIError, TimeoutError, UnexpectedError)):
                raise UnexpectedError(f"Error processing response: {e}", original_error=e, response=response)
            raise

        if return_response:
            return response_data, response
        return response_data

    def patch(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        return_response: bool = False,
    ) -> Union[Dict[str, Any], Tuple[Dict[str, Any], requests.Response]]:
        """
        Make PATCH request.

        Args:
            path: API endpoint path
            data: Request body data
            params: Query parameters
            headers: Additional headers
            return_response: If True, return (data, response) tuple

        Returns:
            Response data or (data, response) tuple
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        request_headers = self._prepare_headers(headers)

        response = self._execute_request("PATCH", url, request_headers, json=data, params=params)

        try:
            response_data = self._handle_response(response)
        except Exception as e:
            # Catch response processing errors and wrap with debugging info
            if not isinstance(e, (OphelosAPIError, TimeoutError, UnexpectedError)):
                raise UnexpectedError(f"Error processing response: {e}", original_error=e, response=response)
            raise

        if return_response:
            return response_data, response
        return response_data

    def delete(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        return_response: bool = False,
    ) -> Union[Dict[str, Any], Tuple[Dict[str, Any], requests.Response]]:
        """
        Make DELETE request.

        Args:
            path: API endpoint path
            params: Query parameters
            headers: Additional headers
            return_response: If True, return (data, response) tuple

        Returns:
            Response data or (data, response) tuple
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        request_headers = self._prepare_headers(headers)

        response = self._execute_request("DELETE", url, request_headers, params=params)

        try:
            response_data = self._handle_response(response)
        except Exception as e:
            # Catch response processing errors and wrap with debugging info
            if not isinstance(e, (OphelosAPIError, TimeoutError, UnexpectedError)):
                raise UnexpectedError(f"Error processing response: {e}", original_error=e, response=response)
            raise

        if return_response:
            return response_data, response
        return response_data
