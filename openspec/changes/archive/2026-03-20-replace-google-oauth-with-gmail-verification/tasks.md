## 1. Auth Verification Refactor

- [x] 1.1 Identify and remove OAuth callback state-verification acceptance checks from auth completion flow.
- [x] 1.2 Add normalized Gmail-domain validation (`@gmail.com`) before setting authenticated mode.
- [x] 1.3 Ensure non-Gmail identities do not persist authenticated mode/session state.
- [x] 1.4 Keep profile extraction safeguards for missing required identity fields (`sub`, `email`, `name`).

## 2. Mode Handling and UX Messaging

- [x] 2.1 Update auth manager/app mode transitions so Gmail verification failures remain in local mode.
- [x] 2.2 Add user-facing error/status messaging for Gmail-required verification failure.
- [x] 2.3 Confirm optional "continue without login" path remains fully functional.
- [x] 2.4 Verify Google-authenticated sheet path is only available after Gmail verification succeeds.

## 3. Specs and Documentation Alignment

- [x] 3.1 Update runtime behavior to match `gmail-account-verification` and modified capability deltas.
- [x] 3.2 Update README auth section to document Gmail-only authenticated mode and BREAKING impact.
- [x] 3.3 Update troubleshooting guidance for rejected non-Gmail logins and local fallback behavior.

## 4. Test Updates and Verification

- [x] 4.1 Replace OAuth state-mismatch behavior tests with Gmail acceptance/rejection tests.
- [x] 4.2 Add tests ensuring non-Gmail login attempts keep scoring enabled in local mode.
- [x] 4.3 Add/adjust tests for mode indicator and messaging on Gmail verification failure.
- [ ] 4.4 Run auth and app mode test suites and fix regressions.
- [ ] 4.5 Perform manual smoke check: Gmail login path, non-Gmail rejection path, and local CSV fallback continuity.
