# MCP Server: Tools, Resources and Prompts

An MCP server can offer an AI application **three kinds of things**. To keep it simple, we use **one example for all three: a Calendar MCP server.**

**On this page**

1. [The three at a glance](#the-three-at-a-glance)
2. [Tools: doing something](#1-tools-doing-something)
3. [Resources: providing information](#2-resources-providing-information)
4. [Prompts: guiding the LLM](#3-prompts-guiding-the-llm)
5. [A common confusion](#a-common-confusion)
6. [In today's notebook](#in-todays-notebook)
7. [Takeaway](#takeaway)

---

## The three at a glance

| | **Tools** | **Resources** | **Prompts** |
|---|---|---|---|
| **In one word** | Do | Inform | Guide |
| **What it is** | Functions the LLM can call to act: write to databases, call APIs, change files, trigger other logic | Read-only information the application fetches and gives to the LLM as context: file contents, database schemas, documentation | Ready-made instruction templates that tell the LLM how to approach a task using the server's tools and resources |
| **Slide examples** | Search flights<br>Send messages<br>Create calendar events | Retrieve documents<br>Access knowledge bases<br>Read calendars | Plan a vacation<br>Summarize my meetings<br>Draft an email |
| **Who controls it** | **The model** decides when to call it | **The application** decides what to read and show the model | **The user** picks it |
| **Calendar example** | `create_event` | Tomorrow's meetings | "Prepare my daily schedule" |

> **Easy way to remember:** a **tool** is like a button the AI can press. A **resource** is like a document the AI can read. A **prompt** is like a recipe the AI can follow.

---

## 1. Tools: doing something

> **A tool is a function the LLM can ask the server to run.**

**At a glance**

- **Purpose:** perform an action
- **Controlled by:** the model
- **Calendar example:** `create_event`

### Step 0: Discovery (happens before the user asks anything)

When the application starts, its MCP client connects to the server and asks: **"What can you do?"** (`tools/list`)

The server replies with each tool's **name**, **description** and **inputs**:

```json
{
  "name": "create_event",
  "description": "Create a new event in the user's calendar",
  "inputSchema": { "title": "string", "date": "string", "time": "string" }
}
```

- The application gives this list to the LLM along with every user message.
- The LLM does **not** know the tools by itself. It **reads the descriptions** and picks the one that fits.

### Example

**User:** "Create a meeting called *Project Review* tomorrow at 10:00."

**How it works**

1. The LLM reads the tool descriptions and decides: *"I need `create_event`."*
2. The AI application passes the request to its MCP client.
3. The MCP client sends the request to the Calendar MCP server.
4. The server creates the event in the real calendar (for example, Google Calendar).
5. The server sends the result back to the MCP client.
6. The application gives the result to the LLM.
7. The LLM tells the user: *"Done, Project Review is booked for 10:00."*

### Behind the scenes

**Request: MCP client → server** ("please run this tool with these details")

```json
{
  "method": "tools/call",
  "params": {
    "name": "create_event",
    "arguments": { "title": "Project Review", "date": "2026-10-28", "time": "10:00" }
  }
}
```

**Response: server → MCP client** ("done, here's the result")

```json
{
  "result": {
    "content": [
      { "type": "text", "text": "Event 'Project Review' created for 2026-10-28 at 10:00." }
    ]
  }
}
```

### Key points

- The **LLM asks** for the action. The **server does** it. The LLM never runs the server's code itself.
- The **model decides when** a tool is needed, based on what you asked.
- Many applications **ask you to confirm** before an action actually happens.

---

## 2. Resources: providing information

> **A resource is information the application reads from the server and hands to the LLM as context.** Like opening a file, reading it changes nothing.

**At a glance**

- **Purpose:** provide information
- **Controlled by:** the application
- **Calendar example:** tomorrow's meetings, at the address `calendar://events/tomorrow`

### Example

**User:** "What meetings do I have tomorrow?"

**How it works**

1. The AI application decides: *"Tomorrow's calendar would help here."*
2. The MCP client sends a request to read the resource `calendar://events/tomorrow`.
3. The server fetches the calendar data (only what the user is allowed to see).
4. The server sends the data back to the MCP client.
5. The application gives the data to the LLM as context.
6. The LLM answers: *"You have two meetings: Team Meeting at 10:00 and Project Review at 14:00."*

### Behind the scenes

**Request: MCP client → server** ("please give me this resource")

```json
{
  "method": "resources/read",
  "params": { "uri": "calendar://events/tomorrow" }
}
```

**Response: server → MCP client** ("here's what's in it", example data)

```json
{
  "result": {
    "contents": [
      {
        "uri": "calendar://events/tomorrow",
        "mimeType": "application/json",
        "text": "{ \"events\": [ { \"title\": \"Team Meeting\", \"time\": \"10:00\" }, { \"title\": \"Project Review\", \"time\": \"14:00\" } ] }"
      }
    ]
  }
}
```

- The `uri` is just the resource's **address**, like a file path. Each server chooses its own addresses.
- Like tools, the client can first ask which resources exist (`resources/list`).

### Fixed or changing?

A resource's content can be either:

| | **Fixed content** | **Changing content** |
|---|---|---|
| **Example** | The "LangChain skill" handbook in today's notebook (`mintlify://skills/langchain`) | Tomorrow's meetings (`calendar://events/tomorrow`) |
| **Like…** | A printed manual on the shelf | A noticeboard that gets updated |

Servers can also offer **address templates** like `calendar://events/{date}`, where the application fills in the date.

### Key points

- Same **request → response** pattern as tools. The difference is **who starts it**: the application, not the model.
- The **application decides** what to read and what the LLM gets to see. The model can't grab anything on its own.
- Reading a resource **never creates, changes or deletes** anything.

---

## 3. Prompts: guiding the LLM

> **A prompt is a ready-made recipe of instructions that the server offers for a common task.**

**At a glance**

- **Purpose:** guide the LLM through a task
- **Controlled by:** the user
- **Calendar example:** `prepare_daily_schedule`

### What's inside the prompt

> Review the user's calendar for the requested day. Sort meetings by start time, point out any meetings that overlap, and write a short schedule with titles and times. Do not invent missing information.

### How it works

1. The user picks **"Prepare my daily schedule"**, usually from a menu or a `/command` in the app.
2. The MCP client gets the prompt template from the server.
3. The application gives those instructions to the LLM.
4. The LLM follows the steps, using the calendar **resource** or **tools** when it needs data.
5. The user gets a clean daily schedule.

### Key points

- A prompt **doesn't fetch data or do anything** by itself. It tells the LLM **how** to approach the task.
- The **tools and resources** do the actual work.
- The **user chooses** the prompt.

> **Resource or prompt? A quick test.**
> - Does it contain a **fact** (tomorrow's meetings)? That's a **resource**.
> - Does it contain **steps** (how to build a schedule)? That's a **prompt**.

---

## A common confusion

**"Reading = resource, doing = tool"?** That's a good first guess, but **not the real rule.**

- **The server's developer decides** what to offer as a tool and what to offer as a resource.
- Some calendar servers offer `list_events` as a **tool**, even though it only reads.
- So the real difference is **who decides**:
  - the **model** calls **tools**
  - the **application** reads **resources**
  - the **user** picks **prompts**

---

## In today's notebook

We connect to the **LangChain Documentation MCP server** (`https://docs.langchain.com/mcp`). Here is what it offers:

| What | Type | Reads or changes something? |
|---|---|---|
| `search_docs_by_lang_chain` | **Tool** | Only reads |
| `query_docs_filesystem_docs_by_lang_chain` | **Tool** | Only reads |
| `submit_feedback` | **Tool** | Sends something |
| "LangChain skill" handbook (`mintlify://skills/langchain`) | **Resource** | Only reads |
| *(none)* | **Prompt** | |

Things to notice:

- **Two tools only read, but they're still tools.** The model calls them with your question. This is the "common confusion" in action.
- **Not every server offers all three.** This one has 3 tools, 1 resource and 0 prompts. Tools are the most common; prompts are the rarest.
- **The agent never sees the resource.** In the code, `get_tools()` is passed to the agent, but `get_resources()` is only printed. The resource reaches the LLM only if *our code* passes it on. That's **"the application controls resources"** in practice.

```python
tools = await mcp_client.get_tools()            # discovery: given to the agent
agent = create_agent(model=llm, tools=tools)    # the agent knows only these 3 tools

resources = await mcp_client.get_resources()    # read, but NOT given to the agent
```

---

## Takeaway

| | | | |
|---|---|---|---|
| **Tools** | **Do** | The LLM asks, the server acts | Controlled by the **model** |
| **Resources** | **Inform** | The application reads, the LLM gets context | Controlled by the **application** |
| **Prompts** | **Guide** | Ready-made instructions for a task | Controlled by the **user** |
