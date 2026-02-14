"""Contract tests for MCP tools - ensures API stability."""

import pytest
from fastmcp import FastMCP

from datagov_mcp.server import mcp


class TestToolContracts:
    """Test that tool names and parameters remain stable."""

    def test_server_is_fastmcp_instance(self):
        """Verify server is a FastMCP instance."""
        assert isinstance(mcp, FastMCP)
        assert mcp.name == "DataGovIL"

    @pytest.mark.asyncio
    async def test_all_tools_exist(self):
        """Verify all expected tools are registered."""
        expected_tools = [
            "status_show",
            "license_list",
            "package_list",
            "package_search",
            "package_show",
            "organization_list",
            "organization_show",
            "resource_search",
            "datastore_search",
            "fetch_data",
        ]

        tools = await mcp.get_tools()
        tool_names = list(tools.keys())
        for tool_name in expected_tools:
            assert tool_name in tool_names, f"Tool {tool_name} not found"

    @pytest.mark.asyncio
    async def test_status_show_signature(self):
        """Verify status_show tool signature."""
        tools = await mcp.get_tools()
        tool = tools["status_show"]
        assert tool is not None
        assert "Get the CKAN version" in tool.description

    @pytest.mark.asyncio
    async def test_package_search_signature(self):
        """Verify package_search tool has expected parameters."""
        tools = await mcp.get_tools()
        tool = tools["package_search"]
        assert tool is not None

        # Check parameter names exist in the schema
        schema = tool.parameters
        props = schema.get("properties", {})

        expected_params = ["q", "fq", "sort", "rows", "start", "include_private"]
        for param in expected_params:
            assert param in props, f"Parameter {param} not found in package_search"

    @pytest.mark.asyncio
    async def test_package_show_signature(self):
        """Verify package_show requires 'id' parameter."""
        tools = await mcp.get_tools()
        tool = tools["package_show"]
        assert tool is not None

        schema = tool.parameters
        required = schema.get("required", [])
        assert "id" in required, "package_show should require 'id' parameter"

    @pytest.mark.asyncio
    async def test_datastore_search_signature(self):
        """Verify datastore_search tool has expected parameters."""
        tools = await mcp.get_tools()
        tool = tools["datastore_search"]
        assert tool is not None

        schema = tool.parameters
        props = schema.get("properties", {})
        required = schema.get("required", [])

        assert "resource_id" in required
        assert "limit" in props
        assert "offset" in props

    @pytest.mark.asyncio
    async def test_fetch_data_signature(self):
        """Verify fetch_data tool signature."""
        tools = await mcp.get_tools()
        tool = tools["fetch_data"]
        assert tool is not None

        schema = tool.parameters
        required = schema.get("required", [])
        assert "dataset_name" in required
