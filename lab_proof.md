# Lab Proof: Agents that Speak MCP Fluently

## 1. Workflow and run

The [executed notebook](Lab_agent_speak_fluently.ipynb) connects a local Filesystem
MCP server over stdio and the public LangChain Docs MCP server over HTTP, using
one client per server. The local data consists of unchanged copies of the two
supplied course handouts. They replace the unavailable Project Atlas documents.
LangChain Docs is the remote alternative permitted by the lab; it needs no token.

This proof describes run `20261028T154143Z-5d8544ae` only. Its artifacts are in
[evidence/runs/20261028T154143Z-5d8544ae](evidence/runs/20261028T154143Z-5d8544ae/manifest.json). Historical material is separately labeled in
`evidence/history/` and is excluded from the current trace.

The run used Python 3.11.16 and model `gpt-4o-mini`. Installed
package versions exactly match [requirements.txt](requirements.txt). Setup
records the interpreter, working directory, credential availability, and versions.

## 2. Query

> Read mcp_servers_local_vs_remote.md. Quote the exact npx command from its JavaScript Filesystem example, including the package name and directory argument. Then search the official Python LangChain documentation for local stdio MCP connections. Which transport fits that configuration, and does using that transport alone guarantee that file contents remain on this computer when the local Python agent uses hosted ChatOpenAI? This is not a Managed Deep Agents deployment. Separate source evidence from the inference about hosted model data flow.

## 3. Tool evidence

The following call IDs belong to this run. Full raw server responses and the
filtered content actually delivered to the model are preserved in
[tool_log.jsonl](evidence/runs/20261028T154143Z-5d8544ae/tool_log.jsonl). Model messages and the final answers are
in [agent_runs.json](evidence/runs/20261028T154143Z-5d8544ae/agent_runs.json).

### call-004: filesystem / list_directory

```json
{
  "path": "F:\\UserData\\Desktop\\AI_Consulting_and_Integration\\Week_04\\Day_3\\lab-mcp-langchain\\sample_docs"
}
```

Error status: `False`. Result excerpt:

```text
[FILE] mcp_servers_local_vs_remote.md
[FILE] mcp_tools_resources_prompts.md
```

### call-005: filesystem / list_directory

```json
{
  "path": "F:\\UserData\\Desktop\\AI_Consulting_and_Integration\\Week_04\\Day_3"
}
```

Error status: `True`. Result excerpt:

```text
Access denied - path outside allowed directories: F:\UserData\Desktop\AI_Consulting_and_Integration\Week_04\Day_3 not in F:\UserData\Desktop\AI_Consulting_and_Integration\Week_04\Day_3\lab-mcp-langchain\sample_docs
```

### call-006: filesystem / read_text_file

```json
{
  "path": "F:\\UserData\\Desktop\\AI_Consulting_and_Integration\\Week_04\\Day_3\\lab-mcp-langchain\\sample_docs\\mcp_servers_local_vs_remote.md"
}
```

Error status: `False`. Result excerpt:

```text
"filesystem": {
    "transport": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "sample_docs"],
}
```

### call-007: langchain-docs / search_docs_by_lang_chain

```json
{
  "query": "local stdio MCP connections"
}
```

Error status: `False`. Result excerpt:

````text
Title: Transports
Link: https://docs.langchain.com/oss/python/langchain/mcp/index#transports
Page: oss/python/langchain/mcp/index
Content: ## Transports

[`MCPAdapter`](https://reference.langchain.com/python/langchain/mcp/adapter/MCPAdapter) infers the transport from the target you provide. The target is the only difference between an in-process server, a local script over stdio, and a remote URL:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from pathlib import Path

from langchain.mcp import MCPAdapter

# An in-process FastMCP server: no subprocess, no socket. Ideal for tests.
in_memory = MCPAdapter(server)  # a FastMCP instance

# A script path is launched over stdio, one subprocess per adapter.
stdio = MCPAdapter(Path("weather_server.py"))

# A string must be an http(s) URL, reached over streamable HTTP.
http = MCPAdapter("https://example.com/mcp")
```

A target can be any of the following:

* **An `http`/`https` URL** (`str`): reached over Streamable HTTP.
* **A script path** (`Path`): launched as a subprocess over stdio.
* **A transport object** (`StreamableTransport`): a preconfigured transport object. See [Client Transports](https://gofastmcp.com/clients/transports).
* **An in-process `FastMCP` server**: connected in memory, without a subprocess or socket.
* **An `MCPConfig` dict** (`{"mcpServers": {...}}`): several servers behind one adapter. See [Connections](/oss/python/langchain/mcp/connections#multiple-servers).
* **A prebuilt `fastmcp.Client`**: for full control over transport, [caching](https://gofastmcp.com/clients/client#response-caching), and [protocol negotiation](https://gofastmcp.com/clients/client#protocol-negotiation).

<Warning>
  A `str` target must be an `http` or `https` URL. FastMCP resolves a string by testing it as a filesystem path before testing it as a URL, so a string naming an existing `.py` or `.js` file would launch that file as a subprocess. Because strings are the form a target most often arrives in from configuration or from a model, [`MCPAdapter`](https://reference.langchain.com/python/langchain/mcp/adapter/MCPAdapter) rejects strings that do not match the shape of a URL.
</Warning>
Tit
````

## 4. Observed final answer

The exact `npx` command from the **mcp_servers_local_vs_remote.md** file is:

```python
"args": ["-y", "@modelcontextprotocol/server-filesystem", "sample_docs"],
```

This command is part of the configuration for a local JavaScript server using the `stdio` transport.

From the LangChain documentation, the transport that fits the local stdio MCP connections is `stdio`. This transport allows a script to be launched as a subprocess, enabling interaction with the local environment.

However, using the `stdio` transport alone does not guarantee that file contents remain on the local computer when the local Python agent uses hosted ChatOpenAI. The hosted model may still access data through the agent's configuration, which could involve sending data over the internet, depending on how the agent is set up. Thus, while the transport facilitates local execution, it does not inherently ensure data isolation from external services.

**Source Evidence:**
- Command from **mcp_servers_local_vs_remote.md**.
- Transport information from LangChain documentation: [Transports](https://docs.langchain.com/oss/python/langchain/mcp/index#transports).

## 5. Claim trace

| Claim | Supporting evidence |
|---|---|
| The handout uses npx and the Filesystem package with a document directory | call-006; exact local configuration excerpt above |
| stdio fits a locally started MCP server | call-007; selected Python LangChain documentation |
| Local server execution does not guarantee local model inference | Inference from this notebook's data flow: tool results are passed to the configured hosted ChatOpenAI model |

Only Python LangChain/LangGraph search results are delivered to the documentation
agents. Other products and language variants remain in the raw log, with the
selected URLs recorded separately. Final documentation citations must match
selected source URLs. These checks verify source scope and trace integrity;
they do not establish that every generated sentence is semantically correct.

## 6. Resource context

The application read `mintlify://skills/langchain` and provided its snapshot to an agent with
`tools=[]`. It supported this question:

> What do I need to add to an agent so that it remembers the conversation between calls?

Observed answer:

To enable an agent to remember the conversation between calls, you need to pass a `thread_id` in the configuration when invoking the agent. This is done by including `config={"configurable": {"thread_id": "..."}}` in the `agent.invoke()` method. Additionally, ensure that a checkpointer is configured to maintain the agent's state across invocations. Without the `thread_id`, the agent won't persist conversation history. 

For more details, refer to the resource at mintlify://skills/langchain.

Supporting excerpts from [langchain_guide.md](evidence/runs/20261028T154143Z-5d8544ae/langchain_guide.md):

Line 160:

> - **Missing thread_id**: Agent won't persist conversation history without `thread_id` in config. Always pass `config={"configurable": {"thread_id": "..."}}` for multi-turn conversations.

Line 167:

> - **Checkpointer required for persistence**: Without a checkpointer, agent state is lost between invocations. Use `InMemorySaver()` locally or configure persistent store in production.

The snapshot SHA-256 is `1d6867cef2213f10610098210ff68444ea29f49731a412220d9d88550bf3b6bb`. The resource agent made no
tool calls. [resource_checks.json](evidence/runs/20261028T154143Z-5d8544ae/resource_checks.json) records the URI,
hash, keyword checks, and source lines. Keyword matches aid review but are not a
general proof of semantic grounding.

## 7. Failure and limitations

Missing-information query:

> Read all documents in the folder. What exact monthly hosting price in EUR do they specify for the LangChain Docs MCP server? If it is not stated, report that explicitly.

Observed answer:

> The documents in the specified folder do not mention any exact monthly hosting price in EUR for the LangChain Docs MCP server. 

1. The first document, "mcp_servers_local_vs_remote.md," discusses the operational aspects of MCP servers but does not provide pricing information.
2. The second document, "mcp_tools_resources_prompts.md," focuses on the functionalities and types of tools, resources, and prompts available in an MCP server, without any reference to costs.

Therefore, it can be concluded that the exact monthly hosting price is not stated in the provided documents.

Evidence: call-012, call-013, call-014. The lack of a price in
the supplied sources does not establish that the service is free.

The historical review in
[grounding_review.json](evidence/history/before-feedback/grounding_review.json)
retains an earlier answer that confused `uvx` and `npx`. Its call identifiers are
historical and are not references into this run. The current combined scenario
checks that the expected Filesystem command and package appear in the answer.

Directory-first middleware and a client-side guard restrict the order of file
operations. The agent receives only read tools, although the underlying trusted
server still implements write operations. A successful call alone does not
guarantee a correct interpretation, and a matching URL alone does not validate
every associated claim. Hosted inference still receives the supplied context.

## 8. Practical document analysis

| Scenario and question | Call IDs | Observed result |
|---|---|---|
| Which documents are in the folder? | call-015 | The documents in the folder are:  1. **mcp_servers_local_vs_remote.md** 2. **mcp_tools_resources_prompts.md** |
| Summarise mcp_servers_local_vs_remote.md in three bullet points. | call-016, call-017 | **Summary of mcp_servers_local_vs_remote.md:**  - **Server Location and Connection**: MCP servers can be either remote (hosted on someone else's computer, accessed via a URL) or local (run on your own computer, started with a command like `npx` for JavaScript or `uvx` for Python) (source: F:\UserData\Desktop\AI_Consulting_and_Integration\Week_04\Day_3\lab-mcp-langchain\sample_docs\mcp_servers_local_vs_remote.md).  - **Installation and Commands**: To run a local server, you need to install Node.js for JavaScript or the `uv` package for Python. The commands to start these servers differ based on the programming language used (source: F:\UserData\Desktop\AI_Consulting_and_Integration\Week_04\Day_3\lab-mcp-langchain\sample_docs\mcp_servers_local_vs_remote.md).  - **Trust and Security**: When using MCP servers, it's crucial to verify the source, check for updates, understand data access, and ensure security scans have been conducted. Always pin the version to avoid unexpected changes (source: F:\UserData\Desktop\AI_Consulting_and_Integration\Week_04\Day_3\lab-mcp-langchain\sample_docs\mcp_servers_local_vs_remote.md). |
| Read all documents. Which files mention the LangChain documentation server? Quote the matching text. | call-018, call-019, call-020 | The files that mention the LangChain documentation server are:  1. **mcp_servers_local_vs_remote.md**    - Quote: "Someone else (LangChain, GitHub, ...) runs the server for you. It's always on. You just call its address."    - Quote: `"url": "https://docs.langchain.com/mcp"`  2. **mcp_tools_resources_prompts.md**    - Quote: "We connect to the **LangChain Documentation MCP server** (`https://docs.langchain.com/mcp`). Here is what it offers:"  These quotes indicate that the LangChain documentation server is referenced in both files, providing details about its operation and connection. |
| Can an MCP tool be read-only? Read the documents and cite a concrete example. | call-021, call-022, call-023 | Yes, an MCP tool can be read-only. For example, in the document "mcp_tools_resources_prompts.md," it states that tools can perform actions, but some tools may only read data without making changes. Specifically, it mentions:  - **Tools**: Functions the LLM can call to act, such as `create_event`. - **Resources**: Read-only information the application fetches and gives to the LLM as context, like retrieving documents or accessing knowledge bases.  In the example provided, two tools (`search_docs_by_lang_chain` and `query_docs_filesystem_docs_by_lang_chain`) are described as only reading data, yet they are still classified as tools because they are called by the model to perform actions (even if those actions are read-only) (source: "F:\\UserData\\Desktop\\AI_Consulting_and_Integration\\Week_04\\Day_3\\lab-mcp-langchain\\sample_docs\\mcp_tools_resources_prompts.md").   This indicates that tools can be designed to perform read-only functions within the MCP framework. |

## 9. MCP and direct HTTP comparison

The same memory question was answered through MCP search and through a direct
request to one known documentation page. The direct response status, page hash,
and both answers are in [direct_comparison.json](evidence/runs/20261028T154143Z-5d8544ae/direct_comparison.json).

| Aspect | MCP | Direct HTTP |
|---|---|---|
| Setup | Server configuration, discovery, adapter, interceptor | Known page URL and HTTP client |
| Flexibility | Agent chooses queries through a standardized tool interface | Model sees the page supplied by the application |
| Maintenance | Client depends on server tool schemas and service availability | Client handles URLs, response format, and HTTP errors |
| Evidence | Full tool results, selected source URLs, message trace | Page snapshot, HTTP status, hash, and model answer |

The table reflects the retained MCP traces and direct comparison artifacts.
Direct HTTP fits a single known page; MCP fits workflows that need discovery or
reusable integrations across compatible frameworks. This is not a latency
benchmark: retrieval content and the number of model calls can differ.

## 10. Verification

The completed run contains 10 scenarios and
23 tool events. Each referenced call exists in this run;
required server evidence, message/tool-call pairing, source and snapshot hashes,
dependency versions, and final citation scope passed validation.
