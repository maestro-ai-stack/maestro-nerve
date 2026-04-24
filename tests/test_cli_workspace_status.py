"""Tests for `mnerve whoami`, `mnerve status`, `mnerve workspace list`."""

from __future__ import annotations

import json

import httpx
import respx
from typer.testing import CliRunner

from maestro_nerve.cli import app
from maestro_nerve.client import DEFAULT_API_BASE_URL

runner = CliRunner()


@respx.mock
def test_whoami_prints_backend_response(logged_in):
    respx.get(f"{DEFAULT_API_BASE_URL}/api/auth/cli/whoami").mock(
        return_value=httpx.Response(200, json={"email": "fixture@maestro.onl", "workspace": {"slug": "founder"}})
    )
    result = runner.invoke(app, ["whoami"])
    assert result.exit_code == 0
    body = json.loads(result.stdout)
    assert body["email"] == "fixture@maestro.onl"


def test_whoami_requires_login(tmp_auth):
    result = runner.invoke(app, ["whoami"])
    assert result.exit_code != 0
    assert "Not logged in" in result.output


@respx.mock
def test_status_ok(logged_in):
    respx.get(f"{DEFAULT_API_BASE_URL}/api/auth/cli/whoami").mock(
        return_value=httpx.Response(200, json={"email": "x"})
    )
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "ok" in result.stdout


@respx.mock
def test_status_reports_unauthorized(logged_in):
    respx.get(f"{DEFAULT_API_BASE_URL}/api/auth/cli/whoami").mock(
        return_value=httpx.Response(401, json={"detail": "invalid api key"})
    )
    result = runner.invoke(app, ["status"])
    assert result.exit_code != 0
    assert "unauthorized" in result.stderr


def test_status_not_logged_in(tmp_auth):
    result = runner.invoke(app, ["status"])
    assert result.exit_code != 0
    assert "not-logged-in" in result.stderr


@respx.mock
def test_workspace_list_table(logged_in):
    respx.get(f"{DEFAULT_API_BASE_URL}/api/workspaces").mock(
        return_value=httpx.Response(
            200,
            json=[{"slug": "founder", "name": "Founder", "role": "owner"}, {"slug": "shared", "name": "Shared", "role": "editor"}],
        )
    )
    result = runner.invoke(app, ["workspace", "list"])
    assert result.exit_code == 0
    # Star marks the default.
    assert "* founder" in result.stdout
    assert "  shared" in result.stdout


@respx.mock
def test_workspace_list_json(logged_in):
    respx.get(f"{DEFAULT_API_BASE_URL}/api/workspaces").mock(
        return_value=httpx.Response(200, json=[{"slug": "founder"}])
    )
    result = runner.invoke(app, ["workspace", "list", "--json"])
    assert result.exit_code == 0
    assert json.loads(result.stdout) == [{"slug": "founder"}]


@respx.mock
def test_workspace_list_empty(logged_in):
    respx.get(f"{DEFAULT_API_BASE_URL}/api/workspaces").mock(
        return_value=httpx.Response(200, json=[])
    )
    result = runner.invoke(app, ["workspace", "list"])
    assert result.exit_code == 0
    assert "(no workspaces)" in result.stdout
