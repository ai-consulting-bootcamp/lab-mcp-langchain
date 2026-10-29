# Lab Proof: Agents that Speak MCP Fluently (three servers)

**Ayhan Demir** · Ironhack AI Consulting & Integration Bootcamp · Module 4, Week 4 · Run date: 2026-10-28

## 1. What I built

An agent that helps a consultant **shortlist agent frameworks for a client RFP**: LangGraph vs the OpenAI Agents SDK. It must answer with facts from sources, not from memory. Code: [`mcp_langchain.ipynb`](mcp_langchain.ipynb) (Steps 1 to 6 of the brief; optional Steps 7 and 8 not done).

All three servers are connected from Step 2, each through its own client with the same  interceptor. So Step 6 uses **tools and the resource** together, as the brief's Step 6 asks ("Load tools and resources"). Each server has **one job**, so each fact has one clear source:

| MCP server | Transport | Client | Its one job |
|---|---|---|---|
| **Fetch** (`mcp-server-fetch@2026.10.24`, runs on my Mac) | stdio, started with `uvx` | `fetch_client`, 1 tool | Read the OpenAI Agents SDK docs page |
| **GitHub** (official, `https://api.githubcopilot.com/mcp/`) | http, token in the headers, toolsets `repos,issues`, read-only | `github_client`, 19 tools | License (`LICENSE` file) and latest release of each repo |
| **LangChain Docs** (`https://docs.langchain.com/mcp`) | http, no token | `docs_client`, 2 tools + 1 resource | Docs search: what LangGraph is for. Resource: the skill guide (11,252 characters), when to choose LangGraph |



### Process map (end to end)

From setup to this proof, with the results of my run. Boxes are notebook steps and their results; diamonds are checks.

```mermaid
flowchart TB
    subgraph SETUP["🔑 Step 1 · Setup"]
        direction LR
        ENV["📄 .env, git-ignored<br/>OpenAI key + GitHub token"] --> UVX["⚙️ uvx<br/>starts local servers"]
        UVX --> LLM["🧠 gpt-4o-mini<br/>temperature 0"]
        LLM --> LOG["🪵 log_tool_calls<br/>prints a LOG line<br/>for every tool call"]
    end

    subgraph CONNECT["🔌 Steps 2-3 · Three clients, one per server, load tools"]
        direction LR
        FC["💻 fetch_client<br/>stdio, runs on my Mac<br/>1 tool, 0 resources"] --> TOOLS["🧰 get_tools()<br/>22 read-only<br/>LangChain tools"]
        GC["☁️ github_client<br/>http + token, read-only<br/>19 tools, 1 resource"] --> TOOLS
        DC["📚 docs_client<br/>http, no token<br/>3 tools, 1 resource"] --> FILTER["🚫 leave out<br/>submit_feedback<br/>the only tool that writes"]
        FILTER --> TOOLS
    end

    subgraph STEP4["🧪 Step 4 · One agent per server"]
        direction LR
        FA["🌐 fetch_agent<br/>OpenAI Agents SDK<br/>docs page"] --> L4["🪵 Every agent called<br/>its tool: LOG lines<br/>behind each answer"]
        GA["🐙 github_agent<br/>LangGraph LICENSE<br/>+ latest release"] --> L4
        DA["📚 docs_agent<br/>searches: what is<br/>LangGraph for?"] --> L4
    end

    subgraph STEP5["📖 Step 5 · Resource, not a tool"]
        direction LR
        RES["📖 get_resources()<br/>from docs_client<br/>guide, 11,252 characters"] --> GU["🤖 guide_agent<br/>no tools, guide text<br/>in the system prompt"]
        GU --> KW{"🔍 Keywords in answer<br/>and in guide?"}
        KW -->|"True / True"| OK5["✅ Answer comes<br/>from the guide"]
    end

    subgraph STEP6["🎯 Step 6 · Combined agent: tools + resource"]
        direction LR
        Q["❓ RFP query<br/>names both repos,<br/>the docs and the URL"] --> CA["🤖 combined_agent<br/>22 tools + guide<br/>in the system prompt"]
        CA --> CALLS["⚡ 4 parallel calls<br/>GitHub only<br/>2x get_latest_release<br/>2x get_file_contents LICENSE"]
        CALLS --> ANS["📊 Answer table<br/>LangGraph: MIT, 1.2.18<br/>Agents SDK: MIT, v0.24.0"]
        ANS --> CHK{"🔍 Every fact behind<br/>a tool call or<br/>the guide?"}
        CHK -->|"5 of 7: yes"| OK6["✅ 4 GitHub facts<br/>+ the guide line"]
        CHK -->|"2 of 7: no"| GAP["⚠️ No fetch, no docs call<br/>LangGraph line: from guide<br/>SDK line: from memory"]
    end

    subgraph PROBE["🧨 Step 6 · Failure probe"]
        direction LR
        PQ["❓ Price question<br/>without repo names"] --> SRC["🔎 docs search + fetch<br/>LangSmith for Enterprise,<br/>langchain.com/pricing"]
        SRC --> RESULT{"Result"}
        RESULT -->|"good"| GOOD["👍 No invented price:<br/>custom, contact sales"]
        RESULT -->|"bad"| BAD["👎 LangSmith plans<br/>presented as<br/>LangGraph support"]
        BAD --> FIX["🔧 Fix: a tool call per fact,<br/>check the LOG in code,<br/>answer the product asked"]
    end

    PROOF["📦 lab_proof.md<br/>query · LOG evidence · answer · trace · failure"]

    SETUP --> CONNECT
    CONNECT --> STEP4
    CONNECT --> STEP5
    STEP4 --> STEP6
    STEP5 --> STEP6
    STEP6 --> PROBE
    PROBE --> PROOF
```

How the notebook works:
| Step | What happens | Result in my run |
|---|---|---|
| 1 Setup | Load keys from the git-ignored `.env`, find `uvx`, create `gpt-4o-mini` (temperature 0) and the `[LOG]` interceptor | Key, `uvx` and token loaded; no key printed |
| 2 Connect | One client per server, each with the interceptor; count tools and resources | Fetch: 1 tool, 0 resources. GitHub: 19 tools, 1 resource. LangChain Docs: 3 tools, 1 resource |
| 3 Load tools | `get_tools()` turns MCP tools into LangChain tools; `submit_feedback` left out | 1 + 19 + 2 = **22 read-only tools** |
| 4 One agent per server | Fetch agent: the SDK docs page. GitHub agent: LangGraph's LICENSE and latest release. Docs agent: what LangGraph is for | Every agent called its tool; `[LOG]` lines behind each answer |
| 5 Resource | The guide text goes into the system prompt of an agent with **no tools** | "deterministic" and "human-in-the-loop" in the answer **and** in the guide |
| 6 Combined agent | 22 tools **plus** the guide in the system prompt; the RFP query below; plus a failure probe | **4 tool calls, GitHub only.** The two descriptions had no tool call behind them (sections 5 and 6) |
| Secrets check | `.env` git-ignored; saved notebook scanned for keys and tokens | PASS, PASS |



## 2. Query

> We are shortlisting agent frameworks for a client RFP. For LangGraph (GitHub repo langchain-ai/langgraph) and the OpenAI Agents SDK (GitHub repo openai/openai-agents-python): give each one's license and latest release from GitHub, and one sentence on what each framework is for: for LangGraph from the LangChain docs, for the OpenAI Agents SDK from https://openai.github.io/openai-agents-python/. Answer as a small table with a source column. Below the table, add one line from the guide: when should a team choose LangGraph instead of LangChain's create_agent?

## 3. Evidence

The `[LOG]` lines from the interceptor (Step 6). The agent sent 4 tool calls at once, all to GitHub. The `returned` lines arrive in the order the server answered; each one is matched to its call by the tag, repo or SHA in the text. **There is no `fetch` and no `langchain-docs` line**, although the question asked for both.

```text
[LOG] github -> get_latest_release  {'owner': 'langchain-ai', 'repo': 'langgraph'}
[LOG] github -> get_latest_release  {'owner': 'openai', 'repo': 'openai-agents-python'}
[LOG] github -> get_file_contents  {'owner': 'langchain-ai', 'repo': 'langgraph', 'path': 'LICENSE'}
[LOG] github -> get_file_contents  {'owner': 'openai', 'repo': 'openai-agents-python', 'path': 'LICENSE'}
[LOG]    returned: {"tag_name":"1.2.18","target_commitish":"3521f08e21a7d89c28331191374bc85c11ecb6e2","name":"langgraph==1.2.18","body":"Changes since 1.2.17\n\n* releas...
[LOG]    returned: {"tag_name":"v0.24.0","target_commitish":"17d994bd3045dae71acda676a4ef4762ed8ecd94","name":"v0.24.0","body":"## [0.24.0](https://github.com/openai/ope...
[LOG]    returned: successfully downloaded text file (SHA: fc0602feecdd6748623c852ab534e1ca612673c7) type='resource' resource=TextResourceContents(uri=AnyUrl('repo://lan...
[LOG]    returned: successfully downloaded text file (SHA: e5ad2c5aa30343f143a5c418004ca1a8d2cfaff4) type='resource' resource=TextResourceContents(uri=AnyUrl('repo://ope...
```

The guide line has no tool call (a resource is read by my code, not by the agent), so its evidence is the keyword check printed after the answer:

```text
'deterministic': in answer = True, in guide = True
'human-in-the-loop': in answer = False, in guide = True
```

## 4. Final answer

| Framework | License | Latest Release | Description | Source |
|---|---|---|---|---|
| LangGraph | MIT License | [1.2.18](https://github.com/langchain-ai/langgraph/releases/tag/1.2.18) | LangGraph is a low-level orchestration runtime for stateful workflows. | LangChain Docs |
| OpenAI Agents SDK | MIT License | [v0.24.0](https://github.com/openai/openai-agents-python/releases/tag/v0.24.0) | The OpenAI Agents SDK provides tools for building and managing AI agents with OpenAI models. | [OpenAI Agents SDK Docs](https://openai.github.io/openai-agents-python/) |

When to use LangGraph instead of LangChain's `create_agent`: Use LangGraph for complex workflows mixing deterministic logic with LLM-driven steps in a single graph.

## 5. Trace

Which claim comes from which tool call or resource. The interceptor shows only the first 150 characters of each result, so where the fact sits further down, I checked it at the source itself.

| Claim in the answer | Tool call or resource | Visible in the `[LOG]` line? | Checked at the source |
|---|---|---|---|
| LangGraph latest release: 1.2.18 | `github -> get_latest_release` (langchain-ai/langgraph) | **Yes**: `"tag_name":"1.2.18"`, `"name":"langgraph==1.2.18"` | Matches |
| OpenAI Agents SDK latest release: v0.24.0 | `github -> get_latest_release` (openai/openai-agents-python) | **Yes**: `"tag_name":"v0.24.0"` | Matches |
| LangGraph license: MIT | `github -> get_file_contents` (LICENSE, SHA fc0602f...) | Partly: the file was downloaded, its text is cut | `LICENSE` starts with "MIT License": matches |
| OpenAI Agents SDK license: MIT | `github -> get_file_contents` (LICENSE, SHA e5ad2c5...) | Partly: the file was downloaded, its text is cut | `LICENSE` starts with "MIT License": matches |
| LangGraph: "a low-level orchestration runtime for stateful workflows" (source: "LangChain Docs") | **None.** The question asked for the LangChain docs search; there is no `langchain-docs` call | No | Word for word in the guide's product summary: "**LangGraph** (low-level orchestration runtime for stateful workflows)". So it is true and comes from the **resource** in the system prompt, but the source column does not say so |
| OpenAI Agents SDK: "provides tools for building and managing AI agents with OpenAI models" (source: link to the docs page) | **None.** There is no `fetch` call in Step 6 | No | **Not on the page.** The page opens with "The OpenAI Agents SDK enables you to build agentic AI apps in a lightweight, easy-to-use package with very few abstractions." The sentence came from the model's memory, with a link it never opened |
| Guide line: "complex workflows mixing deterministic logic with LLM-driven steps in a single graph" | Resource (skill guide) in the system prompt | No `[LOG]` line, by design | Keyword check: "deterministic" in answer and guide. "human-in-the-loop" is `False` only because the line does not use that word; it does not contradict the guide |

**Grounding verdict:** 5 of 7 claims are backed: the 4 GitHub facts by tool calls, the guide line by the resource. The LangGraph sentence is true but comes from the resource, not from the docs search the question asked for. The OpenAI Agents SDK sentence is **unsupported**: no tool call, not on the page, yet it is presented with a source link. The Step 6 "Done when" (calls to all three servers) was **not met**.

## 6. Failure or limitation

**Where could the system produce a plausible but unsupported answer? In my main query, and again in my failure probe.**

### 6a. Main query: two tool calls skipped, sources still cited

| What happened | Good or bad |
|---|---|
| 4 GitHub calls, then the answer. No `fetch` call and no `langchain-docs` call, although the question and the system prompt named both | **Bad.** The "one job per server" plan was only half followed |
| The LangGraph sentence was copied from the guide in the system prompt and labelled "LangChain Docs" | **Plausible and true**, but the source is vague and not the one asked for |
| The OpenAI Agents SDK sentence was written from memory and labelled with the docs URL | **Plausible but unsupported.** The table looks equally confident for grounded and ungrounded rows |

**Likely cause** (one run, so a hypothesis): the guide in the system prompt already describes LangGraph, and the model already "knows" the OpenAI Agents SDK, so it saw no need to call `fetch` or the docs search. In Step 4 the same tools, without the guide in the prompt, were called every time.

**Lesson:** more context and more tools can mean **fewer** tool calls. A source column is not evidence; only a `[LOG]` line is. The trace is what made this visible.

**Fix:**
1. Prompt rule: "Call a tool for every fact in the table, even if you know it. The guide is only for the line below the table."
2. Check in code after the run: every server the question needs must appear in the `[LOG]` lines; if one is missing, mark the answer "not grounded".
3. The source column may only hold a link that appears in a `[LOG]` line.

### 6b. Failure probe: a real source about the wrong product

I asked a question **without** repo names: *"Does LangGraph or the OpenAI Agents SDK offer paid enterprise support, and what does it cost per year? Use only your tools."*

```text
[LOG] langchain-docs -> search_docs_by_lang_chain  {'query': 'LangGraph enterprise support pricing'}
[LOG] fetch -> fetch  {'url': 'https://platform.openai.com/docs/guides/agents'}
[LOG]    returned: Title: LangSmith for Enterprise
Link: https://docs.langchain.com/langsmith/enterprise
Page: langsmith/enterprise
Content: This page is a reference hub...
[LOG]    returned: Contents of https://platform.openai.com/docs/guides/agents: <p>Agents | OpenAI API</p> ...
[LOG] fetch -> fetch  {'url': 'https://www.langchain.com/pricing'}
[LOG] fetch -> fetch  {'url': 'https://www.langchain.com/contact-sales'}
[LOG]    returned: Contents of https://www.langchain.com/contact-sales: <p>Contact the LangChain Sales Team</p> Try LangSmith ...
[LOG]    returned: Contents of https://www.langchain.com/pricing: <p>LangSmith Plans and Pricing</p> ... # Plans for teams of any size ...
```

| What happened | Good or bad |
|---|---|
| Price: *"The enterprise plan has custom pricing ... organizations are encouraged to contact the sales team"* | **Good.** No invented number |
| OpenAI Agents SDK: *"No specific enterprise support or pricing details found"* | **Good.** It admitted the gap |
| *"LangGraph is part of the LangChain ecosystem, which offers enterprise support through its LangSmith platform"*, with SSO, ABAC, RBAC, a support SLA, self-hosted and hybrid deployment | **Plausible but unsupported for LangGraph.** The features are real: the LangSmith Enterprise page lists SSO, RBAC, ABAC, self-hosted and hybrid hosting and SLA guarantees. But every source in the log is about **LangSmith**, and the Enterprise page does not mention LangGraph. The agent made the link from LangGraph to LangSmith itself. It may be right, but no source in the `[LOG]` lines says so |
| It chose its own URLs (`langchain.com/pricing`, `contact-sales`, `platform.openai.com`), none given in the question | **Risky.** `fetch` can reach any public page, so the sources are the model's choice |

**Lesson:** grounding needs the right source **and** the right entity. A client reading this answer would think LangGraph has a paid enterprise support plan. **Fix:** a prompt rule "answer only about the product asked; if a source is about another product, say so", and a list of allowed URLs for `fetch`.

**Other limitations**

- **The docs search can hit the wrong language.** In Step 4 its first result was the **JavaScript** LangGraph overview, while the answer cites the **Python** page and talks about "Pregel", which is not in the visible log.
- **Live sources.** The guide, the releases and the pages can change between runs.
- **One run, temperature 0.** That does not fix which tools the agent picks; a second run can take a different path.
