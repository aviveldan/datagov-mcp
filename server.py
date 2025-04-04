# mcp_server.py
from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__)

# Define the function schema for the MCP protocol
FUNCTION_SCHEMA = {
    "name": "fetch_data_gov_il",
    "description": "Fetch data from the Israeli government public API (data.gov.il) based on a dataset name query",
    "parameters": {
        "type": "object",
        "properties": {
            "dataset_name": {
                "type": "string",
                "description": "The name or partial name of the dataset to fetch"
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
            }
        },
        "required": ["dataset_name"]
    }
}

@app.route("/mcp/functions", methods=["GET"])
def list_functions():
    """Endpoint to list available functions."""
    return jsonify({
        "functions": [FUNCTION_SCHEMA]
    })

def find_resource_id(dataset_name):
    dataset_url = f"https://data.gov.il/api/3/action/package_show?id={dataset_name}"
    response = requests.get(dataset_url)
    if response.status_code == 200:
        dataset_data = response.json()
        resources = dataset_data['result']['resources']
        if resources:
            return resources[0]['id']
    return None

@app.route("/mcp/execute", methods=["POST"])
def execute_function():
    data = request.json
    function_name = data.get("name")
    arguments = data.get("arguments", {})

    if function_name == "fetch_data_gov_il":
        try:
            dataset_name = arguments.get("dataset_name", "")
            limit = arguments.get("limit", 100)
            offset = arguments.get("offset", 0)

            if not dataset_name:
                raise ValueError("Missing required parameter: dataset_name")

            resource_id = find_resource_id(dataset_name)
            if not resource_id:
                return jsonify({"error": f"No dataset found matching '{dataset_name}'"}), 404

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
                return jsonify({"result": api_data["result"]["records"]})
            else:
                return jsonify({"error": api_data.get("error", "Unknown error occurred")}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    else:
        return jsonify({"error": f"Unknown function: {function_name}"}), 404

if __name__ == "__main__":
    print("Starting MCP server on http://localhost:8080")
    print(f"Available functions: {json.dumps([FUNCTION_SCHEMA], indent=2)}")
    app.run(host="0.0.0.0", port=8080)