# DataGov Israel MCP Server

A Model Context Protocol (MCP) server for interacting with the Israeli Government Public API (data.gov.il). Access thousands of public datasets with built-in visualization capabilities.

[![Tests](https://github.com/aviveldan/datagov-mcp/actions/workflows/test.yml/badge.svg)](https://github.com/aviveldan/datagov-mcp/actions/workflows/test.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Screenshots

### MCP Inspector Interface
Test and explore all available tools using the MCP Inspector:

![MCP Inspector Interface](https://github.com/user-attachments/assets/03b675e3-0602-4937-9d09-1569766ce4b8)

### Available Tools
Browse all 13 tools including CKAN API endpoints and visualization generators:

![Tools List](https://github.com/user-attachments/assets/f78e6233-96dd-4d17-bea2-b567bf986c3b)

---

## Features

- ✅ **Async I/O**: True async operations with httpx for optimal performance
- 🔍 **Full CKAN API Coverage**: Search datasets, organizations, and resources
- 📊 **Visualization Tools**: Generate charts and maps from data
- 🧪 **Comprehensive Tests**: 34+ automated tests with HTTP mocking
- 🚀 **Modern FastMCP**: Built on FastMCP 2.14+ with best practices
- 📦 **Type Safe**: Full type hints and validation

---

## Quick Start

### Installation

This project uses [uv](https://docs.astral.sh/uv/) package manager for fast, reliable dependency management.

```bash
git clone https://github.com/aviveldan/datagov-mcp.git
cd datagov-mcp

# Create virtual environment and install
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### Using with Claude Desktop

Install the server directly into Claude Desktop:

```bash
fastmcp install claude desktop server.py
```

Then restart Claude Desktop and you'll see the DataGovIL tools available!

### Testing with MCP Inspector

Launch the interactive inspector to test tools:

```bash
fastmcp dev server.py
```

This opens a web interface where you can:
- Browse all available tools
- Test tool calls with different parameters  
- View real-time responses
- Debug issues

--- 

---

## Available Tools

### Core CKAN Tools

#### `status_show`
Get the CKAN version and installed extensions.

```python
# Example response
{
  "success": true,
  "result": {
    "ckan_version": "2.9.0",
    "site_title": "Israel Open Data Portal"
  }
}
```

#### `license_list`
List all available licenses for datasets.

#### `package_list`
Get a list of all dataset IDs.

#### `package_search`
Search for datasets with filters.

**Parameters:**
- `q` (string): Query string (e.g., "education")
- `fq` (string): Filter query in SOLR format
- `sort` (string): Sort order (e.g., "metadata_modified desc")
- `rows` (int): Number of results (default: 20)
- `start` (int): Pagination offset (default: 0)
- `include_private` (bool): Include private datasets (default: false)

**Example:**
```python
# Search for education-related datasets
package_search(q="education", rows=10, sort="metadata_modified desc")
```

#### `package_show`
Get detailed metadata for a specific dataset.

**Parameters:**
- `id` (string, required): Dataset ID or name

**Example:**
```python
package_show(id="covid-19-data")
```

#### `organization_list`
List all organizations.

#### `organization_show`
Get details about a specific organization.

**Parameters:**
- `id` (string, required): Organization ID or name

#### `resource_search`
Search for resources within datasets.

**Parameters:**
- `query` (string): SOLR query (e.g., "format:CSV")
- `order_by` (string): Sort field
- `offset` (int): Pagination offset
- `limit` (int): Maximum results (default: 100)

#### `datastore_search`
Search data within a datastore resource.

**Parameters:**
- `resource_id` (string, required): Resource ID
- `q` (string): Full-text query
- `limit` (int): Max records (default: 100)
- `offset` (int): Pagination offset
- `sort` (string): Sort order
- `fields` (string): Comma-separated field names
- Other CKAN datastore parameters

**Example:**
```python
datastore_search(
  resource_id="abc123",
  q="Tel Aviv",
  limit=50,
  sort="date desc"
)
```

#### `fetch_data`
Convenience tool to get data from a dataset by name.

Automatically finds the first resource and fetches its data.

**Parameters:**
- `dataset_name` (string, required): Dataset name or ID
- `limit` (int): Number of records (default: 100)
- `offset` (int): Pagination offset

---

### Visualization Tools 📊

#### `dataset_profile`
Profile a dataset to understand its structure and quality.

**Parameters:**
- `resource_id` (string, required): Resource ID to profile
- `sample_size` (int): Number of records to analyze (default: 100)

**Returns:**
- Field types (integer, number, string, coordinate)
- Missing value statistics
- Numeric statistics (min, max, mean)
- Top values for categorical fields

**Example:**
```python
dataset_profile(resource_id="abc123", sample_size=500)
```

**Response:**
```json
{
  "resource_id": "abc123",
  "sample_size": 500,
  "total_fields": 5,
  "fields": [
    {
      "name": "age",
      "type": "integer",
      "stats": {
        "count": 500,
        "null_count": 5,
        "min": 18,
        "max": 95,
        "mean": 42.3
      },
      "missingness": 0.01
    },
    {
      "name": "city",
      "type": "string",
      "stats": {
        "count": 500,
        "null_count": 2,
        "unique_count": 12,
        "top_values": {
          "Tel Aviv": 150,
          "Jerusalem": 120,
          "Haifa": 80
        }
      },
      "missingness": 0.004
    }
  ]
}
```

#### `chart_generator`
Generate interactive Vega-Lite charts.

**Parameters:**
- `resource_id` (string, required): Resource ID
- `chart_type` (string, required): 'histogram', 'bar', 'line', or 'scatter'
- `x_field` (string, required): X-axis field name
- `y_field` (string): Y-axis field name (not needed for histogram)
- `title` (string): Chart title
- `limit` (int): Max records to visualize (default: 100)

**Returns:**
- `vega_lite_spec`: Vega-Lite JSON specification
- `html`: Self-contained HTML with embedded chart

**Example:**
```python
# Create a histogram
chart_generator(
  resource_id="abc123",
  chart_type="histogram",
  x_field="age",
  title="Age Distribution"
)

# Create a bar chart
chart_generator(
  resource_id="abc123",
  chart_type="bar",
  x_field="city",
  y_field="population",
  title="Population by City"
)
```

#### `map_generator`
Generate interactive maps from geographic data.

**Parameters:**
- `resource_id` (string, required): Resource ID
- `lat_field` (string, required): Latitude field name
- `lon_field` (string, required): Longitude field name
- `limit` (int): Max points to map (default: 500)

**Returns:**
- `geojson`: GeoJSON FeatureCollection
- `html`: Interactive Leaflet map
- `point_count`: Number of valid points
- `center`: Map center coordinates

**Example:**
```python
map_generator(
  resource_id="abc123",
  lat_field="latitude",
  lon_field="longitude",
  limit=1000
)
```

---

## Usage Examples

### Finding and Visualizing Data

```python
# 1. Search for datasets
results = package_search(q="traffic accidents", rows=5)

# 2. Get dataset details
dataset = package_show(id=results["result"]["results"][0]["name"])

# 3. Get the resource ID
resource_id = dataset["result"]["resources"][0]["id"]

# 4. Profile the data
profile = dataset_profile(resource_id=resource_id)

# 5. Generate a map if geographic data exists
if any(f["type"] == "coordinate" for f in profile["fields"]):
    map_data = map_generator(
        resource_id=resource_id,
        lat_field="latitude",
        lon_field="longitude"
    )
    # Save the HTML map
    with open("map.html", "w") as f:
        f.write(map_data["html"])
```

### Creating Visualizations

```python
# Get COVID-19 data
data = fetch_data(dataset_name="covid-19-cases")

# Profile to understand the data
profile = dataset_profile(resource_id=data["resource_id"])

# Create a line chart of cases over time
chart = chart_generator(
    resource_id=data["resource_id"],
    chart_type="line",
    x_field="date",
    y_field="new_cases",
    title="COVID-19 New Cases Over Time"
)

# Save the chart
with open("chart.html", "w") as f:
    f.write(chart["html"])
```

---

---

## Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_tools.py -v

# Run with coverage
pytest tests/ --cov=datagov_mcp
```

### Code Style

```bash
# Check code
ruff check .

# Format code
ruff format .
```

### Project Structure

```
datagov-mcp/
├── datagov_mcp/           # Main package
│   ├── __init__.py
│   ├── server.py          # Core CKAN tools
│   ├── api.py             # CKAN API helper
│   ├── client.py          # HTTP client
│   └── visualization.py   # Visualization tools
├── tests/                 # Test suite (34 tests)
│   ├── test_api.py
│   ├── test_contracts.py
│   ├── test_tools.py
│   └── test_visualization.py
├── server.py              # Entrypoint
└── pyproject.toml         # Dependencies
```

---

## Architecture

### Async HTTP Layer

All HTTP requests use `httpx.AsyncClient` with:
- 30-second timeout
- Automatic retries for 5xx errors
- Proper error handling and logging
- Connection pooling

### Error Handling

```python
from datagov_mcp.api import CKANAPIError

try:
    result = await ckan_api_call("package_show", params={"id": "test"})
except CKANAPIError as e:
    print(f"Error: {e.message}")
    print(f"Status code: {e.status_code}")
```

---

## Release Notes

See [CHANGELOG.md](CHANGELOG.md) for detailed release notes.

### Latest: v0.3.0 (2024-02-14)

**Major modernization release:**
- ✅ Migrated to async httpx (from blocking requests)
- ✅ Added 3 visualization tools (profile, charts, maps)
- ✅ Comprehensive test suite (34 tests, 100% pass rate)
- ✅ CI/CD with GitHub Actions
- ✅ Package structure with proper modules
- ✅ Detailed documentation and examples

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Quick start:
1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

For examples of other MCP servers, see the [Model Context Protocol servers repository](https://github.com/modelcontextprotocol/servers).

---

## Troubleshooting

### Port Conflicts

If you encounter port conflicts with MCP Inspector:

```bash
# Install nano-dev-utils
pip install nano-dev-utils

# Release ports
python -c "from nano_dev_utils import release_ports; release_ports.PortsRelease().release_all()"
```

### Windows + OneDrive

For Windows users: avoid running installation in folders watched by OneDrive. See [this issue](https://github.com/astral-sh/uv/issues/7906) for details.

### Import Errors

If you encounter import errors, ensure you installed in editable mode:

```bash
pip install -e ".[dev]"
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

---

## Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp)
- Data from [Israel Open Data Portal](https://data.gov.il)
- Charts powered by [Vega-Lite](https://vega.github.io/vega-lite/)
- Maps powered by [Leaflet](https://leafletjs.com/)
