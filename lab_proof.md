---
## ✅ Write `lab_proof.md` [YOUR TURN]

Create `lab_proof.md` in your repo (the **entry point for your reviewer**):

```markdown
# Lab Proof: Agents that Speak MCP Fluently

## 1. What I built
# I built an agent that answers questions using tools from MCP servers

## 2. Query
# Evidence: do the key words from the answer appear in the resource?

## 3. Evidence
[LOG] filesystem -> read_text_file  {'path': '/Users/pieteralbrecht/Desktop/IRONHACK/WEEK_4/WEEK_4_DAY_3/WEEK_4_DAY_3_LAB/sample_docs/project_notes.md'}
[LOG] github -> get_file_contents  {'owner': 'langchain-ai', 'repo': 'langchain-mcp-adapters', 'path': 'README.md'}
[LOG]    returned: ENOENT: no such file or directory, open '/Users/pieteralbrecht/Desktop/IRONHACK/WEEK_4/WEEK_4_DAY_3/WEEK_4_DAY_3_LAB/sample_docs/project_notes.md'...
[LOG]    returned: successfully downloaded text file (SHA: 0d3e7d0fc7c4facdf437445eaeeb71102de4befe) type='resource' resource=TextResourceContents(uri=AnyUrl('repo://lan...

ANSWER:
 1. **Project Atlas Notes Constraint**: The file `project_notes.md` could not be found, so I cannot provide the specific constraint regarding where ticket data may live.
 The model guessed a file path, the call failed, and you fixed it by tightening the prompt. That’s a real failure, its cause and a mitigation, which is exactly what the section asks for.

2. **Transport for MCP Server**: According to the README of the GitHub repository `langchain-ai/langchain-mcp-adapters`, the transport that would allow running an MCP server inside the client's own environment, ensuring that data never leaves it, is the `stdio` transport. This transport is designed primarily for applications running on a user's machine. 

   Source: `langchain-ai/langchain-mcp-adapters`, README.md.
  
## 4. Final answer
ANSWER:
 1. **Constraint on Ticket Data Location**: I was unable to read the Project Atlas notes from the specified file path, as it appears the file does not exist. Therefore, I cannot provide information about any constraints set regarding where ticket data may live.

2. **Transport for Running MCP Server in Client's Environment**: The README of the GitHub repository `langchain-ai/langchain-mcp-adapters` indicates that the `stdio` transport allows running an MCP server inside the client's own environment, ensuring that data never leaves it. This is highlighted in the example code provided in the README. 

Source for the transport information: `langchain-ai/langchain-mcp-adapters`, README.md.
---

# LangChain Skill

## Product summary

LangChain is a framework for bu

ANSWER:
 You need to pass a `thread_id` in the config to persist conversation history across invocations. Use `config={"configurable": {"thread_id": "..."}}` when invoking the agent. Additionally, ensure you have a checkpointer configured if persistence is needed.

## 5. Trace
[LOG] filesystem -> read_text_file  {'path': '/Users/pieteralbrecht/Desktop/IRONHACK/WEEK_4/WEEK_4_DAY_3/WEEK_4_DAY_3_LAB/sample_docs/project_notes.md'}
[LOG] github -> get_file_contents  {'owner': 'langchain-ai', 'repo': 'langchain-mcp-adapters', 'path': 'README.md'}
[LOG]    returned: ENOENT: no such file or directory, open '/Users/pieteralbrecht/Desktop/IRONHACK/WEEK_4/WEEK_4_DAY_3/WEEK_4_DAY_3_LAB/sample_docs/project_notes.md'...
[LOG]    returned: successfully downloaded text file (SHA: 0d3e7d0fc7c4facdf437445eaeeb71102de4befe) type='resource' resource=TextResourceContents(uri=AnyUrl('repo://lan...

ANSWER:
 1. **Constraint on Ticket Data Location**: I was unable to read the Project Atlas notes from the specified file path, as it does not exist. Therefore, I cannot provide information about the constraints set regarding where ticket data may live.

2. **Transport for Running MCP Server in Client's Environment**: The README of the GitHub repository `langchain-ai/langchain-mcp-adapters` indicates that the `stdio` transport allows running an MCP server inside the client's own environment, ensuring that data never leaves it. This is highlighted in the example code provided in the README. 

Source for the transport information: `langchain-ai/langchain-mcp-adapters`, README.md.

## 6. Failure or limitation

On my first step 4 run, "list_directory" returned empty.
My agent used search_files, witch matches names, not content, and included no document named porject atlas.

LOG] filesystem -> read_text_file  {'path': '/Users/pieteralbrecht/Desktop/IRONHACK/WEEK_4/WEEK_4_DAY_3/WEEK_4_DAY_3_LAB/sample_docs/project_notes.md'}
[LOG] github -> get_file_contents  {'owner': 'langchain-ai', 'repo': 'langchain-mcp-adapters', 'path': 'README.md'}
[LOG]    returned: ENOENT: no such file or directory, open '/Users/pieteralbrecht/Desktop/IRONHACK/WEEK_4/WEEK_4_DAY_3/WEEK_4_DAY_3_LAB/sample_docs/project_notes.md'...
[LOG]    returned: successfully downloaded text file (SHA: 0d3e7d0fc7c4facdf437445eaeeb71102de4befe) type='resource' resource=TextResourceContents(uri=AnyUrl('repo://lan...

```

In both cases, a tool failure or wrong tool choice was turned into a statement about the documents. “My call failed” became “the information doesn’t exist.”

How that could mislead someone

The answers sound careful and honest: “I couldn’t find any documents related to Project Atlas” looks exactly like good grounding behaviour. A user can’t tell the difference between “the files don’t contain this” and “the agent searched the wrong way.” In a client setting, a consultant could conclude that a contract has no clause about data location, or that a project has no go-live date, when the information is sitting right there in the folder. A confident “not found” is arguably more dangerous than an obvious error, because nobody double-checks it.

Mitigation (pick what you actually did)

The stricter prompt with exact paths and “don’t use search_files for content”, restricting the agent to read-only tools, and always checking the [LOG] lines before trusting a “not found” answer.

**Before you submit:**
- [ ] No API keys, tokens or `.env` committed
- [ ] Only files for this lab are in the repo, with clear names
- [ ] `lab_proof.md` is the entry point
- [ ] A reviewer can trace **one** answer back to the exact tool call