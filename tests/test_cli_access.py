"""Tests for `mnerve access` (MCP config printing)."""

from __future__ import annotations

import json

import httpx
import respx
from typer.testing import CliRunner

from maestro_nerve.cli import app
from maestro_nerve.client import DEFAULT_API_BASE_URL

runner = CliRunner()


def _backend_access_response(fmt: str = "envelope"):
    if fmt == "mcp-json" or fmt == "settings-json":
        payload = {
            "mcpServers": {
                "maestro": {
                    "type": "http",
                    "url": f"{DEFAULT_API_BASE_URL}/api/mcp?workspace=founder",
                    "headers": {"Authorization": "Bearer mnr_live_secret"},
                }
            }
        }
    elif fmt == "env":
        payload = {
            "MAESTRO_API_KEY": "mnr_live_secret",
            "MAESTRO_MCP_URL": f"{DEFAULT_API_BASE_URL}/api/mcp?workspace=founder",
            "MAESTRO_WORKSPACE": "founder",
        }
    else:
        payload = {
            "client": "claude-code",
            "transport": "http",
            "workspace": "founder",
            "endpoint": f"{DEFAULT_API_BASE_URL}/api/mcp?workspace=founder",
            "config": {"mcpServers": {"maestro": {"type": "http"}}},
            "note": "Hosted remote MCP is the supported path.",
        }
    return {
        "client": "claude-code",
        "workspace": "founder",
        "format": fmt,
        "endpoint": f"{DEFAULT_API_BASE_URL}/api/mcp?workspace=founder",
        "payload": payload,
        "hint": "Paste into Claude Code." if fmt == "mcp-json" else "",
    }


@respx.mock
def test_access_requires_login(tmp_auth):
    result = runner.invoke(app, ["access", "--client", "claude-code"])
    assert result.exit_code != 0
    assert "Not logged in" in result.output


@respx.mock
def test_access_rejects_unknown_client(logged_in):
    result = runner.invoke(app, ["access", "--client", "claude-desktop"])
    assert result.exit_code != 0
    assert "client must be one of" in result.output


@respx.mock
def test_access_rejects_unknown_format(logged_in):
    result = runner.invoke(app, ["access", "--client", "claude-code", "--format", "yaml"])
    assert result.exit_code != 0
    assert "format must be one of" in result.output


@respx.mock
def test_access_envelope(logged_in):
    respx.get(f"{DEFAULT_API_BASE_URL}/api/auth/cli/mcp-access").mock(
        return_value=httpx.Response(200, json=_backend_access_response("envelope"))
    )
    result = runner.invoke(app, ["access", "--client", "claude-code", "--no-hint"])
    assert result.exit_code == 0, result.output
    body = json.loads(result.stdout)
    assert body["client"] == "claude-code"
    assert body["transport"] == "http"


@respx.mock
def test_access_mcp_json_stdout_is_pasteable(logged_in):
    respx.get(f"{DEFAULT_API_BASE_URL}/api/auth/cli/mcp-access").mock(
        return_value=httpx.Response(200, json=_backend_access_response("mcp-json"))
    )
    result = runner.invoke(app, ["access", "--client", "claude-code", "--format", "mcp-json", "--no-hint"])
    assert result.exit_code == 0
    body = json.loads(result.stdout)
    assert list(body.keys()) == ["mcpServers"]


@respx.mock
def test_access_env_format(logged_in):
    respx.get(f"{DEFAULT_API_BASE_URL}/api/auth/cli/mcp-access").mock(
        return_value=httpx.Response(200, json=_backend_access_response("env"))
    )
    result = runner.invoke(app, ["access", "--client", "codex", "--format", "env", "--no-hint"])
    assert result.exit_code == 0
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    assert "MAESTRO_API_KEY=mnr_live_secret" in lines
    assert any(line.startswith("MAESTRO_MCP_URL=") for line in lines)


@respx.mock
def test_access_hint_flag_writes_to_stderr(logged_in):
    respx.get(f"{DEFAULT_API_BASE_URL}/api/auth/cli/mcp-access").mock(
        return_value=httpx.Response(200, json=_backend_access_response("mcp-json"))
    )
    result = runner.invoke(app, ["access", "--client", "claude-code", "--format", "mcp-json"])
    assert result.exit_code == 0
    # stdout parses as JSON, stderr contains the hint.
    json.loads(result.stdout)
    assert "hint:" in result.stderr


@respx.mock
def test_access_reports_backend_403_as_error(logged_in):
    respx.get(f"{DEFAULT_API_BASE_URL}/api/auth/cli/mcp-access").mock(
        return_value=httpx.Response(403, json={"detail": "workspace access denied"})
    )
    result = runner.invoke(
        app,
        ["access", "--client", "claude-code", "--workspace", "someone-else"],
    )
    assert result.exit_code != 0
    assert "workspace access denied" in result.stderr
