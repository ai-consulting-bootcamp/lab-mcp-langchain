"""A small, traceable MCP + LangChain source-grounded agent demo.

Run from the lab directory with:
    conda run -n bootcamp-env python mcp_langchain.py

This file also runs as the local stdio MCP server when launched with
``--mcp-server``. The server reads the adjacent ``source_facts.md`` file.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


HERE = Path(__file__).resolve().parent
SOURCE_PATH = HERE / "source_facts.md"
RESOURCE_URI = "lab://northstar/facts"


def run_mcp_server() -> None:
    """Serve the source as a read-only MCP tool and resource over stdio."""
    from mcp.server.fastmcp import FastMCP

    server = FastMCP("northstar-source")

    def read_source() -> str:
        return SOURCE_PATH.read_text(encoding="utf-8")

    @server.tool()
    def retrieve_source_evidence(question: str) -> str:
        """Read the Northstar source facts before answering a factual question."""
        del question  # The same complete fact sheet is the evidence for this lab.
        return read_source()

    @server.resource(RESOURCE_URI)
    def northstar_facts() -> str:
        """The Northstar Scout field-trial source document."""
        return read_source()

    server.run(transport="stdio")


async def run_workflow() -> dict[str, Any]:
    """Discover MCP capabilities, retrieve evidence, and run two agent queries."""
    from langchain.agents import create_agent
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from langchain_openai import ChatOpenAI

    load_dotenv(HERE / ".env")
    if not os.environ.get("OPENAI_API_KEY", "").strip():
        raise RuntimeError("OPENAI_API_KEY is missing or empty in .env/environment")
    if not SOURCE_PATH.is_file():
        raise FileNotFoundError(f"Source document not found: {SOURCE_PATH.name}")

    client = MultiServerMCPClient(
        {
            "northstar": {
                "command": sys.executable,
                "args": [str(Path(__file__).resolve()), "--mcp-server"],
                "transport": "stdio",
            }
        }
    )

    tools = await client.get_tools()
    if not tools:
        raise RuntimeError("The MCP server did not advertise any tools")

    # Use an MCP session to verify advertised resources and read one directly.
    async with client.session("northstar") as session:
        resource_listing = await session.list_resources()
        resource_uris = [str(item.uri) for item in resource_listing.resources]
        if RESOURCE_URI not in resource_uris:
            raise RuntimeError(f"Expected MCP resource {RESOURCE_URI!r} was not listed")
        resource_result = await session.read_resource(RESOURCE_URI)
        resource_text = "\n".join(
            item.text for item in resource_result.contents if getattr(item, "text", None)
        )
        if not resource_text:
            raise RuntimeError("The MCP resource returned no text")

    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    model = ChatOpenAI(model=model_name, temperature=0)
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=(
            "You are a source-grounded research assistant. Before every factual answer, "
            "call retrieve_source_evidence. Use only the returned source text. Do not "
            "infer missing facts. If the source does not contain an answer, say exactly "
            "that the source does not provide that information. Cite [source_facts.md]."
        ),
    )

    queries = {
        "grounded": (
            "According to the source, what city is the Northstar Scout test facility in, "
            "when did its field trial begin, and what battery runtime did it record?"
        ),
        "missing_fact": "What was the maximum altitude reached by the Northstar Scout?",
    }
    runs: dict[str, Any] = {}
    for label, query in queries.items():
        result = await agent.ainvoke({"messages": [{"role": "user", "content": query}]})
        messages = result["messages"]
        tool_calls = [
            call
            for message in messages
            for call in getattr(message, "tool_calls", [])
        ]
        tool_messages = [
            message for message in messages if getattr(message, "type", None) == "tool"
        ]
        if not tool_calls or not tool_messages:
            raise RuntimeError(f"Agent did not retrieve MCP evidence for {label} query")
        final_message = next(
            message
            for message in reversed(messages)
            if getattr(message, "type", None) == "ai"
            and not getattr(message, "tool_calls", [])
        )
        runs[label] = {
            "query": query,
            "tool_calls": [
                {"name": call["name"], "arguments": call["args"]}
                for call in tool_calls
            ],
            "tool_responses": [message.content for message in tool_messages],
            "final_answer": final_message.content,
        }

    report = {
        "mcp_server": "northstar (local stdio Python MCP server)",
        "tools_discovered": [tool.name for tool in tools],
        "resources_listed": resource_uris,
        "resource_content": resource_text,
        "model": model_name,
        "runs": runs,
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mcp-server",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args()
    if args.mcp_server:
        run_mcp_server()
        return
    try:
        report = asyncio.run(run_workflow())
    except Exception as exc:
        # Do not dump environment data or credential-bearing request headers.
        print(f"Workflow failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
    print(json.dumps(report, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
