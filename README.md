# DataGov Israel MCP Server

Easily interact with the Israeli Government Public API (data.gov.il) using this project.

---

## Quick Start

### Requirements

#### uv
This project uses the [uv](https://docs.astral.sh/uv/) package manager, a drop-in replacement to pip.

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd datagov-mcp
   ```
2. Install dependencies (for windows users - [refrain from running this script in folders watched by onedrive](https://github.com/astral-sh/uv/issues/7906)):
   ```bash
   uv venv
   .venv\Scripts\activate  # source .venv/bin/activate for MacOS / Linux
   uv pip install -r pyproject.toml
   uv lock # update the project's lockfile
   ```
   

### Usage
You can install this server in [Claude Desktop](https://claude.ai/download) and interact with it right away by running:
```bash
fastmcp install claude desktop server.py
```

Alternatively, you can test it with the MCP Inspector:
```bash
fastmcp dev server.py
```

If client / server ports are busy, you can easily free them using [nano-dev-utils](https://pypi.org/project/nano-dev-utils/):
```bash
uv pip install nano-dev-utils
```
in terminal type 'python', and then run the following code:

```python
from nano_dev_utils import release_ports 
pr = release_ports.PortsRelease()
pr.release_all()
```
type exit() to get back to terminal. Alternatively run the above code as a script. 

## Available Tools

* `status_show` - Display the current status of the server
* `license_list` - List all available licenses
* `package_list` - List all available packages
* `package_search` - Search for packages with various filters
  * Required arguments:
    * `q` (string): Query string to search for
    * `fq` (string): Filter query
    * `sort` (string): Sorting order
    * `rows` (int): Number of rows to return
    * `start` (int): Starting index
    * `include_private` (bool): Include private packages
* `package_show` - Show details of a specific package
  * Required arguments:
    * `id` (string): ID of the package
* `organization_list` - List all organizations
* `organization_show` - Show details of a specific organization
  * Required arguments:
    * `id` (string): ID of the organization
* `resource_search` - Search for resources with various filters
  * Required arguments:
    * `query` (string): Query string to search for
    * `order_by` (string): Order by field
    * `offset` (int): Offset for pagination
    * `limit` (int): Limit for pagination
* `datastore_search` - Search the datastore with various filters
  * Required arguments:
    * `resource_id` (string): ID of the resource
    * `q` (string): Query string to search for
    * `distinct` (bool): Return distinct results
    * `plain` (bool): Return plain results
    * `limit` (int): Limit for pagination
    * `offset` (int): Offset for pagination
    * `fields` (string): Fields to include in the result
    * `sort` (string): Sorting order
    * `include_total` (bool): Include total count
    * `records_format` (string): Format of the records
* `fetch_data` - Fetch data from public API based on a dataset name query
  * Required arguments:
    * `dataset_name` (string): Name of the dataset
    * `limit` (int): Number of records to fetch
    * `offset` (int): Offset for pagination

## Available Prompts

The server now includes guided prompts that help users work more effectively with Israeli government data:

* `discover_datasets` - Guide users through discovering relevant datasets based on topic of interest
  * Required arguments:
    * `topic` (string): Main topic or domain of interest (e.g., "education", "health", "transportation")
    * `organization` (string, optional): Specific organization to focus on (e.g., "משרד החינוך")
  
* `analyze_dataset_workflow` - Comprehensive workflow for analyzing a specific dataset
  * Required arguments:
    * `dataset_id` (string): ID or name of the dataset to analyze
    * `analysis_goal` (string, optional): Analysis objective ("trend analysis", "comparison", "general exploration", "statistical analysis")

* `explore_organization_data` - Guide for exploring all datasets from a specific government organization
  * Required arguments:
    * `organization_name` (string, optional): Name of organization to explore (Hebrew or English)

* `search_optimization_guide` - Optimization guide for creating effective search queries
  * Required arguments:
    * `search_objective` (string, optional): Type of search ("specific dataset", "topic exploration", "recent data", "api data")

### Using Prompts

These prompts provide structured guidance and can be used with MCP-compatible clients like Claude Desktop. Each prompt generates a detailed workflow with specific tool recommendations and parameter suggestions tailored to working with Israeli government data.

Example usage scenarios:
- **Data Discovery**: Use `discover_datasets` with topic "חינוך" to find all education-related datasets
- **Dataset Analysis**: Use `analyze_dataset_workflow` with a specific dataset ID to get a complete analysis workflow
- **Organization Exploration**: Use `explore_organization_data` with "משרד הבריאות" to explore all health ministry data
- **Search Optimization**: Use `search_optimization_guide` to learn advanced search techniques

## Contributing

We welcome contributions to help improve the DataGov Israel MCP server. Whether you want to add new tools, enhance existing functionality, or improve documentation, your input is valuable.

For examples of other MCP servers and implementation patterns, see the [Model Context Protocol servers repository](https://github.com/modelcontextprotocol/servers).

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
