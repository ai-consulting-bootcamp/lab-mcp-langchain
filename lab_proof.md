# LAB | Agents that speak MCP fluently — Grounding Proof

## 1. Goal and scope

This project connects a local MCP server to LangChain over stdio. The server exposes a deterministic, read-only search tool and a read-only resource. The search corpus contains four curated paraphrases attributed to course handouts; it is not full-document retrieval.

**Entry points:** `mcp_server.py`, `mcp_langchain.py`, and `evidence.py`. Offline tests: `test_retrieval.py`.

## 2. User query

> Who controls MCP resources, and does reading one change data?

## 3. Implemented workflow

1. `mcp_langchain.py` loads `.env` from the project directory and configures `MultiServerMCPClient` to launch `mcp_server.py` with stdio.
2. `client.get_tools()` discovers `search_course_notes` and adapts it to a LangChain tool.
3. The program invokes that MCP tool with the exact user query and prints its response.
4. A raw MCP session lists resources and reads `course://mcp/overview`. This resource read is not automatically included in the agent's context.
5. With a configured `OPENAI_API_KEY`, the program constructs a LangChain agent with `ChatOpenAI`, passes the discovered MCP tools to it, invokes it with the user query, and prints the agent messages, tool calls, tool responses, and final answer.

## 4. Captured execution evidence

[`live_trace.txt`](./live_trace.txt) is the transcript captured from the authorized actual execution of `mcp_langchain.py`; it is not a transcript supplied by the user. It shows:

- MCP stdio server startup and `ListToolsRequest` / `CallToolRequest`.
- Discovery of `search_course_notes`.
- Invocation of that tool with the exact query and its N2 result.
- Discovery and successful read of `course://mcp/overview`.
- The agent's `HumanMessage`, `AIMessage` tool calls to `search_course_notes`, two `ToolMessage` responses containing N2, and its final `AIMessage`.
- `FINAL_ANSWER` printed by the application.

The tool response in the trace identifies N2, section “Resources: providing information”:

> A resource is information the application reads from the server and hands to the LLM as context. Reading a resource never creates, changes or deletes anything.

The retrieved record is a curated paraphrase attributed to `mcp_tools_resources_prompts.md`, not a verbatim quotation. I checked it against the local handout copy in the parent `Downloads` folder (outside this project): the “Resources: providing information” section states that resources are controlled by the application (line 113), the application decides what the LLM sees (line 173), and reading never creates, changes, or deletes anything (line 174). The paraphrase is consistent with that source; the handout itself is not part of this project submission.

## 5. Grounded answer status

**Actual agent-generated final answer from `live_trace.txt`:**

> MCP resources are controlled by the application, which reads information from the server and provides it to the LLM (Language Model) as context. Importantly, reading a resource does not create, change, or delete any data (Record ID: N2, source: mcp_tools_resources_prompts.md).

The agent received the exact user query, called `search_course_notes` twice (once for resource control and once for read side effects), and both tool responses returned N2. N2 directly says the application reads resource information and hands it to the LLM as context, and that reading never creates, changes, or deletes anything. The original course handout explicitly says “Controlled by: the application” and “The application decides what to read and what the LLM gets to see.” The answer's expansion “Language Model” is a harmless explanation of “LLM”; no other factual claim is unsupported by N2 and the cited handout. The record ID and source reference are real and match the tool result.

## 6. Verification results

- **PASS:** `python test_retrieval.py` returns N2 as the top match for the exact query.
- **PASS:** The `quantum banana` negative test returns no matches.
- **PASS:** Python syntax compilation and imports of the configured packages.
- **PASS:** Local MCP stdio startup, tool discovery, invocation, resource discovery, and resource reading; see `live_trace.txt`.
- **PASS:** N2 checked against the locally available course handout copy; the relevant source lines are 108, 113, and 172–174.
- **PASS:** Authorized single LangChain LLM agent execution; the agent itself called the MCP search tool twice and returned a final answer citing N2. See `live_trace.txt`.

## 7. Failure mode and grounding limitation

The retriever uses token overlap over only four curated records. A semantically relevant query can therefore miss evidence, and a returned record may not support every claim the model makes. A model could also fabricate an evidence ID. The unsupported-query test covers one empty-result case, but there is no runtime citation validator. The agent should abstain when the returned evidence is missing or insufficient, and citations should be checked against the actual tool response.

## 8. Reproduction

From the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
if [ ! -f .env ]; then cp .env.example .env; fi
# Set your own API key in .env locally. Never put a real key in .env.example.
python test_retrieval.py
python mcp_langchain.py 2>&1 | tee live_trace.txt
```

The first command makes an OpenAI API request if `.env` contains a non-empty `OPENAI_API_KEY`. To verify the MCP server, tool, and resource without an API request, run:

```bash
OPENAI_API_KEY='' python mcp_langchain.py | tee live_trace.txt
```

Only label a trace as an agent run if it contains `AGENT_TRACE` and `FINAL_ANSWER`. Never capture or publish API keys or tokens.

## 9. Reviewer checklist

**Three grounding risks:** (1) fabricated evidence ID, (2) relevant retrieval that does not support all claims, (3) assuming the separately read resource is in the agent context.

**Two trace checks:** (1) confirm the agent called the MCP search tool and inspect its returned records, (2) compare each final-answer claim and citation to those records.

**One simplification:** one local server, one search tool, one resource, and one central query.

## 10. Submission status

The offline tests, MCP protocol, resource access, N2/source comparison, and authorized agent run are verified. The project includes this proof, source, tests, dependencies, and both offline and live traces. Keep `.env`, `.venv/`, `__pycache__/`, and `*.pyc` out of the submission; `.gitignore` contains these exclusions. The expected submission files contain no API-key-shaped strings, but this workspace is not a Git repository, so tracked/staged submission contents could not be inspected. For GitHub submission, fork the Ironhack lab repository to your GitHub account, clone that fork, copy these existing project files into the matching lab directory, verify `git status` excludes `.env` and `.venv/`, then commit and push to your fork and open the required pull request. Do not initialize a new unrelated repository.
