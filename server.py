# server.py
from fastmcp import FastMCP, Context
import requests

# Create an MCP server
mcp = FastMCP("DataGovILServer")

# Base URL for the API
BASE_URL = "https://data.gov.il/api/3"

@mcp.tool()
def status_show():
    """Get the CKAN version and a list of installed extensions."""
    response = requests.post(f"{BASE_URL}/action/status_show")
    response.raise_for_status()
    return response.json()

@mcp.tool()
def license_list():
    """Get the list of licenses available for datasets on the site."""
    response = requests.get(f"{BASE_URL}/action/license_list")
    response.raise_for_status()
    return response.json()

@mcp.tool()
def package_list():
    """Get a list of all package IDs (datasets)."""
    response = requests.get(f"{BASE_URL}/action/package_list")
    response.raise_for_status()
    return response.json()

@mcp.tool()
def package_search(q: str = "", fq: str = "", sort: str = "", rows: int = 20, start: int = 0, include_private: bool = False):
    """Find packages (datasets) matching query terms."""
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
def package_show(id: str):
    """Get metadata about one specific package (dataset)."""
    params = {"id": id}
    response = requests.get(f"{BASE_URL}/action/package_show", params=params)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def organization_list():
    """Get names of all organizations."""
    response = requests.get(f"{BASE_URL}/action/organization_list")
    response.raise_for_status()
    return response.json()

@mcp.tool()
def organization_show(id: str):
    """Get details of a specific organization."""
    params = {"id": id}
    response = requests.get(f"{BASE_URL}/action/organization_show", params=params)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def resource_search(query: str = "", order_by: str = "", offset: int = 0, limit: int = 100):
    """Find resources based on their field values."""
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
def datastore_search(resource_id: str, q: str = "", distinct: bool = False, plain: bool = True, limit: int = 100, offset: int = 0, fields: str = "", sort: str = "", include_total: bool = True, records_format: str = "objects"):
    """Search a datastore resource."""
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

@mcp.tool()
async def fetch_all_packages_metadata(ctx: Context):
    """Fetch metadata for all available packages asynchronously with progress tracking."""
    try:
        # Step 1: Get the list of all package IDs
        package_ids = package_list()
        if not package_ids.get("success"):
            return {"error": "Failed to fetch package list."}

        package_ids = package_ids["result"]
        total_packages = len(package_ids)
        all_metadata = []

        # Step 2: Fetch metadata for each package asynchronously
        for i, package_id in enumerate(package_ids):
            if i == 50: # currently limiting to 50 packages for demonstration purposes
                break
            ctx.info(f"Fetching metadata for package: {package_id}")
            await ctx.report_progress(i, total_packages)

            try:
                metadata = package_show(package_id)
                if metadata.get("success"):
                    all_metadata.append(metadata["result"])
            except Exception as e:
                all_metadata.append({"id": package_id, "error": str(e)})

        # Step 3: Return the compiled metadata
        return {"success": True, "packages": all_metadata}

    except Exception as e:
        return {"error": str(e)}
