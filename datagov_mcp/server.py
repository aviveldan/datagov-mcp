"""Main MCP server implementation with CKAN tools."""

from fastmcp import FastMCP, Context

from datagov_mcp.api import ckan_api_call, CKANAPIError

# Create an MCP server
mcp = FastMCP("DataGovIL", dependencies=["httpx"])


@mcp.tool()
async def status_show(ctx: Context) -> dict:
    """Get the CKAN version and a list of installed extensions."""
    await ctx.info("Fetching CKAN status...")
    try:
        return await ckan_api_call("status_show", method="POST")
    except CKANAPIError as e:
        await ctx.error(f"Failed to fetch status: {e.message}")
        raise


@mcp.tool()
async def license_list(ctx: Context) -> dict:
    """Get the list of licenses available for datasets on the site."""
    await ctx.info("Fetching license list...")
    try:
        return await ckan_api_call("license_list")
    except CKANAPIError as e:
        await ctx.error(f"Failed to fetch licenses: {e.message}")
        raise


@mcp.tool()
async def package_list(ctx: Context) -> dict:
    """Get a list of all package IDs (datasets)."""
    await ctx.info("Fetching package list...")
    try:
        return await ckan_api_call("package_list")
    except CKANAPIError as e:
        await ctx.error(f"Failed to fetch packages: {e.message}")
        raise


@mcp.tool()
async def package_search(
    ctx: Context,
    q: str = "",
    fq: str = "",
    sort: str = "",
    rows: int = 20,
    start: int = 0,
    include_private: bool = False,
) -> dict:
    """
    Find packages (datasets) matching query terms.

    Args:
        q: Query string to search for
        fq: Filter query in SOLR format
        sort: Sorting order (e.g., 'metadata_modified desc')
        rows: Number of results to return (default: 20)
        start: Starting index for pagination (default: 0)
        include_private: Include private datasets (default: False)

    Returns:
        Search results with matching packages
    """
    await ctx.info("Searching for packages...")
    try:
        params = {
            "q": q,
            "fq": fq,
            "sort": sort,
            "rows": rows,
            "start": start,
            "include_private": include_private,
        }
        return await ckan_api_call("package_search", params=params)
    except CKANAPIError as e:
        await ctx.error(f"Failed to search packages: {e.message}")
        raise


@mcp.tool()
async def package_show(ctx: Context, id: str) -> dict:
    """
    Get metadata about one specific package (dataset).

    Args:
        id: The ID or name of the package

    Returns:
        Complete package metadata including resources
    """
    await ctx.info(f"Fetching metadata for package: {id}")
    try:
        return await ckan_api_call("package_show", params={"id": id})
    except CKANAPIError as e:
        await ctx.error(f"Failed to fetch package: {e.message}")
        raise


@mcp.tool()
async def organization_list(ctx: Context) -> dict:
    """Get names of all organizations."""
    await ctx.info("Fetching organization list...")
    try:
        return await ckan_api_call("organization_list")
    except CKANAPIError as e:
        await ctx.error(f"Failed to fetch organizations: {e.message}")
        raise


@mcp.tool()
async def organization_show(ctx: Context, id: str) -> dict:
    """
    Get details of a specific organization.

    Args:
        id: The ID or name of the organization

    Returns:
        Organization details including datasets
    """
    await ctx.info(f"Fetching details for organization: {id}")
    try:
        return await ckan_api_call("organization_show", params={"id": id})
    except CKANAPIError as e:
        await ctx.error(f"Failed to fetch organization: {e.message}")
        raise


@mcp.tool()
async def resource_search(
    ctx: Context,
    query: str = "",
    order_by: str = "",
    offset: int = 0,
    limit: int = 100,
) -> dict:
    """
    Find resources based on their field values.

    Args:
        query: Query string in SOLR format (e.g., 'name:data')
        order_by: Field to order by
        offset: Starting index for pagination
        limit: Maximum number of results

    Returns:
        Search results with matching resources
    """
    await ctx.info("Searching for resources...")
    try:
        params = {
            "query": query,
            "order_by": order_by,
            "offset": offset,
            "limit": limit,
        }
        return await ckan_api_call("resource_search", params=params)
    except CKANAPIError as e:
        await ctx.error(f"Failed to search resources: {e.message}")
        raise


@mcp.tool()
async def datastore_search(
    ctx: Context,
    resource_id: str,
    q: str = "",
    distinct: bool = False,
    plain: bool = True,
    limit: int = 100,
    offset: int = 0,
    fields: str = "",
    sort: str = "",
    include_total: bool = True,
    records_format: str = "objects",
) -> dict:
    """
    Search a datastore resource.

    Args:
        resource_id: ID of the resource to search
        q: Full-text query string
        distinct: Return only distinct results
        plain: Use plain text search (vs. PostgreSQL full-text)
        limit: Maximum number of records to return
        offset: Starting index for pagination
        fields: Comma-separated list of fields to return
        sort: Comma-separated list of fields to sort by
        include_total: Include total result count
        records_format: Format of records ('objects', 'lists', or 'csv')

    Returns:
        Datastore search results with records
    """
    await ctx.info(f"Searching datastore for resource: {resource_id}")
    try:
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
            "records_format": records_format,
        }
        return await ckan_api_call("datastore_search", params=params)
    except CKANAPIError as e:
        await ctx.error(f"Failed to search datastore: {e.message}")
        raise


@mcp.tool()
async def fetch_data(
    ctx: Context,
    dataset_name: str,
    limit: int = 100,
    offset: int = 0,
) -> dict:
    """
    Fetch data from public API based on a dataset name query.

    This is a convenience tool that combines package_show and datastore_search.
    It finds the first resource of a dataset and returns its data.

    Args:
        dataset_name: Name or ID of the dataset
        limit: Number of records to fetch
        offset: Starting index for pagination

    Returns:
        Records from the first resource of the dataset
    """
    await ctx.info(f"Fetching data for dataset: {dataset_name}")
    try:
        # First, get the dataset metadata
        package_data = await ckan_api_call("package_show", params={"id": dataset_name})
        resources = package_data.get("result", {}).get("resources", [])

        if not resources:
            return {"error": f"No resources found in dataset '{dataset_name}'"}

        # Use the first resource
        resource_id = resources[0]["id"]
        await ctx.info(f"Using resource: {resource_id}")

        # Fetch data from the datastore
        result = await ckan_api_call(
            "datastore_search",
            params={
                "resource_id": resource_id,
                "limit": limit,
                "offset": offset,
            },
        )

        # Return just the records for convenience
        if result.get("success"):
            return {"records": result["result"]["records"], "resource_id": resource_id}
        else:
            return {"error": "Failed to fetch data from datastore"}

    except CKANAPIError as e:
        await ctx.error(f"Failed to fetch data: {e.message}")
        return {"error": str(e.message)}
