from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from app_test_tools import register_app_test_tools


def create_server() -> FastMCP:
    """Create the MCP server and register all tool modules."""
    from MCP_file_server import mcp as file_server

    register_app_test_tools(file_server)
    return file_server
