## Context

The current Streamlit cricket scoring app supports optional Google login and falls back to local CSV scoring when login is skipped or unavailable. Authentication currently includes OAuth callback state validation and broad acceptance of any valid Google account.

This change replaces OAuth verification-centric acceptance criteria with Gmail-account verification criteria while preserving cricket scoring behavior, Google Sheets append-only persistence in authenticated mode, and local CSV fallback in unauthenticated mode.

## Goals / Non-Goals

**Goals:**
- Replace OAuth callback verification requirements with Gmail account verification requirements for authenticated mode entry.
- Ensure only profiles with `@gmail.com` email addresses can complete authenticated mode.
- Preserve optional login and uninterrupted local scoring behavior when verification fails.
- Update error/status messaging and tests to reflect Gmail verification outcomes.

**Non-Goals:**
- Changes to ball-by-ball scoring logic, over progression, strike rotation, or roster constraints.
- Changes to Google Sheets append schema and delivery persistence format.
- Multi-provider auth or non-Gmail domain allowlist/denylist policy management.

## Decisions

1. Verify authenticated eligibility using normalized profile email domain.
- Decision: Authentication completion SHALL require a normalized email ending with `@gmail.com`.
- Rationale: Matches requested Gmail-account verification behavior while minimizing surface-area changes.
- Alternative considered: Keep accepting all Google accounts and only show Gmail preference warnings.
  - Rejected because it does not enforce the requested replacement behavior.

2. Remove OAuth callback state-validation requirement from spec contract.
- Decision: Delta specs remove explicit OAuth state nonce verification requirement from behavior contract.
- Rationale: Aligns requirements with requested simplification from OAuth verification to Gmail verification.
- Alternative considered: Keep callback state validation as an implementation hardening detail.
  - Deferred from this change; can be added later as internal security hardening without changing external behavior contract.

3. Keep dual-mode operation with local fallback on verification failure.
- Decision: Failed Gmail verification SHALL keep/return the app to local scoring mode and keep scoring enabled.
- Rationale: Preserves core product expectation that scoring is available without login.
- Alternative considered: Block scoring until a Gmail account is verified.
  - Rejected because it regresses optional-login requirements.

4. Preserve scoring-state transitions and persistence semantics.
- Decision: Over rollover, legal-ball counting, strike changes, and persistence selection rules remain unchanged.
- Rationale: Change scope is auth verification behavior only.
- Alternative considered: Reworking scoring state during auth transitions.
  - Rejected as unnecessary complexity and regression risk.

## Risks / Trade-offs

- [Removing explicit OAuth-state verification requirement can reduce CSRF protection if implementation also drops state checks] → Mitigation: keep internal callback correlation checks where feasible, even if no longer externally mandated by specs.
- [Legitimate Google Workspace users may lose authenticated-mode access] → Mitigation: document BREAKING behavior and provide clear fallback messaging to local mode.
- [User confusion when login appears successful at provider but app falls back to local mode] → Mitigation: show explicit "Gmail account required" error and next-step guidance.
- [Regression risk across auth-mode boundaries and sheet-write gating] → Mitigation: add tests covering accepted Gmail login, rejected non-Gmail login, and local-mode continuity.
- [Potential mismatch between auth mode and sheet access readiness] → Mitigation: ensure authenticated mode is only set after Gmail verification passes and sheet validation behavior remains unchanged.

## Migration Plan

1. Implement Gmail verification check in profile/auth completion flow before setting authenticated mode.
2. Replace/retire OAuth verification tests that assert state-mismatch behavior and add Gmail acceptance/rejection test coverage.
3. Update mode/status messaging for verification failures and fallback behavior.
4. Update README auth section with Gmail-only authenticated-mode requirement and troubleshooting.
5. Validate rollout in both modes:
- Gmail login -> authenticated mode -> Google Sheet flow works.
- Non-Gmail login or verification failure -> local mode remains enabled with CSV persistence.

Rollback strategy:
- Restore prior account-acceptance logic and associated specs/tests if Gmail-only verification causes unacceptable access issues.

## Open Questions

- Should Google Workspace accounts with Gmail aliases be considered valid if primary email is non-`@gmail.com`?
- Should verification be case-insensitive and trimmed before domain checks (`User@GMAIL.com`)?
- Should we expose a feature flag to re-enable all-Google-account acceptance temporarily during rollout?
