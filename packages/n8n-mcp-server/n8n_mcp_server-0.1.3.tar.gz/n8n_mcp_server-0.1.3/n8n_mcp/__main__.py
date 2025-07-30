#!/usr/bin/env python3
"""Main entry point for n8n MCP server."""
import os
import sys
import json
from typing import Dict, Any, Optional
from fastmcp import FastMCP
from dotenv import load_dotenv
from .client import N8nHTTPXClient
from .custom_tools import register_custom_tools
from .parameter_middleware import json_string_fix_middleware

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
    # Get the package root directory
    package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    spec_path = os.path.join(package_dir, 'openapi_spec.json')
    
    with open(spec_path, 'r') as f:
        return json.load(f)


def modify_openapi_spec_for_mcp(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Modify OpenAPI spec to accept strings for object fields due to MCP limitation."""
    modified_spec = json.loads(json.dumps(spec))  # Deep copy
    
    # We need to modify the schema that's actually used in the endpoints
    # The workflow schema is referenced via $ref, so we need to modify it directly
    if 'components' in modified_spec and 'schemas' in modified_spec['components']:
        # Modify the workflow schema
        if 'workflow' in modified_spec['components']['schemas']:
            workflow_schema = modified_spec['components']['schemas']['workflow']
            
            # Update connections to accept string or object
            if 'properties' in workflow_schema and 'connections' in workflow_schema['properties']:
                workflow_schema['properties']['connections'] = {
                    "anyOf": [
                        {"type": "object"},
                        {"type": "string"}
                    ],
                    "example": workflow_schema['properties']['connections'].get('example', {})
                }
            
            # Update settings to accept string or object
            if 'properties' in workflow_schema and 'settings' in workflow_schema['properties']:
                # Settings references workflowSettings schema
                workflow_schema['properties']['settings'] = {
                    "anyOf": [
                        {"$ref": "#/components/schemas/workflowSettings"},
                        {"type": "string"}
                    ]
                }
            
            # Update staticData to accept string or object
            if 'properties' in workflow_schema and 'staticData' in workflow_schema['properties']:
                # staticData already has anyOf, just add string option
                static_data = workflow_schema['properties']['staticData']
                if 'anyOf' in static_data:
                    # Add string to existing anyOf
                    static_data['anyOf'].append({"type": "string"})
    
    # Also need to handle inline schemas in the paths
    if 'paths' in modified_spec:
        # Modify POST /workflows
        if '/workflows' in modified_spec['paths'] and 'post' in modified_spec['paths']['/workflows']:
            post_op = modified_spec['paths']['/workflows']['post']
            if 'requestBody' in post_op:
                # The request body references the workflow schema via $ref
                # Since we modified the component schema above, it should work
                pass
        
        # Modify PUT /workflows/{id}
        if '/workflows/{id}' in modified_spec['paths'] and 'put' in modified_spec['paths']['/workflows/{id}']:
            put_op = modified_spec['paths']['/workflows/{id}']['put']
            if 'requestBody' in put_op:
                # Same as above
                pass
    
    return modified_spec


def main():
    """Main entry point for the MCP server"""
    try:
        # Load OpenAPI spec silently
        spec = get_openapi_spec()
        
        # Modify spec to accept strings due to MCP limitation
        modified_spec = modify_openapi_spec_for_mcp(spec)
        
        # Create authenticated client with JSON string fix
        client = N8nHTTPXClient(
            base_url=f"{N8N_HOST}/api/v1",
            headers={
                "X-N8N-API-KEY": N8N_API_KEY,
                "Content-Type": "application/json"
            }
        )
        
        # Generate MCP server from modified OpenAPI spec
        mcp = FastMCP.from_openapi(
            modified_spec, 
            client=client,
            name="n8n-mcp-server"
        )
        
        # Add middleware to fix JSON string parameters
        mcp.add_middleware(json_string_fix_middleware)
        
        # Register additional custom tools
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