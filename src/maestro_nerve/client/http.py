"""Thin HTTP client against the hosted Maestro backend.

Does NOT hold business state. All endpoints are documented at
`https://github.com/maestro-ai-stack/maestro-nerve-internal` (private)
and served at the public base URL below.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

from maestro_nerve.__version__ import __version__

DEFAULT_API_BASE_URL = "https://nerve-api.maestro.onl"
_USER_AGENT = f"mnerve/{__version__} (+https://github.com/maestro-ai-stack/maestro-nerve)"


class NerveHTTPError(RuntimeError):
    """Raised for HTTP-layer failures the caller should surface as-is."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(f"[{status_code}] {detail}")
        self.status_code = status_code
        self.detail = detail


class NerveUnauthorizedError(NerveHTTPError):
    """401/403 from the backend — the saved API key is stale or the workspace is wrong."""


class NotLoggedInError(RuntimeError):
    """Raised when the caller needs to `mnerve login` first."""


def _resolve_base_url(explicit: str | None = None) -> str:
    return (explicit or os.environ.get("NERVE_API_BASE_URL") or DEFAULT_API_BASE_URL).rstrip("/")


class NerveClient:
    """Synchronous HTTP client. Short-lived; instantiate per-command.

    Preserves connection via `httpx.Client` for the duration of the call tree,
    but is safe to discard immediately after.
    """

    def __init__(
        self,
        *,
        api_base_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.api_base_url = _resolve_base_url(api_base_url)
        self.api_key = api_key
        self._client = httpx.Client(
            base_url=self.api_base_url,
            timeout=timeout,
            headers={"User-Agent": _USER_AGENT},
        )

    def __enter__(self) -> NerveClient:
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    # ------------------------------------------------------------------
    # core request helpers

    def _auth_headers(self) -> dict[str, str]:
        if not self.api_key:
            raise NotLoggedInError("Not logged in. Run `mnerve login` first.")
        return {"Authorization": f"Bearer {self.api_key}"}

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        auth_required: bool = True,
    ) -> Any:
        headers = self._auth_headers() if auth_required else {}
        response = self._client.request(method, path, params=params, json=json_body, headers=headers)
        if response.status_code in (401, 403):
            try:
                detail = str(response.json().get("detail") or response.text)
            except ValueError:
                detail = response.text
            raise NerveUnauthorizedError(response.status_code, detail)
        if response.status_code >= 400:
            try:
                detail = str(response.json().get("detail") or response.text)
            except ValueError:
                detail = response.text
            raise NerveHTTPError(response.status_code, detail)
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    # ------------------------------------------------------------------
    # typed calls

    def whoami(self) -> dict[str, Any]:
        """GET /api/auth/cli/whoami — who am I + my primary workspace."""
        return self._request("GET", "/api/auth/cli/whoami")

    def list_workspaces(self) -> list[dict[str, Any]]:
        """GET /api/workspaces — best-effort. Falls back to whoami.workspace."""
        try:
            data = self._request("GET", "/api/workspaces")
        except NerveHTTPError as exc:
            if exc.status_code == 404:
                me = self.whoami()
                ws = me.get("workspace") or {}
                return [ws] if ws else []
            raise
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and isinstance(data.get("workspaces"), list):
            return data["workspaces"]
        return []

    def mcp_access(
        self,
        *,
        client: str,
        workspace: str | None = None,
        fmt: str = "envelope",
        api_base_url: str | None = None,
    ) -> dict[str, Any]:
        """GET /api/auth/cli/mcp-access — ask the backend to shape the MCP config.

        Single source of truth for "how do I connect client X to my workspace".
        """
        params: dict[str, Any] = {"client": client, "format": fmt}
        if workspace:
            params["workspace"] = workspace
        if api_base_url:
            params["api_base_url"] = api_base_url
        return self._request("GET", "/api/auth/cli/mcp-access", params=params)

    def cli_approve(
        self,
        *,
        state_token: str,
        challenge: str,
        callback_url: str,
        device_label: str | None = None,
    ) -> dict[str, Any]:
        """POST /api/auth/cli/approve — browser-login handshake start.

        Called by `mnerve login` after the user approves the pairing code in
        their browser.
        """
        body: dict[str, Any] = {
            "state": state_token,
            "challenge": challenge,
            "challenge_method": "S256",
            "callback_url": callback_url,
        }
        if device_label:
            body["device_label"] = device_label
        return self._request("POST", "/api/auth/cli/approve", json_body=body, auth_required=False)

    def cli_exchange(self, *, code: str, code_verifier: str) -> dict[str, Any]:
        """POST /api/auth/cli/exchange — exchange one-time code for an API key."""
        return self._request(
            "POST",
            "/api/auth/cli/exchange",
            json_body={"code": code, "code_verifier": code_verifier},
            auth_required=False,
        )
