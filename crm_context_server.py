"""A tiny local MCP server that publishes CRM field semantics as a resource.

This deliberately contains documentation, not CRM records or credentials.
It demonstrates MCP Resources independently from HubSpot's remote MCP tools.
"""

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("CRM Field Guide")


@mcp.resource("crm://field-guide")
def crm_field_guide() -> str:
    """Explain the company fields used by the lab's read-only CRM query."""
    return """CRM company field guide

- name: the CRM record's company name; use this to identify a company by name.
- domain: the company's internet domain, such as example.org; this is the
  requested business value in this lab.
- website: a website URL, which may include a scheme or path; it is not
  interchangeable with the domain field.

This guide defines field meanings only. For actual company values, use the
current result from the HubSpot CRM search tool as the authoritative evidence.
If that search returns no match, do not infer a value from this guide.
"""


if __name__ == "__main__":
    # stdio is the local transport used by the accompanying MCP client.
    mcp.run(transport="stdio")
