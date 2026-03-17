## 1. Project Setup and Dependencies

- [x] 1.1 Create module structure for Streamlit UI, scoring rules engine, auth, and Sheets persistence components.
- [x] 1.2 Add and pin required dependencies for Streamlit, Google OAuth integration, and Google Sheets API client.
- [x] 1.3 Add configuration loading for OAuth credentials and default app settings with startup validation.

## 2. Scoring Domain Model and Rules Engine

- [x] 2.1 Define team roster, delivery event, and innings state models including batting/bowling team ids, legal-ball flag, batter runs, extras, and strike fields.
- [x] 2.2 Implement pure scoring transition logic for legal delivery progression, wide/no-ball handling, and total updates.
- [x] 2.3 Implement strike-rotation logic for odd/even batter runs and end-of-over strike swap after six legal balls.
- [x] 2.4 Implement automatic over rollover after six legal balls and reset legal ball counter for new over.
- [x] 2.5 Add unit tests covering normal balls, wides, no-balls, mixed over sequences, and exact six-ball over rollover behavior.

## 3. Authentication and Google Sheets Integration

- [x] 3.1 Implement Google account sign-in flow and enforce authenticated session gating before score entry.
- [x] 3.2 Build Google Sheet URL validation and connectivity checks with actionable error handling.
- [x] 3.3 Implement append-only delivery row writer with schema header initialization/checks.
- [x] 3.4 Add adapter-level tests or mocks for failed auth, invalid sheet URL, and successful row append flows.

## 4. Streamlit UI Workflow

- [x] 4.1 Build login, team-setup, and sheet-configuration UI panels with clear authenticated/ready states.
- [x] 4.2 Build delivery entry form for bowler, striker/non-striker selection (roster-constrained), batter runs, extras, and optional wicket markers.
- [x] 4.3 Add over transition UX that auto-opens next over and requires selecting current over bowler before next delivery submission.
- [x] 4.4 Wire form submission to scoring engine and persistence adapter so each saved delivery updates live scoreboard.
- [x] 4.5 Add user-facing validation/errors for invalid input combinations and persistence/auth failures.

## 5. Verification and Readiness

- [x] 5.1 Add end-to-end happy-path test for authenticated scoring session with multiple overs and extras.
- [x] 5.2 Validate persisted sheet rows preserve batter-run attribution and extras separation.
- [x] 5.3 Add tests that enforce batter selection from batting roster and bowler selection from bowling roster.
- [x] 5.4 Add tests that ensure new-over delivery is blocked until a valid bowler is selected.
- [x] 5.5 Implement and verify fixed Google Sheet header columns for delivery persistence.
- [x] 5.6 Document local setup steps for OAuth credentials, redirect URIs, team setup flow, over transition behavior, and Google Sheet sharing requirements.
