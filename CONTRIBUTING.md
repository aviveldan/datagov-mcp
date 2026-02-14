# Contributing to DataGov Israel MCP Server

Thank you for your interest in contributing to the DataGov Israel MCP Server! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites
- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended) or pip

### Setting Up Your Development Environment

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/datagov-mcp.git
   cd datagov-mcp
   ```

2. **Create a virtual environment and install dependencies**
   ```bash
   # Using uv (recommended)
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e ".[dev]"
   
   # Or using pip
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Verify installation**
   ```bash
   pytest tests/
   ```

## Development Workflow

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

We use `ruff` for linting and formatting:

```bash
# Check code style
ruff check .

# Format code
ruff format .

# Fix auto-fixable issues
ruff check --fix .
```

### Testing with MCP Inspector

Test the server interactively:

```bash
fastmcp dev server.py
```

This opens the MCP Inspector where you can:
- Browse available tools
- Test tool calls with different parameters
- View responses and errors

## Making Changes

### Adding a New Tool

1. **Define the tool in the appropriate module**
   - Core CKAN tools go in `datagov_mcp/server.py`
   - Visualization tools go in `datagov_mcp/visualization.py`

2. **Use the `@mcp.tool()` decorator**
   ```python
   @mcp.tool()
   async def my_new_tool(ctx: Context, param: str) -> dict:
       """
       Tool description that appears in MCP clients.
       
       Args:
           param: Parameter description
           
       Returns:
           Result description
       """
       await ctx.info("Processing...")
       # Implementation
       return {"result": "data"}
   ```

3. **Add tests**
   - Create tests in `tests/test_*.py`
   - Include both happy path and error scenarios
   - Use `respx` to mock HTTP calls

4. **Update documentation**
   - Add tool to README.md
   - Update CHANGELOG.md

### Adding Tests

We use pytest with async support and HTTP mocking:

```python
import pytest
import respx
from httpx import Response

@pytest.mark.asyncio
@respx.mock
async def test_my_tool():
    # Mock HTTP response
    respx.get("https://data.gov.il/api/3/action/...").mock(
        return_value=Response(
            200,
            json={"success": True, "result": {...}}
        )
    )
    
    # Test the tool
    from datagov_mcp.server import my_tool
    ctx = MockContext()
    result = await my_tool.fn(ctx, param="test")
    
    assert result["success"] is True
```

### Commit Messages

Follow conventional commit format:

- `feat: add new chart type support`
- `fix: handle missing coordinates in map generator`
- `docs: update README with new examples`
- `test: add tests for edge cases`
- `refactor: simplify error handling`
- `chore: update dependencies`

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes**
   - Write code
   - Add tests
   - Update documentation

3. **Ensure tests pass**
   ```bash
   pytest tests/
   ruff check .
   ruff format --check .
   ```

4. **Push and create PR**
   ```bash
   git push origin feature/my-new-feature
   ```

5. **PR Requirements**
   - All tests must pass
   - Code must be properly formatted
   - Include description of changes
   - Reference any related issues

## Project Structure

```
datagov-mcp/
├── datagov_mcp/           # Main package
│   ├── __init__.py        # Package initialization
│   ├── server.py          # Core CKAN tools
│   ├── api.py             # CKAN API helper
│   ├── client.py          # HTTP client management
│   └── visualization.py   # Visualization tools
├── tests/                 # Test suite
│   ├── test_api.py        # API helper tests
│   ├── test_contracts.py  # Tool contract tests
│   ├── test_tools.py      # Tool integration tests
│   └── test_visualization.py  # Visualization tests
├── server.py              # Backward-compatible entrypoint
├── pyproject.toml         # Project metadata and dependencies
├── README.md              # Project documentation
├── CHANGELOG.md           # Version history
└── CONTRIBUTING.md        # This file
```

## Code Guidelines

### Python Style
- Use type hints for function parameters and return values
- Follow PEP 8 style guide (enforced by ruff)
- Maximum line length: 100 characters
- Use descriptive variable names

### Async/Await
- All tools must be `async def`
- Use `httpx.AsyncClient` for HTTP requests
- Use `await` for async operations
- Never use blocking calls (like `requests.get()`) in async functions

### Error Handling
- Catch specific exceptions
- Log errors with `ctx.error()`
- Return meaningful error messages
- Use `CKANAPIError` for API failures

### Documentation
- Write clear docstrings for all public functions
- Include parameter descriptions
- Document return values
- Add examples where helpful

## Release Process

1. **Update version** in `pyproject.toml` and `datagov_mcp/__init__.py`
2. **Update CHANGELOG.md** with release notes
3. **Create a git tag**
   ```bash
   git tag -a v0.X.0 -m "Release v0.X.0"
   git push origin v0.X.0
   ```
4. **Create GitHub Release** with notes from CHANGELOG

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas
- Check existing issues before creating new ones

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

Thank you for contributing! 🎉
