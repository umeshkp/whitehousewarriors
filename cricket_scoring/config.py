from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse


@dataclass(frozen=True)
class AppConfig:
    google_oauth_client_config_json: str
    google_oauth_redirect_uri: str
    google_sheet_url: str
    auth_bypass: bool

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            google_oauth_client_config_json=os.getenv("GOOGLE_OAUTH_CLIENT_CONFIG_JSON", "").strip(),
            google_oauth_redirect_uri=os.getenv("GOOGLE_OAUTH_REDIRECT_URI", "").strip(),
            google_sheet_url=os.getenv("GOOGLE_SHEET_URL", "").strip(),
            auth_bypass=os.getenv("AUTH_BYPASS", "false").lower() == "true",
        )

    def has_google_oauth_config(self) -> bool:
        return bool(self.google_oauth_client_config_json and self.google_oauth_redirect_uri)

    @staticmethod
    def validate_oauth_inputs(client_config_json: str, redirect_uri: str) -> list[str]:
        errors: list[str] = []
        cfg = (client_config_json or "").strip()
        redirect = (redirect_uri or "").strip()
        if not cfg:
            errors.append("Google OAuth client configuration JSON is required.")
            return errors
        try:
            parsed = json.loads(cfg)
            if not isinstance(parsed, dict):
                errors.append("Google OAuth client configuration must be a JSON object.")
            elif "web" not in parsed and "installed" not in parsed:
                errors.append("OAuth client config must include a 'web' or 'installed' object.")
        except json.JSONDecodeError:
            errors.append("Google OAuth client configuration is not valid JSON.")

        if not redirect:
            errors.append("Google OAuth redirect URI is required.")
        else:
            parsed_redirect = urlparse(redirect)
            if not parsed_redirect.scheme or not parsed_redirect.netloc:
                errors.append("Google OAuth redirect URI must be an absolute URL.")
        return errors

    def with_runtime_oauth(self, client_config_json: str, redirect_uri: str) -> "AppConfig":
        return AppConfig(
            google_oauth_client_config_json=(client_config_json or "").strip() or self.google_oauth_client_config_json,
            google_oauth_redirect_uri=(redirect_uri or "").strip() or self.google_oauth_redirect_uri,
            google_sheet_url=self.google_sheet_url,
            auth_bypass=self.auth_bypass,
        )

    def validate_startup(self) -> list[str]:
        errors: list[str] = []
        if self.auth_bypass or not self.google_oauth_client_config_json:
            return errors
        errors.extend(self.validate_oauth_inputs(self.google_oauth_client_config_json, self.google_oauth_redirect_uri))
        return errors

    def oauth_client_config(self) -> dict[str, Any]:
        return json.loads(self.google_oauth_client_config_json)
