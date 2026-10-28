# LAB: Agents that Speak MCP Fluently

## Objective

In `mcp_introduction.ipynb` we connected an agent to **one remote** MCP server. In this lab we go one step further and connect **two very different servers**:

- 📁 a **Filesystem server** that runs **on our own laptop** and reads local project files
- 🐙 a **GitHub server** that runs **on GitHub's computers** and reads code repositories

> 🔄 **You are free to use any MCP server.** Filesystem and GitHub are just our example: one **local** server and one **remote** server. If you pick others (e.g. Notion, Slack, a database), follow the same steps and keep the same rule: every answer needs a tool call as evidence. Browse servers at [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers).

The goal is not just a working agent. The goal is a **provably grounded** agent: for every answer, we can point to the **exact tool call and the exact text** that backs it up.

## 🗺️ Steps we will follow

| # | Step | What happens | Who writes the code |
|---|------|--------------|---|
| 1 | **Setup and installation** | Install packages, load the OpenAI key and the GitHub token, check Node.js | PROVIDED |
| 2 | **Connect to MCP servers** | One client per server: Filesystem (**stdio**) and GitHub (**HTTP** + token). List tools and resources | YOUR TURN |
| 3 | **Load MCP tools into LangChain** | Load the tools and check they are accessible | YOUR TURN |
| 4 | **Create an agent with MCP tools** | Ask a question and print every tool call behind the answer | YOUR TURN |
| 5 | **Access MCP resources** | Give the agent read-only background information | YOUR TURN |
| 6 | **Build a complete MCP-enabled agent** | Two clients, one agent, one question that needs both servers | YOUR TURN |
| 7 | **Optional: MCP vs direct API** | Build the same thing without MCP and compare | OPTIONAL |
| 8 | **Optional: practical example** | A document analysis agent over `sample_docs/` | OPTIONAL |
| ✅ | **Your `lab_proof.md`** | What to hand in | YOUR TURN |

> 💡 **The one rule of this lab:** a working agent isn't the goal. A **provably grounded** agent is.

---

**Your sources**
- `sample_docs/`: two small files about a fictional client project, *Project Atlas* (`project_notes.md`, `faq.md`)
- The GitHub repository `langchain-ai/langchain-mcp-adapters`

**What you submit:** a `lab_proof.md` with your code (or a link to this notebook), **one query**, the **tool evidence**, the **final answer**, and **one failure or limitation**. Template at the end.

---

### How this notebook works

| Label | Meaning |
|---|---|
| **PROVIDED** | Code is given. Run it and read it. |
| **YOUR TURN** | Replace the `# TODO` lines with your own code. |
| **OPTIONAL (Advanced)** | Do this if you have time; it's not required to pass. |

Each step ends with a **Done when** check. Don't move on until it passes.

**Main reference:** `mcp_introduction.ipynb`. Almost every step has a matching section there.

### Prompt discipline
You may use AI to **review, debug or critique** your work, but not to write your final answer or your `lab_proof.md`. A good review prompt:

> *Role: Agent reviewer. Task: Review my plan for grounding and verification. Inputs: my sources, query, tool path and evidence. Constraints: Do not produce the final answer. Identify weak grounding and missing traces. Output: three grounding risks, two trace checks, one simplification.*

---
## Step 1: Setup and Installation [PROVIDED]

1. Create a `.env` file next to this notebook. **Everyone** needs `OPENAI_API_KEY=...`.
2. Add the secrets **your** MCP servers need. Many servers need **nothing**; others need a token or a key:

| If you use... | Add to `.env` |
|---|---|
| Filesystem, Fetch, Time, LangChain docs | Nothing |
| **GitHub** (our example) | `GITHUB_PERSONAL_ACCESS_TOKEN=github_pat_...` |
| Notion | `NOTION_TOKEN=...` |
| Slack | `SLACK_BOT_TOKEN=...` and `SLACK_TEAM_ID=...` |
| Brave Search | `BRAVE_API_KEY=...` |
| A database (e.g. Postgres) | A connection string, e.g. `DATABASE_URL=postgresql://...` |

   The exact variable name is in each server's README. **Only the GitHub token is needed for our example**, and only if you use the GitHub server.
3. Install **Node.js** (nodejs.org) if any of your servers is started with `npx` (our Filesystem server is).
4. Run the cells below.

**How to create the GitHub token:** GitHub → Settings → Developer settings → Personal access tokens → **Fine-grained tokens** → Generate new token. *Public repositories (read-only)* is enough.

**Warning:** Never paste keys or tokens into a notebook cell, and never commit your `.env` file (add it to `.gitignore`).

<details>
<summary><b>Do secrets have to live in <code>.env</code>?</b></summary>

No. `os.getenv(...)` reads **environment variables**, and `.env` is just one easy way to set them. Other options:

| Where | When to use it |
|---|---|
| `.env` + `load_dotenv()` | Local work, this lab (recommended) |
| A system / terminal environment variable | You don't want a file at all |
| `getpass.getpass("Token: ")` | Typed in at runtime, never stored |
| Google Colab **Secrets** (key icon) | Working in Colab |
| A secret manager (Azure Key Vault, AWS Secrets Manager, ...) | Real client projects and production |

Whatever you choose, the code reads it the same way: `os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")`.
</details>


```python
%pip install -qU langchain langchain-openai langchain-mcp-adapters langgraph mcp python-dotenv "pydantic>=2,<3"
```


```python
import os
import shutil
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found. Add it to your .env file.")

GITHUB_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")      # only needed for the GitHub server
SAMPLE_DOCS_DIR = os.path.join(os.getcwd(), "sample_docs")   # the ONLY folder the Filesystem server may see
# Using other servers? Load their secrets here the same way, e.g. NOTION_TOKEN = os.getenv("NOTION_TOKEN")

print("OpenAI key:   loaded")
print("Node.js npx: ", "found" if shutil.which("npx") else "NOT found: needed only for servers started with npx")
print("GitHub token:", "loaded" if GITHUB_TOKEN else "missing: needed only if you use the GitHub server")
print("sample_docs: ", "found" if os.path.isdir(SAMPLE_DOCS_DIR) else "NOT found: put sample_docs/ next to this notebook")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
```

**Windows + Jupyter fix.** Starting a local (stdio) server fails inside Jupyter on Windows because there's nowhere to send the server's error output. This cell sends it to "nowhere". It's plumbing, not MCP.


```python
import sys

if sys.platform == "win32":
    import mcp.client.stdio as _stdio
    _stdio.stdio_client.__wrapped__.__defaults__ = (open(os.devnull, "w"),)
```

**Evidence interceptor.** This is the "receptionist" from **"Tool Interceptors"** in `mcp_introduction.ipynb`. It sits **inside the client** and logs every tool call **live**: which server, which tool, which inputs, and what the server sent back. These `[LOG]` lines are your proof for `lab_proof.md`.

You plug it into **each** client in Step 2 with `tool_interceptors=[log_tool_calls]`.


```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

async def log_tool_calls(request, handler):
    # BEFORE: which server, which tool, which inputs
    print(f"[LOG] {request.server_name} -> {request.name}  {request.args}")
    result = await handler(request)   # the real tool runs on the server
    # AFTER: what the server sent back
    text = " ".join(getattr(part, "text", str(part)) for part in result.content)
    print(f"[LOG]    returned: {text[:150]}...")
    return result
```

**No `[LOG]` lines after an answer?** Then the agent called no tool: the answer is **not grounded** in any source.

**Done when:** the OpenAI key is loaded, and every check for the servers **you** use prints `loaded` / `found`.

---
## Step 2: Connect to MCP Servers [YOUR TURN]

**Goal:** create **one client per server**, then test each connection by listing its tools and resources.

| | 📁 Filesystem | 🐙 GitHub |
|---|---|---|
| **Transport** | `stdio`: the client **starts** the server | `http`: the client **calls** the server |
| **Connection keys** | `command` + `args` | `url` + `headers` |
| **Secret** | None, but it only sees **one folder** | A **token** in the headers |

**Hint:** compare with the config cell in **"Connecting to the LangChain Documentation MCP Server"** in `mcp_introduction.ipynb`. Only the transport and the connection keys change.

> 🔄 **Using other servers?** Copy their config from the server's README. The pattern is always the same: a **stdio** server needs `command` + `args` (secrets go in `"env"`), an **HTTP** server needs `url` (secrets go in `"headers"`). Still one client per server.

### 2a. Filesystem client (stdio)

Your client must start the server exactly as if you typed this in a terminal:

```
npx -y @modelcontextprotocol/server-filesystem <SAMPLE_DOCS_DIR>
```

**What to do**
1. Create `filesystem_client` with `MultiServerMCPClient`, one server called `"filesystem"`.
2. Use `"transport": "stdio"`, a `"command"` and a list of `"args"` (split the terminal command above).
3. Plug in the evidence interceptor: `tool_interceptors=[log_tool_calls]`.


```python
# YOUR TURN: Filesystem client

# TODO: filesystem_client = MultiServerMCPClient({ "filesystem": { ... } }, tool_interceptors=[...])
```

### 2b. GitHub client (HTTP + token)

GitHub hosts its official MCP server at `https://api.githubcopilot.com/mcp/`. You send **`headers`** with every request:

| Header | Value | Why |
|---|---|---|
| `Authorization` | `f"Bearer {GITHUB_TOKEN}"` | Your ID card. Without a valid token GitHub rejects the call (*401* or *400*) |
| `X-MCP-Toolsets` | `"repos,issues"` | Only load these groups of tools |

**What to do:** create `github_client` with one server called `"github"`: `transport`, `url`, `headers`. Plug in the **same** interceptor.

**Warning:** the npm package `@modelcontextprotocol/server-github` is **deprecated**. Use GitHub's official server above.
**Warning:** the interceptor must be set **when you create the client**. Tools loaded from a client without it will never log anything.


```python
# YOUR TURN: GitHub client

# TODO: github_client = MultiServerMCPClient({ "github": { ... } }, tool_interceptors=[...])
```

### 2c. Test both connections

**What to do**
1. For **each** client, call `get_tools()` and print **how many** tools it has.
2. For **each** client, try `get_resources()` inside a `try/except` and print how many resources it has, or that it has none.

**Hint:** older tutorials use `get_langchain_tools()` / `list_resources()`. In the current `langchain-mcp-adapters` the methods are `get_tools()` and `get_resources()`.
**Warning:** both are async. Don't forget `await`. The first Filesystem call can take ~20 s (`npx` downloads the package).


```python
# YOUR TURN: test the connections

# TODO: for each client -> count tools
# TODO: for each client -> try get_resources(), print the count or "no resources"
```

**Done when:** both clients return a tool count, and you know which server offers resources and which doesn't.

### Stop and think
What does the client do differently for **stdio** vs **HTTP**? Where does the secret go in each case?

---
## Step 3: Load MCP Tools into LangChain [YOUR TURN]

**Goal:** turn the MCP tools into LangChain tools and check they are accessible.

`get_tools()` already converts every MCP tool into a LangChain tool.

**Hint:** see **"Loading MCP Tools into LangChain"** in `mcp_introduction.ipynb`.


```python
# YOUR TURN: load the tools from both clients

# TODO: fs_tools = ...
# TODO: github_tools = ...

# TODO: print the name of every tool from both clients
```

**Done when:** you can see the name of every tool from both servers.

---
## Step 4: Create an Agent with MCP Tools [YOUR TURN]

**Goal:** an agent that answers from the files, with a receipt.

**What to do**
1. Create `fs_agent` with `create_agent(model=llm, tools=fs_tools, system_prompt=...)`.
2. Your system prompt must describe the agent's capabilities: give the folder path (`SAMPLE_DOCS_DIR`), tell it to **list the folder first**, **never guess**, and **name the file** it used.
3. Ask: *"Who is the engagement lead for Project Atlas, and what is the target go-live date?"*
4. Read the `[LOG]` lines, then print the final answer (`result["messages"][-1].content`).
5. Do the same for GitHub: build `github_agent` with `github_tools` and ask the second question below.

**Hint:** see **"Using MCP Tools with LangChain Agents"** in `mcp_introduction.ipynb`.
**Warning:** if you don't give the agent the folder path, it may guess wrong paths and fail.

> 🔄 **Using other servers?** Write your own question: one the LLM **cannot** answer from memory, so it must call a tool.


```python
# YOUR TURN: Filesystem agent

# TODO: fs_agent = create_agent(...)

question = "Who is the engagement lead for Project Atlas, and what is the target go-live date?"

# TODO: fs_result = await fs_agent.ainvoke({"messages": [HumanMessage(content=question)]})

# TODO: print the final answer (the [LOG] lines appear automatically)
```


```python
# YOUR TURN: GitHub agent

# TODO: github_agent = create_agent(...)   (system prompt: never guess, name the repo + file)

question = (
    "Read the README of the GitHub repository langchain-ai/langchain-mcp-adapters. "
    "Which MCP transports does it show in its examples?"
)

# TODO: run the agent and print the final answer (check the [LOG] lines)
```

### Check your grounding
1. Find the `[LOG] returned:` line that contains the answer.
2. Open the source yourself (the file in `sample_docs/`, or the README on GitHub). Does it say the same?
3. Does the final answer add anything that is **not** in the tool output?

**Done when:** both agents produce at least one `[LOG]` line, and you can match each part of each answer to the source.

---
## Step 5: Access MCP Resources [YOUR TURN]

**Goal:** give the agent read-only **background knowledge** instead of tools.

| | Tools | Resources |
|---|---|---|
| **What** | Actions: *do* something | Read-only data: *know* something |
| **Who decides** | The **agent** calls them | **Your code** fetches them and hands them over |

In Step 2c you saw that the Filesystem server offers **no** resources. So we use a server you already know that does: the **LangChain docs server** from `mcp_introduction`.

**What to do**
1. Create `docs_client` for `https://docs.langchain.com/mcp` (HTTP) and load its resources.
2. Read the first one as text with `.as_string()`.
3. Create `guide_agent` with **`tools=[]`** and the resource text inside the **system prompt**. Tell it to answer **only** from the guide.
4. Ask: *"What do I need to add to an agent so that it remembers the conversation between calls?"*
5. **Evidence:** a resource has no tool call, so pick a key word **from the agent's answer** and print whether it appears in the resource text (e.g. `"thread_id" in guide_text`).

**Hint:** see **"Accessing MCP Resources"** in `mcp_introduction.ipynb`.


```python
# YOUR TURN: resource -> system prompt

# TODO: docs_client = MultiServerMCPClient({ "langchain-docs": { ... } })
# TODO: load the resources and read the first one as a string

# TODO: guide_agent = create_agent(model=llm, tools=[], system_prompt=...)

question = "What do I need to add to an agent so that it remembers the conversation between calls?"

# TODO: run the agent, print the answer, and print your evidence check
```

**Done when:** the guide agent's answer is backed by a word you found in the resource text.

**Note:** you will see **no** `[LOG]` lines here. A resource is fetched by **your code**, not called by the agent, so the interceptor never sees it. That's why the evidence here is a keyword check.

**Note:** this resource is live. If the agent says *"not in the guide"* and your evidence check is `False`, that's grounding working correctly.

---
## Step 6: Build a Complete MCP-Enabled Agent [YOUR TURN]

**Goal:** one agent that uses tools from **two servers**, through **two clients** (one client per server), to answer a question that needs **both**.

You already have both clients: `filesystem_client` and `github_client`. An agent doesn't care where a tool comes from: it just gets a **list of tools**.

**What to do**
1. Reuse `fs_tools` and `github_tools` from Step 3. No need to load them again.
2. Combine them into one list: `all_tools = ...`
3. Print the tool names. (When the agent runs, the `[LOG]` lines show which server each call went to.)
4. Build `combined_agent` with `all_tools`. The system prompt must describe **both** capabilities: the folder path, and that GitHub repositories are read with the GitHub tools.
5. Ask the question below and read the `[LOG]` lines. Then test it with **one question of your own**.

**Warning:** with many tools (here 40+), a small model may skip listing the folder and **guess** a file name. You'll see `ENOENT: no such file or directory` in the `[LOG]` lines. That's why the question names the file. If it happens in your own question, it's a good failure for `lab_proof.md`.

> 🔄 **Using other servers?** Write a question that needs **both** of your servers, e.g. *"Read our meeting notes in Notion, then check the team's Slack channel: which action items were already discussed?"*

**Done when:** the `[LOG]` lines show calls to **both** `filesystem` and `github`, and each half of the answer matches one of them.


```python
# YOUR TURN: two clients -> one tool list

# TODO: all_tools = ...   (Filesystem tools + GitHub tools)

# TODO: print how many tools come from each client, and their names
```


```python
# YOUR TURN: combined agent

# TODO: combined_agent = create_agent(...)

question = (
    "Read our Project Atlas notes (project_notes.md): what constraint do they set about where ticket data may live? "
    "Then read the README of the GitHub repository langchain-ai/langchain-mcp-adapters: "
    "which transport would let us run an MCP server inside the client's own environment, "
    "so that data never leaves it?"
)

# TODO: run the agent and print the final answer (check the [LOG] lines)
```


```python
# YOUR TURN: test with one question of your own

# TODO
```

### Stop and think
1. You used two clients for two servers. What would you need to change to add a third server (e.g. Slack)?
2. The lab brief says *"disconnect the MCP clients when done"*. Is there anything to disconnect with `MultiServerMCPClient`? (Hint: remember what *stateless* meant in `mcp_introduction`.)

---
## Step 7: Compare MCP vs Direct API Integration [OPTIONAL (Advanced)]

**Goal:** build the **same** GitHub question from Step 4 **without** MCP, and compare.

**What to do**
1. Download the README yourself with a plain HTTP request:
   `requests.get("https://raw.githubusercontent.com/langchain-ai/langchain-mcp-adapters/main/README.md").text`
2. Put the README text in the prompt and ask `llm` the same question (no agent, no tools).
3. Compare both answers, then fill in the table.

| | MCP (Step 4) | Direct API (this step) |
|---|---|---|
| **Lines of code you wrote** | | |
| **Complexity** (what did you need to set up?) | | |
| **Maintainability** (what breaks if GitHub changes?) | | |
| **Flexibility** (could the LLM read a *different* file on its own?) | | |
| **Evidence trail** | | |


```python
# YOUR TURN (optional)
import requests

question = "Which MCP transports does the langchain-mcp-adapters README show in its examples?"

# TODO: readme = requests.get(...).text
# TODO: direct_answer = await llm.ainvoke(...)   (README text + question in the prompt)
# TODO: print the answer
```

**Done when:** you can write 2–3 sentences in `lab_proof.md` on **when** you'd pick MCP and when a direct API call is enough.

---
## Step 8: Build a Practical Example: Document Analysis Agent [OPTIONAL (Advanced)]

**Goal:** a specialised agent that a consultant could use on a client's document folder.

**What to do**
1. Reuse `fs_tools` (the Filesystem server already points to `sample_docs/`).
2. Write a system prompt for **document analysis**: it should be able to **list** the documents, **read** them, **summarise** them, and **search** for specific information. It must name the file behind every claim.
3. Test it with the four queries below and check the `[LOG]` lines for each.

**Hint:** look at the tool list from Step 3. Which tool would you expect for each query? Check whether the agent picked it.
**Warning:** `search_files` matches file **names**, not the text inside files. If the agent uses it to look for a phrase, it finds nothing and may wrongly answer *"no file mentions it"*. Your prompt should tell it to **read** the files to search their content.


```python
# YOUR TURN (optional)

TEST_QUERIES = [
    "Which documents are in the folder?",
    "Summarise project_notes.md in 3 bullet points.",
    "Which files mention the go-live date?",
    "Is Slack ticket intake part of Phase 1?",
]

# TODO: doc_agent = create_agent(...)
# TODO: for each query -> run the agent and print the answer
```

**Done when:** each query shows the tool you expected (or you can explain why the agent chose another one).

---
## ✅ Write `lab_proof.md` [YOUR TURN]

Create `lab_proof.md` in your repo (the **entry point for your reviewer**):

```markdown
# Lab Proof: Agents that Speak MCP Fluently

## 1. What I built
2-3 lines: which servers, which transport. Link to this notebook.

## 2. Query
"..."

## 3. Evidence
The [LOG] lines from the interceptor: every tool call and what it returned.

## 4. Final answer
(paste the agent's answer)

## 5. Trace
Which claim in the answer comes from which tool call / file?

## 6. Failure or limitation
Where could the system produce a plausible but unsupported answer?
```

**Ideas for the failure:**
- Ask something **not** in the files (*"What is Project Atlas's budget?"*). Does it admit it, or invent a number?
- Ask a question where only **part** of the answer is in the files. Does it mix evidence with guesses?
- Look at the Filesystem tool list: some tools can **write** or **move** files. What could go wrong with client data?

**Before you submit:**
- [ ] No API keys, tokens or `.env` committed
- [ ] Only files for this lab are in the repo, with clear names
- [ ] `lab_proof.md` is the entry point
- [ ] A reviewer can trace **one** answer back to the exact tool call

---
### Troubleshooting

| Problem | Fix |
|---|---|
| `npx` not found / Filesystem connection fails | Install Node.js, then restart VS Code |
| `Connection closed` (Filesystem, Windows) | Run the Windows fix cell in Step 1, then retry |
| GitHub `401 Unauthorized` or `400 Bad Request` | Token missing, wrong or expired: check `.env`, then restart the kernel |
| `ExceptionGroup: unhandled errors in a TaskGroup` | The real error is **inside**: scroll down to the sub-exception (often a 400/401 or a wrong command) |
| `pip install` fails with *No such file or directory* on Windows | The folder path is too long: move your project / venv to a shorter path (e.g. `C:\labs\`) |
| You get a `coroutine` instead of a result | Add `await` before `get_tools()`, `get_resources()`, `ainvoke()` |
| Answer but no `[LOG]` lines | The model answered from memory (make the system prompt stricter), or the client was created without `tool_interceptors` |
| `get_resources()` fails | That server offers no resources (expected for Filesystem) |

### Extensions (optional)
- **Three servers:** add a third MCP server to your agent
- **Audit-trail interceptor:** write every tool call (time, server, tool, args, result) to a `tool_log.jsonl` file and attach it to your `lab_proof.md`
- **Error handling:** catch a failed connection (wrong token, Node.js missing) and print a clear message instead of crashing
- **Resource-first agent:** an agent that answers mainly from resources, with no tools
