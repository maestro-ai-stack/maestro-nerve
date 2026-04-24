"""`mnerve login` — browser OAuth handshake for API key provisioning.

Flow:
    1. Ask the backend for an `authorize_url`, pass a PKCE challenge.
    2. Open the URL in the user's browser.
    3. The hosted `/access` page approves the pairing and returns a short code.
    4. Exchange the code (plus the PKCE verifier) for an API key.
    5. Persist the key at `~/.maestro/auth.json`.

The Phase-1 public release ships a CLI-input fallback: users paste the API
key generated on the web `/access` page. The browser-driven handshake is
scaffolded against `/api/auth/cli/approve` + `/api/auth/cli/exchange` for the
next release.
"""

from __future__ import annotations

import typer

from maestro_nerve.client import (
    AuthState,
    NerveClient,
    NerveHTTPError,
    NerveUnauthorizedError,
    save_auth,
)


def login(
    api_key: str | None = typer.Option(
        None,
        "--api-key",
        envvar="MAESTRO_API_KEY",
        help="Paste an API key from https://nerve.maestro.onl/access. Prompted when omitted.",
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
) -> None:
    """Store a Maestro API key so other commands can reach the backend.

    Visit https://nerve.maestro.onl/access to mint a key, then run:

        mnerve login --api-key mnr_live_...
    """
    token = (api_key or "").strip()
    if not token:
        token = typer.prompt("Paste your Maestro API key", hide_input=True).strip()
    if not token:
        raise typer.BadParameter("An API key is required.")

    # Verify the key against the backend before persisting.
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

    state = AuthState(
        api_key=token,
        workspace=resolved_ws,
        api_base_url=api_base_url,
        user_email=me.get("email"),
    )
    path = save_auth(state)
    typer.echo(f"Logged in as {me.get('email') or 'unknown'} ({resolved_ws or 'no default workspace'}).")
    typer.echo(f"Credentials saved to {path}")
