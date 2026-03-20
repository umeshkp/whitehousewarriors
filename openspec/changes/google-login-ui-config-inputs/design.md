## Context

The app already supports optional Google login and local CSV fallback, but Google sign-in appears unavailable unless OAuth values are preconfigured via environment variables. In practical use, users launch the UI and only see local-mode messaging, so the expected Google account chooser never appears. We need an in-app way to provide required OAuth inputs, validate them, and immediately enable the existing popup sign-in flow without breaking scoring rules or local fallback behavior.

## Goals / Non-Goals

**Goals:**
- Add UI inputs for OAuth client config JSON and redirect URI so users can enable Google login from the app.
- Validate OAuth input early and present actionable errors before attempting login.
- Enable popup-style "Continue with Google" once valid input is saved.
- Ensure users can select existing Google accounts and add/sign in to another account via Google's popup account chooser.
- Preserve optional auth behavior: users can always continue in local mode.
- Keep auth/session persistence behavior intact across refresh and app restart.

**Non-Goals:**
- Introducing new identity providers beyond Google.
- Changing cricket scoring domain rules (overs, strike rotation, extras handling).
- Replacing Google OAuth library or adding backend auth services.

## Decisions

1. Runtime OAuth override in config/auth initialization
- Decision: Extend config/auth bootstrap to accept runtime OAuth values from Streamlit session state, with environment values as default.
- Rationale: Keeps existing env-based setup working while enabling no-env UI setup.
- Alternative: Require env vars only and improve messaging.
  - Rejected because it does not solve the user’s core issue in hosted/demo runs.

2. Dedicated login configuration UI block before Google login action
- Decision: In the login panel, show input controls for OAuth JSON and redirect URI whenever Google login is not currently configured.
- Rationale: Makes missing prerequisites explicit and discoverable in the same place users expect sign-in.
- Alternative: Put OAuth inputs in a separate settings page.
  - Rejected due extra navigation friction and weaker troubleshooting flow.

3. Validation-first save flow
- Decision: Add a "Save Google Login Settings" action that validates JSON shape (`web` or `installed`) and redirect URI before enabling the Google login button.
- Rationale: Prevents broken auth URLs and confusing callback failures.
- Alternative: Attempt authorization URL generation directly from raw input and fail late.
  - Rejected because late failures are harder to diagnose.

4. Preserve dual-mode behavior and messaging
- Decision: Keep local scoring mode fully available, and show mode/auth-state messaging that distinguishes "not configured" from OAuth callback/token failures.
- Rationale: Maintains uninterrupted scoring while clarifying login path.
- Alternative: Block scoring until auth configured.
  - Rejected because optional-auth requirement disallows hard gating.

5. Do not collect Google passwords in application UI
- Decision: The app will not render custom Google email/password fields; authentication remains delegated to Google's hosted OAuth pages.
- Rationale: Capturing passwords in first-party UI is insecure and not aligned with Google OAuth best practices.
- Alternative: Add app-managed Google ID/password inputs.
  - Rejected for security, compliance, and account protection reasons.

## Risks / Trade-offs

- [Sensitive OAuth JSON entered in UI] → Mitigation: keep values in session/runtime scope and avoid logging raw secrets in error messages.
- [Users expect direct password entry in app] → Mitigation: add UI copy explaining that account/password entry happens in the Google popup ("Use another account").
- [Invalid redirect URI causes callback confusion] → Mitigation: upfront URI validation plus guided error copy describing expected redirect URL.
- [State mismatch from stale query params] → Mitigation: preserve existing nonce validation and callback query clearing.
- [Users confuse local-mode fallback with auth failure] → Mitigation: add explicit status text: not configured vs failed vs authenticated.

## Migration Plan

1. Add runtime OAuth input model in login/config flow.
2. Add login UI controls to capture/save/validate OAuth JSON and redirect URI.
3. Wire auth manager to use runtime settings when present and valid.
4. Update auth error/status messaging for configuration vs OAuth failures.
5. Add tests for config input validation, Google button visibility, and fallback behavior.
6. Update README/setup notes for in-app OAuth input option.

Rollback strategy:
- Revert login UI config inputs and runtime override logic.
- Keep current env-only configuration path and local fallback mode intact.

## Open Questions

- Should UI-provided OAuth config persist to disk across full server restarts, or remain session-only for security? (default in this change: session/runtime only)
- Should the OAuth JSON be entered as raw text only, or also support file upload for easier setup?
