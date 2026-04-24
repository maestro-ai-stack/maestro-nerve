"""Tests for `maestro_nerve.client.http`.

Uses `respx` to intercept httpx calls; no real network.
"""

from __future__ import annotations

import httpx
import pytest
import respx

from maestro_nerve.client import (
    DEFAULT_API_BASE_URL,
    NerveClient,
    NerveHTTPError,
    NerveUnauthorizedError,
    NotLoggedInError,
)


@respx.mock
def test_default_base_url_is_nerve_api():
    route = respx.get(f"{DEFAULT_API_BASE_URL}/api/auth/cli/whoami").mock(
        return_value=httpx.Response(200, json={"email": "fixture@maestro.onl"})
    )
    with NerveClient(api_key="mnr_live_abc") as client:
        out = client.whoami()
    assert out == {"email": "fixture@maestro.onl"}
    assert route.called


@respx.mock
def test_env_var_overrides_base_url(monkeypatch):
    monkeypatch.setenv("NERVE_API_BASE_URL", "https://stage.maestro.onl")
    route = respx.get("https://stage.maestro.onl/api/auth/cli/whoami").mock(
        return_value=httpx.Response(200, json={"email": "e"})
    )
    with NerveClient(api_key="mnr_live_abc") as client:
        client.whoami()
    assert route.called


def test_not_logged_in_raised_without_key():
    with NerveClient(api_key=None) as client:
        with pytest.raises(NotLoggedInError):
            client.whoami()


@respx.mock
def test_401_raises_unauthorized():
    respx.get(f"{DEFAULT_API_BASE_URL}/api/auth/cli/whoami").mock(
        return_value=httpx.Response(401, json={"detail": "invalid api key"})
    )
    with NerveClient(api_key="mnr_live_abc") as client:
        with pytest.raises(NerveUnauthorizedError) as ex:
            client.whoami()
    assert ex.value.status_code == 401
    assert "invalid" in ex.value.detail


@respx.mock
def test_403_raises_unauthorized_with_status():
    respx.get(f"{DEFAULT_API_BASE_URL}/api/auth/cli/whoami").mock(
        return_value=httpx.Response(403, json={"detail": "workspace access denied"})
    )
    with NerveClient(api_key="mnr_live_abc") as client:
        with pytest.raises(NerveUnauthorizedError) as ex:
            client.whoami()
    assert ex.value.status_code == 403


@respx.mock
def test_500_raises_http_error_with_detail():
    respx.get(f"{DEFAULT_API_BASE_URL}/api/auth/cli/whoami").mock(
        return_value=httpx.Response(500, json={"detail": "internal"})
    )
    with NerveClient(api_key="mnr_live_abc") as client:
        with pytest.raises(NerveHTTPError) as ex:
            client.whoami()
    assert ex.value.status_code == 500


@respx.mock
def test_mcp_access_passes_params():
    route = respx.get(f"{DEFAULT_API_BASE_URL}/api/auth/cli/mcp-access").mock(
        return_value=httpx.Response(200, json={"client": "claude-code", "payload": {"mcpServers": {}}})
    )
    with NerveClient(api_key="mnr_live_abc") as client:
        out = client.mcp_access(client="claude-code", workspace="founder", fmt="mcp-json")
    assert out["client"] == "claude-code"
    assert route.called
    req = route.calls.last.request
    assert req.url.params["client"] == "claude-code"
    assert req.url.params["workspace"] == "founder"
    assert req.url.params["format"] == "mcp-json"


@respx.mock
def test_list_workspaces_handles_list_shape():
    respx.get(f"{DEFAULT_API_BASE_URL}/api/workspaces").mock(
        return_value=httpx.Response(200, json=[{"slug": "a"}, {"slug": "b"}])
    )
    with NerveClient(api_key="mnr_live_abc") as client:
        out = client.list_workspaces()
    assert [w["slug"] for w in out] == ["a", "b"]


@respx.mock
def test_list_workspaces_falls_back_to_whoami_on_404():
    respx.get(f"{DEFAULT_API_BASE_URL}/api/workspaces").mock(return_value=httpx.Response(404))
    respx.get(f"{DEFAULT_API_BASE_URL}/api/auth/cli/whoami").mock(
        return_value=httpx.Response(200, json={"workspace": {"slug": "founder"}})
    )
    with NerveClient(api_key="mnr_live_abc") as client:
        out = client.list_workspaces()
    assert [w["slug"] for w in out] == ["founder"]


@respx.mock
def test_user_agent_header_is_set():
    route = respx.get(f"{DEFAULT_API_BASE_URL}/api/auth/cli/whoami").mock(
        return_value=httpx.Response(200, json={})
    )
    with NerveClient(api_key="mnr_live_abc") as client:
        client.whoami()
    ua = route.calls.last.request.headers["user-agent"]
    assert ua.startswith("mnerve/")


@respx.mock
def test_cli_approve_is_auth_free():
    route = respx.post(f"{DEFAULT_API_BASE_URL}/api/auth/cli/approve").mock(
        return_value=httpx.Response(200, json={"code": "abc", "expires_at": "..."})
    )
    with NerveClient(api_key=None) as client:
        client.cli_approve(state_token="s", challenge="c", callback_url="http://x")
    # Must not include an Authorization header (auth_required=False).
    req = route.calls.last.request
    assert "authorization" not in {k.lower() for k in req.headers.keys()}


@respx.mock
def test_cli_exchange_is_auth_free():
    route = respx.post(f"{DEFAULT_API_BASE_URL}/api/auth/cli/exchange").mock(
        return_value=httpx.Response(200, json={"api_key": "mnr_live_abc"})
    )
    with NerveClient(api_key=None) as client:
        out = client.cli_exchange(code="code", code_verifier="verifier")
    assert out["api_key"] == "mnr_live_abc"
    req = route.calls.last.request
    assert "authorization" not in {k.lower() for k in req.headers.keys()}
