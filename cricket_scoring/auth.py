from __future__ import annotations

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


class GoogleAuthManager:
    def __init__(self, config: AppConfig):
        self._config = config

    def _build_flow(self, state: str | None = None) -> Flow:
        flow = Flow.from_client_config(
            self._config.oauth_client_config(),
            scopes=SCOPES,
            state=state,
        )
        flow.redirect_uri = self._config.google_oauth_redirect_uri
        return flow

    def _save_credentials(self, credentials: Credentials) -> None:
        st.session_state["google_credentials"] = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
        }

    def is_authenticated(self) -> bool:
        if self._config.auth_bypass:
            return st.session_state.get("auth_bypass_user") is True
        return "google_credentials" in st.session_state

    def render_auth_panel(self) -> bool:
        if self._config.auth_bypass:
            st.warning("AUTH_BYPASS is enabled. Use only for local development.")
            if st.button("Continue in bypass mode", key="bypass-login"):
                st.session_state["auth_bypass_user"] = True
                st.rerun()
            return self.is_authenticated()

        query = st.query_params
        if "code" in query:
            incoming_state = query.get("state")
            expected_state = st.session_state.get("oauth_state")
            if expected_state and incoming_state != expected_state:
                st.error("OAuth state mismatch. Please retry sign-in.")
                return False
            try:
                flow = self._build_flow(state=expected_state)
                flow.fetch_token(code=query["code"])
                self._save_credentials(flow.credentials)
                query.clear()
                st.rerun()
            except Exception as exc:
                st.error(f"Google sign-in failed: {exc}")
                return False

        try:
            flow = self._build_flow()
            auth_url, state = flow.authorization_url(
                access_type="offline",
                include_granted_scopes="true",
                prompt="consent",
            )
            st.session_state["oauth_state"] = state
            st.info("Sign in with your Google account to continue.")
            st.link_button("Sign in with Google", auth_url, use_container_width=True)
        except Exception as exc:
            st.error(f"OAuth client configuration issue: {exc}")
            return False

        return self.is_authenticated()


def credentials_from_session(session_state: dict[str, Any]) -> Credentials:
    info = session_state.get("google_credentials")
    if not info:
        raise ValidationError("User is not authenticated with Google.")
    return Credentials.from_authorized_user_info(info)
