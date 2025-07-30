from .server import mcp

def main():
    """Entry point for the Smart Search MCP server."""
    mcp.run(transport="stdio")