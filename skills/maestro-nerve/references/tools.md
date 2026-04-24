# MCP tool reference

Canonical request / response shapes for the 7 V1 tools plus `server_info`.
Copy examples into your agent's reasoning context when you need to show the
user what one call looks like end to end.

## `server_info`

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

```json
{"query": "tender deadline Acme", "limit": 5}
```

Response:

```json
{
  "query_id": "search:2026-04-24:...",
  "findings": [
    {
      "entity_id": "ent_1",
      "canonical_label": "Acme Corp Tender",
      "category": "Project",
      "confidence": 0.92,
      "summary_claims": [{"claim_id": "claim_1", "predicate": "state", "value": "blocked"}],
      "evidence_pills": [{"source_kind": "gmail_message", "summary": "..."}]
    }
  ]
}
```

## `list_entities`

```json
{"category": "Organization", "limit": 20}
```

Pagination via opaque `cursor` string.

## `inspect`

```json
{"entity_id": "ent_1", "evidence_limit": 5}
```

## `profile`

```json
{"entity_id": "ent_1", "focus": "compliance risk", "max_tokens": 400}
```

LLM-backed; counts against the workspace credit budget.

## `ground`

```json
{"claim_id": "claim_1", "limit": 10}
```

## `discover`

```json
{"since": "2026-04-17T00:00:00Z", "limit": 20}
```

## `act.draft`

```json
{"kind": "email_reply", "context": {"thread_id": "thr_123", "tone": "formal"}}
```

Response always includes `draft_id`, `draft_text`, and `evidence_refs`. The draft is advisory — the agent should present it to the user before any external action.
