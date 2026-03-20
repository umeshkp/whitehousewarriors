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
RUNTIME_OAUTH_CLIENT_CONFIG_KEY = "runtime_google_oauth_client_config_json"
RUNTIME_OAUTH_REDIRECT_URI_KEY = "runtime_google_oauth_redirect_uri"


class GoogleAuthManager:
    def __init__(self, config: AppConfig):
        self._config = config
        self._auth_state_path = Path(os.getenv("LOCAL_AUTH_STATE_FILE", ".local_scoring/auth_state.json"))
        self._auth_state_path.parent.mkdir(parents=True, exist_ok=True)

    def _runtime_oauth_values(self) -> tuple[str, str]:
        return (
            str(st.session_state.get(RUNTIME_OAUTH_CLIENT_CONFIG_KEY, "")).strip(),
            str(st.session_state.get(RUNTIME_OAUTH_REDIRECT_URI_KEY, "")).strip(),
        )

    def _effective_config(self) -> AppConfig:
        runtime_client, runtime_redirect = self._runtime_oauth_values()
        if runtime_client or runtime_redirect:
            return self._config.with_runtime_oauth(runtime_client, runtime_redirect)
        return self._config

    def _build_flow(self, state: str | None = None) -> Flow:
        effective_config = self._effective_config()
        flow = Flow.from_client_config(
            effective_config.oauth_client_config(),
            scopes=SCOPES,
            state=state,
        )
        flow.redirect_uri = effective_config.google_oauth_redirect_uri
        return flow

    def has_google_login(self) -> bool:
        return self._config.auth_bypass or self._effective_config().has_google_oauth_config()

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

    @staticmethod
    def _is_gmail_email(email: str) -> bool:
        return email.strip().lower().endswith("@gmail.com")

    def _persist_auth_state(self) -> None:
        payload = {
            "google_credentials": st.session_state.get("google_credentials"),
            "google_profile": st.session_state.get("google_profile"),
            RUNTIME_OAUTH_CLIENT_CONFIG_KEY: st.session_state.get(RUNTIME_OAUTH_CLIENT_CONFIG_KEY, ""),
            RUNTIME_OAUTH_REDIRECT_URI_KEY: st.session_state.get(RUNTIME_OAUTH_REDIRECT_URI_KEY, ""),
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
            runtime_client = str(data.get(RUNTIME_OAUTH_CLIENT_CONFIG_KEY, "")).strip()
            runtime_redirect = str(data.get(RUNTIME_OAUTH_REDIRECT_URI_KEY, "")).strip()
            if runtime_client:
                st.session_state[RUNTIME_OAUTH_CLIENT_CONFIG_KEY] = runtime_client
            if runtime_redirect:
                st.session_state[RUNTIME_OAUTH_REDIRECT_URI_KEY] = runtime_redirect
            if creds and profile:
                email = str(profile.get("email", "")).strip()
                if not self._is_gmail_email(email):
                    st.session_state["auth_mode"] = AUTH_MODE_LOCAL
                    return
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
        runtime_client, runtime_redirect = self._runtime_oauth_values()
        if runtime_client or runtime_redirect:
            self._persist_auth_state()
        elif self._auth_state_path.exists():
            try:
                self._auth_state_path.unlink()
            except OSError:
                pass

    def _save_runtime_oauth_inputs(self, client_config_json: str, redirect_uri: str) -> list[str]:
        errors = AppConfig.validate_oauth_inputs(client_config_json, redirect_uri)
        if errors:
            return errors
        st.session_state[RUNTIME_OAUTH_CLIENT_CONFIG_KEY] = client_config_json.strip()
        st.session_state[RUNTIME_OAUTH_REDIRECT_URI_KEY] = redirect_uri.strip()
        self._persist_auth_state()
        return []

    def _render_oauth_setup_controls(self) -> None:
        runtime_client, runtime_redirect = self._runtime_oauth_values()
        default_client = runtime_client or self._config.google_oauth_client_config_json
        default_redirect = runtime_redirect or self._config.google_oauth_redirect_uri or "http://localhost:8501"
        client_config_json = st.text_area(
            "Google OAuth Client Config JSON",
            value=default_client,
            height=120,
            key="google-oauth-client-config-input",
        )
        redirect_uri = st.text_input(
            "Google OAuth Redirect URI",
            value=default_redirect,
            key="google-oauth-redirect-uri-input",
        )
        st.caption("Use Google popup sign-in. Account and password entry happens on Google-hosted screens.")
        if st.button("Save Google Login Settings", key="save-google-login-settings"):
            errors = self._save_runtime_oauth_inputs(client_config_json, redirect_uri)
            if errors:
                st.session_state["auth_error"] = "Google login configuration is invalid: " + " ".join(errors)
            else:
                st.session_state.pop("auth_error", None)
                st.success("Google login settings saved. You can continue with Google.")
                st.rerun()

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

        expected_state = st.session_state.get("oauth_state")

        try:
            flow = self._build_flow(state=expected_state)
            flow.fetch_token(code=code)
            profile = self._extract_profile(flow.credentials)
            if not self._is_gmail_email(profile["email"]):
                self.clear_auth_state()
                st.session_state["auth_error"] = (
                    "Google sign-in completed, but a Gmail account is required for authenticated mode. "
                    "Continue without login or sign in with a @gmail.com account."
                )
                return
            self._save_credentials(flow.credentials)
            st.session_state["google_profile"] = profile
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

        if self._effective_config().has_google_oauth_config():
            self._handle_oauth_callback()
        else:
            st.info("Google login is not configured. Add OAuth settings below or continue in local scoring mode.")
            self._render_oauth_setup_controls()

        if self.is_authenticated():
            profile = st.session_state.get("google_profile", {})
            st.success(f"Signed in as {profile.get('name', 'Unknown User')}")
            if st.button("Logout", key="logout-button"):
                self.clear_auth_state()
                st.rerun()
            return AUTH_MODE_GOOGLE

        if err := st.session_state.get("auth_error"):
            st.error(err)

        if self._effective_config().has_google_oauth_config():
            auth_url = self._begin_google_auth()
            if auth_url:
                st.link_button("Continue with Google", auth_url, use_container_width=True)
                st.caption("Use another account in the Google popup if needed.")
                st.caption("Google email/password is entered on Google-hosted pages, not in this app.")
        else:
            st.caption("Google sign-in is unavailable until valid OAuth settings are saved.")

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
