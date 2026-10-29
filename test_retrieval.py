"""Offline check of the exact evidence function (does not claim an MCP test)."""
import json
from evidence import search_notes

q = "Who controls MCP resources, and does reading one change data?"
result = json.loads(search_notes(q))
assert result["matches"], "Expected relevant evidence"
assert result["matches"][0]["id"] == "N2", result
assert "never creates, changes or deletes" in result["matches"][0]["text"]
print("OFFLINE_RETRIEVAL_TEST: PASS")
print(json.dumps(result, indent=2))

no_match = json.loads(search_notes("quantum banana"))
assert no_match["matches"] == [], "Unexpected evidence for unsupported query"
print("UNSUPPORTED_QUERY_TEST: PASS (no fabricated matches)")
