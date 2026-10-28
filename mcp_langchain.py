"""Use a local MCP resource and a HubSpot MCP tool in a LangChain agent.

The workflow is read-only. The HubSpot access token is loaded from .env and
is never printed.
"""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI


HUBSPOT_MCP_URL = "https://mcp.hubspot.com/"
RESOURCE_URI = "crm://field-guide"


async def read_local_field_guide() -> str:
    """Read the field guide through MCP's resource API over local stdio."""
    server_script = Path(__file__).with_name("crm_context_server.py")
    server_parameters = StdioServerParameters(
        command=sys.executable,
        args=[str(server_script)],
    )

    # stdio_client launches the local MCP server as a child process.
    # ClientSession then uses the MCP resource methods, not a direct file read.
    async with stdio_client(server_parameters) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            resources = await session.list_resources()
            matching_resource = next(
                (
                    resource
                    for resource in resources.resources
                    if str(resource.uri) == RESOURCE_URI
                ),
                None,
            )
            if matching_resource is None:
                raise RuntimeError(f"MCP resource not found: {RESOURCE_URI}")

            contents = await session.read_resource(matching_resource.uri)
            text_parts = [
                item.text
                for item in contents.contents
                if hasattr(item, "text")
            ]
            if not text_parts:
                raise RuntimeError("The CRM field guide resource had no text.")
            return "\n".join(text_parts)


async def main() -> None:
    """Read an MCP resource, then ground a CRM answer in an MCP tool result."""
    load_dotenv()

    access_token = os.getenv("HUBSPOT_ACCESS_TOKEN")
    if not access_token:
        raise RuntimeError(
            "HUBSPOT_ACCESS_TOKEN was not found. Add it to the local .env file."
        )

    # MultiServerMCPClient speaks MCP and converts the server's tools
    # into LangChain-compatible tools.
    client = MultiServerMCPClient(
        {
            "hubspot": {
                "transport": "streamable_http",
                "url": HUBSPOT_MCP_URL,
                "headers": {
                    "Authorization": f"Bearer {access_token}",
                },
            }
        }
    )

    # This local resource explains field semantics. It is not a source of
    # company facts; those must come from the remote HubSpot search tool.
    field_guide = await read_local_field_guide()
    print(f"\nRead MCP resource {RESOURCE_URI}:")
    print(field_guide)

    tools = await client.get_tools()

    # Inspect the input schema before calling a tool.
    # This makes the tool contract explicit and avoids guessing its arguments.
    search_tool = next(
        (tool for tool in tools if tool.name.endswith("search_crm_objects")),
        None,
    )

    if search_tool is None:
        raise RuntimeError("search_crm_objects was not exposed by HubSpot.")

    print("\nsearch_crm_objects input schema:")
    print(search_tool.args)

    print(f"Discovered {len(tools)} HubSpot MCP tools:")
    for tool in tools:
        print(f"- {tool.name}: {tool.description[:120]}")

    # Use one read-only MCP tool so the agent has a narrow, auditable capability.
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    agent = create_agent(
        model=model,
        tools=[search_tool],
        system_prompt=(
            "You are a CRM research assistant. "
            "Use the CRM field guide below only to interpret property names. "
            "It is not evidence about the current CRM records. "
            "Use the provided HubSpot search tool to retrieve evidence. "
            "Answer only from the tool result. "
            "If no matching record is returned, say that no record was found. "
            "Do not invent missing values. "
            "Do not include internal record IDs, portal IDs, or direct CRM record URLs. "
            "Report only the requested business properties.\n\n"
            "MCP resource context:\n"
            f"{field_guide}"
        ),
    )

    user_query = (
        "Find the company named HubSpot. Report its name and domain. "
        "If the CRM search returns no matching record, say so."
    )

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": user_query}]}
    )

    # Print the interaction trace so the tool evidence can be inspected.
    print("\nAgent and tool trace:")
    for message in result["messages"]:
        print(f"\n{type(message).__name__}:")
        print(message.content)
        if getattr(message, "tool_calls", None):
            print("Tool calls:", message.tool_calls)

if __name__ == "__main__":
    asyncio.run(main())
