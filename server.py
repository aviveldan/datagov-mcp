# server.py
from fastmcp import FastMCP, Context
import requests

# Create an MCP server
mcp = FastMCP("DataGovIL")

# Base URL for the API
BASE_URL = "https://data.gov.il/api/3"


@mcp.tool()
async def status_show(ctx: Context):
    """Get the CKAN version and a list of installed extensions."""
    await ctx.info("Fetching CKAN status...")
    response = requests.post(f"{BASE_URL}/action/status_show")
    response.raise_for_status()
    return response.json()


@mcp.tool()
async def license_list(ctx: Context):
    """Get the list of licenses available for datasets on the site."""
    await ctx.info("Fetching license list...")
    response = requests.get(f"{BASE_URL}/action/license_list")
    response.raise_for_status()
    return response.json()


@mcp.tool()
async def package_list(ctx: Context):
    """Get a list of all package IDs (datasets)."""
    await ctx.info("Fetching package list...")
    response = requests.get(f"{BASE_URL}/action/package_list")
    response.raise_for_status()
    return response.json()


@mcp.tool()
async def package_search(ctx: Context, q: str = "", fq: str = "", sort: str = "", rows: int = 20, start: int = 0, include_private: bool = False):
    """Find packages (datasets) matching query terms."""
    await ctx.info("Searching for packages...")
    params = {
        "q": q,
        "fq": fq,
        "sort": sort,
        "rows": rows,
        "start": start,
        "include_private": include_private
    }
    response = requests.get(f"{BASE_URL}/action/package_search", params=params)
    response.raise_for_status()
    return response.json()


@mcp.tool()
async def package_show(ctx: Context, id: str):
    """Get metadata about one specific package (dataset)."""
    await ctx.info(f"Fetching metadata for package: {id}")
    params = {"id": id}
    response = requests.get(f"{BASE_URL}/action/package_show", params=params)
    response.raise_for_status()
    return response.json()


@mcp.tool()
async def organization_list(ctx: Context):
    """Get names of all organizations."""
    await ctx.info("Fetching organization list...")
    response = requests.get(f"{BASE_URL}/action/organization_list")
    response.raise_for_status()
    return response.json()


@mcp.tool()
async def organization_show(ctx: Context, id: str):
    """Get details of a specific organization."""
    await ctx.info(f"Fetching details for organization: {id}")
    params = {"id": id}
    response = requests.get(f"{BASE_URL}/action/organization_show", params=params)
    response.raise_for_status()
    return response.json()


@mcp.tool()
async def resource_search(ctx: Context, query: str = "", order_by: str = "", offset: int = 0, limit: int = 100):
    """Find resources based on their field values."""
    await ctx.info("Searching for resources...")
    params = {
        "query": query,
        "order_by": order_by,
        "offset": offset,
        "limit": limit
    }
    response = requests.get(f"{BASE_URL}/action/resource_search", params=params)
    response.raise_for_status()
    return response.json()


@mcp.tool()
async def datastore_search(ctx: Context, resource_id: str, q: str = "", distinct: bool = False, plain: bool = True, limit: int = 100, offset: int = 0, fields: str = "", sort: str = "", include_total: bool = True, records_format: str = "objects"):
    """Search a datastore resource."""
    await ctx.info(f"Searching datastore for resource: {resource_id}")
    params = {
        "resource_id": resource_id,
        "q": q,
        "distinct": distinct,
        "plain": plain,
        "limit": limit,
        "offset": offset,
        "fields": fields,
        "sort": sort,
        "include_total": include_total,
        "records_format": records_format
    }
    response = requests.get(f"{BASE_URL}/action/datastore_search", params=params)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def fetch_data_gov_il(dataset_name: str, limit: int = 100, offset: int = 0):
    """Fetch data from the Israeli government public API (data.gov.il) based on a dataset name query"""
    def find_resource_id(dataset_name):
        dataset_url = f"https://data.gov.il/api/3/action/package_show?id={dataset_name}"
        response = requests.get(dataset_url)
        if response.status_code == 200:
            dataset_data = response.json()
            resources = dataset_data['result']['resources']
            if resources:
                return resources[0]['id']
        return None

    resource_id = find_resource_id(dataset_name)
    if not resource_id:
        return {"error": f"No dataset found matching '{dataset_name}'"}

    base_url = "https://data.gov.il/api/3/action/datastore_search"
    params = {
        "resource_id": resource_id,
        "limit": limit,
        "offset": offset
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    api_data = response.json()

    if api_data.get("success"):
        return api_data["result"]["records"]
    else:
        raise Exception(api_data.get("error", "Unknown error occurred"))


if __name__ == "__main__":
    # This code only runs when the file is executed directly
    mcp.run()
