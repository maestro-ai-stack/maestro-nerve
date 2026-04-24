"""Public `maestro-nerve` distribution package.

Provides:

- `mnerve` CLI (via `maestro_nerve.cli`)
- HTTP client (via `maestro_nerve.client`)
- Shared shapes in `maestro_nerve.mcp_access`

All state is remote: this package talks to `https://nerve-api.maestro.onl`
over HTTP and does not own a local database.
"""

from __future__ import annotations

from maestro_nerve.__version__ import __version__

__all__ = ["__version__"]
