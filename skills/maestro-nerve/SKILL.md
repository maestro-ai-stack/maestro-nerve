---
name: maestro-nerve
description: Shared intelligence memory plane for AI agents. Use when an agent (Claude Code, Claude Desktop, Codex, ChatGPT) needs workspace-scoped evidence-grounded memory — search entities / claims / evidence, inspect one entity in detail, ground a claim, profile an entity, or discover what changed recently. Triggers keywords — nerve, mnerve, workspace memory, shared agent memory, procurement memory, compliance memory, tender review, 知识层, 共享记忆, 工作空间记忆. Do NOT use for — Claude Code's built-in auto-memory (different scope), /recall (past sessions), or raw file reading.
---

# maestro-nerve skill

## What this skill is for

`maestro-nerve` is the shared intelligence memory plane for AI agents. Your agent runs in its own process, but the **memory is one workspace-scoped substrate shared with every other agent your user touches** — Claude Code, Claude Desktop, Codex, ChatGPT, or a custom tool. The substrate is reached via the Maestro remote MCP surface.

Seven tools, read-first, workspace-bound:

| Tool | Use when |
|------|----------|
| `search_workspace(query, limit?)` | You need ranked entities + claims + evidence across all sources in the current workspace. |
| `list_entities(category?, limit?, cursor?)` | You want to browse or paginate entities without a query. |
| `inspect(entity_id)` | You already have an entity id and want aliases, claims, and evidence in one call. |
| `profile(entity_id, focus?)` | You want a narrative briefing synthesized from grounded memory (LLM-backed, billable). |
| `ground(claim_id, limit?)` | You have a claim id and need the supporting evidence records with source object refs. |
| `discover(since, subject_entity_id?, event_kinds?)` | You want a time-axis feed of what changed (state changes, new claims, etc.). |
| `act.draft(kind, context)` | You want a candidate action (email, reply, task) drafted from workspace memory; this never executes against external systems. |

Plus `server_info()` — a free probe that returns workspace binding + version + tool names. Call it first to confirm connectivity.

## Before you use the skill

The user needs:
1. A Maestro API key — minted at <https://nerve.maestro.onl/access>.
2. The MCP endpoint registered with their host. Either:
   - `pip install maestro-nerve && mnerve login && mnerve access --client <their client>`
   - OR install the Claude Code plugin via `/plugin marketplace add maestro-ai-stack/maestro-nerve`
   - OR (skill-only) `npx skills add maestro-ai-stack/maestro-nerve`

If the MCP surface is unreachable, refer the user to the README `Install` section and stop — do not try to simulate memory locally.

## How to decide which tool to call

- **"What do we know about X?"** → `search_workspace(query="X")`.
- **"Tell me about entity ent_123"** → `inspect(entity_id="ent_123")`. If you need prose not bullets, follow with `profile`.
- **"Why do you believe this claim?"** → `ground(claim_id="claim_123")`.
- **"What happened in the last 7 days?"** → `discover(since="2026-04-17T00:00:00Z")`.
- **"Draft a reply"** → `act.draft(kind="email_reply", context={...})`. Review the draft with the user — the tool is advisory, never executes.
- Ambiguous request → use `server_info` to confirm workspace binding first, then prefer `search_workspace` over `list_entities`.

## Guarantees and constraints

- **Workspace-scoped.** Every call runs against exactly one workspace (the one bound to the API key). Cross-workspace search is not available via MCP.
- **Evidence-grounded.** Every claim comes with an evidence record pointing at a source object — quote the evidence, don't invent.
- **Read-first V1.** `act.draft` is the only write-ish tool and it never mutates the graph. To write facts, the user should use the web app's Brain surface; agent-authored writes are on the roadmap.
- **Workspace binding is enforced server-side.** A 403 means you are trying to reach a workspace not owned by this API key — do not retry.

## Troubleshooting

- `401 missing api key` — the user has not run `mnerve login` (or the MCP client is not sending the Bearer header).
- `401 invalid api key` — the key was revoked or mis-pasted; `mnerve login` again.
- `403 workspace access denied` — the `?workspace=<slug>` in the MCP URL does not belong to this key.
- `ModuleNotFoundError: mcp` from `mnerve serve-mcp` — the stdio proxy is an optional extra: `pip install 'maestro-nerve[mcp-stdio]'`. Prefer remote MCP instead.

See `references/tools.md` for per-tool request/response examples.
