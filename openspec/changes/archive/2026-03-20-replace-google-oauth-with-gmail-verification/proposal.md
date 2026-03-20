## Why

The current login flow relies on OAuth callback/state verification semantics that are more complex than needed for this product goal. We need to simplify account verification to focus on Gmail-account validation while keeping optional login and uninterrupted local scoring.

## What Changes

- Remove OAuth callback state-verification behavior from login completion requirements.
- Replace OAuth verification checks with Gmail-account verification based on authenticated identity email (`@gmail.com`).
- Keep optional login behavior so scoring remains available without login.
- Keep local CSV fallback behavior unchanged when login is skipped or verification fails.
- **BREAKING**: Accounts without a Gmail address (for example some Workspace-only identities) are no longer accepted for authenticated mode.

## Capabilities

### New Capabilities
- `gmail-account-verification`: Define Gmail-only account acceptance checks and failure messaging for authenticated mode.

### Modified Capabilities
- `google-popup-account-login`: Remove OAuth callback verification requirement and align login completion criteria with Gmail verification flow.
- `authenticated-profile-ingestion`: Ensure profile ingestion validates email presence and supports Gmail-domain checks before authenticated state is persisted.
- `optional-auth-scoring-mode`: Clarify fallback behavior when Gmail verification fails so scoring remains available in local mode.

## Impact

- Affected code: auth manager callback/login completion logic, profile validation, login UI status/error messaging, and mode transition handling.
- Affected docs: README auth setup and troubleshooting notes for Gmail verification outcomes.
- Affected tests: OAuth state/callback verification tests will be replaced by Gmail acceptance/rejection tests and fallback-mode assertions.
- Operational impact: reduces dependency on OAuth state callback handling while preserving Google-authenticated sheet mode and local CSV fallback.
