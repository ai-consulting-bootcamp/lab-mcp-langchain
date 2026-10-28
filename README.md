# Agents that Speak MCP Fluently

[lab_proof.md](lab_proof.md) is the evidence entry point for this submission.

The [executed notebook](Lab_agent_speak_fluently.ipynb) connects a local Filesystem
MCP server over stdio and the public LangChain Docs MCP server over HTTP. Each
server has a separate `MultiServerMCPClient`. The remote service requires no
additional token. This follows the lab's allowance for alternative MCP servers.

## Sources and environment

`sample_docs/` contains unchanged copies of the two supplied course handouts:

- `mcp_servers_local_vs_remote.md`
- `mcp_tools_resources_prompts.md`

These handouts replace the Project Atlas documents referenced by the course
notebook but absent from the supplied materials. The questions concern the
handouts themselves; no Project Atlas facts are invented.

The notebook uses Python, Node.js/npx, the packages in `requirements.txt`, and an
`OPENAI_API_KEY` loaded from the local `.env`. The default model is `gpt-4o-mini`;
`OPENAI_MODEL` can override it. No credential is embedded in the notebook.
The local npm server is pinned to `@modelcontextprotocol/server-filesystem@2.0.1`.

## Reproducible execution and evidence

The validated environment uses Python 3.11.16. `requirements.txt` records the
exact versions used by the notebook, and setup rejects mismatched packages
before making a model request. The setup output includes the active interpreter,
working directory, environment-file presence, model, and package versions.

Every full execution creates `evidence/runs/<run_id>/`. Its artifacts include:

| File within a run | Contents |
|---|---|
| `discovery.json` | Tool inventory and resource discovery |
| `tool_log.jsonl` | Raw MCP results, model-visible filtered results, selected source URLs, and call IDs |
| `agent_runs.json` | Queries, answers, corrections, validation status, and full messages |
| `langchain_guide.md` | Resource snapshot supplied to the resource-only agent |
| `resource_checks.json` | Resource URI, hash, keyword matches, and supporting excerpts |
| `direct_memory_page.md` | Page snapshot for the direct HTTP comparison |
| `direct_comparison.json` | HTTP metadata, page hash, and comparison answers |
| `manifest.json` | Run ID, Python and package versions, source hashes, and scenario counts |
| `validation.json` | Completed artifact-validation summary |

The final notebook cell uses `lab_artifacts.py` to validate the evidence set,
regenerate `lab_proof.md`, and update `evidence/latest.json`. The proof includes
resource excerpts beside the observed resource answer, and a table maps each
practical analysis question to its tool-call IDs. Excerpts use fences long enough
to preserve nested source code blocks.

`evidence/history/before-feedback/` retains earlier material and its provenance
note. Historical call IDs are scoped to those records and are excluded from the
current proof. A fresh run does not overwrite the earlier evidence directory.

Documentation search results are filtered to Python LangChain and LangGraph
pages before reaching the model. Raw results remain available for inspection.
Answer checks require exact selected source URLs and the combined query's
expected Filesystem command. These are source-scope and trace checks, not a
complete semantic verifier.

The regression tests in `tests/test_artifacts.py` cover missing call references,
changed resource snapshots, dependency drift, and nested code fences. They use
copies of the selected evidence run and never copy `.env` or call external APIs.

The notebook uses top-level `await`, as in the course examples. Saved outputs
show the observed run; remote documents and model responses can change later.
The Windows stderr adjustment follows the supplied notebook's workaround.

## Scope and limitations

The agents receive an allowlist of read tools. A client-side guard requires
directory discovery before other filesystem operations; blocked attempts remain
visible as errors in the trace. The filesystem root is restricted
to `sample_docs/`, keeping `.env` outside that root. Documentation feedback and
filesystem write tools are excluded from the agent's tool list. The underlying
Filesystem server is trusted software and still implements write operations.

Local stdio does not guarantee local model inference. Tool results supplied to
ChatOpenAI leave the machine for hosted inference. The local handouts and remote
guide are educational data. Secrets and unrelated local files are excluded.

The original assignment and grading rubric remain in
[instructions.md](instructions.md) and [rubric.md](rubric.md). Commits, pushes,
and pull request submission are separate from this local implementation.
