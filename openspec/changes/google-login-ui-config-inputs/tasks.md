## 1. OAuth Configuration Input Foundation

- [x] 1.1 Add runtime OAuth configuration state fields (client config JSON + redirect URI) and wire them into app/session config resolution.
- [x] 1.2 Implement validation helpers for OAuth JSON structure (`web`/`installed`) and redirect URI presence/format.
- [x] 1.3 Ensure invalid runtime config cannot be used to build authorization flows.

## 2. Login UI and Auth Flow Integration

- [x] 2.1 Add login-panel inputs and a "Save Google Login Settings" action when Google login is not configured.
- [x] 2.2 Update auth manager/login controls to enable "Continue with Google" after valid UI config is saved.
- [x] 2.3 Enforce Google popup account chooser behavior (`prompt=select_account`) so users can pick existing accounts or "Use another account".
- [x] 2.4 Preserve and verify "Continue without login" path so local scoring mode remains fully available.
- [x] 2.5 Add explicit user-facing messages for configuration missing, configuration invalid, and OAuth callback/token failures.
- [x] 2.6 Add login helper text clarifying that Google email/password entry occurs on Google-hosted screens, not in-app fields.

## 3. Persistence and Mode Behavior

- [x] 3.1 Persist runtime OAuth configuration safely for the active UI session and across browser refresh where appropriate.
- [x] 3.2 Keep authenticated/local mode indicator behavior consistent with new configuration states.
- [x] 3.3 Verify scoring workflow, over progression, and local CSV fallback remain unaffected by login configuration changes.

## 4. Verification and Documentation

- [x] 4.1 Add tests for OAuth config input validation success/failure and Google login button visibility toggling.
- [x] 4.2 Add tests for optional-auth behavior when config is missing/invalid and for recovery after config correction.
- [x] 4.3 Add tests for OAuth callback state/error behavior using runtime-provided config.
- [x] 4.4 Add tests/assertions that app UI does not request Google password fields and delegates credential entry to Google-hosted flow.
- [x] 4.5 Update README/help text with in-app Google OAuth setup steps, "Use another account" guidance, and troubleshooting notes.
