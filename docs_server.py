"""
Small local MCP server (stdio) over the ./docs folder.

Exposes:
  Tools:     list_documents, read_document, search_documents
  Resources: docs://index  (read-only list of documents + titles)

Started automatically by mcp_langchain.py; you do not run it by hand.
"""
from pathlib import Path

try:  # MCP Python SDK v1
    from mcp.server.fastmcp import FastMCP as Server
except ImportError:  # MCP Python SDK v2 renamed FastMCP -> MCPServer
    from mcp.server.mcpserver import MCPServer as Server

DOCS_DIR = (Path(__file__).resolve().parent / "docs").resolve()

mcp = Server("docs")


def _doc_paths():
    return sorted(DOCS_DIR.glob("*.md"))


@mcp.tool()
def list_documents() -> str:
    """List the file names of all documents in the docs folder."""
    return "\n".join(p.name for p in _doc_paths()) or "No documents found."


@mcp.tool()
def read_document(filename: str) -> str:
    """Return the full text of one document. Use the exact file name from list_documents, e.g. 'incident_management_policy.md'."""
    path = (DOCS_DIR / filename).resolve()
    if path.parent != DOCS_DIR or not path.is_file():
        return f"ERROR: document '{filename}' not found. Call list_documents first."
    return path.read_text(encoding="utf-8")


@mcp.tool()
def search_documents(keyword: str) -> str:
    """Case-insensitive keyword search across all documents. Returns matching lines as 'file:line: text'."""
    hits = []
    for path in _doc_paths():
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if keyword.lower() in line.lower():
                hits.append(f"{path.name}:{i}: {line.strip()}")
    return "\n".join(hits) if hits else f"No matches for '{keyword}'."


@mcp.resource("docs://index")
def docs_index() -> str:
    """Read-only index of available documents and their titles."""
    lines = []
    for p in _doc_paths():
        title = p.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()
        lines.append(f"- {p.name}: {title}")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()  # stdio transport
