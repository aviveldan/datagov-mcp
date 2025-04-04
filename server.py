# mcp_server.py
from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__)

# Define our addition function
def add_numbers(a, b):
    """Add two numbers together and return the result."""
    return a + b

# Define the function schema for the MCP protocol
FUNCTION_SCHEMA = {
    "name": "fetch_data_gov_il",
    "description": "Fetch data from the Israeli government public API (data.gov.il)",
    "parameters": {
        "type": "object",
        "properties": {
            "resource_id": {
                "type": "string",
                "description": "The resource ID of the dataset to fetch"
            },
            "limit": {
                "type": "integer",
                "description": "The number of records to fetch",
                "default": 100
            },
            "offset": {
                "type": "integer",
                "description": "The starting point for fetching records",
                "default": 0
            },
            "query": {
                "type": "string",
                "description": "Optional query string to filter results",
                "default": ""
            }
        },
        "required": ["resource_id"]
    }
}

@app.route("/mcp/functions", methods=["GET"])
def list_functions():
    """Endpoint to list available functions."""
    return jsonify({
        "functions": [FUNCTION_SCHEMA]
    })

@app.route("/mcp/execute", methods=["POST"])
def execute_function():
    """Endpoint to execute a function."""
    data = request.json

    function_name = data.get("name")
    arguments = data.get("arguments", {})

    if function_name == "fetch_data_gov_il":
        try:
            # Extract arguments
            resource_id = arguments.get("resource_id")
            limit = arguments.get("limit", 100)
            offset = arguments.get("offset", 0)
            query = arguments.get("query", "")

            # Validate required arguments
            if not resource_id:
                raise ValueError("Missing required parameter: resource_id")

            # Call the data.gov.il API
            base_url = "https://data.gov.il/api/3/action/datastore_search"
            params = {
                "resource_id": resource_id,
                "limit": limit,
                "offset": offset,
                "q": query
            }
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raise an error for bad status codes
            api_data = response.json()

            # Check if the request was successful
            if api_data.get("success"):
                return jsonify({
                    "result": api_data["result"]["records"]
                })
            else:
                return jsonify({
                    "error": api_data.get("error", "Unknown error occurred")
                }), 400
        except Exception as e:
            return jsonify({
                "error": str(e)
            }), 400
    else:
        return jsonify({
            "error": f"Unknown function: {function_name}"
        }), 404

if __name__ == "__main__":
    print("Starting MCP server on http://localhost:8080")
    print(f"Available functions: {json.dumps([FUNCTION_SCHEMA], indent=2)}")
    app.run(host="0.0.0.0", port=8080)