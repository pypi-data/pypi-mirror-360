# n8n MCP Server

[![PyPI version](https://badge.fury.io/py/n8n-mcp-server.svg)](https://badge.fury.io/py/n8n-mcp-server)
[![Python](https://img.shields.io/pypi/pyversions/n8n-mcp-server.svg)](https://pypi.org/project/n8n-mcp-server/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An MCP (Model Context Protocol) server that provides seamless integration with n8n workflow automation platform. This server automatically exposes all n8n API endpoints as MCP tools based on the OpenAPI specification.

The server includes 40+ tools covering all n8n API operations including workflows, executions, credentials, tags, users, projects, variables, and more.

**Note**: The server automatically handles JSON string serialization issues that can occur with some MCP clients, ensuring that object fields like `settings` and `connections` are properly formatted for the n8n API.

### Custom Lightweight Tools

In addition to the standard n8n API tools, the server provides custom lightweight alternatives for working within MCP token limits:

- **`list_workflows_minimal`** - Lists workflows with only essential metadata (id, name, active, dates, tags)
- **`get_workflow_summary`** - Gets workflow info with node/connection counts instead of full data

These tools are useful when the standard API responses are too large for MCP clients.

## Features

- Automatic tool generation from n8n OpenAPI spec
- Full authentication support via API key
- Access to all n8n API endpoints (workflows, executions, credentials, etc.)
- Built with FastMCP for reliable performance

## Prerequisites

- Python 3.8 or higher
- An n8n instance with API access enabled
- n8n API key

## Installation

### From PyPI (Recommended)

```bash
pip install n8n-mcp-server
```

### From Source

1. Clone this repository:
```bash
git clone https://github.com/andrewlwn77/n8n-mcp-server.git
cd n8n-mcp-server
```

2. Install in development mode:
```bash
pip install -e .
```

## Configuration

1. Create a `.env` file in the project root:
```bash
N8N_HOST=https://your-n8n-instance.com
N8N_API_KEY=your-api-key-here
```

Replace the values with your actual n8n instance URL and API key.

## Usage

### Running the Server

Start the MCP server:
```bash
n8n-mcp
```

Or if running from source:
```bash
python -m n8n_mcp
```

The server will:
1. Connect to your n8n instance
2. Fetch the OpenAPI specification
3. Generate MCP tools for all available endpoints
4. Start listening for MCP requests

### Testing Connection

Before running the server, you can test your connection:
```bash
python test_connection.py
```

This will verify that your n8n instance is accessible and the API key is valid.

### Available Tools

Once running, the MCP server exposes all n8n API endpoints as tools, including:

- **Workflows**: Create, read, update, delete, and execute workflows
- **Executions**: Monitor and manage workflow executions
- **Credentials**: Manage credentials (with appropriate permissions)
- **Nodes**: Access node information
- **Users**: User management (admin only)
- And many more based on your n8n instance's API

## MCP Client Configuration

To use this server with an MCP client, add it to your client's configuration.

### Option 1: Using .env file (recommended)
If you have already configured your `.env` file:

```json
{
  "servers": {
    "n8n": {
      "command": "n8n-mcp"
    }
  }
}
```

### Option 2: Using environment variables in config
If you prefer to specify credentials in the MCP config:

```json
{
  "servers": {
    "n8n": {
      "command": "n8n-mcp",
      "env": {
        "N8N_HOST": "https://your-n8n-instance.com",
        "N8N_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Security Notes

- Keep your `.env` file secure and never commit it to version control
- Use environment-specific API keys with minimal required permissions
- Consider using read-only API keys for development/testing

## Troubleshooting

### No Tools Showing in MCP Client
- Ensure the server is running (you should see "Created FastMCP OpenAPI server with 40 routes")
- Check that the `openapi_spec.json` file exists in the server directory
- Verify the MCP client configuration includes the correct `cwd` path

### Connection Failed
- Verify your n8n instance URL is correct and includes the protocol (https://)
- Check that your API key is valid and has the necessary permissions
- Ensure your n8n instance has API access enabled
- Test with `python test_connection.py` first

### Missing Tools
- The available tools depend on your n8n instance version and configuration
- Some endpoints may require admin permissions

## License

MIT