# DataGov Israel MCP Server

DataGov Israel MCP Server is a Python-based Model Context Protocol (MCP) server that provides easy interaction with the Israeli Government Public API (data.gov.il). The server exposes 9 tools for querying datasets, organizations, resources, and datastore records.

**ALWAYS reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Working Effectively

### Bootstrap and Environment Setup
Always perform these steps in order:

1. **Install uv package manager** (if not available):
   ```bash
   pip install uv
   export PATH="$HOME/.local/bin:$PATH"
   ```
   - Takes ~30 seconds. Set timeout to 120+ seconds.

2. **Create and activate virtual environment**:
   ```bash
   uv venv
   source .venv/bin/activate  # Linux/macOS
   # OR: .venv\Scripts\activate  # Windows
   ```
   - Takes ~10 seconds. Set timeout to 60+ seconds.

3. **Install dependencies**:
   ```bash
   uv pip install -r pyproject.toml
   uv lock
   ```
   - Takes ~35 seconds total. Set timeout to 180+ seconds.

**NEVER CANCEL** any of these setup commands. Total setup time is approximately 45 seconds but can vary with network conditions.

### Running the Server

**Development with MCP Inspector** (recommended):
```bash
fastmcp dev server.py
```
- Starts server with web-based MCP Inspector at http://localhost:6274
- Takes ~15 seconds to start. Set timeout to 120+ seconds.
- **NEVER CANCEL** - npm package download may take time on first run

**Direct server execution**:
```bash
python server.py
```
- Runs server in STDIO mode for direct MCP client connections
- Starts immediately

**Claude Desktop integration**:
```bash
fastmcp install claude-desktop server.py
```
- Installs server in Claude Desktop configuration
- **Note**: README.md shows incorrect command `claude desktop` - use `claude-desktop` instead

### Development Workflow

**Always validate your changes by**:
1. Run `python -m py_compile server.py` to check syntax
2. Start the dev server with `fastmcp dev server.py`
3. Open the MCP Inspector and test tool functionality
4. Verify API tool imports and structure

**Port management** (if ports are busy):
```bash
uv pip install nano-dev-utils
python -c "
from nano_dev_utils import release_ports 
pr = release_ports.PortsRelease()
pr.release_all()
"
```

## API Tools Available

The server provides these validated tools for data.gov.il API:
- `status_show` - Display CKAN status and extensions
- `license_list` - List available licenses
- `package_list` - List all package IDs (datasets)
- `package_search` - Search packages with filters
- `package_show` - Show specific package details
- `organization_list` - List all organizations
- `organization_show` - Show organization details
- `resource_search` - Search resources with filters
- `datastore_search` - Search datastore records
- `fetch_data` - Fetch data by dataset name

## Validation

**ALWAYS test after making changes**:
1. **Syntax validation**: `python -m py_compile server.py`
2. **Server startup**: `fastmcp dev server.py` and verify it starts without errors
3. **MCP Inspector**: Open http://localhost:6274 and test tool discovery
4. **Tool structure**: Verify all 9 tools are listed in the inspector

**Complete user scenario testing**:
After any API tool modifications, test through the MCP Inspector:
1. Start dev server: `fastmcp dev server.py`
2. Open inspector at http://localhost:6274
3. Verify all tools are listed under "Available Tools"
4. Test at least one tool call (e.g., `status_show`) to ensure API structure is correct
5. Check error handling for invalid parameters

**Note**: External API calls to data.gov.il may not work in all environments due to network restrictions, but tool structure and MCP functionality should always be testable.

## Troubleshooting

**Common issues and solutions**:
- **"uv not found"**: Install with `pip install uv` and add to PATH
- **Import errors**: Ensure virtual environment is activated and dependencies installed
- **Port conflicts**: Use nano-dev-utils port release functionality
- **Slow startup**: Network downloads are normal on first run - **NEVER CANCEL**
- **MCP Inspector not loading**: Check ports 6274/6277 are available

**Build failures**: 
- No formal build process exists - this is a simple Python script
- Only validation is syntax checking with `python -m py_compile`

## Project Structure

```
/home/runner/work/datagov-mcp/datagov-mcp/
├── .github/
│   └── copilot-instructions.md  # This file
├── .venv/                       # Virtual environment (created by uv venv)
├── server.py                    # Main MCP server implementation
├── pyproject.toml              # Project dependencies and metadata
├── README.md                   # Project documentation
├── uv.lock                     # Dependency lock file
├── .python-version             # Python 3.10.11
└── .gitignore                  # Git ignore patterns
```

## Key Development Patterns

**Adding new API tools**:
1. Add `@mcp.tool()` decorated async function to server.py
2. Follow existing parameter patterns with Context and type hints
3. Use `await ctx.info()` for logging
4. Always test with MCP Inspector

**Modifying existing tools**:
1. Update function signature and docstring
2. Test parameter validation
3. Verify API response handling
4. Update README.md if tool behavior changes significantly

**Dependencies**:
- Core: `fastmcp>=2.8.1`, `requests>=2.32.4`
- Development: `nano-dev-utils` (optional, for port management)
- No testing framework configured
- No linting tools configured

**CRITICAL**: This project has no formal test suite or CI/CD pipeline. Always manually validate changes using the MCP Inspector and direct server testing.