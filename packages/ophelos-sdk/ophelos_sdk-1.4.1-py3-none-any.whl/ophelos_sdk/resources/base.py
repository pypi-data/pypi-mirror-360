"""
Base resource class for Ophelos API resources.
"""

from typing import Any, Dict, Generator, List, Optional, Tuple, Type, TypeVar, Union

import requests

from ..exceptions import ParseError
from ..http_client import HTTPClient
from ..models import BaseOphelosModel, PaginatedResponse

T = TypeVar("T", bound=BaseOphelosModel)


class BaseResource:
    """Base class for all API resource managers."""

    def __init__(self, http_client: HTTPClient):
        """
        Initialize base resource.

        Args:
            http_client: HTTP client instance for making requests
        """
        self.http_client = http_client

    def _build_expand_params(self, expand: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Build expand parameters for API requests.

        Args:
            expand: List of fields to expand

        Returns:
            Dictionary with expand parameters that will generate expand[]=value1&expand[]=value2
        """
        params: Dict[str, Any] = {}
        if expand:
            params["expand[]"] = expand
        return params

    def _build_list_params(
        self,
        limit: Optional[int] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        expand: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Build parameters for list requests.

        Args:
            limit: Maximum number of results to return
            after: Cursor for pagination (after this ID)
            before: Cursor for pagination (before this ID)
            expand: List of fields to expand
            **kwargs: Additional query parameters

        Returns:
            Dictionary with query parameters
        """
        params: Dict[str, Any] = {}

        if limit is not None:
            params["limit"] = limit
        if after:
            params["after"] = after
        if before:
            params["before"] = before

        params.update(self._build_expand_params(expand))
        params.update(kwargs)

        return params

    def _build_search_params(
        self,
        query: str,
        limit: Optional[int] = None,
        expand: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Build parameters for search requests.

        Args:
            query: Search query string
            limit: Maximum number of results to return
            expand: List of fields to expand
            **kwargs: Additional query parameters

        Returns:
            Dictionary with query parameters
        """
        params: Dict[str, Any] = {"query": query}

        if limit is not None:
            params["limit"] = limit

        params.update(self._build_expand_params(expand))
        params.update(kwargs)

        return params

    def _is_valid_model_data(self, data: Dict[str, Any], model_class: Type[BaseOphelosModel]) -> bool:
        """
        Check if data looks like valid model data.

        Args:
            data: Dictionary data to check
            model_class: Model class to validate against

        Returns:
            True if data looks valid for the model, False otherwise
        """

        # Check if it has at least one expected model field
        model_fields = set(model_class.model_fields.keys())
        data_keys = set(data.keys())

        # If all keys are unknown to the model, it's probably invalid
        if not (data_keys & model_fields):
            return False

        # If it has only "invalid" or similar non-model keys, it's invalid
        if data_keys <= {"invalid", "missing_required_fields", "error", "message"}:
            return False

        return True

    def _parse_response(
        self,
        response_data: Union[Dict[str, Any], Tuple[Dict[str, Any], requests.Response]],
        model_class: Type[T],
        strict: bool = False,
        response_obj: Optional[requests.Response] = None,
    ) -> Union[T, Dict[str, Any]]:
        """
        Parse API response data into model instance.

        Args:
            response_data: Raw response data from API (dict or tuple with response)
            model_class: Pydantic model class to parse into
            strict: If True, raise ParseError on failure. If False, return raw data.
            response_obj: Optional requests.Response object to attach to model

        Returns:
            Parsed model instance or raw data (if strict=False and parsing fails)

        Raises:
            ParseError: If response data cannot be parsed and strict=True
        """
        # Handle both old and new style responses
        if isinstance(response_data, tuple):
            data, response = response_data
            response_obj = response
        else:
            data = response_data

        if not data:
            if strict:
                raise ParseError("Empty response data", response=response_obj)
            return data

        if not self._is_valid_model_data(data, model_class):
            if strict:
                raise ParseError(
                    f"Response data is not valid for {model_class.__name__}",
                    details={
                        "model_class": model_class.__name__,
                        "response_keys": (list(data.keys()) if isinstance(data, dict) else str(type(data))),
                        "expected_fields": (
                            list(model_class.model_fields.keys()) if hasattr(model_class, "model_fields") else "unknown"
                        ),
                    },
                    response=response_obj,
                )
            return data

        try:
            # Inject response object if available
            if response_obj is not None:
                data["_req_res"] = response_obj
            return model_class(**data)
        except Exception as e:
            if strict:
                raise ParseError(
                    f"Failed to parse response data into {model_class.__name__}: {str(e)}",
                    details={
                        "model_class": model_class.__name__,
                        "original_error": str(e),
                        "response_data": data,
                    },
                    response=response_obj,
                )
            return data

    def _parse_list_response(
        self,
        response_data: Union[Dict[str, Any], Tuple[Dict[str, Any], requests.Response]],
        model_class: Optional[Type[BaseOphelosModel]] = None,
        response_obj: Optional[requests.Response] = None,
    ) -> PaginatedResponse:
        """
        Parse paginated list response.

        Args:
            response_data: Raw response data from API (dict or tuple with response)
            model_class: Pydantic model class for list items
            response_obj: Optional requests.Response object to attach to items

        Returns:
            Paginated response with parsed items
        """
        # Handle both old and new style responses
        if isinstance(response_data, tuple):
            data, response = response_data
            response_obj = response
        else:
            data = response_data

        if not data:
            result = PaginatedResponse(data=[])
            if response_obj is not None:
                object.__setattr__(result, "_req_res", response_obj)
            return result

        items = data.get("data", [])

        if model_class:
            parsed_items: List[Union[Dict[str, Any], BaseOphelosModel]] = []
            for i, item in enumerate(items):
                try:
                    if isinstance(item, dict):
                        # Use non-strict parsing for individual items in lists
                        parsed_item = self._parse_response(item, model_class, strict=False, response_obj=response_obj)
                        parsed_items.append(parsed_item)
                    else:
                        # Already a model object - attach response if available
                        if response_obj is not None and hasattr(item, "__setattr__"):
                            object.__setattr__(item, "_req_res", response_obj)
                        parsed_items.append(item)
                except Exception:
                    # Fallback to raw data if parsing fails
                    parsed_items.append(item)

            parsed_response = data.copy()
            parsed_response["data"] = parsed_items
            if response_obj is not None:
                parsed_response["_req_res"] = response_obj
            return PaginatedResponse(**parsed_response)

        if response_obj is not None:
            data["_req_res"] = response_obj
        return PaginatedResponse(**data)

    def iterate(
        self,
        limit_per_page: int = 50,
        max_pages: Optional[int] = None,
        expand: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Generator[Any, None, None]:
        """
        Generator that yields individual objects with automatic pagination.

        This method provides memory-efficient iteration over large datasets
        by fetching pages on-demand and yielding individual objects.

        Args:
            limit_per_page: Number of items per page (default: 50)
            max_pages: Maximum number of pages to fetch (None = unlimited)
            expand: List of fields to expand
            **kwargs: Additional query parameters for filtering

        Yields:
            Individual model objects

        Raises:
            AttributeError: If the resource doesn't implement list functionality

        Example:
            # Process first 200 items (4 pages of 50)
            for item in resource.iterate(limit_per_page=50, max_pages=4):
                process_item(item)

            # Process all items with specific filters
            for item in resource.iterate(expand=["related"], status="active"):
                process_item(item)
        """
        if not hasattr(self, "list"):
            raise AttributeError(f"{self.__class__.__name__} does not support list functionality")

        after_cursor = None
        pages_fetched = 0

        while True:
            # Check page limit
            if max_pages and pages_fetched >= max_pages:
                break

            # Fetch current page - using getattr to satisfy type checker
            list_method = getattr(self, "list")
            page = list_method(limit=limit_per_page, after=after_cursor, before=None, expand=expand, **kwargs)

            pages_fetched += 1

            # Yield individual items
            for item in page.data:
                yield item

            # Check if we have more pages
            if not page.has_more or not page.data:
                break

            last_item = page.data[-1]
            if hasattr(last_item, "id"):
                after_cursor = last_item.id
            elif isinstance(last_item, dict):
                after_cursor = last_item.get("id")
            else:
                break  # Can't get ID, stop iteration

    def iterate_search(
        self,
        query: str,
        limit_per_page: int = 50,
        max_pages: Optional[int] = None,
        expand: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Generator[Any, None, None]:
        """
        Generator that yields individual objects from search results with pagination.

        Note: This method requires the resource to implement a 'search' method.

        Args:
            query: Search query string
            limit_per_page: Number of items per page (default: 50)
            max_pages: Maximum number of pages to fetch (None = unlimited)
            expand: List of fields to expand
            **kwargs: Additional query parameters

        Yields:
            Individual model objects matching the search criteria

        Raises:
            AttributeError: If the resource doesn't implement search functionality

        Example:
            # Search for specific items
            for item in resource.iterate_search("status:active", max_pages=5):
                process_item(item)
        """
        if not hasattr(self, "search"):
            raise AttributeError(f"{self.__class__.__name__} does not support search functionality")

        pages_fetched = 0

        while True:
            # Check page limit
            if max_pages and pages_fetched >= max_pages:
                break

            # Fetch current page of search results - using getattr to satisfy type checker
            search_method = getattr(self, "search")
            page = search_method(query=query, limit=limit_per_page, expand=expand, **kwargs)

            pages_fetched += 1

            # Yield individual items
            for item in page.data:
                yield item

            # Check if we have more pages
            if not page.has_more or not page.data:
                break
