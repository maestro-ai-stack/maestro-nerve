"""`mnerve login` — production browser login with a paste-key fallback."""

from __future__ import annotations

import base64
import hashlib
import os
import queue
import secrets
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import typer

from maestro_nerve.__version__ import __version__
from maestro_nerve.client import (
    AuthState,
    NerveClient,
    NerveHTTPError,
    NerveUnauthorizedError,
    save_auth,
)

DEFAULT_APP_URL = "https://nerve.maestro.onl"
_CALLBACK_PATH = "/callback"
_SUCCESS_HTML = b"""<!doctype html><title>Maestro Nerve</title><h1>Login complete</h1><p>You can close this window and return to your terminal.</p>"""
_ERROR_HTML = b"""<!doctype html><title>Maestro Nerve</title><h1>Login failed</h1><p>Return to your terminal for details.</p>"""


def _resolve_app_url(explicit: str | None = None) -> str:
    return (explicit or os.environ.get("NERVE_APP_URL") or DEFAULT_APP_URL).rstrip("/")


def _pkce_pair() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return verifier, challenge


def _build_login_url(
    *,
    app_url: str,
    state: str,
    code_challenge: str,
    callback_url: str,
) -> str:
    parsed = urlparse(_resolve_app_url(app_url))
    query = urlencode(
        {
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "callback_url": callback_url,
            "client": "mnerve",
            "cli_version": __version__,
        }
    )
    return urlunparse((parsed.scheme, parsed.netloc, "/access/cli", "", query, ""))


def _make_callback_handler(result_queue: queue.Queue[dict[str, str]], expected_state: str):
    class CallbackHandler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            return

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            code = params.get("code", [""])[0]
            state = params.get("state", [""])[0]
            error = params.get("error", [""])[0]
            if parsed.path != _CALLBACK_PATH:
                self.send_response(404)
                self.end_headers()
                return
            if error:
                result_queue.put({"error": error})
                body = _ERROR_HTML
            elif not code or state != expected_state:
                result_queue.put({"error": "Invalid or missing login callback state."})
                body = _ERROR_HTML
            else:
                result_queue.put({"code": code})
                body = _SUCCESS_HTML
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return CallbackHandler


def _browser_login(
    *,
    app_url: str,
    api_base_url: str | None,
    timeout_seconds: int,
    open_browser: bool,
) -> AuthState:
    verifier, challenge = _pkce_pair()
    state = secrets.token_urlsafe(32)
    result_queue: queue.Queue[dict[str, str]] = queue.Queue(maxsize=1)

    server = ThreadingHTTPServer(("127.0.0.1", 0), _make_callback_handler(result_queue, state))
    callback_url = f"http://127.0.0.1:{server.server_port}{_CALLBACK_PATH}"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    login_url = _build_login_url(
        app_url=app_url,
        state=state,
        code_challenge=challenge,
        callback_url=callback_url,
    )

    typer.echo(f"Opening browser for Maestro login: {login_url}", err=True)
    if open_browser:
        webbrowser.open(login_url)
    else:
        typer.echo("Open the URL above in a browser on this machine.", err=True)

    try:
        result = result_queue.get(timeout=timeout_seconds)
    except queue.Empty as exc:
        raise typer.BadParameter(
            f"Timed out waiting for browser login after {timeout_seconds}s. "
            "Use `mnerve login --manual` to paste an API key instead."
        ) from exc
    finally:
        server.shutdown()
        server.server_close()

    if "error" in result:
        raise typer.BadParameter(f"Browser login failed: {result['error']}")

    try:
        with NerveClient(api_base_url=api_base_url, api_key=None) as client:
            exchanged = client.cli_exchange(code=result["code"], code_verifier=verifier)
    except NerveHTTPError as exc:
        raise typer.BadParameter(f"Backend error while exchanging login code: {exc}") from exc

    token = str(exchanged.get("api_key") or exchanged.get("token") or "").strip()
    if not token:
        raise typer.BadParameter("Backend did not return an API key for the CLI session.")
    return _verified_auth_state(token=token, workspace=None, api_base_url=api_base_url)


def _verified_auth_state(
    *,
    token: str,
    workspace: str | None,
    api_base_url: str | None,
) -> AuthState:
    try:
        with NerveClient(api_base_url=api_base_url, api_key=token) as client:
            me = client.whoami()
    except NerveUnauthorizedError as exc:
        raise typer.BadParameter(
            f"API key rejected by the backend: {exc.detail}. "
            "Did you paste the full `mnr_live_...` value?"
        ) from exc
    except NerveHTTPError as exc:
        raise typer.BadParameter(f"Backend error while verifying key: {exc}") from exc

    primary_ws = (me.get("workspace") or {}).get("slug")
    resolved_ws = (workspace or primary_ws or "").strip() or None
    return AuthState(
        api_key=token,
        workspace=resolved_ws,
        api_base_url=api_base_url,
        user_email=me.get("email"),
    )


def login(
    api_key: str | None = typer.Option(
        None,
        "--api-key",
        envvar="MAESTRO_API_KEY",
        help="Paste an API key directly. Also read from MAESTRO_API_KEY.",
    ),
    manual: bool = typer.Option(
        False,
        "--manual",
        help="Prompt for an API key instead of opening browser login.",
    ),
    browser: bool = typer.Option(
        True,
        "--browser/--no-browser",
        help="Open the login URL automatically. Use --no-browser for SSH/headless sessions.",
    ),
    workspace: str | None = typer.Option(
        None,
        "--workspace",
        help="Optional default workspace slug to remember for `mnerve access`.",
    ),
    api_base_url: str | None = typer.Option(
        None,
        "--api-base-url",
        help="Override the hosted API base URL (defaults to https://nerve-api.maestro.onl).",
    ),
    app_url: str | None = typer.Option(
        None,
        "--app-url",
        help="Override the hosted web app URL (defaults to https://nerve.maestro.onl).",
    ),
    timeout: int = typer.Option(
        180,
        "--timeout",
        min=5,
        help="Seconds to wait for browser login callback.",
    ),
) -> None:
    """Sign in and store a local API key for other `mnerve` commands."""
    token = (api_key or "").strip()
    if token:
        state = _verified_auth_state(token=token, workspace=workspace, api_base_url=api_base_url)
    elif manual:
        token = typer.prompt("Paste your Maestro API key", hide_input=True).strip()
        if not token:
            raise typer.BadParameter("An API key is required.")
        state = _verified_auth_state(token=token, workspace=workspace, api_base_url=api_base_url)
    else:
        state = _browser_login(
            app_url=_resolve_app_url(app_url),
            api_base_url=api_base_url,
            timeout_seconds=timeout,
            open_browser=browser,
        )
        if workspace:
            state.workspace = workspace

    path = save_auth(state)
    typer.echo(f"Logged in as {state.user_email or 'unknown'} ({state.workspace or 'no default workspace'}).")
    typer.echo(f"Credentials saved to {path}")
