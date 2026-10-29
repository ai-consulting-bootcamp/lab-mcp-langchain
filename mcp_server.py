"""Read-only local MCP server, launched by LangChain over stdio."""
from mcp.server.fastmcp import FastMCP
from evidence import search_notes, RECORDS
import json

mcp = FastMCP("MCP Course Notes")

@mcp.tool()
def search_course_notes(query: str) -> str:
    """Search curated course notes. Returns curated source-grounded excerpts with record IDs and source filenames. Use this before answering questions about MCP concepts."""
    return search_notes(query)

@mcp.resource("course://mcp/overview")
def course_overview() -> str:
    """Read-only overview resource covering tools, resources and prompts."""
    return json.dumps(RECORDS[:3], indent=2)

if __name__ == "__main__":
    mcp.run(transport="stdio")
