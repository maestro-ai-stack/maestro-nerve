<p align="center"><img src=".github/maestro-logo.png" alt="Maestro" width="120" /></p>
<h1 align="center">maestro-nerve</h1>
<p align="center"><b>Shared intelligence memory plane for AI agents.</b></p>
<p align="center"><i>One workspace-scoped, evidence-grounded memory. Reachable from Claude Code, Claude Desktop, Codex, ChatGPT, or your own MCP client.</i></p>

<p align="center">
  <a href="https://pypi.org/project/maestro-nerve/"><img src="https://img.shields.io/pypi/v/maestro-nerve.svg" alt="PyPI version" /></a>
  <a href="https://pypi.org/project/maestro-nerve/"><img src="https://img.shields.io/pypi/pyversions/maestro-nerve.svg" alt="Python versions" /></a>
  <a href="https://github.com/maestro-ai-stack/maestro-nerve/actions/workflows/ci.yml"><img src="https://github.com/maestro-ai-stack/maestro-nerve/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT" /></a>
  <a href="https://github.com/maestro-ai-stack"><img src="https://img.shields.io/badge/maestro--ai--stack-skills-6e56cf" alt="Maestro AI Stack" /></a>
</p>

---

`maestro-nerve` is a persistent, workspace-scoped memory substrate for AI agents. Instead of letting every agent (Claude Code / Claude Desktop / Codex / ChatGPT / ...) keep its own private memory silo, Nerve gives all of them **one shared, evidence-grounded memory plane** reachable over MCP.

The seven V1 tools are workspace-bound, read-first, and grounded in source evidence:

| Tool | What it does |
|------|-------------|
| `search_workspace` | Ranked semantic search across entities, claims, and evidence. |
| `list_entities` | Paginated entity browser. |
| `inspect` | Aliases + claims + evidence for one entity. |
| `profile` | Narrative briefing synthesized from grounded memory. |
| `ground` | Evidence records for one claim. |
| `discover` | Time-axis feed of what changed. |
| `act.draft` | Draft an action (email, reply, task) from workspace memory — never executes. |

Plus `server_info` — a free health probe.

## Install (pick one)

You need a Maestro API key first — mint one at <https://nerve.maestro.onl/access>.

### Option A — `pip` + remote MCP (recommended)

```bash
pip install maestro-nerve
mnerve login                                # paste your API key
mnerve access --client claude-code --format mcp-json
# Copy the printed JSON into Claude Code MCP settings. Done.
```

Supported clients today: `claude-code`, `codex`, `chatgpt`.
Formats: `envelope` (default, scripting-friendly), `mcp-json`, `settings-json`, `env`.

### Option B — Claude Code plugin

```
/plugin marketplace add maestro-ai-stack/maestro-nerve
/plugin install maestro-nerve@maestro-nerve
/reload-plugins
```

Plugin brings the skill (agent guidance) and the CLI install hint. You still need `pip install maestro-nerve && mnerve login` for the CLI.

### Option C — Codex plugin

```bash
codex plugin add maestro-ai-stack/maestro-nerve
```

Then `pip install maestro-nerve && mnerve login && mnerve access --client codex`.

### Option D — Skill only (no CLI)

```bash
npx skills add maestro-ai-stack/maestro-nerve -y -g
```

Best for agents that only need the skill guidance and already have an API key in their environment.

## CLI surface

```text
mnerve login                              # paste / prompt for an API key
mnerve logout                             # remove local credentials
mnerve whoami                             # backend confirms identity + primary workspace
mnerve workspace list                     # list workspaces reachable with this key
mnerve status                             # one-line reachability probe
mnerve access --client <c> --format <f>   # print MCP config for host c, shape f
mnerve version                            # installed package version
```

`mnerve access --format` values:

| `--format` | Shape printed on stdout |
|---|---|
| `envelope` (default) | `{client, transport, workspace, endpoint, config, note}` — good for scripts |
| `mcp-json` | Bare `{mcpServers: {...}}` — paste into Claude Desktop / Claude Code |
| `settings-json` | Same as `mcp-json`; merge under `mcpServers` in your `settings.json` |
| `env` | `KEY=value` lines; source into the shell that launches the host |

Hints are printed to stderr so stdout stays parseable.

## Authentication model

- API key lives at `~/.config/maestro/auth.json` (platform-appropriate), mode `0600`.
- Override path with `MAESTRO_AUTH_FILE=/path/to/auth.json`.
- The key is a bearer token for `https://nerve-api.maestro.onl/api/*`. Workspace isolation is enforced server-side; the key cannot reach workspaces it does not own.
- `mnerve logout` removes the local file but does **not** revoke the key server-side. Revoke at <https://nerve.maestro.onl/access>.

## Remote MCP endpoint

```
POST https://nerve-api.maestro.onl/api/mcp?workspace=<your-slug>
Authorization: Bearer <your api key>
Content-Type: application/json
```

Every hosted MCP request is workspace-scoped at the transport. You cannot leak between workspaces with one key.

## Development / internal backend

The backend (pipeline, extraction, Brain UI) is closed source and lives in a private sibling repo. This public repo is the client-only distribution surface. Issues, feature requests, plugin changes: file here. Backend-specific concerns: file here too — we triage and route internally.

## License

MIT — see [LICENSE](LICENSE).

Built by [Maestro](https://maestro.onl) — Singapore AI product studio.
