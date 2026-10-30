# Lab Proof: Agents that Speak MCP Fluently

## 1. What I Built

In this lab, I implemented MCP integrations using LangChain, `MultiServerMCPClient`, and OpenAI's `gpt-4o-mini` model.

I connected two different MCP servers:

- **Filesystem MCP Server (stdio):** Runs locally using Node.js/npx and provides access to files inside the `sample_docs/` directory.
- **GitHub MCP Server (HTTP):** Connects to GitHub using a Personal Access Token to retrieve repository information.

The Filesystem server exposed 14 tools, while the GitHub server exposed 29 tools.

For security and simplicity, I restricted my combined agent to five read-only tools: four Filesystem tools and one GitHub tool.

I also implemented an evidence interceptor that logs the server name, tool name, input arguments, and a preview of the returned data.

After testing both servers individually, I created a combined LangChain agent capable of retrieving information from both sources within a single request.

**Implementation:** [mcp_langchain.ipynb](./mcp_langchain.ipynb)

## 2. Query

I tested the combined agent using the following question:

> Read our Project Atlas notes (project_notes.md): what constraint do they set about where ticket data may live? Then read the README of the GitHub repository langchain-ai/langchain-mcp-adapters: which transport would let us run an MCP server inside the client's own environment, so that data never leaves it?

This question requires the agent to access both local project documents and an external GitHub repository.

## 3. Evidence – MCP Tool Calls

The evidence interceptor confirmed that the agent accessed both MCP servers.

**Tool Call 1 – Filesystem**

```text
[LOG] filesystem -> read_text_file
path: .../sample_docs/project_notes.md
```

The relevant information in the project notes states:

> All project ticket data must remain within the client's internal environment and must not be stored in external third-party services.

**Tool Call 2 – GitHub**

```text
[LOG] github -> get_file_contents
{
    'owner': 'langchain-ai',
    'repo': 'langchain-mcp-adapters',
    'path': 'README.md'
}
```

The GitHub MCP server confirmed that the README was successfully downloaded.

The README discusses MCP transport options, including `stdio` for communication with locally running MCP servers.

Both tool calls were recorded before the final answer was generated.

**Evidence limitation:** The interceptor prints only the first 150 characters of each tool result. Therefore, the logs confirm the tool calls and provide partial output evidence, but do not preserve the complete retrieved README text.

## 4. Final Agent Answer

The combined agent returned:

**Project Atlas Notes**

The Project Atlas notes specify a constraint regarding ticket data:

"All project ticket data must remain within the client's internal environment and must not be stored in external third-party services."

**GitHub Repository README**

The README identifies `stdio` as a transport that allows an MCP server to run inside the client's own environment.

However, the agent also stated that using this transport ensures that data does not leave the local environment.

This final statement is not a valid security guarantee.

## 5. Evidence Trace

| Agent claim | Source | Verification |
|---|---|---|
| Project ticket data must remain within the client's internal environment | `project_notes.md` via `read_text_file` | Supported by the document |
| `stdio` supports locally running MCP servers | GitHub README via `get_file_contents` | Consistent with the documented transport |
| Using `stdio` guarantees that data never leaves the environment | Agent conclusion | Not supported |

The interceptor logs demonstrate that the agent retrieved information from both MCP servers.

The first claim is directly supported by our local document. The second describes a valid use of `stdio`, although the abbreviated GitHub log does not provide the full supporting README excerpt.

The final claim goes beyond what the transport mechanism guarantees.

## 6. Failure or Limitation

The most important limitation I identified was that **successful tool retrieval does not guarantee a completely correct or secure final answer**.

Our combined agent correctly retrieved the local project notes and GitHub README, but incorrectly suggested that using `stdio` ensures data never leaves the local environment.

In reality, `stdio` only describes how the MCP client communicates with the locally running server. It does not control what the LangChain agent does with the retrieved information afterward.

Our implementation uses `ChatOpenAI`, meaning retrieved document content can be transmitted to an external model API for processing.

Therefore, using a local Filesystem MCP server alone does not satisfy a strict requirement that all project data must remain within a client's internal environment.

Even though our system prompt explicitly warned against this assumption, the agent still made the incorrect claim.

This demonstrates why grounding, tool restrictions, and prompt instructions must be complemented by independent validation and appropriate security controls.

For a real client project, I would evaluate whether an approved private model endpoint or locally hosted LLM is required, and ensure that sensitive data cannot be transmitted to unauthorized external services.

## Conclusion

This lab helped me understand how MCP standardizes access to external tools and data sources and how these capabilities can be integrated into LangChain agents.

I successfully connected a local and a remote MCP server, discovered their tools, restricted the available capabilities, and implemented an agent that uses both sources.

The most important learning was the distinction between **retrieving evidence** and **correctly interpreting evidence**.

A functioning MCP integration is only one part of a reliable AI system. The final answer must also be verified against its sources, especially when it makes security-related claims.