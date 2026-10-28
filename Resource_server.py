from mcp.server.fastmcp import FastMCP

mcp = FastMCP("project-info")

@mcp.resource("info://project")
def project_info() -> str:
    return "Project name: MCP Lab. Project owner: Nicolò. Team size: 3 people."

if __name__ == "__main__":
    mcp.run()
