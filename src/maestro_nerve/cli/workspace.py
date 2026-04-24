"""`mnerve workspace` subcommand group."""

from __future__ import annotations

import json

import typer

from maestro_nerve.client import (
    NerveClient,
    NerveHTTPError,
    NerveUnauthorizedError,
    load_auth,
)

workspace = typer.Typer(no_args_is_help=True, help="Inspect workspaces reachable with this API key.")


@workspace.command("list")
def list_workspaces(
    api_base_url: str | None = typer.Option(None, "--api-base-url"),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON instead of a human-friendly table."),
) -> None:
    """List the workspaces associated with the current API key."""
    state = load_auth()
    if not state:
        raise typer.BadParameter("Not logged in. Run `mnerve login` first.")

    try:
        with NerveClient(api_base_url=api_base_url or state.api_base_url, api_key=state.api_key) as client:
            workspaces = client.list_workspaces()
    except NerveUnauthorizedError as exc:
        typer.echo(f"error: {exc.detail}", err=True)
        raise typer.Exit(code=1) from exc
    except NerveHTTPError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    if as_json:
        typer.echo(json.dumps(workspaces, indent=2))
        return

    if not workspaces:
        typer.echo("(no workspaces)")
        return

    for ws in workspaces:
        slug = ws.get("slug") or "?"
        name = ws.get("name") or "?"
        role = ws.get("role") or "?"
        marker = "*" if ws.get("slug") == state.workspace else " "
        typer.echo(f"{marker} {slug}\t{role}\t{name}")
