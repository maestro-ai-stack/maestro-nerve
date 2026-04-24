"""`mnerve serve-mcp` — optional stdio MCP fallback.

Remote MCP (`mnerve access --client <c>`) is the supported product path.
This command is a dev/compat convenience for users whose environment
cannot reach the hosted endpoint directly.

Requires the `mcp-stdio` optional extra:

    pip install 'maestro-nerve[mcp-stdio]'
"""

from __future__ import annotations

import os
import sys

import typer


def serve_mcp(
    workspace: str = typer.Option(
        ...,
        "--workspace",
        envvar="MAESTRO_WORKSPACE",
        help="Workspace slug to bind this stdio MCP session to.",
    ),
) -> None:
    """Run a local stdio MCP server that proxies to the hosted backend.

    NOT the recommended install path. Prefer `mnerve access --client <c>`
    to configure a remote MCP connection on your host.
    """
    try:
        from mcp.server.fastmcp import FastMCP  # noqa: F401
    except ImportError as exc:
        typer.echo(
            "serve-mcp requires the optional `mcp` extra. Install with:\n"
            "  pip install 'maestro-nerve[mcp-stdio]'",
            err=True,
        )
        raise typer.Exit(code=2) from exc

    os.environ["MAESTRO_WORKSPACE"] = workspace
    # Import after env-set so downstream server code can read MAESTRO_WORKSPACE.
    from maestro_nerve.stdio_proxy import build_stdio_proxy  # type: ignore[attr-defined]

    mcp = build_stdio_proxy(workspace=workspace)
    mcp.run()  # pragma: no cover - long-running blocking call
    sys.exit(0)  # pragma: no cover
