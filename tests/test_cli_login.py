"""Tests for `mnerve login` flow."""

from __future__ import annotations

import httpx
import respx
from typer.testing import CliRunner

from maestro_nerve.cli import app
from maestro_nerve.cli.login import DEFAULT_APP_URL, _build_login_url
from maestro_nerve.client import DEFAULT_API_BASE_URL, load_auth

runner = CliRunner()


@respx.mock
def test_login_with_api_key_stores_credentials(tmp_auth):
    respx.get(f"{DEFAULT_API_BASE_URL}/api/auth/cli/whoami").mock(
        return_value=httpx.Response(
            200,
            json={"email": "fixture@maestro.onl", "workspace": {"slug": "founder"}},
        )
    )
    result = runner.invoke(app, ["login", "--api-key", "mnr_live_abc"])
    assert result.exit_code == 0, result.output
    assert "Logged in" in result.output
    state = load_auth()
    assert state is not None
    assert state.api_key == "mnr_live_abc"
    assert state.workspace == "founder"
    assert state.user_email == "fixture@maestro.onl"


@respx.mock
def test_login_verifies_with_backend(tmp_auth):
    route = respx.get(f"{DEFAULT_API_BASE_URL}/api/auth/cli/whoami").mock(
        return_value=httpx.Response(200, json={"email": "x", "workspace": {"slug": "s"}})
    )
    runner.invoke(app, ["login", "--api-key", "mnr_live_abc"])
    assert route.called


@respx.mock
def test_login_rejects_bad_key(tmp_auth):
    respx.get(f"{DEFAULT_API_BASE_URL}/api/auth/cli/whoami").mock(
        return_value=httpx.Response(401, json={"detail": "invalid api key"})
    )
    result = runner.invoke(app, ["login", "--api-key", "bad"])
    assert result.exit_code != 0
    assert "rejected by the backend" in result.output
    # auth.json must not be written on failure.
    assert load_auth() is None


@respx.mock
def test_login_with_explicit_workspace(tmp_auth):
    respx.get(f"{DEFAULT_API_BASE_URL}/api/auth/cli/whoami").mock(
        return_value=httpx.Response(
            200,
            json={"email": "x", "workspace": {"slug": "founder"}},
        )
    )
    runner.invoke(
        app,
        ["login", "--api-key", "mnr_live_abc", "--workspace", "custom"],
    )
    state = load_auth()
    assert state is not None
    assert state.workspace == "custom"


def test_login_requires_key(tmp_auth):
    # No --api-key and empty stdin prompt — should fail.
    result = runner.invoke(app, ["login", "--manual"], input="\n")
    assert result.exit_code != 0


def test_login_url_defaults_to_production_not_localhost():
    url = _build_login_url(
        app_url=DEFAULT_APP_URL,
        state="state",
        code_challenge="challenge",
        callback_url="http://127.0.0.1:54321/callback",
    )
    assert url.startswith("https://nerve.maestro.onl/access/cli?")
    assert "localhost:3000" not in url
    assert "code_challenge=challenge" in url
    assert "callback_url=http%3A%2F%2F127.0.0.1%3A54321%2Fcallback" in url


def test_logout_removes_credentials(logged_in):
    result = runner.invoke(app, ["logout"])
    assert result.exit_code == 0
    assert "removed" in result.output.lower()
    assert load_auth() is None


def test_logout_when_no_credentials(tmp_auth):
    result = runner.invoke(app, ["logout"])
    assert result.exit_code == 0
    assert "no local credentials" in result.output.lower()


def test_version_command_prints_something():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.output.strip()
