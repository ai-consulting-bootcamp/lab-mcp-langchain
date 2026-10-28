# Where Does an MCP Server Live?

Every MCP server lives in **one of two places**. That one fact decides how you connect to it.

| | ☁️ **Remote** | 💻 **Local** |
|---|---|---|
| **Where it runs** | On someone else's computer | On **your** computer |
| **What you do** | You **call** it | You **start** it |
| **What you need** | A **URL** | A **command** (`npx` or `uvx`) |
| **Transport** | `http` | `stdio` |

---

## ☁️ Remote server: you need a **URL**

Someone else (LangChain, GitHub, ...) runs the server for you. It's always on. You just call its address.

```python
"langchain-docs": {
    "transport": "http",
    "url": "https://docs.langchain.com/mcp",
}
```

📞 **Like calling a company:** you only need their phone number.

---

## 💻 Local server: you need a **command**

Nobody runs the server for you. Your code **starts** it on your laptop when it needs it.

The command depends on **which language the server was written in**:

| Server written in | Command | You need installed | Where the server comes from |
|---|---|---|---|
| **JavaScript** | `npx` | Node.js | npm |
| **Python** | `uvx` | uv | PyPI |

### 🛠️ How to install them

| | **Node.js** (gives you `npx`) | **uv** (gives you `uvx`) |
|---|---|---|
| **Easiest way** | Download the **LTS** installer from [nodejs.org](https://nodejs.org) and click through it | In your terminal (with your course environment active): `pip install uv` |
| **Windows** (alternative) | `winget install OpenJS.NodeJS.LTS` | `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` |
| **Mac** (alternative) | `brew install node` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Check it worked** | `node -v` and `npx -v` | `uvx --version` |
| **Then** | Restart VS Code | Restart VS Code / the notebook kernel |

### JavaScript server: `npx`

```python
"filesystem": {
    "transport": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "sample_docs"],
}
```

### Python server: `uvx`

```python
"time": {
    "transport": "stdio",
    "command": "uvx",
    "args": ["mcp-server-time"],
}
```

🧑‍💼 **Like bringing an assistant to your desk:** they aren't there until you invite them.

> 💡 `npx` and `uvx` do the same job for different languages: **download the server and start it** in one step.

---

## How do I know which one to use?

Look at the server's README. It always tells you one of these:

| If the README shows... | It's a... | You write... |
|---|---|---|
| A link like `https://.../mcp` | ☁️ Remote server | `"transport": "http"` + `"url"` |
| `npx ...` | 💻 Local JavaScript server | `"transport": "stdio"` + `"command": "npx"` |
| `uvx ...` | 💻 Local Python server | `"transport": "stdio"` + `"command": "uvx"` |

---

## 🔎 Where do I find MCP servers?

Look in this order:

| # | Where | What you get there | Trust |
|---|---|---|---|
| 1 | **The company's own docs** (GitHub, Notion, Stripe, Atlassian...) | The **official** server for their product, with setup and login steps | ✅ Best choice |
| 2 | **Official MCP Registry**: [registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io) | The official list. Each entry shows the **package name**, **version**, **local or remote**, and a **link to the code** | ✅ Publisher is checked, code is not |
| 3 | **Smithery**: [smithery.ai](https://smithery.ai) | Big catalog with **usage numbers**, a **security scan** result, ready **install commands**, and an option to **run the server for you** (hosted) | ⚠️ Check each server |
| 4 | **PulseMCP** ([pulsemcp.com](https://www.pulsemcp.com)), **mcp.so** | Large community directories with search and short descriptions. Good for **discovering ideas** | ⚠️ Anyone can be listed |
| 5 | **Reference servers**: [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | 7 small example servers (Filesystem, Time, Fetch...) | 🎓 For **learning** only |

> 💡 **Quick tip:** in the official registry, a name like `io.github.<company>/...` or `com.<company>/...` means that company really published it.

---

## 🛡️ Can I trust this server?

An MCP server is **code that runs with your files and your passwords**, or a service that **receives your data**. Treat it like installing an app. Ask 5 questions:

| # | Ask | Where to check | 🚩 Red flag |
|---|---|---|---|
| 1 | **Who made it?** | Registry name, GitHub owner | An unknown person, not the company itself |
| 2 | **Is it still looked after?** | GitHub: last commit, open issues | No updates for months, or marked *deprecated* |
| 3 | **What can it reach?** | README: what folder, token or account it needs | Access to all your files, or a token with full rights |
| 4 | **Where does my data go?** | Local or remote? Hosted by whom? | A remote server outside the client's country or company, or a third party holding your token |
| 5 | **Did a scan find problems?** | Security scan on Smithery (MCP-Scan) | Warnings, or no scan at all |

**Then, when you use it:**

- 📌 **Pin the version** (e.g. `@modelcontextprotocol/server-memory@<version>`), so it can't change behind your back.
- 🧪 **Try it first** with a test folder or test account, never real client data.

> ⚠️ **"It's in the official registry" ≠ "it's safe".** The registry only checks **who** published a server, not **what its code does**.
>
> ⚠️ **"Lots of people use it" ≠ "it's safe".** Popularity only tells you it's widely used.

---

## 🔑 Remember

1. **Remote = URL.** Someone else runs it; you call it.
2. **Local = command.** You start it: `npx` for JavaScript, `uvx` for Python.
3. **For your agent, it makes no difference.** The tools look and work exactly the same, wherever the server lives.
4. **Find servers from the company itself first, check them before you trust them, and pin the version.**
