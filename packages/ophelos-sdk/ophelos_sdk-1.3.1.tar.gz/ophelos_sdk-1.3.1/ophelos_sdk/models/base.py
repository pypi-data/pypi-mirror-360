from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional, Set

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    import requests


class BaseOphelosModel(BaseModel):

    model_config = ConfigDict(
        extra="allow",
        use_enum_values=True,
    )

    def __init__(self, **data: Any) -> None:
        # Extract the response object if provided
        _req_res = data.pop("_req_res", None)
        super().__init__(**data)

        # Store the response object as a private attribute
        if _req_res is not None:
            object.__setattr__(self, "_req_res", _req_res)

    def __setattr__(self, name: str, value: Any) -> None:
        # Allow setting _req_res even if model is frozen
        if name == "_req_res":
            object.__setattr__(self, name, value)
        else:
            super().__setattr__(name, value)

    @classmethod
    def _get_api_body_fields(cls) -> Optional[Set[str]]:
        return getattr(cls, "__api_body_fields__", None)

    @classmethod
    def _get_api_exclude_fields(cls) -> Set[str]:
        return getattr(cls, "__api_exclude_fields__", {"id", "object", "created_at", "updated_at"})

    def to_api_body(self, exclude_none: bool = True) -> Dict[str, Any]:
        api_body_fields = self._get_api_body_fields()
        if api_body_fields is not None:
            allowed_fields = api_body_fields
        else:
            all_field_names = set(self.__class__.model_fields.keys())
            allowed_fields = all_field_names - self._get_api_exclude_fields()

        api_data = {}

        for field_name in allowed_fields:
            value = getattr(self, field_name, None)

            if exclude_none and value is None:
                continue

            processed_value = self._process_nested_value(value, field_name)
            api_data[field_name] = processed_value

        return api_data

    def _process_nested_value(self, value: Any, field_name: str = "") -> Any:
        if isinstance(value, BaseOphelosModel):
            should_convert_to_id = (
                field_name in {"customer", "organisation"}
                and hasattr(value, "id")
                and getattr(value, "id", None)
                and not getattr(value, "id", "").startswith("temp")
            )

            if should_convert_to_id:
                return getattr(value, "id")

            return value.to_api_body()

        elif isinstance(value, (datetime, date)):
            return value.isoformat()

        elif isinstance(value, list):
            return [self._process_nested_value(item, field_name) for item in value]

        elif isinstance(value, dict):
            return {k: self._process_nested_value(v, k) for k, v in value.items()}

        else:
            return value

    @property
    def request_info(self) -> Optional[Dict[str, Any]]:
        """
        Get request information from the Response object.

        Returns:
            Dictionary with request details or None if no response available
        """
        if not hasattr(self, "_req_res") or self._req_res is None:
            return None

        response = self._req_res
        request = response.request

        return {
            "method": request.method,
            "url": request.url,
            "headers": dict(request.headers),
            "body": request.body.decode("utf-8") if request.body else None,
        }

    @property
    def response_info(self) -> Optional[Dict[str, Any]]:
        """
        Get response information from the Response object.

        Returns:
            Dictionary with response details or None if no response available
        """
        if not hasattr(self, "_req_res") or self._req_res is None:
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
    def response_raw(self) -> Optional["requests.Response"]:
        """
        Get the raw requests.Response object.

        Returns:
            The original requests.Response object or None
        """
        return getattr(self, "_req_res", None)


class Currency(str, Enum):
    GBP = "GBP"
    EUR = "EUR"
    USD = "USD"
