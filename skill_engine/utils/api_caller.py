"""
ApiCaller - Utility for making HTTP requests to fetch API context data.

Supports GET, POST, PUT, DELETE with query parameters, JSON body,
and JSONPath-based response extraction.
"""

import json
from typing import Any, Optional
from loguru import logger
import httpx

from skill_engine.models.skill import ApiContextDefinition


class ApiCallError(Exception):
    """Raised when an API call fails."""

    def __init__(self, message: str, alias: str = "", status_code: Optional[int] = None):
        super().__init__(message)
        self.alias = alias
        self.status_code = status_code


class ApiCaller:
    """
    Handles HTTP requests for API Context definitions.

    Makes synchronous HTTP calls and optionally extracts a subset
    of the response using JSONPath dot-notation.
    """

    DEFAULT_TIMEOUT = 30  # seconds
    DEFAULT_HEADERS = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        self.timeout = timeout

    def call_api(self, api_def: ApiContextDefinition) -> Any:
        """
        Execute an API call based on an ApiContextDefinition.

        Args:
            api_def: The API definition to execute

        Returns:
            Parsed response data (possibly extracted via JSONPath)

        Raises:
            ApiCallError: If the request fails
        """
        url = self._build_url(api_def.endpoint, api_def.query_params)
        body = json.loads(api_def.body) if api_def.body else None

        logger.info(f"Calling API [{api_def.method.value}] {url} (alias: {api_def.alias})")

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(
                    method=api_def.method.value,
                    url=url,
                    json=body,
                    headers=self.DEFAULT_HEADERS,
                )
                response.raise_for_status()

            # Parse response
            try:
                data = response.json()
            except (json.JSONDecodeError, ValueError):
                data = response.text

            # Apply JSONPath extraction if specified
            if api_def.extract and isinstance(data, (dict, list)):
                data = self._extract_jsonpath(data, api_def.extract)

            logger.info(f"API call successful: {api_def.alias} ({len(str(data))} chars)")
            return data

        except httpx.HTTPStatusError as e:
            raise ApiCallError(
                f"API call failed for '{api_def.alias}': HTTP {e.response.status_code}",
                alias=api_def.alias,
                status_code=e.response.status_code,
            )
        except httpx.RequestError as e:
            raise ApiCallError(
                f"API call failed for '{api_def.alias}': {str(e)}",
                alias=api_def.alias,
            )

    def _build_url(self, endpoint: str, query_params: Optional[str]) -> str:
        """Append query params to endpoint URL."""
        if not query_params:
            return endpoint
        separator = "&" if "?" in endpoint else "?"
        return f"{endpoint}{separator}{query_params}"

    def _extract_jsonpath(self, data: Any, path: str) -> Any:
        """
        Simple JSONPath extraction supporting dot notation.

        Examples:
            $.data.financials  -> data["data"]["financials"]
            $.items.0.name     -> data["items"][0]["name"]

        Falls back to full data if extraction fails.
        """
        # Strip leading $.
        path = path.lstrip("$").lstrip(".")
        if not path:
            return data

        parts = path.split(".")
        current = data

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            elif isinstance(current, list):
                try:
                    current = current[int(part)]
                except (ValueError, IndexError):
                    logger.warning(f"JSONPath extraction failed at '{part}' in path '{path}'")
                    return data
            else:
                logger.warning(f"JSONPath extraction failed at '{part}' in path '{path}'")
                return data

        return current
