"""Integration tests for MCP tools with mocked HTTP responses."""

import pytest
import respx
from httpx import Response

from datagov_mcp.api import BASE_URL
from datagov_mcp.server import (
    datastore_search,
    fetch_data,
    license_list,
    organization_list,
    organization_show,
    package_list,
    package_search,
    package_show,
    resource_search,
    status_show,
)


class MockContext:
    """Mock Context for testing."""

    def __init__(self):
        self.info_messages = []
        self.error_messages = []

    async def info(self, message: str):
        self.info_messages.append(message)

    async def error(self, message: str):
        self.error_messages.append(message)


@pytest.mark.asyncio
class TestTools:
    """Test all MCP tools with mocked API responses."""

    @respx.mock
    async def test_status_show(self):
        """Test status_show tool."""
        respx.post(f"{BASE_URL}/action/status_show").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "ckan_version": "2.9.0",
                        "site_title": "Data.gov.il",
                    },
                },
            )
        )

        ctx = MockContext()
        result = await status_show.fn(ctx)

        assert result["success"] is True
        assert "ckan_version" in result["result"]
        assert len(ctx.info_messages) > 0

    @respx.mock
    async def test_license_list(self):
        """Test license_list tool."""
        respx.get(f"{BASE_URL}/action/license_list").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "result": [
                        {"id": "cc-by", "title": "Creative Commons Attribution"},
                    ],
                },
            )
        )

        ctx = MockContext()
        result = await license_list.fn(ctx)

        assert result["success"] is True
        assert len(result["result"]) > 0

    @respx.mock
    async def test_package_list(self):
        """Test package_list tool."""
        respx.get(f"{BASE_URL}/action/package_list").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "result": ["dataset1", "dataset2", "dataset3"],
                },
            )
        )

        ctx = MockContext()
        result = await package_list.fn(ctx)

        assert result["success"] is True
        assert len(result["result"]) == 3

    @respx.mock
    async def test_package_search(self):
        """Test package_search tool."""
        respx.get(f"{BASE_URL}/action/package_search").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "count": 2,
                        "results": [
                            {"name": "test-dataset-1", "title": "Test Dataset 1"},
                            {"name": "test-dataset-2", "title": "Test Dataset 2"},
                        ],
                    },
                },
            )
        )

        ctx = MockContext()
        result = await package_search.fn(ctx, q="test", rows=10)

        assert result["success"] is True
        assert result["result"]["count"] == 2
        assert len(result["result"]["results"]) == 2

    @respx.mock
    async def test_package_show(self):
        """Test package_show tool."""
        respx.get(f"{BASE_URL}/action/package_show").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "id": "test-dataset",
                        "name": "test-dataset",
                        "title": "Test Dataset",
                        "resources": [
                            {"id": "resource1", "format": "CSV"},
                        ],
                    },
                },
            )
        )

        ctx = MockContext()
        result = await package_show.fn(ctx, id="test-dataset")

        assert result["success"] is True
        assert result["result"]["name"] == "test-dataset"
        assert len(result["result"]["resources"]) == 1

    @respx.mock
    async def test_organization_list(self):
        """Test organization_list tool."""
        respx.get(f"{BASE_URL}/action/organization_list").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "result": ["org1", "org2"],
                },
            )
        )

        ctx = MockContext()
        result = await organization_list.fn(ctx)

        assert result["success"] is True
        assert len(result["result"]) == 2

    @respx.mock
    async def test_organization_show(self):
        """Test organization_show tool."""
        respx.get(f"{BASE_URL}/action/organization_show").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "id": "test-org",
                        "name": "test-org",
                        "title": "Test Organization",
                        "package_count": 5,
                    },
                },
            )
        )

        ctx = MockContext()
        result = await organization_show.fn(ctx, id="test-org")

        assert result["success"] is True
        assert result["result"]["name"] == "test-org"

    @respx.mock
    async def test_resource_search(self):
        """Test resource_search tool."""
        respx.get(f"{BASE_URL}/action/resource_search").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "count": 1,
                        "results": [
                            {"id": "resource1", "name": "Test Resource"},
                        ],
                    },
                },
            )
        )

        ctx = MockContext()
        result = await resource_search.fn(ctx, query="name:test", limit=10)

        assert result["success"] is True
        assert result["result"]["count"] == 1

    @respx.mock
    async def test_datastore_search(self):
        """Test datastore_search tool."""
        respx.get(f"{BASE_URL}/action/datastore_search").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "total": 100,
                        "records": [
                            {"id": 1, "name": "Item 1"},
                            {"id": 2, "name": "Item 2"},
                        ],
                    },
                },
            )
        )

        ctx = MockContext()
        result = await datastore_search.fn(ctx, resource_id="test-resource", limit=2)

        assert result["success"] is True
        assert len(result["result"]["records"]) == 2

    @respx.mock
    async def test_fetch_data_success(self):
        """Test fetch_data tool with successful flow."""
        # Mock package_show
        respx.get(f"{BASE_URL}/action/package_show").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "name": "test-dataset",
                        "resources": [
                            {"id": "resource1", "format": "CSV"},
                        ],
                    },
                },
            )
        )

        # Mock datastore_search
        respx.get(f"{BASE_URL}/action/datastore_search").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "records": [
                            {"id": 1, "value": "data1"},
                            {"id": 2, "value": "data2"},
                        ],
                    },
                },
            )
        )

        ctx = MockContext()
        result = await fetch_data.fn(ctx, dataset_name="test-dataset", limit=10)

        assert "records" in result
        assert len(result["records"]) == 2
        assert result["resource_id"] == "resource1"

    @respx.mock
    async def test_fetch_data_no_resources(self):
        """Test fetch_data tool when dataset has no resources."""
        respx.get(f"{BASE_URL}/action/package_show").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "name": "test-dataset",
                        "resources": [],
                    },
                },
            )
        )

        ctx = MockContext()
        result = await fetch_data.fn(ctx, dataset_name="test-dataset")

        assert "error" in result
        assert "No resources found" in result["error"]

    @respx.mock
    async def test_tool_error_handling(self):
        """Test that tools handle API errors gracefully."""
        respx.get(f"{BASE_URL}/action/package_list").mock(
            return_value=Response(
                200,
                json={
                    "success": False,
                    "error": {"message": "Database connection failed"},
                },
            )
        )

        ctx = MockContext()
        with pytest.raises(Exception):
            await package_list.fn(ctx)

        assert len(ctx.error_messages) > 0
