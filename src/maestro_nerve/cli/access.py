"""`mnerve access` — print the MCP client config for a supported host.

Thin wrapper around `GET /api/auth/cli/mcp-access`: the backend is the
source of truth for per-client JSON shapes, so adding support for a new
client (Cursor, Windsurf, etc.) is a backend-only change and existing
CLI installs pick it up automatically.
"""

from __future__ import annotations

import json

import typer

from maestro_nerve.client import (
    NerveClient,
    NerveHTTPError,
    NerveUnauthorizedError,
    load_auth,
)

_KNOWN_CLIENTS = ("claude-code", "codex", "chatgpt")
_KNOWN_FORMATS = ("envelope", "mcp-json", "settings-json", "env")


def access(
    client: str = typer.Option(..., "--client", "-c", help=f"Target host: one of {', '.join(_KNOWN_CLIENTS)}."),
    workspace: str | None = typer.Option(
        None,
        "--workspace",
        "-w",
        help="Workspace slug to expose over MCP (defaults to primary).",
    ),
    fmt: str = typer.Option(
        "envelope",
        "--format",
        "-f",
        help=f"Output shape: one of {', '.join(_KNOWN_FORMATS)}.",
    ),
    api_base_url: str | None = typer.Option(
        None,
        "--api-base-url",
        help="Override the hosted Maestro API base URL.",
    ),
    show_hint: bool = typer.Option(
        True,
        "--hint/--no-hint",
        help="Print a one-line 'where to paste this' hint to stderr. Use --no-hint for fully pipe-friendly output.",
    ),
) -> None:
    """Print MCP connection config for one client + workspace pair."""
    state = load_auth()
    if not state:
        raise typer.BadParameter("Not logged in. Run `mnerve login` first.")

    if client.strip().lower() not in _KNOWN_CLIENTS:
        raise typer.BadParameter(f"client must be one of: {', '.join(_KNOWN_CLIENTS)}")
    if fmt.strip().lower() not in _KNOWN_FORMATS:
        raise typer.BadParameter(f"format must be one of: {', '.join(_KNOWN_FORMATS)}")

    resolved_workspace = workspace or state.workspace

    try:
        with NerveClient(api_base_url=api_base_url or state.api_base_url, api_key=state.api_key) as nerve:
            response = nerve.mcp_access(
                client=client,
                workspace=resolved_workspace,
                fmt=fmt,
            )
    except NerveUnauthorizedError as exc:
        typer.echo(f"error: {exc.detail}", err=True)
        raise typer.Exit(code=1) from exc
    except NerveHTTPError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    payload = response.get("payload")
    fmt_norm = response.get("format", fmt).strip().lower()

    if fmt_norm == "env":
        if not isinstance(payload, dict):
            raise typer.BadParameter("backend returned unexpected shape for env format")
        typer.echo("\n".join(f"{k}={v}" for k, v in payload.items()))
    else:
        typer.echo(json.dumps(payload, indent=2))

    hint = response.get("hint")
    if show_hint and hint:
        typer.echo(f"# hint: {hint}", err=True)
