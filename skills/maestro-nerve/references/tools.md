# Maestro Nerve MCP Tool Reference

Use this reference when an agent needs the exact V1 request shape. All calls are scoped to the workspace bound by the MCP endpoint and API key.

## `server_info`

Probe connectivity before relying on memory.

Request:

```json
{}
```

Response:

```json
{
  "server_name": "maestro-nerve",
  "server_version": "0.1.0",
  "workspace": "founder",
  "tools": ["search_workspace", "list_entities", "inspect", "profile", "ground", "discover", "act.draft"]
}
```

## `search_workspace`

Use first for "what do we know about X?"

Request:

```json
{"query": "tender deadline Acme", "limit": 5}
```

Response:

```json
{
  "query_id": "search:2026-04-24:abc123",
  "findings": [
    {
      "entity_id": "ent_1",
      "canonical_label": "Acme Corp Tender",
      "category": "Project",
      "confidence": 0.92,
      "summary_claims": [
        {"claim_id": "claim_1", "predicate": "state", "value": "blocked"}
      ],
      "evidence_pills": [
        {"source_kind": "gmail_message", "summary": "Procurement team asked for revised security annex."}
      ]
    }
  ]
}
```

## `list_entities`

Browse entities when the user asks for a category or inventory.

Request:

```json
{"category": "Organization", "limit": 20, "cursor": null}
```

Response:

```json
{
  "entities": [
    {"entity_id": "ent_1", "canonical_label": "Acme Corp", "category": "Organization"}
  ],
  "next_cursor": null
}
```

## `inspect`

Use after `search_workspace` returns an entity id.

Request:

```json
{"entity_id": "ent_1", "evidence_limit": 5}
```

Response:

```json
{
  "entity_id": "ent_1",
  "canonical_label": "Acme Corp",
  "aliases": ["Acme", "Acme Corporation"],
  "claims": [
    {"claim_id": "claim_1", "predicate": "has_deadline", "value": "2026-05-02"}
  ],
  "evidence": [
    {"evidence_id": "ev_1", "source_kind": "document", "quote": "Submission closes on 2 May 2026."}
  ]
}
```

## `profile`

Use only when the user needs a synthesized briefing. This is LLM-backed and counts against the workspace credit budget.

Request:

```json
{"entity_id": "ent_1", "focus": "compliance risk", "max_tokens": 400}
```

Response:

```json
{
  "profile": "Acme Corp is currently blocked on the security annex...",
  "evidence_refs": ["ev_1", "ev_2"]
}
```

## `ground`

Use when challenged on a claim or when the user asks "why do we believe this?"

Request:

```json
{"claim_id": "claim_1", "limit": 10}
```

Response:

```json
{
  "claim_id": "claim_1",
  "evidence": [
    {"evidence_id": "ev_1", "source_kind": "gmail_message", "quote": "Please revise the security annex before submission."}
  ]
}
```

## `discover`

Use for recent changes or monitoring.

Request:

```json
{"since": "2026-04-17T00:00:00Z", "limit": 20}
```

Response:

```json
{
  "events": [
    {
      "event_id": "evt_1",
      "timestamp": "2026-04-23T09:30:00Z",
      "kind": "claim_added",
      "subject_entity_id": "ent_1",
      "summary": "New deadline claim added from tender document."
    }
  ]
}
```

## `act.draft`

Use for memory-grounded draft text. The tool never sends messages, mutates the graph, or executes external actions.

Request:

```json
{"kind": "email_reply", "context": {"thread_id": "thr_123", "tone": "formal"}}
```

Response:

```json
{
  "draft_id": "draft_1",
  "draft_text": "Thanks for the update. We will revise the annex...",
  "evidence_refs": ["ev_1", "ev_2"]
}
```
