
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from langchain_mcp_adapters.client import MultiServerMCPClient

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI


async def main():
    data_folder = str(Path("data").resolve())

    client = MultiServerMCPClient({
        "filesystem": {
            "command": r"C:\Program Files\nodejs\npx.cmd",
            "args": [
                "-y",
                "@modelcontextprotocol/server-filesystem",
                data_folder
            ],
            "transport": "stdio",
            "env": {
                **os.environ,
                "PATH": r"C:\Program Files\nodejs;" + os.environ.get("PATH", "")
            }
            
        },
        "langchain-docs": {
            "transport": "http",
            "url": "https://docs.langchain.com/mcp"
        },
            "github": {
            "transport": "http",
            "url": "https://api.githubcopilot.com/mcp/",
            "headers": {
                "Authorization": f"Bearer {os.environ['GITHUB_PERSONAL_ACCESS_TOKEN']}",
                "X-MCP-Readonly": "true"
            }
        }

    })
        # Test the GitHub MCP server
    print("\nConnecting to GitHub MCP server...")
    try:
        github_tools = await client.get_tools(server_name="github")
        print("GitHub connection successful!")
        print("Number of GitHub tools:", len(github_tools))
        for tool in github_tools:
            print("-", tool.name)
    except Exception as error:
        print("GitHub connection error:", type(error).__name__, str(error))

    # Test the LangChain documentation MCP server
    print("\nConnecting to LangChain documentation MCP server...")
    try:
        docs_tools = await client.get_tools(server_name="langchain-docs")
        print("LangChain documentation tools:", len(docs_tools))
        for tool in docs_tools:
            print("-", tool.name)
    except Exception as error:
        print("Documentation server error:", str(error))

    print("Connecting to filesystem MCP server...")

    tools = await client.get_tools(server_name="filesystem")

    print("Connection successful!")
    print("Number of tools:", len(tools))

    for tool in tools:
        print("-", tool.name)

      
    # Check available MCP resources
    resource_context = ""
    print("\nChecking MCP resources...")
    try:
        resources = await client.get_resources(server_name="langchain-docs")
        
        resource_context = "\n\n".join(resource.as_string() for resource in resources)

        print("Resources returned:", len(resources))
        for resource in resources:
            print("Resource content preview:", resource.as_string()[:300])

    except Exception as error:
        print("Resource check failed:", type(error).__name__, str(error))
        
        import traceback
        traceback.print_exception(error)

  


    # Test whether the filesystem MCP tool can read our document
    read_tool = next(
        tool for tool in tools if tool.name == "read_text_file"
    )

    result = await read_tool.ainvoke({
        "path": str(Path("data/sample_policy.txt").resolve())
    })

    print("\nDocument retrieved through MCP:")
    print(result)

    # Step 4: Create a LangChain agent using MCP tools
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    agent = create_agent(
        model=model,
        tools=tools + github_tools,
        system_prompt=(
            "You are a document analysis assistant. "
            "Use the filesystem MCP tools to read documents before answering. "
            "Base your answers on information retrieved from MCP tools or MCP resources. "
            "If the information is missing, say you do not know. "
            "Mention the source filename when answering questions about local files. "
            "Use the following LangChain documentation as background context "
            "when answering questions about LangChain:\n\n"
            + resource_context

        )
    )

    print("\nLangChain MCP agent created successfully!")

    # Test the agent with a question about our document
    question = "Using GitHub MCP tools, inspect the public repository psf/requests. Read its README.md and briefly explain what the project does. Mention the repository name."


    response = await agent.ainvoke({
        "messages": [
            {"role": "user", "content": question}
        ]
    })

    print("\nQuestion:", question)
    print("\nAgent answer:")
    print(response["messages"][-1].content)

    print("\nMCP tool calls:")
    for message in response["messages"]:
        if getattr(message, "tool_calls", None):
            for call in message.tool_calls:
                print("Tool:", call["name"])
                print("Arguments:", call["args"])


if __name__ == "__main__":
    asyncio.run(main())

