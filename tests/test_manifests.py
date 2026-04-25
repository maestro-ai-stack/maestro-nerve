"""Validate the plugin manifests + skill metadata.

These tests run without any backend; they just parse and assert shape.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_claude_plugin_manifest_minimum_fields():
    manifest = _read_json(REPO_ROOT / ".claude-plugin/plugin.json")
    for key in ("name", "version", "description", "skills", "license"):
        assert key in manifest, f"missing {key}"
    assert manifest["name"] == "maestro-nerve"
    assert manifest["skills"] == "./skills/"


def test_claude_marketplace_contains_maestro_nerve_plugin():
    marketplace = _read_json(REPO_ROOT / ".claude-plugin/marketplace.json")
    names = [p.get("name") for p in marketplace.get("plugins", [])]
    assert "maestro-nerve" in names
    plugin = next(p for p in marketplace["plugins"] if p["name"] == "maestro-nerve")
    assert plugin["source"] == "./"
    assert plugin["category"]
    keywords = plugin.get("keywords", [])
    assert "mcp" in keywords
    assert "memory" in keywords


def test_codex_plugin_manifest_minimum_fields():
    manifest = _read_json(REPO_ROOT / ".codex-plugin/plugin.json")
    for key in ("name", "version", "description", "cli", "mcp"):
        assert key in manifest, f"missing {key}"
    assert manifest["cli"]["entrypoint"] == "mnerve"
    assert manifest["mcp"]["transport"] == "http"
    assert "${MAESTRO_WORKSPACE}" in manifest["mcp"]["url_template"]


def test_codex_marketplace_plugin_manifest_minimum_fields():
    manifest = _read_json(REPO_ROOT / "plugins/maestro-nerve/.codex-plugin/plugin.json")
    for key in ("name", "version", "description", "cli", "mcp"):
        assert key in manifest, f"missing {key}"
    assert manifest["cli"]["entrypoint"] == "mnerve"
    assert manifest["cli"]["install"] == "uv tool install maestro-nerve"
    assert manifest["mcp"]["transport"] == "http"


def test_codex_marketplace_index_points_to_plugin():
    marketplace = _read_json(REPO_ROOT / ".agents/plugins/marketplace.json")
    names = [p.get("name") for p in marketplace.get("plugins", [])]
    assert "maestro-nerve" in names
    plugin = next(p for p in marketplace["plugins"] if p["name"] == "maestro-nerve")
    assert plugin["source"]["path"] == "./plugins/maestro-nerve"


def test_skill_md_has_frontmatter():
    skill_path = REPO_ROOT / "skills/maestro-nerve/SKILL.md"
    text = skill_path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), "SKILL.md must begin with YAML frontmatter"
    closing = text.find("\n---\n", 4)
    assert closing > 0, "frontmatter must be closed"
    frontmatter = text[4:closing]
    assert "name: maestro-nerve" in frontmatter
    assert "description:" in frontmatter
    assert "Triggers" in frontmatter


def test_skill_md_mentions_seven_tools():
    skill_path = REPO_ROOT / "skills/maestro-nerve/SKILL.md"
    text = skill_path.read_text(encoding="utf-8")
    for tool in (
        "search_workspace",
        "list_entities",
        "inspect",
        "profile",
        "ground",
        "discover",
        "act.draft",
    ):
        assert tool in text, f"SKILL.md must mention {tool}"


def test_manifest_versions_agree_with_pyproject():
    import tomllib

    manifest = _read_json(REPO_ROOT / ".claude-plugin/plugin.json")
    codex = _read_json(REPO_ROOT / ".codex-plugin/plugin.json")
    codex_marketplace = _read_json(REPO_ROOT / "plugins/maestro-nerve/.codex-plugin/plugin.json")
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    py_version = pyproject["project"]["version"]
    assert manifest["version"] == py_version, (
        f".claude-plugin version {manifest['version']} != pyproject version {py_version}"
    )
    assert codex["version"] == py_version, (
        f".codex-plugin version {codex['version']} != pyproject version {py_version}"
    )
    assert codex_marketplace["version"] == py_version, (
        f"plugins/maestro-nerve version {codex_marketplace['version']} != pyproject version {py_version}"
    )
