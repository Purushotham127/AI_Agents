from mcp.server.fastmcp import FastMCP

from app_test_tools import register_app_test_tools
from db_tools import register_db_tools
from file_tools import register_file_tools

mcp = FastMCP("FileIO_Server")

register_file_tools(mcp)
register_db_tools(mcp)
register_app_test_tools(mcp)

if __name__ == "__main__":
    mcp.run(transport="stdio")