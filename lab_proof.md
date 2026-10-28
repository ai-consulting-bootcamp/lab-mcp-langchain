# Lab Proof: Agents that Speak MCP Fluently

## 1. What I built

I built a LangChain agent connected to a local Filesystem MCP server over `stdio` and the GitHub MCP server over `streamable_http`. The Filesystem server is scoped to `sample_docs/`; the agent combines tools from both servers. See the [notebook](./mcp_langchain.ipynb).

## 2. Query

> Read the MCP lesson file in sample_docs and find which MCP transports it mentions. Then read the README of the GitHub repository langchain-ai/langchain-mcp-adapters and tell me which of those transports its examples show.

## 3. Evidence

The notebook's interceptor captured these calls, in order:

```text
[LOG] filesystem -> read_text_file  {'path': '.../sample_docs/mcp_lesson.txt'}
[LOG]    returned: ENOENT: no such file or directory, open '.../sample_docs/mcp_lesson.txt'...
[LOG] filesystem -> list_directory  {'path': '.../sample_docs'}
[LOG]    returned: [FILE] Lab_agent_speak_fluently.md
[FILE] mcp_introduction.md...
[LOG] filesystem -> read_text_file  {'path': '.../sample_docs/Lab_agent_speak_fluently.md'}
[LOG] filesystem -> read_text_file  {'path': '.../sample_docs/mcp_introduction.md'}
[LOG]    returned: # MCP Introduction with LangChain...
[LOG]    returned: # LAB: Agents that Speak MCP Fluently...
[LOG] github -> get_file_contents  {'owner': 'langchain-ai', 'repo': 'langchain-mcp-adapters', 'path': 'README.md'}
[LOG]    returned: successfully downloaded text file (SHA: 0d3e7d0fc7c4facdf437445eaeeb71102de4befe)...

Tools called: ['read_text_file', 'list_directory', 'read_text_file', 'read_text_file', 'get_file_contents']
```

The failed first read was a guessed filename. The directory listing exposed the actual lesson filename, which the agent then read. The interceptor prints only the first 150 characters of each returned content, so the log previews are abbreviated. This sequence is from the combined-agent run in the [notebook](./mcp_langchain.ipynb).

## 4. Final answer

> ### MCP Transports Mentioned in the Lesson File
>
> From the **MCP lesson file**, the following MCP transports are mentioned:
>
> 1. **stdio** - Used for the Filesystem server that runs locally.
> 2. **HTTP** - Used for the GitHub server that runs remotely.
>
> ### MCP Transports in the README of `langchain-ai/langchain-mcp-adapters`
>
> In the **README** of the `langchain-ai/langchain-mcp-adapters` repository, the following transports are shown in its examples:
>
> 1. **stdio** - Used for local server connections (e.g., math server).
> 2. **HTTP** - Used for remote server connections (e.g., weather server).
> 3. **streamable_http** - Mentioned as a transport that supports streaming.
>
> ### Summary
>
> - The lesson file mentions **stdio** and **HTTP** as the MCP transports.
> - The README of the `langchain-ai/langchain-mcp-adapters` repository includes examples of **stdio**, **HTTP**, and **streamable_http** transports.

## 5. Trace

| Answer claim | Evidence |
|---|---|
| The lesson mentions `stdio` and `HTTP`. | `read_text_file` successfully read `sample_docs/Lab_agent_speak_fluently.md`; its server-connection section labels Filesystem as `stdio` and GitHub as `http`. |
| The adapter README examples show `stdio`, `HTTP`, and `streamable_http`. | `get_file_contents` fetched `README.md` from `langchain-ai/langchain-mcp-adapters`. The agent's answer attributes these transports to that README; the interceptor log only captures a 150-character preview, not the README text. |

## 6. Failure or limitation

The Filesystem fetch needed recovery: the agent first tried `sample_docs/mcp_lesson.txt`, which did not exist (`ENOENT`). It then called `list_directory`, found `Lab_agent_speak_fluently.md`, and read the correct file. This is a useful recovery path, but it costs an extra tool call and depends on the agent responding to the error by listing the directory. If the listing or corrected read also failed, the agent would not have evidence for the lesson's transports and should say so rather than guess.

There is also a proof limitation: the interceptor truncates returned text to 150 characters for its log preview. The tool calls are traceable, but this capture alone does not display the full README content supporting the final three-transport claim.
