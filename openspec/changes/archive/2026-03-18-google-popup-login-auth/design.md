## Context

The current app already has Google OAuth plumbing but presents login as a basic redirect-driven flow and does not clearly emulate the familiar popup account-selector experience users expect from modern products. We need to provide a login UX that behaves like “Continue with Google,” while also allowing scoring when authentication is skipped or unavailable by persisting to local CSV with browser download at match end.

This change affects UI flow, auth/session handling, identity data retrieval, and a fallback persistence path. It does not change scoring rules or over logic.

## Goals / Non-Goals

**Goals:**
- Provide a login entry point that opens Google authentication in a popup/new-window style flow and allows account selection.
- Make login optional and allow full scoring flow without Google authentication.
- Complete OAuth exchange safely and store authenticated state in session.
- Fetch and store user identity information from Google while rendering name-only text identity in UI.
- Persist authenticated login state across browser refresh and UI restarts.
- Allow all Google accounts without domain restriction.
- Persist unauthenticated scoring data in local CSV format across browser refresh.
- Provide match-end CSV download action for locally persisted scoring.
- Show signed-in user identity in UI while allowing scoring in both auth and no-auth modes.
- Provide clear user-facing handling for auth cancellation and OAuth/token errors.

**Non-Goals:**
- Multi-provider auth (Microsoft, GitHub, etc.).
- Role/permission management beyond “authenticated vs unauthenticated.”
- Building a custom identity provider backend.
- Replacing existing cricket scoring domain logic.

## Decisions

1. Popup-style UX via dedicated Google sign-in trigger and callback completion
- Decision: Use a “Continue with Google” button that initiates OAuth with account selection prompt and returns to callback handling that finalizes session in-app.
- Rationale: Aligns with user expectation of account chooser flow while keeping Streamlit-compatible implementation.
- Alternative considered: Keep fully inline redirect-only login without account-selection prompt.
  - Rejected because it feels less familiar and does not explicitly encourage account choice behavior.

2. Use OAuth `prompt=select_account consent` and strict state validation
- Decision: Force account selection through OAuth prompt parameters and validate returned `state` against stored session nonce.
- Rationale: Ensures users can pick the intended Google account and protects against CSRF/state mismatch risks.
- Alternative considered: Rely on default prompt behavior.
  - Rejected because default behavior may silently reuse prior sessions without clear account selection.

3. Store normalized user profile in session after token exchange
- Decision: After successful login, parse ID token/userinfo and persist normalized fields (`sub`, `email`, `name`) with name as the only user-facing identity display field.
- Rationale: Keeps UI simple while preserving required identity keys for session integrity.
- Alternative considered: Render avatar/picture and extra profile attributes in primary UI.
  - Rejected to keep login identity display text-only and minimal.

4. Persist auth state across refresh and app restarts
- Decision: Persist authenticated identity/credentials in a secure storage abstraction (for example encrypted cookie/session backend) so auth survives browser refresh and Streamlit UI restart.
- Rationale: Meets product requirement for durable login without forcing repeated sign-ins.
- Alternative considered: In-memory session state only.
  - Rejected because it is lost on refresh/restart and degrades UX.

5. No domain restriction on Google accounts
- Decision: Do not enforce Workspace/domain allowlist; accept any valid Google account.
- Rationale: Requirement explicitly calls for broad account support.
- Alternative considered: Restrict to specific domains.
  - Rejected because it would block expected users.

6. Optional-auth scoring mode selector
- Decision: Introduce explicit scoring mode state with two paths: `google-authenticated` and `local-csv-fallback`, selected automatically based on login availability/user choice.
- Rationale: Keeps scoring available regardless of auth state while preserving enhanced identity/persistence when authenticated.
- Alternative considered: Hard gate all scoring behind authentication.
  - Rejected because requirement explicitly allows scoring without authentication.

7. Local CSV persistence for unauthenticated mode
- Decision: Persist fallback scoring to a local CSV-backed store and track its path/session key so data survives browser refresh; expose a match-end download button.
- Rationale: Meets continuity requirement when Google auth/storage is not used and gives user-controlled export.
- Alternative considered: Keep fallback data in memory only.
  - Rejected because memory state does not survive refresh and would lose data.

8. Explicit failure states with recoverable actions
- Decision: Map cancellation, token exchange failure, and state mismatch to specific UI messages with retry action.
- Rationale: Reduces user confusion and support burden, and makes login failures diagnosable.
- Alternative considered: Generic “login failed” error.
  - Rejected because it is hard to troubleshoot and leads to repeated failed attempts.

## Risks / Trade-offs

- [Popup behavior differs across browsers/environments] -> Mitigation: Provide fallback link-based flow that still enforces account selection prompt.
- [OAuth callback race or stale query params] -> Mitigation: Clear callback query params after processing and use idempotent completion handling.
- [Token/profile parsing inconsistency across Google responses] -> Mitigation: Normalize fields with defensive parsing and required-field validation.
- [Session persistence introduces security exposure if stored insecurely] -> Mitigation: Store minimal identity claims, secure/httponly where applicable, and enforce token expiry/rotation checks.
- [Fallback CSV loss/corruption across refresh] -> Mitigation: Use append-only writes with file existence checks and recovery handling.
- [Download action fails or exports incomplete data] -> Mitigation: Generate CSV from latest persisted state and validate row counts before enabling download.

## Migration Plan

1. Add/extend auth module APIs to support account-selection prompt and normalized user profile extraction.
2. Implement durable auth-session persistence mechanism that survives refresh/restart.
3. Implement optional-auth mode handling and local CSV fallback persistence path.
4. Update login UI to show popup-style “Continue with Google” entry and signed-in name-only identity summary.
5. Add match-end CSV download action for fallback scoring sessions.
6. Add tests for success path, cancellation/error path, profile ingestion behavior, auth persistence, fallback CSV persistence, and download behavior.
7. Deploy with existing OAuth client settings, verify callback URI configuration and both auth/fallback scoring paths.

Rollback strategy:
- Revert to prior redirect-based login handler while preserving existing OAuth credentials config.
- Temporarily disable durable session persistence feature flag if security/compatibility issues occur.
- Keep fallback local CSV mode enabled so scoring continuity remains available.
