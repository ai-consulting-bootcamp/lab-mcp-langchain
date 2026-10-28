# Lab Proof: Agents that Speak MCP Fluently

## Workflow

I connected a LangChain agent to two MCP servers: a local Filesystem server and the GitHub MCP server. I selected read-only tools, ran questions that needed evidence from both servers, and inspected the tool calls and returned content before checking the answers.

## Step 6 — Combined Filesystem and GitHub query

**Question**

In `faq.md`, what decision is pending about which clients can access the portal? According to the `README.md`, which MCP transports are described? Does the README show that the transport limits access to a specific group of clients? If it does not say, report this as unknown.

**Tool evidence**

- Filesystem `list_directory` showed `faq.md` and `project_notes.md`.
- Filesystem `read_text_file` returned the FAQ. It says the access decision is pending: all clients or only clients with ongoing advisory plans.
- GitHub `get_file_contents` read `README.md` from `langchain-ai/langchain-mcp-adapters` (SHA: `0d3e7d0fc7c4facdf437445eaeeb71102de4befe`). The README gives an MCP server example using `stdio`, a server example using `http`, and a section about Streamable HTTP.
- These are MCP communication transports. The README does not describe document delivery for the PCI-02 portal or say that one transport limits access to a specific client group.

**Final answer**

The decision about portal access is still pending: the portal may be offered to all clients or only to clients with ongoing advisory plans. The README describes MCP communication transports, including `stdio`, `http`, and Streamable HTTP. It does not explain whether these transports require access to be limited to a particular client group, so this question remains unanswered. The README describes MCP communication, not document delivery by the portal.

**Limitation**

The README is technical documentation for the LangChain MCP adapter. It does not provide the portal’s infrastructure requirements or resolve the client-access decision.

**Evidence note**

The notebook contains the tool-call logs and returned content. I checked the FAQ and README results against the final answer. The README is technical documentation for the LangChain MCP adapter, so it cannot resolve the portal’s infrastructure or client-access decisions.

## Step 6 — Combined query: project facts and MCP transport

**Question**

Who is responsible for project PCI-02, and what is its target launch date? Also, which transport does the `README.md` show for starting a local MCP server? Does this transport prove that project data stays on the local machine?

**Tool evidence**

- Filesystem `list_directory` showed `faq.md` and `project_notes.md`.
- Filesystem `read_text_file` read `project_notes.md`. It identifies Lucía Fernández Arroyo as responsible for the project and gives the target launch date as 30 June 2027.
- GitHub `get_file_contents` read `README.md` from `langchain-ai/langchain-mcp-adapters` (SHA: `0d3e7d0fc7c4facdf437445eaeeb71102de4befe`). The README shows a local server example using `stdio`.

**Final answer**

The project notes name Lucía Fernández Arroyo as responsible for PCI-02 and set its target launch date as 30 June 2027. The README shows `stdio` in an example for starting a local MCP server. That example does not prove that project data stays on the local machine; the README does not establish where the model or application processes or stores data.

**Limitation**

The project information comes from fictional lab documents. The README is technical documentation for the MCP adapter and does not describe the PCI-02 system or guarantee its data residency.