# Lab Proof: Agents that Speak MCP Fluently

## 1. What I built

The implementation is in [`mcp_langchain.ipynb`](./mcp_langchain.ipynb). It connects LangChain to the remote LangChain Documentation MCP server over HTTP, discovers its tools and resource, and uses both in a LangChain agent workflow.

The server exposed three tools:

- `search_docs_by_lang_chain`
- `query_docs_filesystem_docs_by_lang_chain`
- `submit_feedback`

It also exposed one read-only resource, which was read with `.as_string()` and supplied as context to an agent.

## 2. Query

> Using the official LangChain documentation, explain how to create an agent with tools, and identify the configuration value used to keep separate conversations apart.

The complete agent was created with the discovered MCP tools and the fetched resource text, then invoked with `await complete_agent.ainvoke(...)`.

## 3. Evidence

The agent made these MCP tool calls:

```text
called: search_docs_by_lang_chain with {'query': 'create an agent with tools'}
called: search_docs_by_lang_chain with {'query': 'configuration value to keep separate conversations apart'}
```

The server returned documentation evidence including:

```text
Title: Use MCP tools in an agent
Link: https://docs.langchain.com/oss/python/langchain/mcp/tools#use-mcp-tools-in-an-agent
Content: ... give the returned tools to create_agent ...
```

and:

```text
Title: Combine with thread isolation
Link: https://docs.langchain.com/langsmith/store-auth#combine-with-thread-isolation
Content: ... thread isolation ...
```

The resource evidence was also checked independently. The resource contained the term `thread_id`:

```text
Evidence check: 'thread_id' appears in the resource: True
```

## 4. Final answer

The agent answered that LangChain creates an agent with `create_agent()`, passing a model and a list of tools. It also identified `thread_id` as the configuration value used to keep separate conversations apart, with an example using:

```python
config={"configurable": {"thread_id": "user-123"}}
```

## 5. Trace

- The `create_agent()` claim is supported by the `search_docs_by_lang_chain` result titled **“Use MCP tools in an agent”**.
- The `thread_id` claim is supported by the `search_docs_by_lang_chain` result titled **“Combine with thread isolation”** and by the independently read MCP resource.
- The tool calls were made by the LangChain agent; the resource was fetched by the application before the resource-grounded agent ran.

## 6. Failure or limitation

The MCP server and its documentation are remote and can change. Also, the agent is instructed to use the tools, but the prompt is not a hard guarantee: a model could still produce an unsupported answer if a tool call fails or if the returned documentation is incomplete. A production version should add error handling, stronger output validation, and a persisted checkpointer when conversation memory is required.
