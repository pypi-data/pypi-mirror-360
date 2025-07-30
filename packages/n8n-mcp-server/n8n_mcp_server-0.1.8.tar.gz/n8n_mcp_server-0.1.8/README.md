# n8n MCP Server

[![PyPI version](https://badge.fury.io/py/n8n-mcp-server.svg)](https://badge.fury.io/py/n8n-mcp-server)
[![Python](https://img.shields.io/pypi/pyversions/n8n-mcp-server.svg)](https://pypi.org/project/n8n-mcp-server/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Connect your AI assistant to n8n workflow automation platform through the Model Context Protocol. This server provides direct access to n8n's entire REST API, enabling AI-powered workflow management, execution monitoring, and automation control.

## Quick Start

1. Install with uvx: `uvx n8n-mcp-server`
2. Add to your Claude Desktop config:
```json
{
  "mcpServers": {
    "n8n": {
      "command": "uvx",
      "args": ["n8n-mcp-server"],
      "env": {
        "N8N_HOST": "https://your-n8n.com",
        "N8N_API_KEY": "your-api-key"
      }
    }
  }
}
```
3. Restart Claude Desktop and start automating!

## Features

- **40+ Auto-generated Tools** - Full access to n8n's REST API
- **Smart JSON Handling** - Automatically fixes JSON serialization issues
- **Custom Lightweight Tools** - Optimized tools for working within token limits
- **Full Authentication** - Secure API key authentication
- **Built with FastMCP** - Reliable, high-performance MCP implementation

### Custom Tools for Large Workflows

The server includes custom tools designed for handling large workflows that might exceed token limits:

- **`list_workflows_minimal`** - Lists workflows with only essential metadata (id, name, active, dates, tags)
- **`get_workflow_summary`** - Gets workflow info with node/connection counts instead of full data
- **`partial_update_workflow`** - Updates specific nodes without sending the entire workflow
- **`add_nodes_to_workflow`** - Adds new nodes and automatically handles connection rewiring

## Prerequisites

- Python 3.8 or higher
- An n8n instance with API access enabled
- n8n API key

## Installation

### Using uvx (Recommended)

The easiest way to use n8n MCP Server is with [uvx](https://github.com/astral-sh/uv), which runs the server in an isolated environment:

```json
{
  "mcpServers": {
    "n8n": {
      "command": "uvx",
      "args": ["n8n-mcp-server"],
      "env": {
        "N8N_HOST": "https://your-n8n-instance.com",
        "N8N_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Using pip

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

The server requires two environment variables:

- `N8N_HOST`: Your n8n instance URL (e.g., https://n8n.example.com)
- `N8N_API_KEY`: Your n8n API key

You can provide these through:

1. **Environment variables in your MCP client configuration** (recommended for uvx)
2. **A `.env` file** in your working directory:

```bash
N8N_HOST=https://your-n8n-instance.com
N8N_API_KEY=your-api-key-here
```

## Usage

### Running the Server

Start the MCP server:
```bash
n8n-mcp-server
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


### What Can You Do?

With n8n MCP Server, your AI assistant can:

- **Manage Workflows** - Create, update, delete, and organize automation workflows
- **Execute Workflows** - Trigger workflow runs and pass custom data
- **Monitor Executions** - Check workflow status, review logs, and handle errors
- **Work with Credentials** - Safely manage authentication for external services
- **Handle Large Workflows** - Use optimized tools designed for token limits
- **Update Specific Nodes** - Modify individual workflow nodes without affecting others
- **Add Nodes Dynamically** - Insert new nodes and automatically rewire connections

Example commands you can give your AI assistant:
- "List all my active workflows"
- "Execute the 'Daily Report' workflow with today's date"
- "Show me failed executions from the last 24 hours"
- "Add a Slack notification node to my error handling workflow"
- "Update the schedule trigger to run every hour instead of daily"

## MCP Client Configuration

### Claude Desktop

Add to your Claude Desktop configuration:

#### Using uvx (Recommended)
```json
{
  "mcpServers": {
    "n8n": {
      "command": "uvx",
      "args": ["n8n-mcp-server"],
      "env": {
        "N8N_HOST": "https://your-n8n-instance.com",
        "N8N_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

#### Using pip installation
```json
{
  "mcpServers": {
    "n8n": {
      "command": "n8n-mcp-server",
      "env": {
        "N8N_HOST": "https://your-n8n-instance.com",
        "N8N_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

#### Using .env file
If you have a `.env` file in your working directory:
```json
{
  "mcpServers": {
    "n8n": {
      "command": "n8n-mcp-server"
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
- Ensure the server started successfully
- Check that your n8n credentials are correct
- Verify the MCP client can connect to the server

### Connection Failed
- Verify your n8n instance URL is correct and includes the protocol (https://)
- Check that your API key is valid and has the necessary permissions
- Ensure your n8n instance has API access enabled
- Make sure the n8n instance is accessible from your network

### Missing Tools
- The available tools depend on your n8n instance version and configuration
- Some endpoints may require admin permissions
- Check the server logs for any errors during initialization

## Related Documentation

- [n8n API Documentation](https://docs.n8n.io/api/)
- [n8n Authentication](https://docs.n8n.io/api/authentication/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Framework](https://github.com/dotinc/fastmcp)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) file for details.