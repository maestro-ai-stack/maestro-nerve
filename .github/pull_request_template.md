<!--
Thank you for contributing to maestro-nerve. This repo is the *public*
distribution surface (CLI + skill + plugin manifests). Backend changes
live in a private sibling repo; if your PR needs a backend change too,
note that here so we can coordinate.
-->

## Summary

<!-- 1-3 bullets describing what this PR changes and why. -->

## Checklist

- [ ] `ruff check src tests` passes
- [ ] `pytest --cov=maestro_nerve` passes (≥75% total coverage)
- [ ] `CHANGELOG.md` updated (under `[Unreleased]` or a new version)
- [ ] If a new MCP client is supported: matching backend change in `maestro-ai-stack/maestro-nerve-internal` is merged or staged
- [ ] Plugin manifests (`.claude-plugin/*.json`, `.codex-plugin/plugin.json`) updated if the skill or client list changed

## Test plan

<!--
- [ ] Unit tests added/updated for new behavior
- [ ] Tested CLI manually in a clean venv: `pip install -e '.[dev]' && mnerve --help`
- [ ] Verified `mnerve access --client <c>` output paste-tests cleanly in the target client
-->
