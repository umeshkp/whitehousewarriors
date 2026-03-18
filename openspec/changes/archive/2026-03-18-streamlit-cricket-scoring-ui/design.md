## Context

The change introduces a new Streamlit application to capture over-wise cricket scoring while enforcing scoring rules around legal deliveries, extras, and strike rotation. The app must support authenticated access via Google account and persist ball-level records to a user-provided shared Google Sheet URL. The match setup must include two teams with player rosters, and scorer selections for striker/non-striker and bowler must be restricted to the correct team roster. The current repository has no existing OpenSpec capability specs for this domain, so this design establishes a fresh scoring, authentication, and persistence architecture.

Constraints:
- The UI should remain simple for manual scoring during live play.
- The UI must support exactly two teams in a match session with configurable roster lists.
- Wides and no-balls must add runs but not increment legal ball count.
- Batter run attribution must remain separate from extras.
- Strike change is based on batter runs parity (odd swaps, even retains), with over-end strike swap after six legal balls.
- Striker/non-striker selection must come from the batting team roster and bowler selection must come from the bowling team roster.
- After six legal balls, the system must transition to a new over and require selecting the next over bowler from the bowling team roster.
- Google OAuth and Sheets API integration must be handled securely.

## Goals / Non-Goals

**Goals:**
- Provide an intuitive Streamlit form to record each delivery with batter runs, extras, and optional wicket events.
- Provide a simple team setup step to define Team 1 and Team 2 rosters before scoring begins.
- Maintain a deterministic score engine that computes over/ball state, striker/non-striker, and totals.
- Enforce roster-constrained player role selection for striker/non-striker and bowler on every delivery.
- Auto-create the next over after six legal balls and gate delivery submission until a valid over bowler is selected.
- Authenticate users with Google sign-in before allowing scoring operations.
- Persist each delivery to a configured Google Sheet in append-only fashion with enough fields for replay/audit.

**Non-Goals:**
- Full match lifecycle features (team management, toss workflows, bowling analysis, innings transitions).
- Complex cricket edge cases beyond requested behavior (penalty runs, retired out logic, DLS, super over handling).
- Offline sync, multi-user real-time collaboration, or conflict resolution across concurrent scorers.

## Decisions

1. Streamlit single-page flow with session-state backing store
- Decision: Build a single Streamlit app using `st.session_state` for active innings state and delivery list.
- Rationale: Minimizes implementation complexity while enabling immediate feedback to scorers.
- Alternative considered: Multi-page architecture with backend API.
  - Rejected for initial scope because it adds infrastructure overhead before requirements demand it.

2. Explicit ball event model with legal-ball flag
- Decision: Represent each delivery as a structured event containing over index, legal ball count, batting team id, bowling team id, striker, non-striker, bowler, batter runs, extra type, extra runs, total runs added, and wicket metadata.
- Rationale: A normalized event model makes strike/runs logic testable and simplifies Google Sheet append behavior.
- Alternative considered: Store only cumulative totals.
  - Rejected because cumulative-only state is hard to audit and cannot reconstruct per-ball scoring decisions.

3. Deterministic scoring rules engine module
- Decision: Encapsulate scoring calculations in a pure-function module that takes previous state + new delivery input and returns next state.
- Rationale: Enables straightforward unit tests for wide/no-ball handling, strike rotation, and over progression.
- Alternative considered: Inline logic inside UI callbacks.
  - Rejected due to high regression risk and lower testability.

4. Over state machine with mandatory bowler selection per over
- Decision: Maintain explicit over state (`current_over_no`, `legal_balls_in_over`, `over_open`) and transition to a new over automatically after six legal balls; require a new bowler selection event before next ball entry.
- Rationale: Enforces cricket over boundaries and prevents invalid continuation without an assigned bowler.
- Alternative considered: Keep same bowler by default for next over unless changed.
  - Rejected because it hides a critical scoring action and can persist incorrect bowler attribution.

5. Match setup with team roster state and role constraints
- Decision: Introduce an explicit pre-scoring setup state that captures Team 1 and Team 2 names plus player lists, then derive batting and bowling eligible-player selectors from innings state.
- Rationale: Prevents invalid player attribution and ensures scorer can only pick batters and bowlers from valid teams.
- Alternative considered: Free-text player fields on every delivery form.
  - Rejected because it allows invalid players and inconsistent naming in persisted records.

6. Google OAuth via standard web flow and scoped Sheets access
- Decision: Use Google OAuth login in Streamlit and request minimal scopes needed for writing to Google Sheets.
- Rationale: Meets requirement for Google account authentication and controlled access.
- Alternative considered: Service-account-only write flow.
  - Rejected because the requirement explicitly asks users to login/authenticate using Google account.

7. Append-only sheet persistence with fixed scoring schema
- Decision: Validate sheet URL, ensure expected header columns exist (create header row if missing), and append one row per delivery using this fixed schema: `match_id`, `innings_no`, `over_no`, `ball_in_over_legal`, `delivery_seq`, `batting_team`, `bowling_team`, `striker`, `non_striker`, `bowler`, `batter_runs`, `extra_type`, `extra_runs`, `total_runs_on_ball`, `is_legal_ball`, `over_completed`, `team_total_runs`, `team_total_wickets`, `timestamp_utc`.
- Rationale: Append-only records preserve auditability and simplify recovery/replay of scoring sessions.
- Alternative considered: Periodic overwrite of summary rows.
  - Rejected because overwrite risks data loss and obscures per-ball attribution.

## Risks / Trade-offs

- [OAuth setup complexity for local and deployed Streamlit callbacks] -> Mitigation: Document redirect URI requirements and include startup validation with clear error messages.
- [Incorrect strike rotation in edge sequences (e.g., no-ball + batter run + over-end)] -> Mitigation: Add exhaustive unit tests for representative delivery sequences.
- [Incorrect over rollover or missing bowler assignment for new over] -> Mitigation: Add state-machine tests that assert rollover at exactly six legal balls and require bowler selection before next submission.
- [Invalid player-role selection (bowler from batting team, batter from bowling team)] -> Mitigation: Bind selectors to roster subsets and block submission if a selected player is not eligible.
- [Sheet URL misconfiguration or insufficient permissions] -> Mitigation: Validate URL format and perform a write-access probe with actionable user feedback.
- [Session loss in Streamlit refresh leading to partial scoring state] -> Mitigation: Persist each ball immediately to Google Sheets and support rehydrate from latest sheet rows.
- [Scope creep into full scoring platform] -> Mitigation: Keep strict boundary to over-wise entry, attribution, and persistence in first implementation.

## Migration Plan

1. Add application modules for team roster setup, scoring model, rules engine, Google auth, and Google Sheets adapter.
2. Build Streamlit UI for login, team setup, sheet configuration, delivery entry, and live score summary.
3. Add tests for roster eligibility constraints and scoring invariants.
4. Add integration tests/mocks for Google auth and persistence adapter.
5. Validate deployment configuration for OAuth client credentials and callback URL.
6. Roll out with a pilot sheet and manual verification of recorded deliveries.

Rollback strategy:
- Disable the feature by withholding OAuth configuration/env vars if critical issues appear.
- Preserve historical data because persistence is append-only in Google Sheets.

## Open Questions

- Should authentication allow only specific Google Workspace domains or any Google account?
- Should wicket handling be included in first pass (boolean + dismissal type) or postponed to a follow-up change?
