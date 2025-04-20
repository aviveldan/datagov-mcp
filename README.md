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
2. Install dependencies:
   ```bash
   uv venv
   .venv\Scripts\activate  # source .venv/bin/activate for MacOS / Linux
   uv pip install -r pyproject.toml
   uv lock # update the project's lockfile
   ```
   

### Usage
You can install this server in [Claude Desktop](https://claude.ai/download) and interact with it right away by running:
```bash
mcp install server.py
```

Alternatively, you can test it with the MCP Inspector:
```bash
mcp dev server.py
```

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

## Contributing

We welcome contributions to help improve the DataGov Israel MCP server. Whether you want to add new tools, enhance existing functionality, or improve documentation, your input is valuable.

For examples of other MCP servers and implementation patterns, see the [Model Context Protocol servers repository](https://github.com/modelcontextprotocol/servers).

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
