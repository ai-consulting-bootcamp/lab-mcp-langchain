"""Small, auditable dataset and deterministic retrieval used by the MCP tool."""
from __future__ import annotations
import json
import re

RECORDS = [
    {"id": "N1", "source": "mcp_tools_resources_prompts.md", "section": "The three at a glance", "text": "Tools are functions the LLM can call to act. The model decides when to call a tool."},
    {"id": "N2", "source": "mcp_tools_resources_prompts.md", "section": "Resources: providing information", "text": "A resource is information the application reads from the server and hands to the LLM as context. Reading a resource never creates, changes or deletes anything."},
    {"id": "N3", "source": "mcp_tools_resources_prompts.md", "section": "Prompts: guiding the LLM", "text": "A prompt is a ready-made recipe of instructions that the server offers for a common task. The user chooses the prompt."},
    {"id": "N4", "source": "mcp_servers_local_vs_remote.md", "section": "Where Does an MCP Server Live?", "text": "A local MCP server runs on your computer. You start it using a command, and its transport is stdio. A remote MCP server uses a URL and HTTP."},
]


def search_notes(query: str) -> str:
    """Return exact, cited records using conservative token overlap; no LLM involved."""
    words = set(re.findall(r"[a-zA-Z]+", query.lower())) - {"a", "an", "the", "is", "are", "who", "does", "what", "and", "of", "in", "to", "mcp", "server", "which", "controls", "control"}
    results = []
    for record in RECORDS:
        text_words = set(re.findall(r"[a-zA-Z]+", (record["text"] + " " + record["section"]).lower()))
        score = len(words & text_words)
        if score:
            results.append((score, record))
    results.sort(key=lambda item: (-item[0], item[1]["id"]))
    return json.dumps({"query": query, "matches": [{**record, "score": score} for score, record in results[:3]], "notice": "Evidence is limited to the four curated course-note records."}, indent=2)
