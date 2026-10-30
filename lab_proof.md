
# Lab Proof: Agents That Speak MCP Fluently

## 1. What I Built

I connected a local filesystem MCP server to a LangChain agent using Python and `langchain-mcp-adapters`.

The agent uses OpenAI's `gpt-4o-mini` model and can access documents through MCP filesystem tools.

I created a sample company AI policy document and tested whether the agent could read it, answer a question, and identify the source of its answer.

**Implementation:** [mcp_test.py](mcp_test.py)

**Source document:** [sample_policy.txt](data/sample_policy.txt)

## 2. MCP Server and Tools

- **MCP server:** `@modelcontextprotocol/server-filesystem`
- **Connection method:** `stdio`
- **MCP client:** `MultiServerMCPClient`
- **Framework:** LangChain
- **Tools discovered:** 14
- **Tool used for the test:** `read_text_file`

## 3. Test Query

**Question:**

According to sample_policy.txt, who approves new AI tools?

**Purpose:**

To verify that the LangChain agent can use an MCP filesystem tool to retrieve information from a document and answer a question using that information.

## 4. MCP Tool Evidence

The agent executed the following MCP tool call:

**Tool:** `read_text_file`

**Arguments:**
```python
{"path": "sample_policy.txt"}
```

**Source document:** `data/sample_policy.txt`

**Retrieved evidence (Section 5):**

> The IT department is responsible for approving new AI tools.

The tool call was recorded in the agent's execution output, and the document content was independently retrieved through the MCP filesystem server.

## 5. Final Agent Answer

**Question:**

According to sample_policy.txt, who approves new AI tools?

**Actual agent output:**

> According to the "sample_policy.txt," the IT department is responsible for approving new AI tools.

## 6. Grounding Verification

I verified that the agent's answer was supported by the source document.

**Evidence trace:**

1. The user asked who approves new AI tools.
2. The LangChain agent called the MCP tool `read_text_file`.
3. The tool was called with the argument `{"path": "sample_policy.txt"}`.
4. Section 5 of the document states: "The IT department is responsible for approving new AI tools."
5. The agent answered that the IT department approves new AI tools.

**Verification result:** The answer matches the retrieved document and is supported by the MCP tool evidence.

This demonstrates that the agent used an MCP filesystem tool to retrieve information before generating its final answer.

## 7. Failure or Limitation

One limitation of this MCP-enabled agent is that it may generate a plausible but unsupported answer when the requested information is missing from the source document.

For example, the sample policy identifies who approves new AI tools in the fictional company, but it does not establish who approves AI tools in other organisations.

A potential failure would occur if the agent answered such a question using general knowledge instead of acknowledging that the available document does not contain the information.

**Mitigation:** The agent's system prompt instructs it to use document evidence and say "I do not know" when the information is unavailable.

**Remaining risk:** Prompt instructions alone cannot guarantee that every answer is grounded. Tool calls and source content must still be inspected.

This is a potential failure mode, not a failure observed during the successful test.

## 8. MCP Resources Investigation

I attempted to retrieve MCP resources using the LangChain MCP adapter:

```python
resources = await client.get_resources(server_name="filesystem")
```

The request failed with the following underlying error:

```text
mcp.shared.exceptions.McpError: Method not found
```

**Finding:** The filesystem MCP server supports MCP tools but does not implement the resource-listing method required by this request.

The agent can still retrieve document content through the `read_text_file` MCP tool.

**Limitation:** I could not demonstrate reading MCP resources with this server. A resource-capable MCP server would be needed to complete that part of the exercise.

This limitation did not prevent the LangChain agent from successfully answering the test question using MCP tools.

### 8.1 Successful MCP Resource Retrieval

To overcome the filesystem server's resource limitation, I connected a second MCP server: the LangChain Documentation MCP server.

**Server URL:** `https://docs.langchain.com/mcp`

**Connection method:** HTTP

**Tools discovered:** 3

**Resources retrieved:** 1

**Python implementation:**

```python
resources = await client.get_resources(server_name="langchain-docs")
resource_context = "\n\n".join(
    resource.as_string() for resource in resources
)
```

**Test question:**

According to the provided LangChain documentation, when should I use LangGraph instead of LangChain?

**Agent result:**

The agent explained that LangGraph is appropriate for complex, multi-step workflows involving deterministic and agentic logic, particularly when stateful orchestration and fine-grained workflow control are required.

**Verification:** The agent answered using documentation retrieved as an MCP resource and supplied through its system prompt. No additional tool call was required during this question.

**Conclusion:** MCP resource retrieval and resource-based agent context were successfully demonstrated.

## 9. GitHub MCP Integration and Repository Inspection

I integrated the official GitHub MCP server into my LangChain application to inspect public GitHub repositories.

**MCP server:** GitHub MCP Server  
**Connection method:** HTTP  
**Endpoint:** `https://api.githubcopilot.com/mcp/`  
**Authentication:** GitHub Personal Access Token stored in `.env`  
**Access:** Public repositories, read-only  
**Tools discovered:** 28

### Test Question

Using GitHub MCP tools, inspect the public repository psf/requests. Read its README.md and briefly explain what the project does. Mention the repository name.

### MCP Tool Execution

The agent called the GitHub MCP tool:

**Tool:** `get_file_contents`

**Arguments:**

```json
{
  "owner": "psf",
  "repo": "requests",
  "path": "README.md"
}
```

### Agent Response

The agent identified **Requests** as a Python HTTP library that simplifies sending HTTP requests.

It explained that the library supports features such as connection pooling, authentication, and automatic content decoding.

**Repository identified:** `psf/requests`

### Verification

The terminal output confirmed that the agent called `get_file_contents` with the correct repository owner, repository name, and file path.

This demonstrates that the agent retrieved repository content using GitHub MCP rather than relying solely on its existing knowledge.

### Conclusion

The GitHub MCP integration was successful.

The application now connects to three MCP servers:

1. Filesystem MCP — 14 tools
2. LangChain Documentation MCP — 3 tools
3. GitHub MCP — 28 tools

**Total tools discovered:** 45

The agent currently receives the Filesystem and GitHub tools, while LangChain documentation is supplied as retrieved MCP resource context.
