"""Custom HTTP client for n8n API with JSON string fix."""
import json
import sys
from typing import Any, Union
import httpx


class N8nHTTPXClient(httpx.AsyncClient):
    """Custom HTTPX client that fixes JSON string serialization issues"""
    
    def _fix_json_strings(self, data: Any) -> Any:
        """Recursively fix JSON strings that should be objects"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                # Known fields that should be objects but might come as JSON strings
                if key in ['settings', 'staticData', 'connections', 'parameters', 'credentials', 'nodes', 'tags', 'meta', 'pinData']:
                    if isinstance(value, str):
                        try:
                            # Try to parse as JSON
                            parsed = json.loads(value)
                            result[key] = parsed
                            # Fixed JSON string in field
                        except (json.JSONDecodeError, TypeError):
                            # Not a JSON string, keep as is
                            result[key] = value
                    else:
                        # Already an object, keep as is
                        result[key] = value
                elif isinstance(value, str) and value.strip() and value.strip()[0] in ['{', '['] and value.strip()[-1] in ['}', ']']:
                    # Try to parse any string that looks like JSON
                    try:
                        parsed = json.loads(value)
                        result[key] = parsed
                    except (json.JSONDecodeError, TypeError):
                        # Not valid JSON, keep as is
                        result[key] = value
                else:
                    # Recursively process nested structures
                    result[key] = self._fix_json_strings(value)
            return result
        elif isinstance(data, list):
            return [self._fix_json_strings(item) for item in data]
        else:
            return data
    
    async def request(self, method: str, url: Union[httpx.URL, str], **kwargs) -> httpx.Response:
        """Override request to fix JSON string issues before sending"""
        # Check if there's JSON content in the request
        if 'json' in kwargs:
            original_json = kwargs['json']
            fixed_json = self._fix_json_strings(original_json)
            # Apply the fix silently
            kwargs['json'] = fixed_json
        
        # Call the parent request method
        return await super().request(method, url, **kwargs)