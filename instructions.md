# Agents that speak MCP fluently

> **How you'll submit this lab**
>
> This repo is your lab. Fork it, do the work described below in your fork, then open a pull
> request back into this repository. An AI reviewer will check your PR against `rubric.md` and
> leave feedback directly on the PR. See `README.md` for the full workflow.

## Learning Goal

You will build or evaluate one Using MCP in LangChain path and prove the answer is grounded in inspectable evidence.

## Working Context

This lab focuses on the chain between source material, tool behavior, and final answer.
You keep the system small enough to trace one query, one retrieval or tool step, and one final output.
The proof should show grounding, not just a successful response.

## Proof of Learning

Submit one `lab_proof.md` with the code or workflow, one query, retrieved or tool evidence, final output, and one failure or limitation.

## Pseudocode

```text
INPUT: source documents, tool result, or user query
DECIDE: retrieval, tool, agent, or guardrail path
BUILD: prepare source -> run path -> capture output
VERIFY: inspect evidence that supports the answer
EXPLAIN: identify one grounding risk or failure mode
```

## Build

## Step-by-Step Instructions

### Step 1: Setup and Installation

Do: Install required packages and set up your environment.

Do:
1. Create a new Python file: `mcp_langchain.py` or notebook
2. Install required packages: `langchain`, `langchain-openai`, `langchain-mcp-adapters`, `mcp`, `python-dotenv`
3. Set up environment variables and verify your OpenAI API key is loaded

---

### Step 2: Connect to MCP Server

Do: Establish connection to an MCP server. This can be any server of your choice. We recommend starting small and connecting to a local filesystem MCP server first.

Do:
1. Import MCP client libraries (`langchain_mcp_adapters`, `mcp`, etc.)
2. Configure MCP server connection (use `MultiServerMCPClient` or direct MCP client)
3. Test the connection by listing available tools and resources

**Approach:**
- Use `langchain-mcp-adapters` for easier integration (recommended)
- Or use direct MCP client for more control
- Connect to a filesystem MCP server as a starting example

---

### Step 3: Load MCP Tools into LangChain

Do: Convert MCP tools to LangChain tools for use in agents.

Do:
1. Connect to MCP server
2. Retrieve available tools
3. Convert to LangChain tool format (use `langchain-mcp-adapters` for automatic conversion)
4. Verify tools are accessible

**Approach:**
- Use `MultiServerMCPClient.get_langchain_tools()` for automatic conversion (recommended)
- Or manually wrap MCP tools as LangChain tools if needed
- Verify tools are properly loaded and accessible

---

### Step 4: Create Agent with MCP Tools

Do: Build a LangChain agent that uses MCP tools.

Do:
1. Load MCP tools (from previous step)
2. Create a LangChain agent.
3. Test agent with MCP tools

**Approach:**
- Initialize LLM (e.g., `ChatOpenAI`)
- Create a prompt that describes available MCP capabilities
- Pass MCP tools to the agent
- Test with queries that require MCP tool usage

---

### Step 5: Access MCP Resources

Do: Use MCP resources to provide context to your agent.

Do:
1. List available resources using the MCP client (check `langchain-mcp-adapters` docs for the current method name: it may be `list_resources()` or accessed via the raw MCP client)
2. Read resource content (again, check the current `langchain-mcp-adapters` API; the method may be `read_resource()` on the raw MCP session)
3. Use resources in agent context (add to prompt or use as background information)

> **Note:** Method names like `get_langchain_resources()` and `read_resource()` may differ depending on the installed version of `langchain-mcp-adapters`. Always check the [package README](https://github.com/langchain-ai/langchain-mcp-adapters) for your installed version before using.

**Approach:**
- Resources provide read-only data for context
- Can be included in agent prompts or used as background information
- Useful for providing document context without requiring tool calls

---

### Step 6: Build a Complete MCP-Enabled Agent

Do: Create a functional agent that demonstrates MCP capabilities.

Do:
1. Set up MCP client with multiple servers (optional)
2. Load tools and resources
3. Create comprehensive agent
4. Test with real-world scenarios

**Approach:**
- Use `MultiServerMCPClient` to manage multiple MCP servers
- Connect all servers and load their tools
- Create agent with comprehensive prompt describing MCP capabilities
- Test with various queries that exercise different MCP tools
- Remember to disconnect MCP clients when done

---

### Step 7: OPTIONAL, Compare MCP vs Direct API Integration

Do: Understand when to use MCP vs direct API calls.

Do:
1. Implement the same functionality with direct API calls
2. Compare complexity, maintainability, and flexibility
3. Document trade-offs

**Key Comparisons:**

**MCP Integration:**
- Pros: Standardized protocol, reusable across frameworks, built-in abstraction, easy to add integrations
- Cons: Additional abstraction layer, requires MCP server setup, potential performance overhead
- Best for: Multiple integrations, standardized patterns, cross-framework compatibility

**Direct API Integration:**
- Pros: Direct control, no abstraction overhead, simpler for single integrations, better performance
- Cons: Custom code per integration, not reusable, more maintenance, inconsistent interfaces
- Best for: Single specific integration, full API control needed, performance-critical applications

---

### Step 8: OPTIONAL, Build a Practical Example

Do: Create a real-world agent that uses MCP for a practical task.

**Example: Document Analysis Agent**

Do:
1. Set up filesystem MCP server
2. Create agent that can:
   - Read documents from a directory
   - Analyze content
   - Generate summaries
   - Search for specific information

**Approach:**
- Configure filesystem MCP server pointing to documents directory
- Load MCP tools into LangChain
- Create specialized agent prompt for document analysis
- Test with queries like listing files, reading documents, generating summaries, and searching content

---

## Submission Guidelines


## Extension Activities (Optional)

1. **Multiple MCP Servers:** Integrate 2-3 different MCP servers in one agent
2. **Custom MCP Tool Wrapper:** Create custom wrappers for specific MCP tools
3. **Resource-Based Context:** Build agent that primarily uses MCP resources
4. **Error Handling:** Add robust error handling for MCP connection failures
5. **Performance Optimization:** Optimize MCP tool calls for better performance

---

## Resources

- [LangChain MCP Integration](https://python.langchain.com/docs/integrations/mcp/)
- [langchain-mcp-adapters GitHub](https://github.com/langchain-ai/langchain-mcp-adapters)
- [MCP Official Documentation](https://modelcontextprotocol.io/)
- [MCP Servers Repository](https://github.com/modelcontextprotocol/servers)

---

## Troubleshooting

**Issue:** MCP client connection fails
- **Solution:** Verify MCP server command is correct, check Node.js is installed, verify server is available

**Issue:** Tools not loading into LangChain
- **Solution:** Check MCP connection is established, verify tool conversion, check async/await usage

**Issue:** Agent doesn't use MCP tools
- **Solution:** Verify tools are properly registered, check tool descriptions are clear, ensure prompt encourages tool use

**Issue:** Async/await errors
- **Solution:** Ensure all MCP operations use async/await, use `asyncio.run()` for main execution, check for proper async function definitions

**Issue:** Resource access fails
- **Solution:** Verify resource URI format, check resource exists, ensure proper permissions

## Verify

The reviewer can trace one answer back to retrieved content, tool output, or guardrail evidence.

## Explain

Where could the system produce a plausible but unsupported answer?

## Submission Sanity Check

Before you submit:
- Keep only files for this lab.
- Name files clearly.
- Remove secrets, API keys, tokens, and unrelated data.
- Make `lab_proof.md` the entry point for the reviewer.

## Optional Stretch

- Add one targeted improvement: better chunking, reranking, a guardrail, a trace view, or a failure-case test.
- Create a small demo UI with vibecoding only if it helps inspect sources and answers. Deploy only if it can run safely without exposed secrets.
