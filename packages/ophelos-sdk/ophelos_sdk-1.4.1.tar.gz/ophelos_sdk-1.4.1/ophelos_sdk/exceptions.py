"""
Exception classes for the Ophelos SDK.
"""

from typing import Any, Dict, Optional

import requests


class OphelosError(Exception):
    """Base exception class for all Ophelos SDK errors."""

    def __init__(
        self, message: str, details: Optional[Dict[str, Any]] = None, response: Optional[requests.Response] = None
    ):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self._req_res = response

    @property
    def request_info(self) -> Optional[Dict[str, Any]]:
        """
        Get request information from the Response object.

        Returns:
            Dictionary with request details or None if no response available
        """

        if self._req_res is None:
            return None

        request = self._req_res.request

        return {
            "method": request.method,
            "url": request.url,
            "headers": dict(request.headers),
            "body": request.body.decode("utf-8") if isinstance(request.body, bytes) else request.body,
        }

    @property
    def response_info(self) -> Optional[Dict[str, Any]]:
        """
        Get response information from the Response object.

        Returns:
            Dictionary with response details or None if no response available
        """
        if self._req_res is None:
            return None

        response = self._req_res

        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "elapsed_ms": response.elapsed.total_seconds() * 1000,
            "encoding": response.encoding,
            "url": response.url,
            "reason": response.reason,
        }

    @property
    def response_raw(self) -> Optional[requests.Response]:
        """
        Get the raw requests.Response object that caused this error.

        Returns:
            The original requests.Response object or None
        """
        return self._req_res


class OphelosAPIError(OphelosError):
    """Exception raised for API-related errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
        response: Optional[requests.Response] = None,
    ):
        super().__init__(message, details, response)
        self.status_code = status_code
        self.response_data = response_data or {}


class AuthenticationError(OphelosAPIError):
    """Exception raised for authentication-related errors."""

    def __init__(self, message: str = "Authentication failed", **kwargs: Any):
        super().__init__(message, status_code=401, **kwargs)


class ValidationError(OphelosAPIError):
    """Exception raised for validation errors."""

    def __init__(self, message: str = "Validation failed", **kwargs: Any):
        super().__init__(message, status_code=422, **kwargs)


class NotFoundError(OphelosAPIError):
    """Exception raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found", **kwargs: Any):
        super().__init__(message, status_code=404, **kwargs)


class RateLimitError(OphelosAPIError):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", **kwargs: Any):
        super().__init__(message, status_code=429, **kwargs)


class ConflictError(OphelosAPIError):
    """Exception raised for conflict errors."""

    def __init__(self, message: str = "Resource conflict", **kwargs: Any):
        super().__init__(message, status_code=409, **kwargs)


class ForbiddenError(OphelosAPIError):
    """Exception raised for forbidden access errors."""

    def __init__(self, message: str = "Access forbidden", **kwargs: Any):
        super().__init__(message, status_code=403, **kwargs)


class ServerError(OphelosAPIError):
    """Exception raised for server errors."""

    def __init__(self, message: str = "Internal server error", **kwargs: Any):
        if "status_code" not in kwargs:
            kwargs["status_code"] = 500
        super().__init__(message, **kwargs)


class TimeoutError(OphelosError):
    """Exception raised when request times out."""

    def __init__(
        self, message: str = "Request timed out", request_info: Optional[Dict[str, Any]] = None, **kwargs: Any
    ):
        super().__init__(message, **kwargs)
        self._request_info = request_info

    @property
    def request_info(self) -> Optional[Dict[str, Any]]:
        return self._request_info

    @property
    def response_info(self) -> Optional[Dict[str, Any]]:
        return None

    @property
    def response_raw(self) -> Optional[requests.Response]:
        return None


class ParseError(OphelosError):
    """Exception raised when response parsing fails."""

    def __init__(self, message: str = "Failed to parse response", **kwargs: Any):
        super().__init__(message, **kwargs)


class UnexpectedError(OphelosError):
    """Exception raised for unexpected errors during request processing."""

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        original_error: Optional[Exception] = None,
        request_info: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ):
        super().__init__(message, **kwargs)
        self.original_error = original_error
        self._request_info = request_info

    @property
    def request_info(self) -> Optional[Dict[str, Any]]:
        """Return request info if available, otherwise try to get from response."""
        if self._request_info is not None:
            return self._request_info
        return super().request_info

    @property
    def response_info(self) -> Optional[Dict[str, Any]]:
        """Return response info if available (may be None for pre-request errors)."""
        return super().response_info

    @property
    def response_raw(self) -> Optional[requests.Response]:
        """Return raw response if available (may be None for pre-request errors)."""
        return super().response_raw
