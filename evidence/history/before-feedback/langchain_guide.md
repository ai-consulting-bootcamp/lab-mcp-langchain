---
name: langchain
description: Use when building AI agents, integrating language models with
  tools, orchestrating multi-step workflows, or deploying production agent
  systems. Reach for this skill when working with LangChain, LangGraph, Deep
  Agents, or LangSmith for agent development, testing, and deployment.
metadata:
  mintlify-proj: langchain
  version: "1.0"
---

# LangChain Skill

## Product summary

LangChain is an open-source framework for building AI agents and LLM applications. It provides three core layers: **LangChain** (high-level agent harness with `create_agent`), **LangGraph** (low-level orchestration runtime for stateful workflows), and **Deep Agents** (batteries-included harness with planning, filesystem, subagents, and memory). Use LangChain's `create_agent` for customizable agents, LangGraph for deterministic + agentic workflows, or Deep Agents for complex multi-step tasks. Deploy with LangSmith Cloud for managed infrastructure or self-host with LangSmith Deployment. Trace and debug with LangSmith observability.

**Key files and commands:**
- `create_agent()` - Main agent factory (Python/JS)
- `@tool` decorator - Define tools for agents
- `StateGraph` - LangGraph graph construction
- `langgraph deploy` - Deploy to LangSmith Cloud
- Environment: `LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY`
- Primary docs: https://docs.langchain.com

## When to use

Reach for this skill when:
- **Building agents**: Creating AI agents that call tools in a loop until tasks complete
- **Defining tools**: Writing custom functions, APIs, or MCP servers for agents to invoke
- **Orchestrating workflows**: Mixing deterministic logic with LLM-driven steps in a single graph
- **Handling state**: Managing conversation history, custom fields, and persistence across runs
- **Deploying production agents**: Setting up stateful, long-running agents with checkpointing and recovery
- **Testing and evaluation**: Running evals, benchmarking versions, or catching regressions
- **Debugging agent behavior**: Tracing tool calls, state transitions, and latency with LangSmith
- **Multi-agent systems**: Building subagents, delegating tasks, or routing between specialized agents
- **Context management**: Loading skills, memory, and domain knowledge progressively during execution

## Quick reference

### Agent creation

| Task | Command |
|------|---------|
| Create basic agent | `create_agent(model="openai:gpt-5.5", tools=[...], system_prompt="...")` |
| Invoke agent | `agent.invoke({"messages": [{"role": "user", "content": "..."}]}, config={"configurable": {"thread_id": "..."}})` |
| Stream agent output | `agent.stream({"messages": [...]}, config={"configurable": {"thread_id": "..."}})` |
| Access runtime context | `runtime.state`, `runtime.context`, `runtime.store` in tool signature |

### Tool definition

| Pattern | Usage |
|---------|-------|
| `@tool` decorator | `@tool` def my_tool(arg: str) -> str: """Docstring."""` |
| Custom name/description | `@tool("custom_name", description="...")` |
| Pydantic schema | `@tool(args_schema=MyModel)` |
| Access state in tool | `def my_tool(arg: str, runtime: ToolRuntime) -> str:` |
| Return structured data | Return dict/object for model to parse |
| Return Command | `return Command(update={"field": value}, graph=None)` |

### Middleware

| Type | Hook | Use case |
|------|------|----------|
| Node-style | `before_model`, `after_model` | Logging, validation, state updates |
| Wrap-style | `wrap_model_call`, `wrap_tool_call` | Retry, fallback, filtering, caching |
| Built-in | `ModelRetryMiddleware`, `PIIMiddleware`, `SummarizationMiddleware` | Common patterns pre-built |

### LangGraph basics

| Concept | Pattern |
|---------|---------|
| Define state | `class State(TypedDict): messages: list[BaseMessage]` |
| Create graph | `graph = StateGraph(State)` |
| Add node | `graph.add_node("node_name", function)` |
| Add edge | `graph.add_edge(START, "node_name")` or `graph.add_edge("node_name", END)` |
| Compile | `compiled = graph.compile()` |
| Invoke | `compiled.invoke({"messages": [...]})` |

### Deployment

| Target | Command |
|--------|---------|
| LangSmith Cloud (Serverless) | `langgraph deploy` |
| LangSmith Cloud (Dedicated) | `langgraph deploy --deployment-type dedicated` |
| Local testing | `langgraph dev` |
| Self-hosted | Push to GitHub + configure LangSmith control plane |

## Decision guidance

### When to use LangChain vs. LangGraph vs. Deep Agents

| Scenario | Use | Why |
|----------|-----|-----|
| Simple agent with custom tools | **LangChain** `create_agent` | High-level harness, minimal config, integrations built-in |
| Complex workflow mixing logic + LLM | **LangGraph** | Low-level control, deterministic steps, human-in-the-loop |
| Multi-step research/coding task | **Deep Agents** | Planning, filesystem, subagents, memory included |
| Production without infrastructure | **Managed Deep Agents** | Fully managed runtime, no server setup needed |

### When to use different tool return types

| Return type | Use when |
|-------------|----------|
| String | Result is human-readable text the model should reason over |
| Object/dict | Result is structured data with fields the model should inspect |
| Command | Tool needs to update agent state (preferences, counters, memory) |
| return_direct=True | Tool output is final answer; skip model processing |
| Multimodal content | Tool returns images, audio, or mixed media |

### When to use middleware vs. custom logic

| Approach | Use when |
|----------|----------|
| **Middleware** | Concern applies across all tool calls or model invocations (retry, PII, summarization) |
| **Tool logic** | Concern is specific to one tool's execution |
| **System prompt** | Concern is guidance for the model's reasoning |

## Workflow

### Building an agent

1. **Define tools**: Write `@tool` functions or import from MCP servers
2. **Choose model**: Pick provider and model string (`"openai:gpt-5.5"`, `"claude-sonnet-4-6"`, etc.)
3. **Create agent**: Call `create_agent(model=..., tools=..., system_prompt=...)`
4. **Add middleware**: Pass `middleware=[...]` for retry, summarization, PII, or custom logic
5. **Invoke**: Call `agent.invoke({"messages": [...]}, config={"configurable": {"thread_id": "..."}})` with thread_id for persistence
6. **Stream**: Use `agent.stream()` to surface progress updates
7. **Trace**: Set `LANGSMITH_TRACING=true` to debug in LangSmith

### Building a LangGraph workflow

1. **Define state**: Create `TypedDict` with `messages` and custom fields
2. **Write nodes**: Functions that read state and return updates
3. **Build graph**: `StateGraph(State)` → add nodes → add edges
4. **Add tools**: Use `ToolNode` for tool execution or call tools directly in nodes
5. **Compile**: `graph.compile(checkpointer=...)` for persistence
6. **Invoke**: Pass state dict with `thread_id` for resumable execution
7. **Debug**: Visualize with `graph.get_graph().draw_mermaid_png()`

### Testing and evaluation

1. **Create dataset**: Curate examples with inputs and reference outputs
2. **Define evaluator**: LLM-as-judge, code-based, or trajectory matching
3. **Run offline eval**: Test on dataset before deployment
4. **Run online eval**: Monitor real traffic in production
5. **Compare versions**: Benchmark new agent against baseline
6. **Iterate**: Update prompts, tools, or middleware based on results

### Deploying to production

1. **Test locally**: `langgraph dev` to verify agent runs
2. **Push to GitHub**: Commit code to connected repository
3. **Deploy**: `langgraph deploy` (Serverless default) or `--deployment-type dedicated`
4. **Configure**: Set environment variables, API keys, checkpointer
5. **Monitor**: View traces, metrics, and errors in LangSmith
6. **Scale**: Adjust deployment size or type as load changes

## Common gotchas

- **Missing thread_id**: Agent won't persist conversation history without `thread_id` in config. Always pass `config={"configurable": {"thread_id": "..."}}` for multi-turn conversations.
- **Tool schema not inferred**: Type hints are required on tool arguments; without them, the model won't see the tool's input schema.
- **Reserved parameter names**: Don't use `config` or `runtime` as tool argument names; they're reserved for internal use. Use `ToolRuntime` parameter instead.
- **State not updated by tools**: Returning a string from a tool doesn't update agent state. Use `Command` with `update=` to modify state fields.
- **Middleware order matters**: Place critical middleware (retry, auth) early in the list; they execute in order.
- **Context vs. thread_id confusion**: `thread_id` scopes conversation history; `context` carries per-run data (user ID, API keys). Pass both for full context.
- **Model doesn't see runtime parameter**: `runtime: ToolRuntime` is injected automatically and hidden from the model's tool schema.
- **Checkpointer required for persistence**: Without a checkpointer, agent state is lost between invocations. Use `InMemorySaver()` locally or configure persistent store in production.
- **Tool call ID mismatch**: When returning `Command` with state updates, include a `ToolMessage` with matching `tool_call_id` or `ToolNode` raises `ValueError`.
- **Parallel tool calls and reducers**: If model calls multiple tools in one step, use reducers on state fields that may be updated concurrently.
- **MCP server lifecycle**: Keep MCP adapter open while agent can call its tools; call `await adapter.close()` when done.
- **Streaming requires LangGraph context**: `runtime.stream_writer` only works inside LangGraph execution; won't work in standalone tool testing.

## Verification checklist

Before submitting agent code:

- [ ] All tools have type hints on arguments
- [ ] Tool docstrings are clear and describe when to use them
- [ ] Agent is created with `create_agent()` or `StateGraph` compiled
- [ ] `thread_id` is passed in config for multi-turn conversations
- [ ] Checkpointer is configured (local or production)
- [ ] Middleware is ordered correctly (critical concerns first)
- [ ] Tools that update state return `Command` with `ToolMessage`
- [ ] `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` are set for debugging
- [ ] Agent is tested locally with `langgraph dev` before deployment
- [ ] Evaluation dataset exists and baseline metrics are recorded
- [ ] Error handling is in place (retry middleware, fallbacks)
- [ ] Tool return types match expected model behavior (string vs. object vs. Command)
- [ ] Custom state fields are defined in `state_schema` if needed
- [ ] MCP servers are properly closed after use
- [ ] Deployment target (Serverless vs. Dedicated) matches latency requirements

## Resources

- **Comprehensive navigation**: https://docs.langchain.com/llms.txt
- **LangChain agents**: https://docs.langchain.com/oss/python/langchain/agents
- **LangGraph overview**: https://docs.langchain.com/oss/python/langgraph/overview
- **Deep Agents**: https://docs.langchain.com/oss/python/deepagents/overview
- **LangSmith observability**: https://docs.langchain.com/langsmith/observability
- **LangSmith deployment**: https://docs.langchain.com/langsmith/deployment

---

> For additional documentation and navigation, see: https://docs.langchain.com/llms.txt