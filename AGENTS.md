# maestro-nerve (public) — Agent Instructions

This repo ships the **public distribution surface** for Maestro Nerve:
CLI (`mnerve`), Claude Code / Codex plugin manifests, a skill, and a thin
HTTP client against `https://nerve-api.maestro.onl`.

The **backend source is closed**; it lives in a private sibling repo
(`maestro-ai-stack/maestro-nerve-internal`). Do not copy backend logic,
storage schema, or extraction pipelines into this repo.

## Scope

In scope:
- CLI UX: login, logout, whoami, access config printing, workspace list.
- Plugin / marketplace / skill manifests for Claude Code and Codex.
- Minimal stdio MCP proxy (`mnerve serve-mcp`) as a dev fallback only.
- HTTP client against the hosted API — thin, typed, retryable.
- Tests, CI, release automation (PyPI via trusted publisher).

Out of scope:
- Retrieval, ranking, extraction, normalization, reconciliation — live in the
  private backend.
- Any direct DB / blob store access.
- Duplicating business logic from the backend.

## Engineering Principles

- Depend on the narrowest useful set: `httpx`, `typer`, `rich`, `platformdirs`. `mcp` is an optional extra.
- Treat the hosted API as the source of truth; new client formats should be
  added to `/api/auth/cli/mcp-access` first, then surfaced via CLI.
- Keep CLI stdout pipe-friendly (JSON or `KEY=value` lines); send human hints
  to stderr.
- Every CLI command has a test; every HTTP client method has a respx test.
- Coverage gate in CI: ≥ 85% on `src/maestro_nerve/`.

## Release

- Version lives in `pyproject.toml` only.
- Push a tag `v<x.y.z>` to trigger `.github/workflows/release.yml` which
  publishes to PyPI via trusted publisher (no API key stored in repo).
- Update `CHANGELOG.md` in the same PR that bumps the version.
