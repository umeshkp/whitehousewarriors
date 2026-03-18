from __future__ import annotations

import base64
import json
import os
import secrets
from pathlib import Path
from typing import Any

import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

from cricket_scoring.config import AppConfig
from cricket_scoring.models import ValidationError

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/spreadsheets",
]

AUTH_MODE_GOOGLE = "google-authenticated"
AUTH_MODE_LOCAL = "local-csv-fallback"


class GoogleAuthManager:
    def __init__(self, config: AppConfig):
        self._config = config
        self._auth_state_path = Path(os.getenv("LOCAL_AUTH_STATE_FILE", ".local_scoring/auth_state.json"))
        self._auth_state_path.parent.mkdir(parents=True, exist_ok=True)

    def _build_flow(self, state: str | None = None) -> Flow:
        flow = Flow.from_client_config(
            self._config.oauth_client_config(),
            scopes=SCOPES,
            state=state,
        )
        flow.redirect_uri = self._config.google_oauth_redirect_uri
        return flow

    def has_google_login(self) -> bool:
        return self._config.auth_bypass or self._config.has_google_oauth_config()

    def is_authenticated(self) -> bool:
        if self._config.auth_bypass:
            return st.session_state.get("auth_bypass_user") is True
        return "google_credentials" in st.session_state and "google_profile" in st.session_state

    def current_mode(self) -> str:
        return AUTH_MODE_GOOGLE if self.is_authenticated() else AUTH_MODE_LOCAL

    def _save_credentials(self, credentials: Credentials) -> None:
        st.session_state["google_credentials"] = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
            "id_token": getattr(credentials, "id_token", None),
        }

    def _decode_jwt_payload(self, jwt_token: str) -> dict[str, Any]:
        try:
            payload_segment = jwt_token.split(".")[1]
            padded = payload_segment + "=" * (-len(payload_segment) % 4)
            decoded = base64.urlsafe_b64decode(padded.encode("utf-8"))
            return json.loads(decoded.decode("utf-8"))
        except Exception as exc:
            raise ValidationError(f"Unable to decode Google identity token: {exc}") from exc

    def _extract_profile(self, credentials: Credentials) -> dict[str, str]:
        id_token = getattr(credentials, "id_token", None)
        if not id_token:
            raise ValidationError("Missing Google identity token; cannot extract profile.")
        payload = self._decode_jwt_payload(id_token)
        sub = str(payload.get("sub", "")).strip()
        email = str(payload.get("email", "")).strip()
        name = str(payload.get("name", "")).strip()
        if not sub or not email or not name:
            raise ValidationError("Google profile is missing required fields (sub/email/name).")
        return {"sub": sub, "email": email, "name": name}

    def _persist_auth_state(self) -> None:
        payload = {
            "google_credentials": st.session_state.get("google_credentials"),
            "google_profile": st.session_state.get("google_profile"),
        }
        self._auth_state_path.write_text(json.dumps(payload), encoding="utf-8")
        try:
            os.chmod(self._auth_state_path, 0o600)
        except OSError:
            pass

    def restore_auth_state(self) -> None:
        if self.is_authenticated() or not self._auth_state_path.exists() or self._config.auth_bypass:
            return
        try:
            data = json.loads(self._auth_state_path.read_text(encoding="utf-8"))
            creds = data.get("google_credentials")
            profile = data.get("google_profile")
            if creds and profile:
                st.session_state["google_credentials"] = creds
                st.session_state["google_profile"] = profile
                st.session_state["auth_mode"] = AUTH_MODE_GOOGLE
        except json.JSONDecodeError:
            return

    def clear_auth_state(self) -> None:
        st.session_state.pop("google_credentials", None)
        st.session_state.pop("google_profile", None)
        st.session_state.pop("oauth_state", None)
        st.session_state.pop("auth_bypass_user", None)
        st.session_state["auth_mode"] = AUTH_MODE_LOCAL
        if self._auth_state_path.exists():
            try:
                self._auth_state_path.unlink()
            except OSError:
                pass

    def _begin_google_auth(self) -> str | None:
        try:
            flow = self._build_flow(state=secrets.token_urlsafe(32))
            auth_url, state = flow.authorization_url(
                access_type="offline",
                include_granted_scopes="true",
                prompt="select_account consent",
            )
            st.session_state["oauth_state"] = state
            return auth_url
        except Exception as exc:
            st.session_state["auth_error"] = f"OAuth client configuration issue: {exc}"
            return None

    def _handle_oauth_callback(self) -> None:
        query = st.query_params
        if "error" in query:
            st.session_state["auth_error"] = (
                f"Google sign-in was not completed ({query.get('error')}). "
                "Please retry or continue without login."
            )
            query.clear()
            return

        code = query.get("code")
        if not code:
            return

        incoming_state = query.get("state")
        expected_state = st.session_state.get("oauth_state")
        if expected_state and incoming_state != expected_state:
            st.session_state["auth_error"] = "OAuth state mismatch. Please retry sign-in."
            query.clear()
            return

        try:
            flow = self._build_flow(state=expected_state)
            flow.fetch_token(code=code)
            self._save_credentials(flow.credentials)
            st.session_state["google_profile"] = self._extract_profile(flow.credentials)
            st.session_state["auth_mode"] = AUTH_MODE_GOOGLE
            st.session_state.pop("auth_error", None)
            self._persist_auth_state()
        except ValidationError as exc:
            self.clear_auth_state()
            st.session_state["auth_error"] = f"Google profile missing required data: {exc}. Please retry sign-in."
        except Exception as exc:
            self.clear_auth_state()
            st.session_state["auth_error"] = f"Google sign-in failed: {exc}. Please retry."
        finally:
            st.session_state.pop("oauth_state", None)
            query.clear()

    def render_login_controls(self) -> str:
        self.restore_auth_state()

        if self._config.auth_bypass:
            st.warning("AUTH_BYPASS is enabled. Use only for local development.")
            if st.button("Sign in (bypass)", key="bypass-login"):
                st.session_state["auth_bypass_user"] = True
                st.session_state["google_profile"] = {
                    "sub": "local",
                    "email": "local@bypass",
                    "name": "Local User",
                }
                st.session_state["auth_mode"] = AUTH_MODE_GOOGLE
                st.rerun()
            if st.button("Continue without login", key="continue-local-bypass"):
                self.clear_auth_state()
                st.rerun()
            return self.current_mode()

        if self._config.has_google_oauth_config():
            self._handle_oauth_callback()
        else:
            st.info("Google login is not configured. You can continue in local scoring mode.")

        if self.is_authenticated():
            profile = st.session_state.get("google_profile", {})
            st.success(f"Signed in as {profile.get('name', 'Unknown User')}")
            if st.button("Logout", key="logout-button"):
                self.clear_auth_state()
                st.rerun()
            return AUTH_MODE_GOOGLE

        if err := st.session_state.get("auth_error"):
            st.error(err)

        if self._config.has_google_oauth_config():
            auth_url = self._begin_google_auth()
            if auth_url:
                st.link_button("Continue with Google", auth_url, use_container_width=True)

        if st.button("Continue without login", key="continue-local"):
            self.clear_auth_state()
            st.rerun()

        st.session_state["auth_mode"] = AUTH_MODE_LOCAL
        return AUTH_MODE_LOCAL


def credentials_from_session(session_state: dict[str, Any]) -> Credentials:
    info = session_state.get("google_credentials")
    if not info:
        raise ValidationError("User is not authenticated with Google.")
    return Credentials.from_authorized_user_info(info)
