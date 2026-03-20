## Why

Users currently see only a local-mode login message because Google OAuth settings are not configured from the UI. This blocks expected Google sign-in and creates confusion when users want to authenticate without editing environment variables.

## What Changes

- Add an in-app Google OAuth configuration panel that accepts required login settings (client config JSON and redirect URI) and validates them before sign-in.
- Update login behavior to surface Google login controls when valid UI-provided settings are saved for the session.
- Ensure the Google popup uses account chooser behavior so users can pick an existing account or use Google's "Use another account" path.
- Keep credential entry (email/password) on Google's hosted login screen only; do not collect Google passwords inside this app UI.
- Add clear validation and recovery messaging when OAuth input is missing/invalid.
- Preserve optional-login behavior so users can still continue in local scoring mode.
- Document required Google login inputs and troubleshooting steps in the UI/help text.

## Capabilities

### New Capabilities
- `google-login-ui-configuration`: UI capture and validation of Google OAuth input required to enable popup sign-in.

### Modified Capabilities
- `google-popup-account-login`: Login availability logic now includes runtime UI-provided OAuth configuration, not only environment config.
- `optional-auth-scoring-mode`: Local-mode fallback messaging and mode transitions are updated to reflect configurable Google login availability.

## Impact

- Affected code: Streamlit login/auth UI, config loading/validation path, and auth manager initialization flow.
- Dependencies/APIs: Existing Google OAuth flow and callbacks (no new external provider).
- UX impact: Users can enable Google login directly in the app and receive actionable configuration feedback.
- Risk: Misconfigured JSON or redirect URI can still fail login; mitigated by input validation and explicit error states.
