"""Build and validate a proof against one completed MCP lab run."""
import hashlib
import json
from pathlib import Path
import re


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def fence(text, language="text"):
    width = max([3, *[len(m[0]) + 1 for m in re.finditer(r"`{3,}", text)]])
    marker = "`" * width
    return f"{marker}{language}\n{text}\n{marker}\n"


def validate_run(project, evidence):
    project, evidence = Path(project), Path(evidence)
    manifest = read_json(evidence / "manifest.json")
    runs = read_json(evidence / "agent_runs.json")
    events = [json.loads(line) for line in (evidence / "tool_log.jsonl").read_text(encoding="utf-8").splitlines()]
    by_id = {event["id"]: event for event in events}
    assert len(by_id) == len(events), "Duplicate tool-call IDs"
    assert all(event["run_id"] == manifest["run_id"] for event in events)
    assert len(events) == manifest["tool_calls"]
    assert set(runs) == set(manifest["scenarios"])
    for name, run in runs.items():
        assert run["run_id"] == manifest["run_id"]
        assert all(call in by_id for call in run["call_ids"]), name
        selected = [by_id[call] for call in run["call_ids"]]
        assert all(event["scenario"] == name and event["run_id"] == manifest["run_id"] for event in selected)
        success = [event for event in selected if not event.get("is_error", True)]
        assert set(run["required_servers"]) <= {event["server"] for event in success}, name
        assert set(run["observed_servers"]) == {event["server"] for event in success}, name
        allowed = {url for event in selected for url in event.get("selected_source_urls", [])}
        cited = set(re.findall(r'https?://[^\s<>")]+', str(run["answer"])))
        if allowed:
            assert cited and cited <= allowed, f"Citation scope mismatch: {name}"
            assert all(re.match(r"https://docs\.langchain\.com/oss/python/(?:langchain|langgraph)/", url) for url in allowed)
        local = [event for event in success if event["server"] == "filesystem"]
        if local:
            assert local[0]["tool"] == "list_directory", name
        calls = [call for msg in run["messages"] for call in msg.get("tool_calls", [])]
        replies = {msg["tool_call_id"] for msg in run["messages"] if msg["type"] == "tool"}
        assert {call["id"] for call in calls} == replies, name
        assert not run["validation_errors"], name
    resource = read_json(evidence / "resource_checks.json")
    assert resource["sha256"] == hashlib.sha256((evidence / "langchain_guide.md").read_bytes()).hexdigest()
    assert resource["tool_calls"] == []
    assert all(resource["answer_keywords"].values())
    direct = read_json(evidence / "direct_comparison.json")
    assert direct["sha256"] == hashlib.sha256((evidence / "direct_memory_page.md").read_bytes()).hexdigest()
    for filename, digest in manifest["files"].items():
        assert hashlib.sha256((project / filename).read_bytes()).hexdigest() == digest
    requirements = dict(line.strip().split("==") for line in (project / "requirements.txt").read_text().splitlines() if line.strip())
    assert requirements == manifest["packages"], "Requirements differ from the recorded environment"
    return {"run_id": manifest["run_id"], "scenarios": len(runs), "tool_events": len(events), "status": "passed"}


def write_proof(project, evidence):
    project, evidence = Path(project), Path(evidence)
    validation = validate_run(project, evidence)
    manifest = read_json(evidence / "manifest.json")
    runs = read_json(evidence / "agent_runs.json")
    checks = read_json(evidence / "resource_checks.json")
    events = [json.loads(line) for line in (evidence / "tool_log.jsonl").read_text(encoding="utf-8").splitlines()]
    by_id = {event["id"]: event for event in events}
    prefix = evidence.relative_to(project).as_posix()
    main = runs["combined"]
    sections = [f"""# Lab Proof: Agents that Speak MCP Fluently

## 1. Workflow and run

The [executed notebook](Lab_agent_speak_fluently.ipynb) connects a local Filesystem
MCP server over stdio and the public LangChain Docs MCP server over HTTP, using
one client per server. The local data consists of unchanged copies of the two
supplied course handouts. They replace the unavailable Project Atlas documents.
LangChain Docs is the remote alternative permitted by the lab; it needs no token.

This proof describes run `{manifest['run_id']}` only. Its artifacts are in
[{prefix}]({prefix}/manifest.json). Historical material is separately labeled in
`evidence/history/` and is excluded from the current trace.

The run used Python {manifest['python']} and model `{manifest['model']}`. Installed
package versions exactly match [requirements.txt](requirements.txt). Setup
records the interpreter, working directory, credential availability, and versions.

## 2. Query

> {main['query']}

## 3. Tool evidence

The following call IDs belong to this run. Full raw server responses and the
filtered content actually delivered to the model are preserved in
[tool_log.jsonl]({prefix}/tool_log.jsonl). Model messages and the final answers are
in [agent_runs.json]({prefix}/agent_runs.json).

"""]
    for call_id in main["call_ids"]:
        event = by_id[call_id]
        result = event.get("delivered_result", event.get("result", {}))
        text = "\n".join(block.get("text", "") for block in result.get("content", []))
        if event["server"] == "filesystem" and "read" in event["tool"]:
            pattern = r'"filesystem":\s*\{.*?\n\}'
            match = re.search(pattern, text, re.S)
            excerpt = match[0] if match else text[:1400]
        else:
            excerpt = text[:2200]
        sections += [f"### {call_id}: {event['server']} / {event['tool']}\n\n",
                     fence(json.dumps(event["arguments"], indent=2), "json"),
                     f"\nError status: `{event.get('is_error')}`. Result excerpt:\n\n",
                     fence(excerpt), "\n"]
    local = [call for call in main["call_ids"] if by_id[call]["server"] == "filesystem" and "read" in by_id[call]["tool"] and not by_id[call].get("is_error")]
    remote = [call for call in main["call_ids"] if by_id[call]["server"] == "langchain-docs" and not by_id[call].get("is_error")]
    sections += ["## 4. Observed final answer\n\n", str(main["answer"]), f"""

## 5. Claim trace

| Claim | Supporting evidence |
|---|---|
| The handout uses npx and the Filesystem package with a document directory | {', '.join(local)}; exact local configuration excerpt above |
| stdio fits a locally started MCP server | {', '.join(remote)}; selected Python LangChain documentation |
| Local server execution does not guarantee local model inference | Inference from this notebook's data flow: tool results are passed to the configured hosted ChatOpenAI model |

Only Python LangChain/LangGraph search results are delivered to the documentation
agents. Other products and language variants remain in the raw log, with the
selected URLs recorded separately. Final documentation citations must match
selected source URLs. These checks verify source scope and trace integrity;
they do not establish that every generated sentence is semantically correct.

## 6. Resource context

The application read `{checks['uri']}` and provided its snapshot to an agent with
`tools=[]`. It supported this question:

> {runs['resource']['query']}

Observed answer:

{runs['resource']['answer']}

Supporting excerpts from [langchain_guide.md]({prefix}/langchain_guide.md):

"""]
    for excerpt in checks["supporting_excerpts"]:
        sections += [f"Line {excerpt['line']}:\n\n", "> " + excerpt["text"] + "\n\n"]
    sections += [f"""The snapshot SHA-256 is `{checks['sha256']}`. The resource agent made no
tool calls. [resource_checks.json]({prefix}/resource_checks.json) records the URI,
hash, keyword checks, and source lines. Keyword matches aid review but are not a
general proof of semantic grounding.

## 7. Failure and limitations

Missing-information query:

> {runs['missing_price']['query']}

Observed answer:

> {runs['missing_price']['answer']}

Evidence: {', '.join(runs['missing_price']['call_ids'])}. The lack of a price in
the supplied sources does not establish that the service is free.

The historical review in
[grounding_review.json](evidence/history/before-feedback/grounding_review.json)
retains an earlier answer that confused `uvx` and `npx`. Its call identifiers are
historical and are not references into this run. The current combined scenario
checks that the expected Filesystem command and package appear in the answer.

Directory-first middleware and a client-side guard restrict the order of file
operations. The agent receives only read tools, although the underlying trusted
server still implements write operations. A successful call alone does not
guarantee a correct interpretation, and a matching URL alone does not validate
every associated claim. Hosted inference still receives the supplied context.

## 8. Practical document analysis

| Scenario and question | Call IDs | Observed result |
|---|---|---|
"""]
    for name, run in runs.items():
        if name.startswith("document_analysis_"):
            answer = str(run["answer"]).replace("\n", " ").replace("|", "\\|")
            sections.append(f"| {run['query']} | {', '.join(run['call_ids'])} | {answer} |\n")
    sections += [f"""
## 9. MCP and direct HTTP comparison

The same memory question was answered through MCP search and through a direct
request to one known documentation page. The direct response status, page hash,
and both answers are in [direct_comparison.json]({prefix}/direct_comparison.json).

| Aspect | MCP | Direct HTTP |
|---|---|---|
| Setup | Server configuration, discovery, adapter, interceptor | Known page URL and HTTP client |
| Flexibility | Agent chooses queries through a standardized tool interface | Model sees the page supplied by the application |
| Maintenance | Client depends on server tool schemas and service availability | Client handles URLs, response format, and HTTP errors |
| Evidence | Full tool results, selected source URLs, message trace | Page snapshot, HTTP status, hash, and model answer |

The table reflects the retained MCP traces and direct comparison artifacts.
Direct HTTP fits a single known page; MCP fits workflows that need discovery or
reusable integrations across compatible frameworks. This is not a latency
benchmark: retrieval content and the number of model calls can differ.

## 10. Verification

The completed run contains {validation['scenarios']} scenarios and
{validation['tool_events']} tool events. Each referenced call exists in this run;
required server evidence, message/tool-call pairing, source and snapshot hashes,
dependency versions, and final citation scope passed validation.
"""]
    proof = "".join(sections)
    references = set(re.findall(r"\bcall-\d+\b", proof))
    assert references <= set(by_id), "Proof references missing calls"
    (project / "lab_proof.md").write_text(proof, encoding="utf-8")
    (evidence / "validation.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    (project / "evidence" / "latest.json").write_text(json.dumps({"run_id": manifest["run_id"], "directory": prefix}, indent=2), encoding="utf-8")
    return validation
