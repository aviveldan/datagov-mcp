"""HTTP client lifecycle management for CKAN API requests."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

import httpx


class HTTPClient:
    """Manages httpx.AsyncClient lifecycle for the MCP server."""

    def __init__(self):
        self._client: httpx.AsyncClient | None = None

    @asynccontextmanager
    async def get_client(self) -> AsyncIterator[httpx.AsyncClient]:
        """Get or create an async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                headers={
                    "User-Agent": "DataGovIL-MCP/0.3.0",
                },
                follow_redirects=True,
            )
        try:
            yield self._client
        finally:
            pass  # Don't close on each use, let lifecycle manage it

    async def close(self):
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None


# Global client instance
_http_client = HTTPClient()


async def get_http_client() -> AsyncIterator[httpx.AsyncClient]:
    """Get the global HTTP client."""
    async with _http_client.get_client() as client:
        yield client


async def cleanup_http_client():
    """Cleanup the global HTTP client."""
    await _http_client.close()
