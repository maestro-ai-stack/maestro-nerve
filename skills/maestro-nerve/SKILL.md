---
name: maestro-nerve
description: Shared intelligence memory plane for AI agents. Use when Claude Code, Codex, ChatGPT, Claude Desktop, or another MCP host needs workspace-scoped evidence-grounded memory: search workspace memory, inspect entities, ground claims, profile entities, discover changes, or draft from known context. Triggers: nerve, mnerve, workspace memory, shared agent memory, MCP memory, evidence, claims, entities, procurement memory, compliance memory, tender review, 知识层, 共享记忆, 工作空间记忆. Do NOT use for raw file reading, local session recall, or the host's private auto-memory.
---

# maestro-nerve

Maestro Nerve is a hosted MCP memory plane. Treat it as shared infrastructure: one workspace-scoped memory substrate that multiple agents can read, with claims tied back to evidence.

Call `server_info()` first when the connection is new or uncertain. It confirms the workspace binding, server version, and available tools.

## Tools

| Tool | Use |
|---|---|
| `server_info()` | Verify connectivity and workspace binding. |
| `search_workspace(query, limit?)` | Find entities, claims, and evidence by natural-language query. |
| `list_entities(category?, limit?, cursor?)` | Browse known entities when there is no precise query. |
| `inspect(entity_id, evidence_limit?)` | Read aliases, claims, and evidence for one entity. |
| `profile(entity_id, focus?, max_tokens?)` | Generate a grounded narrative briefing; LLM-backed and billable. |
| `ground(claim_id, limit?)` | Fetch evidence records for a claim. |
| `discover(since, subject_entity_id?, event_kinds?, limit?)` | Read recent changes on a time axis. |
| `act.draft(kind, context)` | Draft text from workspace memory; it never sends, mutates, or executes. |

## Operating Rules

- Prefer `search_workspace` before answering "what do we know about X?"
- Quote or summarize evidence from `ground` or `inspect`; do not invent missing facts.
- A 401 means credentials are missing or revoked. Ask the user to run `mnerve login`.
- A 403 means the requested workspace is not allowed for this key. Do not retry with guessed slugs.
- `act.draft` is advisory only. Present the draft to the user before any external action.
- Do not simulate Nerve locally if the MCP server is unavailable.

## Setup Hints For Users

Production CLI install:

```bash
uv tool install maestro-nerve
mnerve login
mnerve access --client claude-code --format mcp-json
```

Other supported CLI install paths:

```bash
uvx maestro-nerve login
pipx install maestro-nerve
python -m pip install --user maestro-nerve
```

`mnerve login` uses the hosted Maestro web app by default. It should not redirect to `localhost:3000` unless the user explicitly passes `--app-url http://localhost:3000` for local development.

For headless sessions:

```bash
mnerve login --no-browser
mnerve login --manual
```

Claude Code plugin:

```text
/plugin marketplace add maestro-ai-stack/maestro-nerve
/plugin install maestro-nerve@maestro-nerve
/reload-plugins
```

Codex plugin:

```bash
codex plugin add maestro-ai-stack/maestro-nerve
```

See `references/tools.md` for request and response examples.
