"""http interface for FastMCP Server."""
from .server import mcp
def main():
    mcp.run(transport="sse")
if __name__ == "__main__":
    main()