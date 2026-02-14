"""Centralized CKAN API helper with error handling and retry logic."""

from typing import Any

import httpx

from datagov_mcp.client import get_http_client

# Base URL for the CKAN API
BASE_URL = "https://data.gov.il/api/3"


class CKANAPIError(Exception):
    """Exception raised for CKAN API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


async def ckan_api_call(
    action: str,
    method: str = "GET",
    params: dict[str, Any] | None = None,
    max_retries: int = 2,
) -> dict[str, Any]:
    """
    Make a CKAN API call with error handling and retry logic.

    Args:
        action: CKAN action name (e.g., 'package_search')
        method: HTTP method (GET or POST)
        params: Query parameters or request body
        max_retries: Maximum number of retry attempts for transient failures

    Returns:
        API response as a dictionary

    Raises:
        CKANAPIError: If the API call fails after retries
    """
    url = f"{BASE_URL}/action/{action}"
    params = params or {}

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            async for client in get_http_client():
                if method == "GET":
                    response = await client.get(url, params=params)
                elif method == "POST":
                    response = await client.post(url, json=params)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                data = response.json()

                # Check for CKAN-level errors
                if not data.get("success", False):
                    error_msg = data.get("error", {})
                    if isinstance(error_msg, dict):
                        error_msg = error_msg.get("message", str(error_msg))
                    raise CKANAPIError(f"CKAN API error: {error_msg}")

                return data

        except httpx.HTTPStatusError as e:
            last_error = CKANAPIError(
                f"HTTP {e.response.status_code}: {e.response.text}",
                status_code=e.response.status_code,
            )
            # Retry on transient errors (5xx)
            if e.response.status_code >= 500 and attempt < max_retries:
                continue
            raise last_error

        except httpx.RequestError as e:
            last_error = CKANAPIError(f"Request error: {str(e)}")
            # Retry on network errors
            if attempt < max_retries:
                continue
            raise last_error

        except Exception as e:
            raise CKANAPIError(f"Unexpected error: {str(e)}")

    # Should not reach here, but just in case
    if last_error:
        raise last_error
    raise CKANAPIError("API call failed after retries")
