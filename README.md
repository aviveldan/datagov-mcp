# DataGov Israel MCP Server

Easily interact with the Israeli Government Public API (data.gov.il) using this project, which combines a Flask-based MCP server and an OpenAI-integrated client to fetch and process data.

---

## Quick Start

### Prerequisites
- Python 3.x
- OpenAI API key

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd datagov-mcp
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration
Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Usage
1. Start the MCP server:
   ```bash
   python server.py
   ```
2. In a separate terminal, run the client:
   ```bash
   python client.py
   ```

---

## How It Works

### Server (`server.py`)
- A Flask-based MCP server that:
  - Fetches data from the Israeli Government Public API (`fetch_data_gov_il`)
  - Implements MCP protocol endpoints for function listing and execution
  - Provides JSON schema definitions for functions
- Runs on `http://localhost:8080`

### Client (`client.py`)
- Integrates with OpenAI's API and the MCP server to:
  - Fetch available functions from the MCP server
  - Convert MCP functions to OpenAI function specifications
  - Use OpenAI's chat completions to call functions
  - Fetch and display data from the Israeli Government Public API

---

## Example Workflow

1. The client connects to the MCP server.
2. It fetches available functions and starts a conversation with OpenAI's model.
3. The model decides to use the data fetching function.
4. The function executes and retrieves data from the Israeli Government Public API.
5. Results are displayed in the terminal.

---

## Project Structure

```
.
├── README.md           # Project documentation
├── requirements.txt    # Python dependencies
├── server.py           # MCP server implementation
└── client.py           # OpenAI client implementation
```

---

## Dependencies

- `python-dotenv`: Manage environment variables
- `openai`: OpenAI API client
- `flask`: Web server framework
- `requests`: HTTP client library

---

## Contributing

We welcome contributions! Feel free to submit issues or enhancement requests.