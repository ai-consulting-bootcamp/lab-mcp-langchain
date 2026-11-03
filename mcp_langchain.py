import asyncio

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

load_dotenv()


async def main():
    # 1. اتصال به سرور MCP مستندات LangChain
    client = MultiServerMCPClient({
        "langchain_docs": {
            "transport": "http",
            "url": "https://docs.langchain.com/mcp",
        }
    })

    # 2. دریافت ابزارهای سرور
    tools = await client.get_tools()

    print("TOOLS:")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")

    # 3. دریافت منابع و آماده‌کردن متن آن‌ها برای عامل
    resources = await client.get_resources()
    resource_context_parts = []

    print("\nRESOURCES:")
    for resource in resources:
        content = resource.data

        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="replace")
        else:
            content = str(content)

        print("URI:", resource.metadata.get("uri"))
        print("Preview:", content[:500])

        resource_context_parts.append(content[:2000])

    resource_context = "\n\n".join(resource_context_parts)

    # 4. ساخت مدل و عامل
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    system_prompt = (
        "Use the MCP resource context for general LangChain concepts. "
        "For API-specific questions, call search_docs_by_lang_chain first. "
        "Use the Python documentation results and ignore JavaScript examples. "
        "Base factual claims on the resource or tool result. "
        "If the evidence is insufficient, say so. "
        "Do not claim that documentation examples were executed in this script.\n\n"
        "MCP RESOURCE CONTEXT:\n"
        f"{resource_context}"
    )

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
    )

    # 5. فرستادن پرسش به عامل
    query = (
        "According to the Python LangChain docs, how do MCP tools become "
        "available to an agent, and what does the agent do with them?"
    )

    result = await agent.ainvoke({
        "messages": [{
            "role": "user",
            "content": query,
        }]
    })

    # 6. چاپ پرسش، فراخوانی ابزار، نتیجه و پاسخ
    print("\nTRACE:")
    for message in result["messages"]:
        print(f"\n{type(message).__name__}")

        if getattr(message, "tool_calls", None):
            print("TOOL CALL:", message.tool_calls)

        if getattr(message, "name", None):
            print("TOOL:", message.name)

        content = message.content

        if isinstance(content, list):
            content = "\n".join(
                block.get("text", str(block))
                if isinstance(block, dict)
                else str(block)
                for block in content
            )

        print("CONTENT:", str(content)[:4000])


if __name__ == "__main__":
    asyncio.run(main())