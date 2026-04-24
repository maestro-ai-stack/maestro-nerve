"""`mnerve` — public CLI entrypoint.

Subcommands:
    login, logout, whoami, access, workspace, status, serve-mcp, version
"""

from __future__ import annotations

import json
import sys

import typer

from maestro_nerve.__version__ import __version__
from maestro_nerve.cli.access import access as access_cmd
from maestro_nerve.cli.login import login as login_cmd
from maestro_nerve.cli.serve_mcp import serve_mcp as serve_mcp_cmd
from maestro_nerve.cli.workspace import workspace as workspace_app
from maestro_nerve.client import (
    NerveClient,
    NerveHTTPError,
    NerveUnauthorizedError,
    NotLoggedInError,
    clear_auth,
    load_auth,
)

app = typer.Typer(
    name="mnerve",
    help="Shared intelligence memory plane for AI agents — login, workspaces, and MCP access configs.",
    no_args_is_help=True,
    add_completion=False,
)

app.command("login")(login_cmd)
app.command("access")(access_cmd)
app.command("serve-mcp")(serve_mcp_cmd)
app.add_typer(workspace_app, name="workspace", help="Inspect the workspaces reachable with this API key.")


@app.command("logout")
def logout() -> None:
    """Remove locally stored credentials. Does not revoke the API key server-side."""
    removed = clear_auth()
    if removed:
        typer.echo("Local credentials removed.")
    else:
        typer.echo("No local credentials were stored.")


@app.command("whoami")
def whoami(
    api_base_url: str | None = typer.Option(None, "--api-base-url", help="Override the hosted Maestro API base URL."),
) -> None:
    """Print the current caller's identity and primary workspace."""
    state = load_auth()
    if not state:
        raise typer.BadParameter("Not logged in. Run `mnerve login` first.")

    try:
        with NerveClient(api_base_url=api_base_url or state.api_base_url, api_key=state.api_key) as client:
            me = client.whoami()
    except NerveUnauthorizedError as exc:
        typer.echo(f"error: {exc.detail}", err=True)
        raise typer.Exit(code=1) from exc
    except NerveHTTPError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(json.dumps(me, indent=2))


@app.command("status")
def status(
    api_base_url: str | None = typer.Option(None, "--api-base-url", help="Override the hosted Maestro API base URL."),
) -> None:
    """One-line reachability probe: prints OK on 2xx, REASON on failure."""
    state = load_auth()
    if not state:
        typer.echo("status: not-logged-in", err=True)
        raise typer.Exit(code=1)
    try:
        with NerveClient(api_base_url=api_base_url or state.api_base_url, api_key=state.api_key) as client:
            client.whoami()
    except NotLoggedInError as exc:
        typer.echo(f"status: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    except NerveUnauthorizedError as exc:
        typer.echo(f"status: unauthorized ({exc.detail})", err=True)
        raise typer.Exit(code=1) from exc
    except NerveHTTPError as exc:
        typer.echo(f"status: http-{exc.status_code} ({exc.detail})", err=True)
        raise typer.Exit(code=1) from exc
    except Exception as exc:
        typer.echo(f"status: network-error ({exc})", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo("status: ok")


@app.command("version")
def version() -> None:
    """Print the installed `maestro-nerve` version."""
    typer.echo(__version__)


def main() -> None:  # pragma: no cover - console-script entrypoint
    app()


if __name__ == "__main__":  # pragma: no cover
    sys.exit(app())
