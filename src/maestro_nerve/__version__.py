"""Single source of truth for the package version string."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version


def _resolve() -> str:
    try:
        return _pkg_version("maestro-nerve")
    except PackageNotFoundError:  # pragma: no cover - editable / uninstalled dev checkout
        return "0+editable"


__version__: str = _resolve()
