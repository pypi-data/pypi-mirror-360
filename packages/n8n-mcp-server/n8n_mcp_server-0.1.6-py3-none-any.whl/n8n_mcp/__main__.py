#!/usr/bin/env python3
"""Main entry point for n8n MCP server."""
import os
import sys
import json
from typing import Dict, Any
from fastmcp import FastMCP
from dotenv import load_dotenv
from .client import N8nHTTPXClient
from .custom_tools import register_custom_tools

# Load .env from the script directory
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(script_dir, '.env')
load_dotenv(env_path)

N8N_HOST = os.getenv("N8N_HOST", "").rstrip("/")
N8N_API_KEY = os.getenv("N8N_API_KEY", "")

if not N8N_HOST or not N8N_API_KEY:
    print(f"Error: Missing required environment variables", file=sys.stderr)
    print(f"N8N_HOST: {'set' if N8N_HOST else 'not set'}", file=sys.stderr)
    print(f"N8N_API_KEY: {'set' if N8N_API_KEY else 'not set'}", file=sys.stderr)
    print(f"Looking for .env at: {env_path}", file=sys.stderr)
    print(f".env exists: {os.path.exists(env_path)}", file=sys.stderr)
    sys.exit(1)


def get_openapi_spec() -> Dict[str, Any]:
    """Load the OpenAPI specification from local file"""
    # Get the package directory
    package_dir = os.path.dirname(os.path.abspath(__file__))
    spec_path = os.path.join(package_dir, 'openapi_spec.json')
    
    with open(spec_path, 'r') as f:
        return json.load(f)


def main():
    """Main entry point for the MCP server"""
    try:
        # Load OpenAPI spec silently
        spec = get_openapi_spec()
        
        # Create authenticated client with JSON string fix
        client = N8nHTTPXClient(
            base_url=f"{N8N_HOST}/api/v1",
            headers={
                "X-N8N-API-KEY": N8N_API_KEY,
                "Content-Type": "application/json"
            }
        )
        
        # Generate MCP server from OpenAPI spec
        # This returns a FastMCPOpenAPI instance with all the tools
        mcp = FastMCP.from_openapi(
            spec, 
            client=client,
            name="n8n-mcp-server"  # Custom name for the server
        )
        
        # Register custom tools
        register_custom_tools(mcp, client)
        
        # Run the server
        mcp.run()
        
    except FileNotFoundError as e:
        print(f"Error: Could not find file: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in OpenAPI spec: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error setting up server: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()