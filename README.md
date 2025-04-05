# DataGov Israel MCP Server

Easily interact with the Israeli Government Public API (data.gov.il) using this project, which combines a Flask-based MCP server and an OpenAI-integrated client to fetch and process data.

---

## Quick Start


### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd datagov-mcp
   ```
2. Install dependencies:
   ```bash
   uv pip install -r pyproject.toml
   ```



### Usage
You can install this server in [Claude Desktop](https://claude.ai/download) and interact with it right away by running:
```bash
fastmcp install server.py
```

Alternatively, you can test it with the MCP Inspector:
```bash
fastmcp dev server.py
```
