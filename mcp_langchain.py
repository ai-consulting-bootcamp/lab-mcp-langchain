import os
import sys
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

# Step 1: load API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print("API key loaded")
else:
    print("API key NOT found")

# Step 2: connect to the MCP servers
docs_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
resource_server_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resource_server.py")

client = MultiServerMCPClient({
    "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", docs_folder],
        "transport": "stdio",
    },
    "project": {
        "command": sys.executable,
        "args": [resource_server_path],
        "transport": "stdio",
    },
})

# Step 6: complete MCP-enabled agent
async def main():
    # Load resources (Step 5)
    resources = await client.get_resources("project")
    resource_text = ""
    for resource in resources:
        resource_text = resource_text + resource.as_string() + "\n"

    # Load tools from all servers (Step 3)
    tools = await client.get_tools()
    print("Tools loaded:", len(tools))

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    system_prompt = (
        "You are a helpful assistant with access to filesystem tools through MCP. "
        "You can list, read and search files in this folder: " + docs_folder + ". "
        "You also have some background information below. "
        "If the background information does not fully answer the question, "
        "you MUST check the files before answering. "
        "Important: search_files only matches file NAMES, not the text inside files. "
        "To find information, first use list_directory to see all files, "
        "then use read_text_file to read each file. "
        "Never say information is missing until you have read every file. "
        "Only answer using information found in the files or in the background information.\n\n"
        "Background information:\n" + resource_text
    )

    agent = create_agent(llm, tools, system_prompt=system_prompt)

    # Test with several different queries
    queries = [
        "What files are in the docs folder?",
        "Who is the project owner, and what is the project deadline?",
        "How many people are on the team?",
        "What is the project budget?",
    ]

    for query in queries:
        print("\n\n########## QUERY:", query, "##########")
        result = await agent.ainvoke({"messages": [{"role": "user", "content": query}]})
        for message in result["messages"]:
            message.pretty_print()

asyncio.run(main())