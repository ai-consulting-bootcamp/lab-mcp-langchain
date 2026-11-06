# MCP + LangChain Lab Proof

## Objective

Demonstrate a LangChain agent retrieving evidence through MCP before answering factual questions, and verify one answer against its source.

## Implementation

`mcp_langchain.py` launches a local stdio MCP server that reads [source_facts.md](./source_facts.md). The server exposes the `retrieve_source_evidence(question)` tool and the `lab://northstar/facts` resource. `MultiServerMCPClient` discovers the tool; an MCP session lists and reads the resource; LangChain's `create_agent` runs `ChatOpenAI` with the MCP tool and instructions to retrieve evidence before answering.

The client uses `get_tools()` and a session to access the server:

```python
tools = await client.get_tools()
async with client.session("northstar") as session:
    resource_listing = await session.list_resources()
    resource_result = await session.read_resource(RESOURCE_URI)
agent = create_agent(model=ChatOpenAI(...), tools=tools, system_prompt=...)
```

The workflow ran in the existing `bootcamp-env` with `langchain` 1.4.6, `langchain-openai` 1.7.3, `langchain-mcp-adapters` 0.3.2, `mcp` 1.30.0, and `python-dotenv` 1.2.4. The API key was loaded from the ignored `.env` file; its value was not printed.

## Test Query

Grounded query:

> According to the source, what city is the Northstar Scout test facility in, when did its field trial begin, and what battery runtime did it record?

Missing-fact query:

> What was the maximum altitude reached by the Northstar Scout?

## MCP Evidence

The server reported the tool `retrieve_source_evidence` and resource `lab://northstar/facts`. The resource was read successfully. The agent then made these tool calls for the grounded query:

```text
retrieve_source_evidence({"question": "What city is the Northstar Scout test facility in?"})
retrieve_source_evidence({"question": "When did the field trial for the Northstar Scout begin?"})
retrieve_source_evidence({"question": "What battery runtime did the Northstar Scout record?"})
```

Each call returned the same source text:

```text
# Northstar Robotics field trial facts

- The Northstar Scout test facility is in Lyon, France.
- The Northstar Scout field trial began on 12 April 2025.
- During the trial, the Scout recorded a battery runtime of 18.5 hours in a controlled chamber at 20 degrees Celsius.
- The source does not report the maximum altitude reached.
```

For the missing-fact query, the agent called `retrieve_source_evidence` with `{"question": "What was the maximum altitude reached by the Northstar Scout?"}` and received the same source text.

The pasted run's top-level `resource_content` field spells the final line as “doesnot” (without a space). The on-disk source file and all tool responses spell it “does not.”

## Final Output

Grounded query response:

> The Northstar Scout test facility is located in Lyon, France. The field trial for the Northstar Scout began on 12 April 2025, and it recorded a battery runtime of 18.5 hours in a controlled chamber at 20 degrees Celsius. [source_facts.md]

Missing-fact query response:

> The source does not provide that information.

## Grounding Verification

The source states that the test facility is in Lyon, the trial began on 12 April 2025, and the recorded battery runtime was 18.5 hours in a chamber at 20 degrees Celsius. Those statements support each claim in the grounded response. For the second query, the source explicitly says it does not report the maximum altitude, matching the agent's abstention.

## Limitation

The retrieval tool returns the entire fact sheet for every question, so the three-part question causes three redundant tool calls. The agent is instructed to answer only from retrieved text, but the implementation does not independently validate each final claim against the tool response. The resource-output spelling discrepancy noted above also means that exact resource text should be checked against the source file when reviewing a run.

## Conclusion

The run demonstrated local MCP connection, tool discovery and execution, resource listing and reading, and a LangChain agent response supported by retrieved source text. The missing-fact check also returned the source-grounded abstention.
