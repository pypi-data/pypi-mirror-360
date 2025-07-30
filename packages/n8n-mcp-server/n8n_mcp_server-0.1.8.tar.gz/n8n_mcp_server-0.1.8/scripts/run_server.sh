#!/bin/bash
# Launcher script for n8n MCP server

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to script directory
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Run the server
exec python server.py