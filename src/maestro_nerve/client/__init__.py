"""HTTP and auth layer for the public `maestro-nerve` CLI.

The client is the only place in this package that makes network I/O.
`cli/` composes on top of it.
"""

from __future__ import annotations

from maestro_nerve.client.auth import (
    AUTH_FILENAME,
    AuthState,
    auth_path,
    clear_auth,
    load_auth,
    save_auth,
)
from maestro_nerve.client.http import (
    DEFAULT_API_BASE_URL,
    NerveClient,
    NerveHTTPError,
    NerveUnauthorizedError,
    NotLoggedInError,
)

__all__ = [
    "AUTH_FILENAME",
    "DEFAULT_API_BASE_URL",
    "AuthState",
    "NerveClient",
    "NerveHTTPError",
    "NerveUnauthorizedError",
    "NotLoggedInError",
    "auth_path",
    "clear_auth",
    "load_auth",
    "save_auth",
]
