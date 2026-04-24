"""Unit tests for `maestro_nerve.client.auth`."""

from __future__ import annotations

import json
import os

from maestro_nerve.client import (
    AUTH_FILENAME,
    AuthState,
    auth_path,
    clear_auth,
    load_auth,
    save_auth,
)


def test_auth_path_respects_override(tmp_path, monkeypatch):
    target = tmp_path / "override.json"
    monkeypatch.setenv("MAESTRO_AUTH_FILE", str(target))
    assert auth_path() == target


def test_auth_path_falls_back_to_user_config_dir(tmp_path, monkeypatch):
    monkeypatch.delenv("MAESTRO_AUTH_FILE", raising=False)
    path = auth_path()
    assert path.name == AUTH_FILENAME
    assert "maestro" in str(path).lower()


def test_load_returns_none_when_missing(tmp_path, monkeypatch):
    target = tmp_path / "never-written.json"
    monkeypatch.setenv("MAESTRO_AUTH_FILE", str(target))
    assert load_auth() is None


def test_save_then_load_roundtrips(tmp_path, monkeypatch):
    target = tmp_path / "auth.json"
    monkeypatch.setenv("MAESTRO_AUTH_FILE", str(target))
    state = AuthState(
        api_key="mnr_live_abc",
        workspace="founder",
        api_base_url="https://nerve-api.maestro.onl",
        user_email="fixture@maestro.onl",
    )
    path = save_auth(state)
    assert path == target
    loaded = load_auth()
    assert loaded is not None
    assert loaded.api_key == "mnr_live_abc"
    assert loaded.workspace == "founder"
    assert loaded.api_base_url == "https://nerve-api.maestro.onl"
    assert loaded.user_email == "fixture@maestro.onl"


def test_save_chmods_0600_when_possible(tmp_path, monkeypatch):
    target = tmp_path / "auth.json"
    monkeypatch.setenv("MAESTRO_AUTH_FILE", str(target))
    save_auth(AuthState(api_key="mnr_live_abc"))
    mode = os.stat(target).st_mode & 0o777
    # 0o600 may not be enforceable on every OS; enforce on POSIX only.
    if os.name == "posix":
        assert mode == 0o600, f"expected 0600, got {oct(mode)}"


def test_load_ignores_empty_api_key(tmp_path, monkeypatch):
    target = tmp_path / "auth.json"
    monkeypatch.setenv("MAESTRO_AUTH_FILE", str(target))
    target.write_text(json.dumps({"api_key": "", "workspace": "x"}))
    assert load_auth() is None


def test_load_ignores_garbage_file(tmp_path, monkeypatch):
    target = tmp_path / "auth.json"
    monkeypatch.setenv("MAESTRO_AUTH_FILE", str(target))
    target.write_text("not json {{{")
    assert load_auth() is None


def test_clear_auth_removes_existing_file(tmp_path, monkeypatch):
    target = tmp_path / "auth.json"
    monkeypatch.setenv("MAESTRO_AUTH_FILE", str(target))
    save_auth(AuthState(api_key="mnr_live_abc"))
    assert target.exists()
    assert clear_auth() is True
    assert not target.exists()


def test_clear_auth_is_noop_when_file_absent(tmp_path, monkeypatch):
    target = tmp_path / "never.json"
    monkeypatch.setenv("MAESTRO_AUTH_FILE", str(target))
    assert clear_auth() is False


def test_save_omits_none_fields(tmp_path, monkeypatch):
    target = tmp_path / "auth.json"
    monkeypatch.setenv("MAESTRO_AUTH_FILE", str(target))
    save_auth(AuthState(api_key="mnr_live_abc"))
    raw = json.loads(target.read_text())
    assert raw == {"api_key": "mnr_live_abc"}
