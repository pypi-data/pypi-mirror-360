"""n8n MCP Server - Model Context Protocol server for n8n workflow automation."""

__version__ = "0.1.0"
__author__ = "n8n MCP Server Contributors"

from .client import N8nHTTPXClient

__all__ = ["N8nHTTPXClient"]