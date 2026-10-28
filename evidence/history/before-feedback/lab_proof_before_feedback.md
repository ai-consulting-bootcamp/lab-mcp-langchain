# Lab Proof: Agents that Speak MCP Fluently

## 1. What I built

The [executed notebook](Lab_agent_speak_fluently.ipynb) connects a local Filesystem
MCP server over stdio and the public LangChain Docs MCP server over HTTP, with
one client per server. LangChain agents use converted MCP tools; a separate
agent receives an MCP resource as context without any tools.

The local data consists of unchanged copies of the supplied course handouts in
`sample_docs/`. These replace the unavailable Project Atlas sample files. The
lab permits other servers and corresponding questions; LangChain Docs replaces
GitHub so no GitHub token is required. The model is `gpt-4o-mini`.

## 2. Query

> Read mcp_servers_local_vs_remote.md. Quote the exact npx command from its JavaScript Filesystem example, including the package name and directory argument. Then search the official Python LangChain documentation for local stdio MCP connections. Which transport fits that configuration, and does using that transport alone guarantee that file contents remain on this computer when the local Python agent uses hosted ChatOpenAI? This is not a Managed Deep Agents deployment. Separate source evidence from the inference about hosted model data flow.

## 3. Evidence

The entries below are from the actual interceptor log for the combined query.
Result excerpts are abbreviated for readability; the complete responses are in
[tool_log.jsonl](evidence/tool_log.jsonl), and the corresponding model messages
and tool-call identifiers are in [agent_runs.json](evidence/agent_runs.json).
Policy blocks, if present, are client-side rejections rather than server results.

### call-025: filesystem / list_directory

Arguments:

```json
{
  "path": "F:\\UserData\\Desktop\\AI_Consulting_and_Integration\\Week_04\\Day_3\\lab-mcp-langchain\\sample_docs"
}
```

Observed error status: `False`.

Result excerpt:

```text
[FILE] mcp_servers_local_vs_remote.md
[FILE] mcp_tools_resources_prompts.md
```

### call-026: filesystem / list_directory

Arguments:

```json
{
  "path": "F:\\UserData\\Desktop\\AI_Consulting_and_Integration\\Week_04\\Day_3\\lab-mcp-langchain"
}
```

Observed error status: `True`.

Result excerpt:

```text
Access denied - path outside allowed directories: F:\UserData\Desktop\AI_Consulting_and_Integration\Week_04\Day_3\lab-mcp-langchain not in F:\UserData\Desktop\AI_Consulting_and_Integration\Week_04\Day_3\lab-mcp-langchain\sample_docs
```

### call-027: filesystem / read_text_file

Arguments:

```json
{
  "path": "F:\\UserData\\Desktop\\AI_Consulting_and_Integration\\Week_04\\Day_3\\lab-mcp-langchain\\sample_docs\\mcp_servers_local_vs_remote.md"
}
```

Observed error status: `False`.

Result excerpt:

```text
|---|---|---|
| **Where it runs** | On someone else's computer | On **your** computer |
| **What you do** | You **call** it | You **start** it |
| **What you need** | A **URL** | A **command** (`npx` or `uvx`) |
| **Transport** | `http` | `stdio` |

---
"filesystem": {
    "transport": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "sample_docs"],
}
```
"time": {
    "transport": "stdio",
    "command": "uvx",
    "args": ["mcp-server-time"],
}
```
| A link like `https://.../mcp` | ☁️ Remote server | `"transport": "http"` + `"url"` |
| `npx ...` | 💻 Local JavaScript server | `"transport": "stdio"` + `"command": "npx"` |
| `uvx ...` | 💻 Local Python server | `"transport": "stdio"` + `"command": "uvx"` |

---
| 3 | **What can it reach?** | README: what folder, token or account it needs | Access to all your files, or a token with full rights |
| 4 | **Where does my data go?** | Local or remote? Hosted by whom? | A remote server outside the client's country or company, or a third party holding your token |
| 5 | **Did a scan find problems?** | Security scan on Smithery (MCP-Scan) | Warnings, or no scan at all |

```

### call-028: langchain-docs / search_docs_by_lang_chain

Arguments:

```json
{
  "query": "local stdio MCP connections"
}
```

Observed error status: `False`.

Result excerpt:

```text
Title: Transports
Link: https://docs.langchain.com/oss/javascript/langchain/mcp/index#transports
Page: oss/javascript/langchain/mcp/index
Content: ## Transports

[`MCPAdapter`](https://reference.langchain.com/javascript/langchain-mcp-adapters/MCPAdapter) accepts a map of named server definitions. It selects the transport from each definition, so one adapter can connect to local stdio servers and remote HTTP servers at the same time:

```ts theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
import { MCPAdapter } from "@langchain/mcp-adapters";

const adapter = new MCPAdapter({
  servers: {
    // A local server launched as a subprocess over stdio.
    local: {
      command: "node",
      args: ["./weather-server.js"],
    },

    // A remote server reached over Streamable HTTP.
    remote: {
      url: "https://example.com/mcp",
    },

    // A legacy server with an explicit SSE endpoint.
    legacy: {
      url: "https://legacy.example.com/sse",
      transport: "sse",
      mode: "legacy",
    },
  },
});

try {
  const tools = await adapter.listTools();
  // Pass tools to createAgent({ tools, ... }).
} finally {
  await adapter.close();
}
```

<Card title="View example trace" icon="chart-line" href="https://smith.langchain.com/public/d9a802f7-75cf-45b4-b0f6-f4a62fa06e27/r" arrow horizontal>
  Open a public LangSmith run for this example.
</Card>

Each server definition can use one of these transports:

* **stdio**: Provide `command` and `args`. The adapter starts the command as a child process and communicates over standard input and output.
* **Streamable HTTP**: Provide `url`. This is the default transport for URL-based servers, so `transport: "http"` is optional.
* **SSE**: Provide `url` and set `transport: "sse"`. Use this transport only for legacy servers that expose an SSE endpoint.

Transport selection and protocol negotiation are separate. The optional `mode` setting controls which MCP protocol era the client accepts. See [Protocol eras](/oss/javascript/langchain/mcp/connections#protocol-eras).

<Note>
  For new remote servers, omit both `transport` and `mode`. The adapter uses Streamable HTTP with automatic protocol negotiation. Specify these settings only when connecting to a server with known legacy requirements.
</Note>
Title: stdio servers (default)
Link: https://docs.langchain.com/oss/deepagents/code/mcp-tools#stdio-servers-default
Page: oss/deepagents/code/mcp-tools
Content: ### stdio servers (default)

stdio servers are spawned as child processes. Deep Agents Code communicates with them over stdin/stdout.

Approved
```

## 4. Final answer

The exact `npx` command from the JavaScript Filesystem example in the file `mcp_servers_local_vs_remote.md` is:

```python
"command": "npx",
"args": ["-y", "@modelcontextprotocol/server-filesystem", "sample_docs"],
```

Regarding local stdio MCP connections in the official Python LangChain documentation, the transport that fits this configuration is **stdio**. 

Using stdio alone does not guarantee that file contents remain on the local computer when the local Python agent uses hosted ChatOpenAI. The configured model is a hosted OpenAI model, which means that while the stdio transport allows for local execution, any data processed by the hosted model could potentially be sent to external servers, depending on the model's architecture and data handling policies. 

Thus, while stdio facilitates local execution, it does not inherently prevent data from being transmitted to external services when using hosted models. This distinction is crucial for understanding data flow and privacy implications in such configurations. 

For further details, refer to the documentation on transports: [LangChain Transports](https://docs.langchain.com/oss/python/langchain/mcp/index#transports).

## 5. Trace

| Claim or observation | Evidence |
|---|---|
| The local handout starts Filesystem with npx and a directory argument | `call-027`; `sample_docs/mcp_servers_local_vs_remote.md` |
| The course configuration uses stdio for a locally started server | `call-027`; the handout's local-server configuration |
| Live documentation supports a local stdio connection | `call-028`; returned documentation text and links |
| Local transport alone does not establish where model inference occurs | A limitation inferred from the notebook configuration: tool results become model context and `ChatOpenAI` uses a hosted model. This is not a promise made by the stdio protocol |

Both servers were observed in the combined scenario:
`filesystem, langchain-docs`. The check asserts successful calls from
both servers, not merely that both tool lists were loaded.

### Resource context

The application fetched `mintlify://skills/langchain` and passed its text into an agent's
system prompt with `tools=[]`. The snapshot is
[langchain_guide.md](evidence/langchain_guide.md). Its SHA-256 is
`1d6867cef2213f10610098210ff68444ea29f49731a412220d9d88550bf3b6bb`. The resource answer and messages appear under `resource`
in `agent_runs.json`; it produced no MCP tool calls.

The [resource checks](evidence/resource_checks.json) preserve matching source
lines for the answer's keywords, including persistence setup and conversation
configuration. These checks aid inspection but do not prove arbitrary semantic
claims. The source explains both a checkpointer and a `thread_id`.

## 6. Failure or limitation

The missing-information scenario asked:

> Read all documents in the folder. What exact monthly hosting price in EUR do they specify for the LangChain Docs MCP server? If it is not stated, report that explicitly.

The observed answer was:

> The documents do not specify an exact monthly hosting price in EUR for the LangChain Docs MCP server. Therefore, the answer is: **not stated in the documents**.

Its tool evidence is retained under `missing_price` in `agent_runs.json` and
`tool_log.jsonl`. The absence of an exact price in these documents does not mean
the real service has no costs; it means the supplied sources do not establish one.

A concrete source-reading error was also observed during review. The earlier
combined answer called the Filesystem command `uvx`, while the handout's
JavaScript example uses `npx`. This was a false interpretation despite successful
tool calls. [grounding_review.json](evidence/grounding_review.json) retains that
answer and its original message trace. The corrected scenario requests the exact
command and verifies the expected package name before accepting the result.
Earlier related tool events remain labeled `*_before_review` in the full log.

An additional grounding risk is confusing local server execution with local
model execution. A local MCP server can still return information that the client
passes to a remote model. The combined query explicitly exposes this distinction.

Agent middleware exposes only the directory listing tool until discovery succeeds.
A client-side guard also requires a successful directory listing before other
filesystem operations. The agents receive only read tools, although the trusted
Filesystem server itself implements write tools. Remote search can return
related but different APIs, so source links and full text still require review.

## 7. Additional completed checks

| Lab step | Implementation and observed evidence |
|---|---|
| 1. Setup | `.env` credential presence check, pinned Python dependencies, pinned npm server, runtime manifest |
| 2. Connect | Two separate clients; tools and resources listed in `discovery.json` |
| 3. Convert tools | `get_tools()` converts MCP tools; available and selected names appear in notebook output |
| 4. Individual agents | `filesystem` and `documentation` scenarios, each with successful server calls |
| 5. Resource context | Actual resource read, snapshot, resource-only agent, keyword and line checks |
| 6. Complete agent | `combined` and `own_query` each use both servers |
| 7. Direct comparison, optional | Same memory question over direct HTTP; page snapshot, HTTP status, hash, and answers in `direct_comparison.json` |
| 8. Practical example, optional | Four `document_analysis_*` scenarios: listing, summary, content search, and read-only tool classification |

Direct HTTP is sufficient for a known page. MCP adds discovery and lets the
agent choose searches through the server's tool schema. The direct comparison
is not a performance benchmark because it may retrieve different text and use
a different number of model calls.

The final run completed 10 scenarios and recorded
32 interceptor events. Exact runtime versions, source
hashes, and completion time are in [manifest.json](evidence/manifest.json).
