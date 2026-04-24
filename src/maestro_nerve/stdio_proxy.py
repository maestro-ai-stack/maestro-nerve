"""Tiny stdio MCP proxy that forwards tool calls to the hosted backend.

Loaded lazily by `mnerve serve-mcp`. Not imported by the default CLI path
so that users without the `mcp` extra installed still get help output from
`mnerve --help`.
"""

from __future__ import annotations

from typing import Any


def build_stdio_proxy(*, workspace: str):
    """Return a ready-to-run FastMCP server that proxies to the hosted MCP."""
    from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

    from maestro_nerve.client import NerveClient, load_auth

    mcp = FastMCP("maestro-nerve-stdio-proxy", streamable_http_path="/")

    def _call_remote(tool: str, **kwargs: Any) -> Any:
        state = load_auth()
        if not state:
            raise RuntimeError("Not logged in. Run `mnerve login` first.")
        # The hosted backend already exposes these as MCP tools over HTTP.
        # For stdio parity we short-circuit to the REST shape, using the
        # shared `/api/auth/cli/...` helpers as placeholders until the
        # remote MCP → REST shim ships.
        with NerveClient(api_base_url=state.api_base_url, api_key=state.api_key) as client:
            return client._request(
                "POST",
                f"/api/mcp/tools/{tool}",
                json_body={"workspace": workspace, **kwargs},
            )

    @mcp.tool(name="server_info")
    def server_info() -> dict:
        return {
            "server_name": "maestro-nerve-stdio-proxy",
            "workspace": workspace,
            "note": "stdio proxy — prefer remote MCP via `mnerve access --client <c>`.",
        }

    @mcp.tool(name="search_workspace")
    def search_workspace(query: str, limit: int = 5) -> dict:
        return _call_remote("search_workspace", query=query, limit=limit)

    @mcp.tool(name="list_entities")
    def list_entities(limit: int = 20) -> dict:
        return _call_remote("list_entities", limit=limit)

    @mcp.tool(name="inspect")
    def inspect(entity_id: str) -> dict:
        return _call_remote("inspect", entity_id=entity_id)

    return mcp
