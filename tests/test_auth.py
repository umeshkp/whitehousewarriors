from __future__ import annotations

import base64
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from cricket_scoring.auth import (
    AUTH_MODE_GOOGLE,
    AUTH_MODE_LOCAL,
    RUNTIME_OAUTH_CLIENT_CONFIG_KEY,
    RUNTIME_OAUTH_REDIRECT_URI_KEY,
    GoogleAuthManager,
)
from cricket_scoring.config import AppConfig
from cricket_scoring.models import ValidationError


class FakeQueryParams(dict):
    pass


class FakeStreamlit:
    def __init__(self):
        self.session_state = {}
        self.query_params = FakeQueryParams()
        self.messages: dict[str, list[str]] = {
            "success": [],
            "error": [],
            "info": [],
            "warning": [],
            "caption": [],
        }
        self.button_responses: dict[str, bool] = {}
        self.link_calls: list[tuple[str, str]] = []
        self.text_input_values: dict[str, str] = {}
        self.text_area_values: dict[str, str] = {}
        self.text_input_labels: list[str] = []
        self.text_area_labels: list[str] = []

    def button(self, label: str, key: str | None = None, **_: object) -> bool:
        token = key or label
        return self.button_responses.get(token, False)

    def link_button(self, label: str, url: str, **_: object) -> None:
        self.link_calls.append((label, url))

    def text_input(self, label: str, value: str = "", key: str | None = None, **_: object) -> str:
        self.text_input_labels.append(label)
        token = key or label
        return self.text_input_values.get(token, value)

    def text_area(self, label: str, value: str = "", key: str | None = None, **_: object) -> str:
        self.text_area_labels.append(label)
        token = key or label
        return self.text_area_values.get(token, value)

    def caption(self, message: str) -> None:
        self.messages["caption"].append(message)

    def success(self, message: str) -> None:
        self.messages["success"].append(message)

    def error(self, message: str) -> None:
        self.messages["error"].append(message)

    def info(self, message: str) -> None:
        self.messages["info"].append(message)

    def warning(self, message: str) -> None:
        self.messages["warning"].append(message)

    def rerun(self) -> None:
        raise RuntimeError("rerun called")


def _config() -> AppConfig:
    return AppConfig(
        google_oauth_client_config_json=json.dumps({"web": {"client_id": "id", "client_secret": "secret"}}),
        google_oauth_redirect_uri="http://localhost:8501",
        google_sheet_url="",
        auth_bypass=False,
    )


def _make_id_token(payload: dict[str, str]) -> str:
    header = base64.urlsafe_b64encode(json.dumps({"alg": "none"}).encode("utf-8")).decode("utf-8").rstrip("=")
    body = base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8").rstrip("=")
    return f"{header}.{body}.sig"


def test_non_gmail_account_is_rejected_and_kept_local(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    fake_st = FakeStreamlit()
    fake_st.session_state["oauth_state"] = "nonce"
    fake_st.query_params.update({"code": "abc", "state": "nonce"})
    monkeypatch.setenv("LOCAL_AUTH_STATE_FILE", str(tmp_path / "auth_state.json"))
    monkeypatch.setattr("cricket_scoring.auth.st", fake_st)

    id_token = _make_id_token({"sub": "123", "email": "user@company.com", "name": "Umesh"})
    creds = SimpleNamespace(
        token="t",
        refresh_token="r",
        token_uri="uri",
        client_id="id",
        client_secret="secret",
        scopes=["openid"],
        id_token=id_token,
    )

    class FakeFlow:
        def __init__(self):
            self.credentials = creds

        def fetch_token(self, code: str) -> None:
            assert code == "abc"

    manager = GoogleAuthManager(_config())
    monkeypatch.setattr(manager, "_build_flow", lambda state=None: FakeFlow())
    manager._handle_oauth_callback()

    assert "gmail account is required" in fake_st.session_state["auth_error"].lower()
    assert fake_st.session_state["auth_mode"] == AUTH_MODE_LOCAL
    assert "google_credentials" not in fake_st.session_state
    assert "google_profile" not in fake_st.session_state


def test_oauth_state_mismatch_no_longer_blocks_login(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    fake_st = FakeStreamlit()
    fake_st.session_state["oauth_state"] = "expected"
    fake_st.query_params.update({"code": "abc", "state": "incoming"})
    monkeypatch.setenv("LOCAL_AUTH_STATE_FILE", str(tmp_path / "auth_state.json"))
    monkeypatch.setattr("cricket_scoring.auth.st", fake_st)

    id_token = _make_id_token({"sub": "123", "email": "user@gmail.com", "name": "Umesh"})
    creds = SimpleNamespace(
        token="t",
        refresh_token="r",
        token_uri="uri",
        client_id="id",
        client_secret="secret",
        scopes=["openid"],
        id_token=id_token,
    )

    class FakeFlow:
        def __init__(self):
            self.credentials = creds

        def fetch_token(self, code: str) -> None:
            assert code == "abc"

    manager = GoogleAuthManager(_config())
    monkeypatch.setattr(manager, "_build_flow", lambda state=None: FakeFlow())

    manager._handle_oauth_callback()

    assert fake_st.session_state["auth_mode"] == AUTH_MODE_GOOGLE
    assert "auth_error" not in fake_st.session_state


def test_oauth_callback_success_sets_profile_and_mode(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    fake_st = FakeStreamlit()
    fake_st.session_state["oauth_state"] = "nonce"
    fake_st.query_params.update({"code": "abc", "state": "nonce"})
    monkeypatch.setenv("LOCAL_AUTH_STATE_FILE", str(tmp_path / "auth_state.json"))
    monkeypatch.setattr("cricket_scoring.auth.st", fake_st)

    id_token = _make_id_token({"sub": "123", "email": "user@gmail.com", "name": "Umesh"})
    creds = SimpleNamespace(
        token="t",
        refresh_token="r",
        token_uri="uri",
        client_id="id",
        client_secret="secret",
        scopes=["openid"],
        id_token=id_token,
    )

    class FakeFlow:
        def __init__(self):
            self.credentials = creds

        def fetch_token(self, code: str) -> None:
            assert code == "abc"

    manager = GoogleAuthManager(_config())
    monkeypatch.setattr(manager, "_build_flow", lambda state=None: FakeFlow())

    manager._handle_oauth_callback()

    assert fake_st.session_state["auth_mode"] == AUTH_MODE_GOOGLE
    assert fake_st.session_state["google_profile"] == {"sub": "123", "email": "user@gmail.com", "name": "Umesh"}
    assert "google_credentials" in fake_st.session_state


def test_missing_required_profile_fields_rejected(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    fake_st = FakeStreamlit()
    fake_st.session_state["oauth_state"] = "nonce"
    fake_st.query_params.update({"code": "abc", "state": "nonce"})
    monkeypatch.setenv("LOCAL_AUTH_STATE_FILE", str(tmp_path / "auth_state.json"))
    monkeypatch.setattr("cricket_scoring.auth.st", fake_st)

    id_token = _make_id_token({"sub": "123", "name": "Umesh"})
    creds = SimpleNamespace(
        token="t",
        refresh_token="r",
        token_uri="uri",
        client_id="id",
        client_secret="secret",
        scopes=["openid"],
        id_token=id_token,
    )

    class FakeFlow:
        def __init__(self):
            self.credentials = creds

        def fetch_token(self, code: str) -> None:
            assert code == "abc"

    manager = GoogleAuthManager(_config())
    monkeypatch.setattr(manager, "_build_flow", lambda state=None: FakeFlow())

    manager._handle_oauth_callback()

    assert "missing required data" in fake_st.session_state["auth_error"].lower()
    assert "google_credentials" not in fake_st.session_state


def test_optional_login_defaults_to_local_mode_when_google_not_configured(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    fake_st = FakeStreamlit()
    monkeypatch.setenv("LOCAL_AUTH_STATE_FILE", str(tmp_path / "auth_state.json"))
    monkeypatch.setattr("cricket_scoring.auth.st", fake_st)

    config = AppConfig(
        google_oauth_client_config_json="",
        google_oauth_redirect_uri="",
        google_sheet_url="",
        auth_bypass=False,
    )
    manager = GoogleAuthManager(config)

    mode = manager.render_login_controls()

    assert mode == AUTH_MODE_LOCAL
    assert any("not configured" in msg.lower() for msg in fake_st.messages["info"])


def test_render_authenticated_name_only_display_and_logout_to_local(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    fake_st = FakeStreamlit()
    fake_st.session_state["google_credentials"] = {"token": "t"}
    fake_st.session_state["google_profile"] = {"sub": "1", "email": "a@b.com", "name": "Player One"}
    fake_st.button_responses["logout-button"] = True
    monkeypatch.setenv("LOCAL_AUTH_STATE_FILE", str(tmp_path / "auth_state.json"))
    monkeypatch.setattr("cricket_scoring.auth.st", fake_st)

    manager = GoogleAuthManager(_config())

    with pytest.raises(RuntimeError, match="rerun"):
        manager.render_login_controls()

    assert any("signed in as player one" in msg.lower() for msg in fake_st.messages["success"])
    assert fake_st.session_state["auth_mode"] == AUTH_MODE_LOCAL


def test_auth_state_persists_across_restart(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    auth_file = tmp_path / "auth_state.json"
    monkeypatch.setenv("LOCAL_AUTH_STATE_FILE", str(auth_file))

    st1 = FakeStreamlit()
    st1.session_state["google_credentials"] = {"token": "t", "id_token": "abc"}
    st1.session_state["google_profile"] = {"sub": "1", "email": "user@gmail.com", "name": "User"}
    monkeypatch.setattr("cricket_scoring.auth.st", st1)
    manager = GoogleAuthManager(_config())
    manager._persist_auth_state()

    st2 = FakeStreamlit()
    monkeypatch.setattr("cricket_scoring.auth.st", st2)
    manager2 = GoogleAuthManager(_config())
    manager2.restore_auth_state()

    assert st2.session_state["google_profile"]["name"] == "User"
    assert st2.session_state["auth_mode"] == AUTH_MODE_GOOGLE


def test_non_gmail_auth_state_not_restored_as_authenticated(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    auth_file = tmp_path / "auth_state.json"
    monkeypatch.setenv("LOCAL_AUTH_STATE_FILE", str(auth_file))

    st1 = FakeStreamlit()
    st1.session_state["google_credentials"] = {"token": "t", "id_token": "abc"}
    st1.session_state["google_profile"] = {"sub": "1", "email": "user@company.com", "name": "User"}
    monkeypatch.setattr("cricket_scoring.auth.st", st1)
    manager = GoogleAuthManager(_config())
    manager._persist_auth_state()

    st2 = FakeStreamlit()
    monkeypatch.setattr("cricket_scoring.auth.st", st2)
    manager2 = GoogleAuthManager(_config())
    manager2.restore_auth_state()

    assert st2.session_state.get("auth_mode") == AUTH_MODE_LOCAL
    assert "google_profile" not in st2.session_state
    assert "google_credentials" not in st2.session_state


def test_runtime_oauth_config_saved_and_restored(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    auth_file = tmp_path / "auth_state.json"
    monkeypatch.setenv("LOCAL_AUTH_STATE_FILE", str(auth_file))

    st1 = FakeStreamlit()
    st1.session_state[RUNTIME_OAUTH_CLIENT_CONFIG_KEY] = json.dumps({"web": {"client_id": "id"}})
    st1.session_state[RUNTIME_OAUTH_REDIRECT_URI_KEY] = "http://localhost:8501"
    monkeypatch.setattr("cricket_scoring.auth.st", st1)
    manager = GoogleAuthManager(
        AppConfig(google_oauth_client_config_json="", google_oauth_redirect_uri="", google_sheet_url="", auth_bypass=False)
    )
    manager._persist_auth_state()

    st2 = FakeStreamlit()
    monkeypatch.setattr("cricket_scoring.auth.st", st2)
    manager2 = GoogleAuthManager(
        AppConfig(google_oauth_client_config_json="", google_oauth_redirect_uri="", google_sheet_url="", auth_bypass=False)
    )
    manager2.restore_auth_state()

    assert st2.session_state[RUNTIME_OAUTH_CLIENT_CONFIG_KEY]
    assert st2.session_state[RUNTIME_OAUTH_REDIRECT_URI_KEY] == "http://localhost:8501"


def test_render_setup_controls_validate_runtime_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    fake_st = FakeStreamlit()
    fake_st.button_responses["save-google-login-settings"] = True
    fake_st.text_area_values["google-oauth-client-config-input"] = "{bad"
    fake_st.text_input_values["google-oauth-redirect-uri-input"] = "not-a-url"
    monkeypatch.setenv("LOCAL_AUTH_STATE_FILE", str(tmp_path / "auth_state.json"))
    monkeypatch.setattr("cricket_scoring.auth.st", fake_st)

    manager = GoogleAuthManager(
        AppConfig(google_oauth_client_config_json="", google_oauth_redirect_uri="", google_sheet_url="", auth_bypass=False)
    )
    mode = manager.render_login_controls()

    assert mode == AUTH_MODE_LOCAL
    assert "invalid" in fake_st.session_state["auth_error"].lower()
    assert not fake_st.link_calls


def test_render_setup_controls_enable_google_login_after_valid_save(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    fake_st = FakeStreamlit()
    fake_st.button_responses["save-google-login-settings"] = True
    fake_st.text_area_values["google-oauth-client-config-input"] = json.dumps({"web": {"client_id": "id", "client_secret": "s"}})
    fake_st.text_input_values["google-oauth-redirect-uri-input"] = "http://localhost:8501"
    monkeypatch.setenv("LOCAL_AUTH_STATE_FILE", str(tmp_path / "auth_state.json"))
    monkeypatch.setattr("cricket_scoring.auth.st", fake_st)

    manager = GoogleAuthManager(
        AppConfig(google_oauth_client_config_json="", google_oauth_redirect_uri="", google_sheet_url="", auth_bypass=False)
    )

    with pytest.raises(RuntimeError, match="rerun"):
        manager.render_login_controls()

    assert RUNTIME_OAUTH_CLIENT_CONFIG_KEY in fake_st.session_state


def test_extract_profile_allows_consumer_google_account(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    fake_st = FakeStreamlit()
    monkeypatch.setenv("LOCAL_AUTH_STATE_FILE", str(tmp_path / "auth_state.json"))
    monkeypatch.setattr("cricket_scoring.auth.st", fake_st)
    manager = GoogleAuthManager(_config())

    creds = SimpleNamespace(id_token=_make_id_token({"sub": "abc", "email": "someone@gmail.com", "name": "Someone"}))

    profile = manager._extract_profile(creds)

    assert profile["email"].endswith("@gmail.com")


def test_extract_profile_rejects_missing_fields(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    fake_st = FakeStreamlit()
    monkeypatch.setenv("LOCAL_AUTH_STATE_FILE", str(tmp_path / "auth_state.json"))
    monkeypatch.setattr("cricket_scoring.auth.st", fake_st)
    manager = GoogleAuthManager(_config())

    with pytest.raises(ValidationError):
        manager._extract_profile(SimpleNamespace(id_token=_make_id_token({"sub": "x", "name": "Name"})))


def test_extract_profile_raises_for_invalid_token(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    fake_st = FakeStreamlit()
    monkeypatch.setenv("LOCAL_AUTH_STATE_FILE", str(tmp_path / "auth_state.json"))
    monkeypatch.setattr("cricket_scoring.auth.st", fake_st)
    manager = GoogleAuthManager(_config())

    with pytest.raises(ValidationError):
        manager._extract_profile(SimpleNamespace(id_token="bad-token"))


def test_google_password_not_collected_in_app_ui(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    fake_st = FakeStreamlit()
    monkeypatch.setenv("LOCAL_AUTH_STATE_FILE", str(tmp_path / "auth_state.json"))
    monkeypatch.setattr("cricket_scoring.auth.st", fake_st)

    manager = GoogleAuthManager(
        AppConfig(google_oauth_client_config_json="", google_oauth_redirect_uri="", google_sheet_url="", auth_bypass=False)
    )
    manager.render_login_controls()

    assert all("password" not in label.lower() for label in fake_st.text_input_labels)
    assert any("google-hosted" in msg.lower() for msg in fake_st.messages["caption"])
