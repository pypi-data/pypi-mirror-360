"""Middleware to fix JSON string parameters before tool execution."""
import json
import sys
from typing import Any, Callable


async def json_string_fix_middleware(handler: Callable, context: Any) -> Any:
    """Middleware that converts JSON string parameters to objects."""
    # Debug what we receive
    if hasattr(context, 'arguments'):
        # Check if this is a workflow-related operation
        tool_name = getattr(context, 'tool_name', '') or getattr(context, 'method', '')
        
        if 'workflow' in str(tool_name).lower() and hasattr(context, 'arguments'):
            args = context.arguments
            
            # Known fields that should be objects but might come as JSON strings
            json_fields = ['connections', 'settings', 'staticData', 'parameters', 'credentials', 'nodes', 'tags', 'meta']
            
            # Transform JSON strings to objects
            for field in json_fields:
                if field in args and isinstance(args[field], str):
                    try:
                        # Try to parse as JSON
                        parsed = json.loads(args[field])
                        args[field] = parsed
                        print(f"[Middleware] Converted {field} from JSON string to object", file=sys.stderr)
                    except (json.JSONDecodeError, TypeError) as e:
                        print(f"[Middleware] Failed to parse {field}: {e}", file=sys.stderr)
                        # Keep as is if not valid JSON
                        pass
    
    # Continue with the handler
    return await handler(context)