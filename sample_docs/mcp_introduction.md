# MCP Introduction with LangChain

This notebook demonstrates connecting to MCP servers and integrating them with LangChain agents using the `langchain-mcp-adapters` package.

## Setup

!pip install langchain langchain-openai langchain-mcp-adapters langgraph mcp python-dotenv -q


```python
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables from .env file
load_dotenv()

# Verify API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please create a .env file with your API key.")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
```

    /home/bella/miniforge3/envs/consulting/lib/python3.13/site-packages/tqdm/auto.py:21: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html
      from .autonotebook import tqdm as notebook_tqdm


## LangChain Integration with MCP

### Using langchain-mcp-adapters

LangChain provides the `langchain-mcp-adapters` package, which offers a seamless way to connect LangChain applications to MCP servers. This package includes `MultiServerMCPClient`, which allows you to connect to multiple MCP servers and load their tools, resources, and prompts into LangChain agents.

### Key Benefits

- **Standardized Protocol**: Work with one protocol instead of juggling multiple APIs
- **Multiple Servers**: Connect to multiple MCP servers simultaneously
- **LangChain Native**: Tools, resources, and prompts are automatically LangChain-compatible
- **Stateless by Default**: Each tool call creates a fresh session, no context manager needed
- **Tool Interceptors**: Middleware pattern for customizing tool behavior

### The LangChain Documentation MCP Server

We'll use the LangChain documentation MCP server as our example:
- **MCP Server URL**: `https://docs.langchain.com/mcp`
- **Documentation Index**: `https://docs.langchain.com/llms.txt`
- **Transport**: HTTP (not stdio)
- **Provides**: Access to LangChain, LangGraph, and LangSmith documentation

This MCP server allows you to query the latest LangChain documentation programmatically, making it perfect for building agents that can answer questions about LangChain features and APIs.

### Connecting to the LangChain Documentation MCP Server

Now let's connect to the LangChain documentation MCP server using HTTP transport.

`MultiServerMCPClient` accepts a dictionary where keys are server names and values are configuration dicts specifying `transport` and connection details:


```python
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

# Configure the LangChain documentation MCP server
# MultiServerMCPClient takes a dict of server configs
# Each config specifies transport type and connection details
mcp_client = MultiServerMCPClient({
    "langchain-docs": {
        "transport": "http",
        "url": "https://docs.langchain.com/mcp"
    }
})

print("MCP client configured for LangChain documentation server")
print(f"Server: langchain-docs → https://docs.langchain.com/mcp")
```

    MCP client configured for LangChain documentation server
    Server: langchain-docs → https://docs.langchain.com/mcp


    /home/bella/miniforge3/envs/consulting/lib/python3.13/site-packages/langgraph/checkpoint/base/__init__.py:17: LangChainPendingDeprecationWarning: The default value of `allowed_objects` will change in a future version. Pass an explicit value (e.g., allowed_objects='messages' or allowed_objects='core') to suppress this warning.
      from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer



```python
mcp_client
```




    <langchain_mcp_adapters.client.MultiServerMCPClient at 0x71290f31cc20>



### Loading MCP Tools into LangChain

The `get_tools()` method retrieves all tools from connected MCP servers and converts them to LangChain-compatible tools.

**Note:** `MultiServerMCPClient` is stateless by default — each call to `get_tools()` internally creates and tears down fresh sessions automatically. No `async with` context manager is needed:


```python
# Load tools from the MCP server
# The client is stateless: get_tools() creates ephemeral sessions under the hood
mcp_tools = await mcp_client.get_tools()

print(f"Loaded {len(mcp_tools)} tools from MCP server(s)")
print("\nAvailable tools:")
for tool in mcp_tools:
    print(f"  - {tool.name}: {tool.description[:80]}...")
```

    Loaded 2 tools from MCP server(s)
    
    Available tools:
      - search_docs_by_lang_chain: Search across the Docs by LangChain knowledge base to find relevant information,...
      - query_docs_filesystem_docs_by_lang_chain: Run a read-only shell-like query against a virtualized, in-memory filesystem roo...



```python
mcp_tools
```




    [StructuredTool(name='search_docs_by_lang_chain', description='Search across the Docs by LangChain knowledge base to find relevant information, code examples, API references, and guides. Use this tool when you need to answer questions about Docs by LangChain, find specific documentation, understand how features work, or locate implementation details. The search returns contextual content with titles and direct links to the documentation pages. If you need the full content of a specific page, use the query_docs_filesystem tool to `head` or `cat` the page path (append `.mdx` to the path returned from search — e.g. `head -200 /api-reference/create-customer.mdx`).', args_schema={'type': 'object', 'properties': {'query': {'type': 'string', 'description': 'Search query'}}, 'required': ['query'], 'additionalProperties': False, '$schema': 'http://json-schema.org/draft-07/schema#'}, response_format='content_and_artifact', coroutine=<function convert_mcp_tool_to_langchain_tool.<locals>.call_tool at 0x7a6a868f8860>),
     StructuredTool(name='query_docs_filesystem_docs_by_lang_chain', description='Run a read-only shell-like query against a virtualized, in-memory filesystem rooted at `/` that contains ONLY the Docs by LangChain documentation pages and OpenAPI specs. This is NOT a shell on any real machine — nothing runs on the user\'s computer, the server host, or any network. The filesystem is a sandbox backed by documentation chunks.\n\nThis is how you read documentation pages: there is no separate "get page" tool. To read a page, pass its `.mdx` path (e.g. `/quickstart.mdx`, `/api-reference/create-customer.mdx`) to `head` or `cat`. To search the docs with exact keyword or regex matches, use `rg`. To understand the docs structure, use `tree` or `ls`.\n\n**Workflow:** Start with the search tool for broad or conceptual queries like "how to authenticate" or "rate limiting". Use this tool when you need exact keyword/regex matching, structural exploration, or to read the full content of a specific page by path.\n\nSupported commands: rg (ripgrep), grep, find, tree, ls, cat, head, tail, stat, wc, sort, uniq, cut, sed, awk, jq, plus basic text utilities. No writes, no network, no process control. Run `--help` on any command for usage.\n\nEach call is STATELESS: the working directory always resets to `/` and no shell variables, aliases, or history carry over between calls. If you need to operate in a subdirectory, chain commands in one call with `&&` or pass absolute paths (e.g., `cd /api-reference && ls` or `ls /api-reference`). Do NOT assume that `cd` in one call affects the next call.\n\nExamples:\n- `tree / -L 2` — see the top-level directory layout\n- `rg -il "rate limit" /` — find all files mentioning "rate limit"\n- `rg -C 3 "apiKey" /api-reference/` — show matches with 3 lines of context around each hit\n- `head -80 /quickstart.mdx` — read the top 80 lines of a specific page\n- `head -80 /quickstart.mdx /installation.mdx /guides/first-deploy.mdx` — read multiple pages in one call\n- `cat /api-reference/create-customer.mdx` — read a full page when you need everything\n- `cat /openapi/spec.json | jq \'.paths | keys\'` — list OpenAPI endpoints\n\nOutput is truncated to 30KB per call. Prefer targeted `rg -C` or `head -N` over broad `cat` on large files. To read only the relevant sections of a large file, use `rg -C 3 "pattern" /path/file.mdx`. Batch multiple file reads into a single `head` or `cat` call whenever possible.\n\nWhen referencing pages in your response to the user, convert filesystem paths to URL paths by removing the `.mdx` extension. For example, `/quickstart.mdx` becomes `/quickstart` and `/api-reference/overview.mdx` becomes `/api-reference/overview`.', args_schema={'type': 'object', 'properties': {'command': {'type': 'string', 'description': 'A shell command to run against the virtualized documentation filesystem (e.g., `rg -il "keyword" /`, `tree / -L 2`, `head -80 /path/file.mdx`).'}}, 'required': ['command'], 'additionalProperties': False, '$schema': 'http://json-schema.org/draft-07/schema#'}, response_format='content_and_artifact', coroutine=<function convert_mcp_tool_to_langchain_tool.<locals>.call_tool at 0x7a6a868f8720>)]



### Using MCP Tools with LangChain Agents

Now let's create a LangChain agent that can use these MCP tools to query the LangChain documentation.

We use `create_react_agent` from `langgraph.prebuilt` with the `prompt` parameter to set the system message:


```python
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

# Get tools from MCP server
tools = await mcp_client.get_tools()

# Create agent with the model and MCP tools
# Use the 'prompt' parameter (not 'state_modifier', which is deprecated)
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are a helpful assistant that can answer questions about LangChain, LangGraph, and LangSmith by searching the official documentation. Always provide accurate, up-to-date information based on the documentation."
)

print(f"Agent created with {len(tools)} MCP tools")
print(f"Tools: {[tool.name for tool in tools]}")
```

    Agent created with 2 MCP tools
    Tools: ['search_docs_by_lang_chain', 'query_docs_filesystem_docs_by_lang_chain']


### Querying LangChain Documentation

Let's test the agent by asking it questions about LangChain:


```python
# Query the agent about LangChain
question = "How do I create a LangChain agent with tools?"
print(f"Question: {question}\n")

result = await agent.ainvoke({
    "messages": [HumanMessage(content=question)]
})

print(f"Answer: {result['messages'][-1].content}")
```

    Question: How do I create a LangChain agent with tools?
    
    Answer: To create a LangChain agent with tools, you can follow these steps. Below are examples in both JavaScript and Python.
    
    ### JavaScript Example
    
    1. **Install Required Packages**:
       ```bash
       npm install langchain zod @langchain/openai
       ```
    
    2. **Create the Agent**:
       ```typescript
       import { createAgent, tool } from "langchain";
       import * as z from "zod";
    
       // Define a tool
       const getWeather = tool(
         (input) => `It's always sunny in ${input.city}!`,
         {
           name: "get_weather",
           description: "Get the weather for a given city",
           schema: z.object({
             city: z.string().describe("The city to get the weather for"),
           }),
         }
       );
    
       // Create the agent
       const agent = createAgent({
         model: "gpt-5.5", // or any other model you want to use
         tools: [getWeather],
       });
    
       // Invoke the agent
       console.log(
         await agent.invoke({
           messages: [{ role: "user", content: "What's the weather in San Francisco?" }],
         })
       );
       ```
    
    ### Python Example
    
    1. **Install Required Packages**:
       ```bash
       pip install -qU langchain "langchain[openai]"
       ```
    
    2. **Create the Agent**:
       ```python
       from langchain.agents import create_agent
    
       # Define a tool
       def get_weather(city: str) -> str:
           """Get weather for a given city."""
           return f"It's always sunny in {city}!"
    
       # Create the agent
       agent = create_agent(
           model="openai:gpt-5.5",  # or any other model you want to use
           tools=[get_weather],
           system_prompt="You are a helpful assistant",
       )
    
       # Invoke the agent
       result = agent.invoke(
           {"messages": [{"role": "user", "content": "What's the weather in San Francisco?"}]}
       )
       print(result["messages"][-1].content_blocks)
       ```
    
    ### Key Points
    - **Tools**: You can define custom tools using the `tool` function in JavaScript or as regular functions in Python.
    - **Model**: Specify the model you want to use for the agent.
    - **Invocation**: Use the `invoke` method to interact with the agent, passing in the user messages.
    
    For more detailed information, you can refer to the [LangChain documentation](https://docs.langchain.com/oss/javascript/langchain/overview#create-an-agent) for JavaScript and [Python documentation](https://docs.langchain.com/oss/python/langchain/overview#create-an-agent).


### Accessing MCP Resources

MCP resources provide read-only access to data. The `get_resources()` method returns LangChain `Blob` objects.

You can optionally filter by server name or specific URIs:


```python
# Access MCP resources
# get_resources() is also stateless — no context manager needed
mcp_resources = await mcp_client.get_resources()

```


```python
mcp_resources
```




    [Blob 124424902288368]




```python
print(mcp_resources[0].as_string())
```

    ---
    name: Langchain
    description: Use when building AI agents, orchestrating LLM workflows, deploying stateful applications, evaluating agent quality, or tracing and debugging LLM application behavior. Covers agent development with LangChain/Deep Agents, workflow orchestration with LangGraph, observability with LangSmith, and testing/evaluation frameworks.
    metadata:
        mintlify-proj: langchain
        version: "1.0"
    ---
    
    # LangChain Skill
    
    ## Product summary
    
    LangChain is an open-source framework for building AI agents and LLM applications. It provides three core layers: **LangChain** (agent framework with models, tools, and abstractions), **LangGraph** (low-level orchestration runtime for stateful workflows), and **Deep Agents** (high-level harness with planning, subagents, and filesystem tools). LangSmith is the companion platform for observability, evaluation, and deployment. Use `pip install langchain langgraph deepagents` to get started. Key files: agent definitions (Python/TypeScript), LangGraph state schemas, tool definitions, and LangSmith configuration via environment variables (`LANGSMITH_API_KEY`, `LANGSMITH_TRACING`). Primary docs: https://docs.langchain.com
    
    ## When to use
    
    Reach for this skill when:
    - **Building agents**: Creating AI agents that call tools, maintain conversation state, or execute multi-step tasks
    - **Orchestrating workflows**: Designing stateful, long-running processes with branching, loops, and human-in-the-loop checkpoints
    - **Deploying to production**: Running agents at scale with durable execution, streaming, and persistence
    - **Evaluating quality**: Running experiments against datasets, comparing agent outputs, or measuring performance metrics
    - **Debugging failures**: Tracing LLM calls, inspecting agent state, or analyzing tool execution
    - **Integrating models**: Connecting to OpenAI, Anthropic, Google, Ollama, or other LLM providers
    - **Managing context**: Handling long conversations, summarizing history, or loading persistent memory
    
    ## Quick reference
    
    ### Installation & setup
    
    | Task | Command |
    |------|---------|
    | Install core | `pip install langchain langgraph` |
    | Install Deep Agents | `pip install deepagents` |
    | Install provider | `pip install langchain-openai` (or `-anthropic`, `-google-genai`, etc.) |
    | Enable tracing | `export LANGSMITH_API_KEY=...` and `export LANGSMITH_TRACING=true` |
    
    ### Agent creation patterns
    
    | Pattern | Use case | Code |
    |---------|----------|------|
    | **LangChain agent** | Fine-grained control, custom middleware | `create_agent(model="openai:gpt-5.4", tools=[...], system_prompt="...")` |
    | **Deep Agent** | Built-in planning, subagents, filesystem | `create_deep_agent(model="...", tools=[...], system_prompt="...")` |
    | **LangGraph workflow** | Custom orchestration, complex state | `StateGraph(MyState).add_node(...).add_edge(...).compile()` |
    
    ### Core components
    
    | Component | Purpose | Example |
    |-----------|---------|---------|
    | **Model** | LLM provider and model | `"openai:gpt-5.4"` or `init_chat_model("gpt-5.4")` |
    | **Tools** | Functions agent can call | `@tool def search(query: str) -> str: ...` |
    | **System prompt** | Agent behavior instructions | `system_prompt="You are a helpful assistant"` |
    | **Checkpointer** | Persist state across runs | `InMemorySaver()` or `PostgresSaver(...)` |
    | **Middleware** | Extend agent capabilities | `FilesystemMiddleware`, `SummarizationMiddleware`, `SubAgentMiddleware` |
    
    ### Invocation & streaming
    
    ```python
    # Basic invocation with thread persistence
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "..."}]},
        config={"configurable": {"thread_id": "user-123"}}
    )
    
    # Stream intermediate steps
    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": "..."}]},
        stream_mode="values"
    ):
        print(chunk["messages"][-1])
    ```
    
    ### LangSmith observability
    
    | Task | Setup |
    |------|-------|
    | Enable tracing | `export LANGSMITH_TRACING=true` and set `LANGSMITH_API_KEY` |
    | View traces | Visit https://smith.langchain.com after running agent |
    | Evaluate agent | Create dataset, define evaluators, run experiment via SDK or UI |
    | Deploy agent | Use `langgraph deploy` CLI or LangSmith Cloud UI |
    
    ## Decision guidance
    
    ### When to use LangChain vs. LangGraph vs. Deep Agents
    
    | Scenario | Use | Reason |
    |----------|-----|--------|
    | **Just starting, want quick setup** | Deep Agents | Built-in planning, subagents, filesystem; minimal config |
    | **Need fine-grained control over tools & middleware** | LangChain agent | Composable middleware, custom hooks, no overhead |
    | **Building complex multi-step workflows** | LangGraph | Low-level state management, branching, loops, human-in-the-loop |
    | **Deploying to production** | LangGraph + LangSmith | Durable execution, streaming, observability, scaling |
    | **Evaluating agent quality** | LangSmith evaluation | Datasets, evaluators, experiment tracking, metrics |
    
    ### When to use checkpointer types
    
    | Checkpointer | Use case |
    |--------------|----------|
    | `InMemorySaver()` | Local development, testing |
    | `PostgresSaver(...)` | Production, persistent state |
    | `SqliteSaver(...)` | Single-machine production |
    | None (LangSmith managed) | Deployed on LangSmith Cloud |
    
    ### Middleware selection
    
    | Middleware | When to add |
    |------------|------------|
    | `FilesystemMiddleware` | Agent needs to read/write files |
    | `SummarizationMiddleware` | Long conversations exceed context window |
    | `SubAgentMiddleware` | Delegating subtasks to isolated agents |
    | `MemoryMiddleware` | Loading persistent instructions/knowledge |
    | `SkillsMiddleware` | Providing domain-specific workflows on demand |
    | `ModelRetryMiddleware` | Handling rate limits and transient failures |
    | `HumanInTheLoopMiddleware` | Requiring approval before high-impact actions |
    
    ## Workflow
    
    ### Building and testing an agent locally
    
    1. **Define tools**: Write Python functions decorated with `@tool` or use LangChain tool classes. Include docstrings—they become part of the model's prompt.
       ```python
       @tool
       def search(query: str) -> str:
           """Search for information."""
           return f"Results for {query}"
       ```
    
    2. **Choose a model**: Pick a provider and model. Set API keys as environment variables.
       ```python
       model = init_chat_model("openai:gpt-5.4", temperature=0.5)
       ```
    
    3. **Create the agent**: Use `create_agent()` for control or `create_deep_agent()` for built-in capabilities.
       ```python
       agent = create_agent(model=model, tools=[search], system_prompt="...")
       ```
    
    4. **Add a checkpointer**: Enable conversation memory with `InMemorySaver()` for local work.
       ```python
       from langgraph.checkpoint.memory import InMemorySaver
       agent = create_agent(..., checkpointer=InMemorySaver())
       ```
    
    5. **Enable tracing**: Set `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` to see traces in LangSmith.
    
    6. **Invoke and test**: Call `agent.invoke()` with a message and `thread_id`.
       ```python
       result = agent.invoke(
           {"messages": [{"role": "user", "content": "Search for AI news"}]},
           config={"configurable": {"thread_id": "test-1"}}
       )
       ```
    
    7. **Stream for UX**: Use `agent.stream()` to show progress to users.
    
    8. **Evaluate quality**: Create a dataset in LangSmith, define evaluators, and run an experiment to measure performance.
    
    9. **Deploy**: Use `langgraph deploy` to push to LangSmith Cloud or deploy a standalone server with Docker.
    
    ### Deploying an agent to production
    
    1. **Prepare the app**: Organize code with `langgraph.json` config, define state schema, and add a checkpointer (PostgreSQL recommended).
    
    2. **Test locally**: Run `langgraph up` to test the server locally.
    
    3. **Deploy to Cloud**: Use `langgraph deploy` to push to LangSmith Cloud (requires Plus plan or above).
    
    4. **Or deploy standalone**: Use Docker/Kubernetes with your own PostgreSQL and Redis; optional LangSmith tracing.
    
    5. **Monitor with LangSmith**: Set up dashboards, alerts, and Engine to detect and fix failures.
    
    ## Common gotchas
    
    - **Forgetting checkpointer**: Without a checkpointer, conversation history is lost between invocations. Always pass one locally; LangSmith provides it automatically.
    - **Tool docstrings matter**: The model only sees tool names and docstrings. Write clear, specific descriptions or the model won't use tools correctly.
    - **Context window overflow**: Long conversations fill the context window. Use `SummarizationMiddleware` or offload to filesystem to prevent failures.
    - **Model string format**: Use `"provider:model"` format (e.g., `"openai:gpt-5.4"`) or pass an initialized model instance. Mixing formats causes errors.
    - **Thread ID scoping**: `thread_id` persists conversation history. Use unique IDs per user/session or history will bleed across conversations.
    - **Middleware order matters**: Middleware hooks fire in order. Place summarization before memory loading so compressed history is available.
    - **Streaming mode confusion**: `stream_mode="values"` returns full state; `stream_mode="updates"` returns only changed fields. Choose based on your UI needs.
    - **API key not set**: Agents fail silently if provider API keys aren't in environment. Always check `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.
    - **LangSmith tracing overhead**: Tracing adds latency. Disable in performance-critical paths with `LANGSMITH_TRACING=false` or use sampling.
    - **Subagent context isolation**: Subagents run in isolated context windows. Don't assume they have access to parent agent's full history.
    
    ## Verification checklist
    
    Before submitting agent code or deploying:
    
    - [ ] All tools have clear docstrings describing inputs and outputs
    - [ ] API keys are set as environment variables (not hardcoded)
    - [ ] Checkpointer is configured (InMemorySaver for dev, PostgresSaver for prod)
    - [ ] System prompt is specific and actionable
    - [ ] Agent invocation includes `thread_id` for conversation persistence
    - [ ] Streaming is tested if used in production UI
    - [ ] LangSmith tracing is enabled and traces appear in dashboard
    - [ ] Evaluation dataset created and baseline metrics recorded
    - [ ] Error handling covers API failures, rate limits, and timeouts
    - [ ] Middleware stack is ordered correctly (summarization before memory)
    - [ ] Context window usage is monitored (check token counts in traces)
    - [ ] Deployment tested locally with `langgraph up` before pushing to cloud
    - [ ] Production checkpointer (PostgreSQL) is configured and tested
    - [ ] Monitoring dashboards and alerts are set up in LangSmith
    
    ## Resources
    
    **Comprehensive navigation**: https://docs.langchain.com/llms.txt
    
    **Critical documentation pages**:
    1. [LangChain Quickstart](https://docs.langchain.com/oss/python/langchain/quickstart) — Build your first agent in minutes
    2. [LangGraph Overview](https://docs.langchain.com/oss/python/langgraph/overview) — Understand orchestration, persistence, and streaming
    3. [LangSmith Observability](https://docs.langchain.com/langsmith/observability) — Trace, evaluate, and monitor agents in production
    
    ---
    
    > For additional documentation and navigation, see: https://docs.langchain.com/llms.txt



```python
mcp_tools = await mcp_client.get_tools()
```


```python
mcp_tools
```




    [StructuredTool(name='search_docs_by_lang_chain', description='Search across the Docs by LangChain knowledge base to find relevant information, code examples, API references, and guides. Use this tool when you need to answer questions about Docs by LangChain, find specific documentation, understand how features work, or locate implementation details. The search returns contextual content with titles and direct links to the documentation pages. If you need the full content of a specific page, use the query_docs_filesystem tool to `head` or `cat` the page path (append `.mdx` to the path returned from search — e.g. `head -200 /api-reference/create-customer.mdx`).', args_schema={'type': 'object', 'properties': {'query': {'type': 'string', 'description': 'Search query'}}, 'required': ['query'], 'additionalProperties': False, '$schema': 'http://json-schema.org/draft-07/schema#'}, response_format='content_and_artifact', coroutine=<function convert_mcp_tool_to_langchain_tool.<locals>.call_tool at 0x7e263f93c5e0>),
     StructuredTool(name='query_docs_filesystem_docs_by_lang_chain', description='Run a read-only shell-like query against a virtualized, in-memory filesystem rooted at `/` that contains ONLY the Docs by LangChain documentation pages and OpenAPI specs. This is NOT a shell on any real machine — nothing runs on the user\'s computer, the server host, or any network. The filesystem is a sandbox backed by documentation chunks.\n\nThis is how you read documentation pages: there is no separate "get page" tool. To read a page, pass its `.mdx` path (e.g. `/quickstart.mdx`, `/api-reference/create-customer.mdx`) to `head` or `cat`. To search the docs with exact keyword or regex matches, use `rg`. To understand the docs structure, use `tree` or `ls`.\n\n**Workflow:** Start with the search tool for broad or conceptual queries like "how to authenticate" or "rate limiting". Use this tool when you need exact keyword/regex matching, structural exploration, or to read the full content of a specific page by path.\n\nSupported commands: rg (ripgrep), grep, find, tree, ls, cat, head, tail, stat, wc, sort, uniq, cut, sed, awk, jq, plus basic text utilities. No writes, no network, no process control. Run `--help` on any command for usage.\n\nEach call is STATELESS: the working directory always resets to `/` and no shell variables, aliases, or history carry over between calls. If you need to operate in a subdirectory, chain commands in one call with `&&` or pass absolute paths (e.g., `cd /api-reference && ls` or `ls /api-reference`). Do NOT assume that `cd` in one call affects the next call.\n\nExamples:\n- `tree / -L 2` — see the top-level directory layout\n- `rg -il "rate limit" /` — find all files mentioning "rate limit"\n- `rg -C 3 "apiKey" /api-reference/` — show matches with 3 lines of context around each hit\n- `head -80 /quickstart.mdx` — read the top 80 lines of a specific page\n- `head -80 /quickstart.mdx /installation.mdx /guides/first-deploy.mdx` — read multiple pages in one call\n- `cat /api-reference/create-customer.mdx` — read a full page when you need everything\n- `cat /openapi/spec.json | jq \'.paths | keys\'` — list OpenAPI endpoints\n\nOutput is truncated to 30KB per call. Prefer targeted `rg -C` or `head -N` over broad `cat` on large files. To read only the relevant sections of a large file, use `rg -C 3 "pattern" /path/file.mdx`. Batch multiple file reads into a single `head` or `cat` call whenever possible.\n\nWhen referencing pages in your response to the user, convert filesystem paths to URL paths by removing the `.mdx` extension. For example, `/quickstart.mdx` becomes `/quickstart` and `/api-reference/overview.mdx` becomes `/api-reference/overview`.', args_schema={'type': 'object', 'properties': {'command': {'type': 'string', 'description': 'A shell command to run against the virtualized documentation filesystem (e.g., `rg -il "keyword" /`, `tree / -L 2`, `head -80 /path/file.mdx`).'}}, 'required': ['command'], 'additionalProperties': False, '$schema': 'http://json-schema.org/draft-07/schema#'}, response_format='content_and_artifact', coroutine=<function convert_mcp_tool_to_langchain_tool.<locals>.call_tool at 0x7e263ef5efc0>)]



### Middleware and Tool Interceptors

One of the powerful features of `langchain-mcp-adapters` is the ability to use tool interceptors (middleware) to customize tool behavior. This allows you to:

- **Log tool calls**: Track when and how tools are used
- **Modify requests/responses**: Transform tool inputs or outputs
- **Add validation**: Ensure tool inputs meet certain criteria
- **Implement retry logic, caching, or rate limiting**

Interceptors follow a handler callback pattern (similar to middleware in web frameworks). Any async callable matching the `(request, handler) -> result` signature works. Interceptors compose in an "onion" pattern where the first interceptor is the outermost layer.

Let's create a simple tool interceptor that logs tool usage:


```python
from langchain_mcp_adapters.client import MultiServerMCPClient

# Tool interceptors are async callables with signature:
#   async def interceptor(request, handler) -> result
# - request: MCPToolCallRequest with .name and .arguments
# - handler: callable to invoke the next interceptor or the actual tool
# - return: MCPToolCallResult

async def logging_interceptor(request, handler):
    """Interceptor that logs tool calls and responses."""
    print(f"[LOG] Tool '{request.name}' called with input: {request.args}")
    result = await handler(request)
    print(f"[LOG] Tool '{request.name}' returned result: {str(result.content)[:100]}...")
    return result

# Create MCP client with tool interceptor
# Pass interceptors as a list via the tool_interceptors parameter
mcp_client_with_logging = MultiServerMCPClient(
    {
        "langchain-docs": {
            "transport": "http",
            "url": "https://docs.langchain.com/mcp"
        }
    },
    tool_interceptors=[logging_interceptor]
)

print("MCP client configured with logging interceptor")
```

    MCP client configured with logging interceptor


### Complete Example: Agent with Logging

Let's create a complete example that uses the logging interceptor:


```python
# Get tools (interceptor will log tool calls)
tools = await mcp_client_with_logging.get_tools()

# Create agent
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are a helpful assistant that answers questions about LangChain documentation."
)

# Ask a question
question = "What is LangChain and what are its main features?"
print(f"\nQuestion: {question}\n")
print("=" * 60)

result = await agent.ainvoke({
    "messages": [HumanMessage(content=question)]
})

print("=" * 60)
print(f"\nFinal Answer:\n{result['messages'][-1].content}")
```

    
    Question: What is LangChain and what are its main features?
    
    ============================================================
    [LOG] Tool 'search_docs_by_lang_chain' called with input: {'query': 'What is LangChain and its main features'}
    [LOG] Tool 'search_docs_by_lang_chain' returned result: [TextContent(type='text', text="Title: What's new in LangChain v1\nLink: https://docs.langchain.com/...
    ============================================================
    
    Final Answer:
    LangChain is a framework designed for building applications that utilize language models (LLMs). It provides a structured way to create agents that can interact with various LLMs and tools, making it easier to develop complex applications that require natural language understanding and generation.
    
    ### Main Features of LangChain:
    
    1. **Agent Framework**: LangChain allows developers to create agents that consist of a model and a harness. The harness includes the prompt, tools, and middleware that shape the agent's behavior. This modular approach enables customization and flexibility in how agents operate.
    
    2. **Standardized Components**: LangChain provides a set of standardized components that adhere to a common interface. This includes chat models, tools, and middleware, which can be easily swapped or integrated into applications.
    
    3. **Integration with Multiple Providers**: LangChain supports various LLM providers, including OpenAI, Anthropic, and Google, allowing developers to choose the best model for their specific use case.
    
    4. **Middleware Support**: Middleware can be used to customize agent behavior by hooking into model calls, tool calls, and agent lifecycle events. This allows for features like logging, rate limiting, and content moderation.
    
    5. **Deep Agents**: LangChain offers a "batteries-included" agent option called Deep Agents, which includes advanced features like automatic context compression and subagent spawning.
    
    6. **Simplified Package Structure**: The framework has been streamlined to focus on essential building blocks for agents, with legacy functionality moved to separate packages, making it easier to manage dependencies.
    
    7. **Trace and Debugging Tools**: LangChain integrates with tools like LangSmith for tracing, debugging, and evaluating agents, helping developers monitor and improve their applications.
    
    8. **Customizability**: Developers can start with basic primitives and compose them to fit their specific use cases, allowing for a high degree of customization in how agents are built and function.
    
    For more detailed information, you can refer to the [LangChain overview](https://docs.langchain.com/oss/python/langchain/overview).


### Key Takeaways

1. **langchain-mcp-adapters** provides a seamless way to integrate MCP servers with LangChain
2. **MultiServerMCPClient** accepts a dict of server configurations — no separate parameter classes needed
3. **Stateless by default** — each `get_tools()` or `get_resources()` call handles sessions internally, no `async with` needed
4. **HTTP Transport** is used for web-based MCP servers like the LangChain documentation server
5. **Tool Interceptors** are async callables with `(request, handler) -> result` signature, passed via `tool_interceptors=`
6. **`create_react_agent`** uses the `prompt` parameter (not `state_modifier`, which is deprecated)

### Documentation References

- **LangChain Documentation MCP**: `https://docs.langchain.com/mcp`
- **Documentation Index**: `https://docs.langchain.com/llms.txt`
- **langchain-mcp-adapters**: [LangChain MCP Documentation](https://docs.langchain.com/oss/python/langchain/mcp)
- **API Reference**: [langchain-mcp-adapters Reference](https://reference.langchain.com/python/langchain_mcp_adapters/)

### Next Steps

- Explore other MCP servers from the [official MCP servers repository](https://github.com/modelcontextprotocol/servers)
- Build custom tool interceptors for your specific use cases
- Combine multiple MCP servers for comprehensive agent capabilities


```python
from langchain_core.documents.base import Blob

blob = Blob.from_data("Hello, world!")

# Read the blob as a string
print(blob.as_string())

# Read the blob as bytes
print(blob.as_bytes())


```

    Hello, world!
    b'Hello, world!'



