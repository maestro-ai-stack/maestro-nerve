"""Local auth-state storage for `mnerve`.

The CLI stores one small JSON blob per machine at `~/.maestro/auth.json`
(overridable via `MAESTRO_AUTH_FILE`). It is written 0600 and never synced
to the cloud by this package.

Shape:
    {"api_key": "mnr_live_...", "workspace": "founder", "api_base_url": "https://nerve-api.maestro.onl"}
"""

from __future__ import annotations

import contextlib
import json
import os
import stat
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from platformdirs import user_config_dir

AUTH_FILENAME = "auth.json"
_APP_DIR_NAME = "maestro"


@dataclass(slots=True)
class AuthState:
    api_key: str
    workspace: str | None = None
    api_base_url: str | None = None
    user_email: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_mapping(cls, payload: dict[str, Any] | None) -> AuthState | None:
        if not payload:
            return None
        api_key = str(payload.get("api_key") or "").strip()
        if not api_key:
            return None
        return cls(
            api_key=api_key,
            workspace=payload.get("workspace"),
            api_base_url=payload.get("api_base_url"),
            user_email=payload.get("user_email"),
        )


def auth_path() -> Path:
    """Resolve the local path for the auth file.

    Precedence:
    1. `MAESTRO_AUTH_FILE` env var (used by tests and advanced users)
    2. platform user config dir + `auth.json` (e.g. `~/.config/maestro/auth.json`
       on Linux, `~/Library/Application Support/maestro/auth.json` on macOS)
    """
    override = os.environ.get("MAESTRO_AUTH_FILE")
    if override:
        return Path(override).expanduser()
    return Path(user_config_dir(_APP_DIR_NAME)) / AUTH_FILENAME


def load_auth() -> AuthState | None:
    path = auth_path()
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(raw, dict):
        return None
    return AuthState.from_mapping(raw)


def save_auth(state: AuthState) -> Path:
    path = auth_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state.to_dict(), indent=2), encoding="utf-8")
    tmp.replace(path)
    with contextlib.suppress(OSError):  # pragma: no cover - Windows / restricted FS
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)  # 0600
    return path


def clear_auth() -> bool:
    path = auth_path()
    if not path.exists():
        return False
    try:
        path.unlink()
    except OSError:
        return False
    return True
