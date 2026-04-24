"""Shared fixtures for the public `maestro-nerve` test suite.

The suite never hits the real backend; all HTTP is intercepted with
respx. Auth state is redirected to a tmp path per-test so the runner's
real `~/.config/maestro/auth.json` is untouched.
"""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest

from maestro_nerve.client import AuthState, save_auth


@pytest.fixture
def tmp_auth(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[Path, None, None]:
    """Redirect the auth file to a tmp path. Returns the path (may not exist yet)."""
    path = tmp_path / "auth.json"
    monkeypatch.setenv("MAESTRO_AUTH_FILE", str(path))
    yield path


@pytest.fixture
def logged_in(tmp_auth: Path) -> Path:
    """Like `tmp_auth` but also writes a valid-looking auth state."""
    save_auth(
        AuthState(
            api_key="mnr_live_secret",
            workspace="founder",
            api_base_url="https://nerve-api.maestro.onl",
            user_email="fixture@maestro.onl",
        )
    )
    return tmp_auth
