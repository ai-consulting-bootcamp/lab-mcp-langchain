"""Run: python mcp_langchain.py  (requires dependencies and OPENAI_API_KEY)."""
import asyncio
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient

HERE = Path(__file__).resolve().parent
QUESTION = "Who controls MCP resources, and does reading one change data?"

async def main():
    load_dotenv(HERE / ".env")
    client = MultiServerMCPClient({"course": {"transport": "stdio", "command": sys.executable, "args": [str(HERE / "mcp_server.py")], "cwd": str(HERE)}})
    tools = await client.get_tools()
    print("DISCOVERED_TOOLS:", [tool.name for tool in tools])
    assert "search_course_notes" in [t.name for t in tools], "MCP tool was not discovered"

    # Ground truth: execute the actual MCP-loaded tool and retain its response.
    search_tool = next(t for t in tools if t.name == "search_course_notes")
    evidence = await search_tool.ainvoke({"query": QUESTION})
    print("MCP_TOOL_EVIDENCE:\n", evidence)

    # Inspect resources with a raw MCP session, distinct from tools.
    async with client.session("course") as session:
        resources = await session.list_resources()
        print("DISCOVERED_RESOURCES:", [str(r.uri) for r in resources.resources])
        resource = await session.read_resource("course://mcp/overview")
        print("RESOURCE_PREVIEW:", str(resource.contents[0])[:500])

    if not os.getenv("OPENAI_API_KEY"):
        print("SKIPPED_AGENT: Set OPENAI_API_KEY in .env to run the LangChain LLM agent.")
        return

    agent = create_agent(
        model=ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0),
        tools=tools,
        system_prompt=("You answer only from MCP course-note tool evidence. "
                       "Always call search_course_notes before answering. "
                       "Cite record IDs in your answer; when absent, state insufficient evidence."),
    )
    result = await agent.ainvoke({"messages": [{"role": "user", "content": QUESTION}]})
    print("AGENT_TRACE:")
    for message in result["messages"]:
        print(json.dumps({"type": message.__class__.__name__, "content": str(message.content),
                          "tool_calls": getattr(message, "tool_calls", [])}, default=str))
    print("FINAL_ANSWER:", result["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())
