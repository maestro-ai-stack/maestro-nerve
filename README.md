<p align="center"><img src=".github/maestro-logo.png" alt="Maestro" width="120" /></p>
<h1 align="center">maestro-nerve</h1>
<p align="center"><b>Shared, evidence-grounded memory for AI agents.</b></p>
<p align="center"><i>One workspace memory plane for Claude Code, Codex, ChatGPT, Claude Desktop, and custom MCP clients.</i></p>

<p align="center">
  <a href="https://pypi.org/project/maestro-nerve/"><img src="https://img.shields.io/pypi/v/maestro-nerve.svg" alt="PyPI version" /></a>
  <a href="https://pypi.org/project/maestro-nerve/"><img src="https://img.shields.io/pypi/pyversions/maestro-nerve.svg" alt="Python versions" /></a>
  <a href="https://github.com/maestro-ai-stack/maestro-nerve/actions/workflows/ci.yml"><img src="https://github.com/maestro-ai-stack/maestro-nerve/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT" /></a>
</p>

`maestro-nerve` is the public client distribution for Maestro Nerve. It ships:

- `mnerve`, a production CLI for login, workspace inspection, and MCP config generation.
- Claude Code and Codex plugin manifests.
- A portable agent skill that explains the hosted MCP tool contract.
- A thin HTTP client against `https://nerve-api.maestro.onl`.

The backend is hosted by Maestro and remains closed source. This repository does not contain retrieval, ranking, extraction, normalization, storage schema, or reconciliation logic.

## Quick Start

Use `uv` or `pipx` for the CLI. They install Python command-line applications in isolated tool environments and avoid modifying a project virtualenv.

```bash
uv tool install maestro-nerve
mnerve login
mnerve access --client claude-code --format mcp-json
```

Other good install paths:

```bash
# Run once without a persistent install.
uvx maestro-nerve login

# Persistent CLI install with pipx.
pipx install maestro-nerve

# Fallback when your environment already manages Python packages.
python -m pip install --user maestro-nerve
```

`mnerve login` opens the hosted Maestro login page and completes through a local loopback callback on `127.0.0.1`. It does not use `localhost:3000` in production. For SSH or browser-restricted sessions:

```bash
mnerve login --no-browser
mnerve login --manual
```

Development builds can explicitly target a local web app:

```bash
mnerve login --app-url http://localhost:3000
```

## Agent Setup

Install the CLI once, then ask the backend for the exact MCP config shape your host expects:

```bash
mnerve access --client claude-code --format mcp-json
mnerve access --client codex --format mcp-json
mnerve access --client chatgpt --format envelope
```

Supported formats:

| Format | Use |
|---|---|
| `envelope` | Script-friendly response with client, transport, workspace, endpoint, config, and note. |
| `mcp-json` | Pasteable MCP server JSON. |
| `settings-json` | JSON shaped for settings files that merge under `mcpServers`. |
| `env` | `KEY=value` lines for shell launchers and automation. |

Human hints are written to stderr. Stdout remains parseable.

## Claude Code Plugin

```text
/plugin marketplace add maestro-ai-stack/maestro-nerve
/plugin install maestro-nerve@maestro-nerve
/reload-plugins
```

The plugin brings the skill and metadata. The hosted MCP connection still needs CLI auth:

```bash
uv tool install maestro-nerve
mnerve login
mnerve access --client claude-code --format mcp-json
```

## Codex Plugin

```bash
codex plugin add maestro-ai-stack/maestro-nerve
uv tool install maestro-nerve
mnerve login
mnerve access --client codex --format mcp-json
```

If your agent/plugin tooling is installed with npm, pnpm, or Bun, keep using that tool for the host. `mnerve` itself is distributed as a Python CLI on PyPI, so `uv` or `pipx` is the cleaner install path for the command.

## Skill Only

Use this when the host already has an MCP connection and only needs agent instructions:

```bash
npx skills add maestro-ai-stack/maestro-nerve -y -g
```

Equivalent package runners such as `pnpm dlx` or `bunx` are fine if your local skill manager supports them.

## CLI Commands

```text
mnerve login                              # browser login; stores local credentials
mnerve login --manual                     # paste an API key
mnerve logout                             # remove local credentials
mnerve whoami                             # print backend identity + primary workspace
mnerve workspace list                     # list reachable workspaces
mnerve status                             # one-line reachability probe
mnerve access --client <c> --format <f>   # print MCP config for a host
mnerve serve-mcp                          # optional stdio MCP dev fallback
mnerve version                            # installed package version
```

## Authentication

- Browser login uses a loopback callback on `http://127.0.0.1:<ephemeral-port>/callback` plus PKCE.
- Credentials are stored in the platform user config directory, for example `~/Library/Application Support/maestro/auth.json` on macOS or `~/.config/maestro/auth.json` on Linux.
- The auth file is written with mode `0600` where the OS allows it.
- Override the auth path with `MAESTRO_AUTH_FILE=/path/to/auth.json`.
- Override the hosted API with `NERVE_API_BASE_URL=...`.
- Override the web login app with `NERVE_APP_URL=...` or `mnerve login --app-url ...`.
- `mnerve logout` removes only the local file. Revoke server-side keys from the Maestro web app.

## MCP Surface

Hosted MCP endpoint:

```http
POST https://nerve-api.maestro.onl/api/mcp?workspace=<workspace-slug>
Authorization: Bearer <maestro-api-key>
Content-Type: application/json
```

Tools:

| Tool | Purpose |
|---|---|
| `server_info` | Connectivity, workspace binding, server version, tool names. |
| `search_workspace` | Ranked search across entities, claims, and evidence. |
| `list_entities` | Browse or paginate workspace entities. |
| `inspect` | Aliases, claims, and evidence for one entity. |
| `profile` | Narrative briefing synthesized from grounded memory. |
| `ground` | Evidence records for a claim. |
| `discover` | Time-axis feed of recent workspace changes. |
| `act.draft` | Draft an action from memory; never executes externally. |

## Development

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
```

Release notes:

- Version lives in `pyproject.toml`.
- Update `CHANGELOG.md` in the release PR.
- Push `v<x.y.z>` to trigger PyPI publishing through GitHub trusted publishing.

## License

MIT. Built by [Maestro](https://maestro.onl).
