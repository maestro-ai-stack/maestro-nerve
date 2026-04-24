#!/usr/bin/env bash
# harness-fast.sh — local pre-commit gate for the public maestro-nerve repo.
#
# Mirrors the GitHub CI `test` + `manifest-check` jobs without a matrix,
# so you can reproduce the PR gate in under 10 seconds from a warm venv.
#
# Usage:
#   ./scripts/harness-fast.sh              # lint + tests + coverage + manifest check
#   COVERAGE_MIN=80 ./scripts/harness-fast.sh
#
# Exits non-zero on any step failure.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

: "${COVERAGE_MIN:=75}"
: "${PY:=python}"

# Prefer the repo-local venv if it exists.
if [[ -x ".venv/bin/python" ]]; then
  PY=".venv/bin/python"
fi

echo "[harness] lint"
"$PY" -m ruff check src tests

echo "[harness] tests + coverage (min ${COVERAGE_MIN}%)"
"$PY" -m pytest \
  --cov=maestro_nerve \
  --cov-report=term-missing \
  --cov-fail-under="$COVERAGE_MIN" \
  -q

echo "[harness] manifest sanity"
"$PY" - <<'PY'
import json
import tomllib
from pathlib import Path

root = Path(".")


def load_json(p: str) -> dict:
    return json.loads((root / p).read_text(encoding="utf-8"))


claude = load_json(".claude-plugin/plugin.json")
marketplace = load_json(".claude-plugin/marketplace.json")
codex = load_json(".codex-plugin/plugin.json")
pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
version = pyproject["project"]["version"]

assert claude["name"] == "maestro-nerve"
assert claude["version"] == version, (claude["version"], version)
assert codex["version"] == version, (codex["version"], version)
assert any(p["name"] == "maestro-nerve" for p in marketplace["plugins"])
print(f"manifests ok @ {version}")
PY

echo "[harness] OK"
