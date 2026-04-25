# Changelog

All notable changes to this project will be documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] — 2026-04-25

Production CLI login and public distribution polish.

### Added

- Browser-based `mnerve login` with hosted Maestro login, loopback callback, and PKCE.
- Manual API-key login fallback via `mnerve login --manual` and `mnerve login --api-key`.
- Production CLI research notes for native-app auth and CLI installation.

### Changed

- Reworked README install paths around `uv tool install`, `uvx`, `pipx`, and `python -m pip` instead of assuming `pip3`.
- Updated Claude Code, Codex, marketplace, skill, and reference copy for a more professional public distribution surface.
- Clarified that `localhost:3000` is development-only via `mnerve login --app-url http://localhost:3000`.

## [0.1.0] — 2026-04-24

Initial public release.

### Added

- `mnerve` CLI with commands: `login`, `logout`, `whoami`, `access`, `workspace list`, `status`, `serve-mcp`.
- Thin HTTP client against `https://nerve-api.maestro.onl`.
- Claude Code plugin + marketplace manifest under `.claude-plugin/`.
- Codex plugin manifest under `.codex-plugin/`.
- Skill at `skills/maestro-nerve/SKILL.md` with the 7 MCP tools' contract.
- Four install paths documented in README: `pip install` + remote MCP; Claude Code plugin; Codex plugin; `npx skills add`.
- Auth storage at `~/.maestro/auth.json` (created by `mnerve login`).
