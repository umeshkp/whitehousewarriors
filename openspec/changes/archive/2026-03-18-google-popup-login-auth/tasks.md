## 1. Auth Flow Foundations

- [x] 1.1 Review existing auth module and add/adjust interfaces for popup-style Google sign-in initiation.
- [x] 1.2 Implement OAuth authorization URL generation with account-selection prompt parameters.
- [x] 1.3 Implement strict OAuth state nonce creation, storage, and callback validation.
- [x] 1.4 Add robust callback handling for success, cancellation, and token exchange failure paths.
- [x] 1.5 Add “continue without login” path to enter unauthenticated local scoring mode.

## 2. Profile Ingestion and Session State

- [x] 2.1 Implement normalized Google profile extraction (`sub`, `email`, `name`) from token/userinfo.
- [x] 2.2 Persist normalized profile and auth credentials safely in Streamlit session state.
- [x] 2.3 Reject login completion when required profile fields are missing and surface actionable retry guidance.
- [x] 2.4 Add logout behavior that clears credentials/profile and transitions app to local scoring mode.
- [x] 2.5 Implement secure auth persistence across browser refresh and UI restarts.

## 3. UI Integration and Guarding

- [x] 3.1 Add popup-style “Continue with Google” login UI entry and signed-in name-only identity display.
- [x] 3.2 Add explicit scoring mode indicator for authenticated Google mode vs unauthenticated local mode.
- [x] 3.3 Ensure scoring and match progression stay enabled while unauthenticated.
- [x] 3.4 Add local CSV persistence path when in unauthenticated mode.
- [x] 3.5 Restore local CSV-backed scoring state across browser refresh and UI restart.
- [x] 3.6 Add match-end CSV download button for local-mode scoring sessions.
- [x] 3.7 Add user-facing auth state/error messaging for all major login outcomes.
- [x] 3.8 Ensure login supports all Google accounts with no domain restriction checks.

## 4. Verification and Documentation

- [x] 4.1 Add unit tests for OAuth state validation and callback success/error handling.
- [x] 4.2 Add tests for normalized profile ingestion and required-field enforcement.
- [x] 4.3 Add UI behavior tests for optional login, mode indicator, name-only authenticated display, and logout transition to local mode.
- [x] 4.4 Add tests that verify local CSV persistence across refresh/UI restart and match-end CSV download.
- [x] 4.5 Add tests that verify auth persistence across browser refresh/UI restart and unrestricted Google account acceptance.
- [x] 4.6 Update project documentation for optional login, local CSV fallback, download flow, OAuth setup, and troubleshooting guidance.
