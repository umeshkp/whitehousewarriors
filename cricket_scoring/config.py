from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any


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

    def validate_startup(self) -> list[str]:
        errors: list[str] = []
        if self.auth_bypass or not self.google_oauth_client_config_json:
            return errors
        try:
            parsed = json.loads(self.google_oauth_client_config_json)
            if not isinstance(parsed, dict):
                errors.append("GOOGLE_OAUTH_CLIENT_CONFIG_JSON must be a JSON object.")
            elif "web" not in parsed and "installed" not in parsed:
                errors.append("OAuth client config must include a 'web' or 'installed' object.")
        except json.JSONDecodeError:
            errors.append("GOOGLE_OAUTH_CLIENT_CONFIG_JSON is not valid JSON.")
        if self.google_oauth_client_config_json and not self.google_oauth_redirect_uri:
            errors.append("GOOGLE_OAUTH_REDIRECT_URI is required when GOOGLE_OAUTH_CLIENT_CONFIG_JSON is set.")
        return errors

    def oauth_client_config(self) -> dict[str, Any]:
        return json.loads(self.google_oauth_client_config_json)
