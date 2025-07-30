# Troubleshooting n8n MCP Server

## Server Fails to Start in MCP Inspector

### Symptoms
- Status shows "failed" in MCP inspector
- No tools are visible
- Server works when run manually

### Solutions

1. **Use the launcher script**:
   ```json
   {
     "servers": {
       "n8n": {
         "command": "/path/to/n8n-mcp/run_server.sh"
       }
     }
   }
   ```

2. **Check stderr output**:
   The server logs important information to stderr. You can test manually:
   ```bash
   cd /path/to/n8n-mcp
   source venv/bin/activate
   python server.py 2>debug.log
   # Check debug.log for errors
   ```

3. **Verify environment variables**:
   - Ensure `.env` file exists in the server directory
   - Check that N8N_HOST and N8N_API_KEY are set
   - Test with: `python test_connection.py`

4. **Use absolute paths**:
   Make sure all paths in your MCP config are absolute, not relative.

5. **Check file permissions**:
   ```bash
   ls -la server.py openapi_spec.json .env
   # All should be readable
   ```

## Common Errors

### "request/body/settings must be object"
- This error occurs when JSON objects are sent as strings
- The server now automatically fixes this issue
- If you still see this error, check stderr output for "Fixed JSON string" messages
- Affected fields: settings, connections, staticData, parameters, credentials

### "response exceeds maximum allowed tokens"
- This occurs when workflow data is too large for MCP limits
- Use the custom lightweight tools instead:
  - `list_workflows_minimal` instead of `Retrieve_all_workflows`
  - `get_workflow_summary` instead of `Retrieve_a_workflow` when you don't need full node data
- These custom tools strip out large fields while keeping essential information

### "Missing required environment variables"
- The .env file is not being found
- Solution: Use the launcher script or specify `cwd` in config

### "Could not find file: openapi_spec.json"
- The OpenAPI spec file is missing or in wrong location
- Solution: Run `node extract_openapi.js` to regenerate it

### No output at all
- The server might be outputting to stdout instead of stderr
- FastMCP uses stdio transport which requires clean stdout
- Solution: Use server_minimal.py for debugging

## Testing the Server

1. **Direct test**:
   ```bash
   cd /path/to/n8n-mcp
   source venv/bin/activate
   python server.py
   ```
   You should see:
   - "Loading OpenAPI spec..."
   - "Created FastMCP OpenAPI server with 40 routes"
   - "Starting MCP server..."

2. **Test with MCP protocol**:
   ```bash
   python test_mcp_protocol.py
   ```

3. **Check API connection**:
   ```bash
   python test_connection.py
   ```

## Debug Configuration

Use this minimal config for debugging:
```json
{
  "servers": {
    "n8n-debug": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/n8n-mcp/server_minimal.py"],
      "cwd": "/path/to/n8n-mcp"
    }
  }
}
```

The server_minimal.py provides more detailed error output to stderr.