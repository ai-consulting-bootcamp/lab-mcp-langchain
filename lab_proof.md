# Lab Proof: Agents that speak MCP fluently

## Project

A LangChain agent uses two MCP capabilities in one small workflow:

1. A local stdio MCP server publishes a read-only CRM field guide as a
   resource.
2. HubSpot's hosted MCP server exposes a read-only CRM search tool.

The resource explains field semantics; the HubSpot tool is the source of live
company values. No CRM write operation is exposed to the agent.

## Setup and workflow

Install the pinned packages from `requirements.txt`. Put the HubSpot OAuth
access token in a local `.env` file as `HUBSPOT_ACCESS_TOKEN`; do not commit
that file. The script loads the token from the environment and never prints it.

Run `python mcp_langchain.py`. The script:

1. Starts `crm_context_server.py` as a local MCP stdio subprocess.
2. Initializes a `ClientSession`, lists the server's resources, and reads
   `crm://field-guide` with the MCP resource API.
3. Connects to `https://mcp.hubspot.com/` over Streamable HTTP and discovers
   its tools through `langchain-mcp-adapters`.
4. Gives the field guide to a LangChain agent as interpretation context, and
   gives the agent only the read-only `search_crm_objects` tool.
5. Prints the resource text and LangChain message/tool trace for inspection.

## Query

> Find the company named HubSpot. Report its name and domain. If the CRM search
> returns no matching record, say so.

## MCP resource evidence

The local server advertises `crm://field-guide`. The text returned by
`read_resource` includes:

> `name`: the CRM record's company name; use this to identify a company by
> name. `domain`: the company's internet domain, such as example.org; this is
> the requested business value in this lab. The guide also says to use the
> HubSpot search result as the authoritative evidence for actual values.

## MCP tool evidence

Tool: `search_crm_objects`

Input:

```json
{
  "objectType": "companies",
  "query": "HubSpot",
  "properties": ["name", "domain"]
}
```

The captured HubSpot result contained one record with:

```json
{
  "name": "HubSpot",
  "domain": "hubspot.com"
}
```

Internal record IDs and record URLs are omitted from this proof.

## Final output

The company named HubSpot has the following properties:

- Name: HubSpot
- Domain: hubspot.com

## Grounding check

The local MCP resource informed the meaning of `name` and `domain` but did not
provide a company value. Both values in the answer match the HubSpot tool
result. If the search returns no record, the agent is instructed to report
that and not infer values from the field guide.

## Failure or limitation

A search for `test` returned zero records, while searching for `HubSpot`
returned the company. This demonstrates that empty results depend on query
terms and searchable properties; they do not establish that no relevant
record exists.

The HubSpot connection currently uses a static OAuth access token in the
local environment. Tokens expire, so a later run may return `401 Unauthorized`
until the authorization is refreshed. This example does not automate token
refresh. The local field guide is static educational context; it does not
demonstrate reading HubSpot's own business data through an MCP Resource.

## Scope

This lab demonstrates MCP resource discovery and reading, MCP tool discovery
and use, LangChain tool integration, and an answer grounded in inspectable
evidence. It does not prove integration with an on-premises CRM, email server,
or SharePoint deployment.
