
"""
Example MCP server for testing mcp4mcp functionality
"""

from fastmcp import FastMCP
from .tools import register_file_tools, register_math_tools

# Create FastMCP server
mcp = FastMCP("example-mcp-server")

# Register tool modules
register_file_tools(mcp)
register_math_tools(mcp)

if __name__ == "__main__":
    mcp.run()
