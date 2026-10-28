# Lab Proof: Agents that speak MCP fluently

## Goal

Build a small LangChain agent that uses MCP tools and MCP resources, and prove that its answers are grounded in evidence you can inspect: every fact in the final answer can be traced back to a tool output or a resource.

## Files

| File | What it does |
|---|---|
| `mcp_langchain.py` | Main script: connects to two MCP servers, loads tools and resources, builds the agent, runs test queries and prints the full trace |
| `resource_server.py` | Small custom MCP server that exposes one read-only resource: `info://project` |
| `docs/notes.txt` | Source document the agent can read through the filesystem MCP server |
| `.env` | OpenAI API key (not committed, listed in `.gitignore`) |

## Setup

```
pip install langchain langchain-openai langchain-mcp-adapters mcp python-dotenv
```

Node.js is required for the filesystem server (tested with v26). Versions used: `langchain-mcp-adapters` 0.3.2, `mcp` 1.30.0, `langchain` 1.4.6. Model: `gpt-4o-mini`, temperature 0.

Run with:

```
python mcp_langchain.py
```

## Workflow

```
User query
   │
   ▼
LangChain agent (gpt-4o-mini)
   │  system prompt includes the resource content as background information
   │
   ├── MCP server 1: filesystem (@modelcontextprotocol/server-filesystem)
   │      14 tools, restricted to the docs/ folder
   │      e.g. list_directory, read_text_file, search_files
   │
   └── MCP server 2: project (resource_server.py, built with FastMCP)
          1 resource: info://project
          "Project name: MCP Lab. Project owner: Nicolò. Team size: 3 people."
   │
   ▼
Final answer, printed with the full message trace (pretty_print)
```

1. **Connect:** `MultiServerMCPClient` starts both servers over stdio.
2. **Load tools:** `client.get_tools()` returns the 14 filesystem tools already converted to LangChain `StructuredTool` objects. Verified by calling `list_directory` directly, which returned `[FILE] notes.txt`.
3. **Load resources:** `client.get_resources("project")` returns 1 resource (`info://project`). Its text is added to the system prompt as background information.
4. **Build agent:** `create_agent(llm, tools, system_prompt=...)`.
5. **Run and trace:** each query's messages are printed, showing every tool call, its arguments, the tool output and the final answer.

## Main query and evidence

**Query:** "Who is the project owner, and what is the project deadline?"

This query was chosen because the two facts live in different places: the owner is only in the MCP resource, and the deadline is only in `docs/notes.txt`.

**Trace (final version):**

| Step | Action | Output |
|---|---|---|
| 1 | Resource `info://project` (loaded into prompt) | "Project owner: Nicolò" |
| 2 | Tool call `list_directory(docs/)` | `[FILE] notes.txt` |
| 3 | Tool call `read_text_file(docs/notes.txt)` | "This is a test note for the MCP lab. The project deadline is Friday." |
| 4 | Final answer | **"The project owner is Nicolò, and the project deadline is Friday."** |

**Grounding check:** "Nicolò" comes from the resource in step 1. "Friday" comes from the tool output in step 3. The answer contains no fact that isn't in one of those two sources.

## Additional test queries

| Query | Source used | Answer | Grounded? |
|---|---|---|---|
| What files are in the docs folder? | `list_directory` | notes.txt | Yes |
| How many people are on the team? | Resource only, no tool call | 3 people | Yes |
| What is the project budget? | `list_directory` + `read_text_file` | Read the only file, found no budget, said it cannot provide one | Yes, it did not invent a number |

## Failure / limitation

The same query failed twice before it worked. The only thing that changed between runs was the system prompt.

**Run 1: agent skipped the tools.**
The prompt said "always use the tools", but also gave background information. The agent answered from the background only, made no tool call, and replied: "The project owner is Nicolò. However, the project deadline is not provided in the background information." The deadline was in `notes.txt` all along.

**Run 2: agent used the wrong tool and drew the wrong conclusion.**
After telling it to check the files when background info isn't enough, it called `search_files` with patterns `*deadline*` and `*due date*`. `search_files` matches file **names**, not file contents, so both returned "No matches found". The agent concluded: "the project deadline is not available." That answer sounds confident but isn't supported: the tool never looked inside the file.

**Run 3: fixed.**
The prompt was changed to explain how the tools work: `search_files` only matches names; to find information, use `list_directory` and then `read_text_file` on each file; never say something is missing until every file has been read. The agent then followed that path and answered correctly.

**What this shows:** a plausible but unsupported answer can come from the agent trusting partial context, or from misreading what a tool's empty result means. Here the error was "information missing" rather than a made-up fact, but it's the same root problem: the final answer was not checked against the source. The fix depended entirely on prompt wording, which is fragile: with more files or a different model, the agent could skip files again. A more robust fix would be a check in code (e.g. require that a `read_text_file` call happened before the agent says information is missing).

## Other notes

- The filesystem MCP server exposes **no resources**, only tools (`get_resources` on it fails). That is why a second, custom server was built for the resource part of the lab.
- The lab text mentions `get_langchain_tools()`. That method does not exist in `langchain-mcp-adapters` 0.3.2; the current method is `get_tools()`.
- **Disconnecting:** in this version, the client opens a new session for each call and closes it automatically (visible in the logs as repeated "Secure MCP Filesystem Server running on stdio" lines), so no manual disconnect is needed.
- The filesystem server is restricted to the `docs/` folder only, so the agent cannot read or write anything else on the machine. It does still have write tools (`write_file`, `edit_file`, `move_file`) inside that folder; for a read-only use case those should be removed from the tool list.
