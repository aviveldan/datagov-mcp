# server.py
from fastmcp import FastMCP
import requests

# Create an MCP server
mcp = FastMCP("DataGovILServer")


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
