"""Tests for CKAN API helper functions."""

import pytest
import respx
from httpx import Response

from datagov_mcp.api import BASE_URL, CKANAPIError, ckan_api_call


@pytest.mark.asyncio
class TestCKANAPICall:
    """Test the ckan_api_call helper function."""

    @respx.mock
    async def test_successful_get_request(self):
        """Test successful GET request."""
        respx.get(f"{BASE_URL}/action/package_list").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "result": ["dataset1", "dataset2"],
                },
            )
        )

        result = await ckan_api_call("package_list")
        assert result["success"] is True
        assert len(result["result"]) == 2

    @respx.mock
    async def test_successful_post_request(self):
        """Test successful POST request."""
        respx.post(f"{BASE_URL}/action/status_show").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "ckan_version": "2.9.0",
                        "extensions": ["datastore"],
                    },
                },
            )
        )

        result = await ckan_api_call("status_show", method="POST")
        assert result["success"] is True
        assert "ckan_version" in result["result"]

    @respx.mock
    async def test_get_with_params(self):
        """Test GET request with query parameters."""
        respx.get(f"{BASE_URL}/action/package_search").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "count": 1,
                        "results": [{"name": "test-dataset"}],
                    },
                },
            )
        )

        result = await ckan_api_call(
            "package_search",
            params={"q": "test", "rows": 10},
        )
        assert result["success"] is True
        assert result["result"]["count"] == 1

    @respx.mock
    async def test_ckan_error_response(self):
        """Test handling of CKAN API error response."""
        respx.get(f"{BASE_URL}/action/package_show").mock(
            return_value=Response(
                200,
                json={
                    "success": False,
                    "error": {
                        "message": "Not found",
                        "__type": "Not Found Error",
                    },
                },
            )
        )

        with pytest.raises(CKANAPIError) as exc_info:
            await ckan_api_call("package_show", params={"id": "nonexistent"})

        assert "Not found" in str(exc_info.value)

    @respx.mock
    async def test_http_error_404(self):
        """Test handling of HTTP 404 error."""
        respx.get(f"{BASE_URL}/action/package_show").mock(
            return_value=Response(404, text="Not Found")
        )

        with pytest.raises(CKANAPIError) as exc_info:
            await ckan_api_call("package_show", params={"id": "nonexistent"})

        assert exc_info.value.status_code == 404

    @respx.mock
    async def test_http_error_500_with_retry(self):
        """Test that 5xx errors trigger retry logic."""
        # First two requests fail with 500, third succeeds
        route = respx.get(f"{BASE_URL}/action/package_list")
        route.side_effect = [
            Response(500, text="Internal Server Error"),
            Response(500, text="Internal Server Error"),
            Response(
                200,
                json={
                    "success": True,
                    "result": ["dataset1"],
                },
            ),
        ]

        result = await ckan_api_call("package_list", max_retries=2)
        assert result["success"] is True

    @respx.mock
    async def test_http_error_500_max_retries_exceeded(self):
        """Test that max retries are respected."""
        respx.get(f"{BASE_URL}/action/package_list").mock(
            return_value=Response(500, text="Internal Server Error")
        )

        with pytest.raises(CKANAPIError) as exc_info:
            await ckan_api_call("package_list", max_retries=1)

        assert exc_info.value.status_code == 500

    @respx.mock
    async def test_network_error_with_retry(self):
        """Test that network errors trigger retry logic."""
        route = respx.get(f"{BASE_URL}/action/package_list")

        # Simulate network errors then success
        call_count = 0

        def side_effect(request):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                # Return 503 to simulate a transient error instead of raising
                return Response(503, text="Service Unavailable")
            return Response(
                200,
                json={
                    "success": True,
                    "result": ["dataset1"],
                },
            )

        route.side_effect = side_effect

        result = await ckan_api_call("package_list", max_retries=2)
        assert result["success"] is True
        assert call_count == 3
