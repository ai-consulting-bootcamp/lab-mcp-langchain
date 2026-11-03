# Lab Proof: Agents That Speak MCP Fluently

## Workflow

`mcp_langchain.py` connects to the LangChain Docs MCP server, loads its tools and resource, creates a LangChain agent, and sends one question to it.

Execution path:

`MCP server → tools and resource → LangChain agent → question → tool call → tool result → final response`

The resource was `mintlify://skills/langchain`. The script passed its content to the agent as context. The available tools included `search_docs_by_lang_chain` and `query_docs_filesystem_docs_by_lang_chain`.

## Query

> According to the Python LangChain docs, how do MCP tools become available to an agent, and what does the agent do with them?

## MCP Tool Evidence

The trace shows that the agent called:

`search_docs_by_lang_chain`

The search query was:

`MCP tools availability to an agent`

The returned results included a page titled **“Expose an agent as MCP tool.”** It said that a deployed agent can appear as a tool in an MCP endpoint.

The results also included a JavaScript page titled **“Use MCP tools in an agent.”** It described discovering tools with `MCPAdapter.listTools` and passing them to `createAgent`. The visible trace did not include the corresponding Python page content, although the final answer linked to a Python documentation page.

## Resource Evidence

The script read the MCP resource:

`mintlify://skills/langchain`

Its preview described LangChain agents as systems where a model calls tools in a loop and identified the pattern as “Agent = Model + Harness.”

## Final Output

> In LangChain, MCP tools become available to an agent through the Model Context Protocol (MCP), which allows agents to connect to various external services like databases, APIs, and file systems. When an agent is deployed, it appears as a tool in the MCP endpoint with specific configurations, including a tool name, title, description, input schema, and annotations.
>
> To utilize these tools, the agent can discover the available tools from the MCP server using an adapter (like `MCPAdapter`). Once the tools are listed, they can be passed to the agent during its creation using the `create_agent()` function. The agent then uses these tools by selecting one based on the context of the task at hand, invoking it, and processing the resulting output.

## Grounding Check

The returned JavaScript documentation supports the general idea of discovering MCP tools and passing them to an agent. However, the answer also says a deployed agent appears as a tool in an MCP endpoint. That claim came from a different result about exposing an agent as an MCP tool, which describes the opposite direction of integration.

The trace therefore shows a grounding failure: the search returned related but distinct topics, and the agent combined them. The answer also claimed to rely on Python documentation without visible Python-page evidence in the retrieved trace.

## Failure or Limitation

The broad search query returned mixed results: Python and JavaScript material, plus documentation about exposing an agent as an MCP tool. The agent did not keep these concepts separate. A safer version should search for the exact Python page and use only evidence returned from that page.