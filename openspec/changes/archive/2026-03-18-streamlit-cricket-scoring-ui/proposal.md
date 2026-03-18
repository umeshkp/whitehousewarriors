## Why

Cricket scorers need a lightweight, browser-based way to record ball-by-ball outcomes without relying on complex scoring software. We need this now to enable quick over-wise scoring, correct strike handling, and immediate persistence to Google Sheets for sharing and analysis.

## What Changes

- Add a Streamlit-based cricket scoring UI for over-wise score entry.
- Add match setup for two teams with editable player rosters (for example 7 players per team).
- Support ball result entry with batter runs, wicket state, and extras (`wide`, `no-ball`, and extra runs).
- Restrict striker/non-striker selection to players from the batting team roster.
- Restrict bowler selection to players from the bowling team roster.
- Enforce scoring rules where wides and no-balls add extras and do not consume a legal ball.
- Automatically start a new over after six legal balls and prompt/select the bowler for that over from the bowling team roster.
- Attribute batter runs to the striker while keeping extras separate from batter run tallies.
- Auto-manage strike rotation based on odd/even batter runs and over completion.
- Add Google login/authentication to gate access before scoring.
- Add Google Sheets configuration and persistence so each delivery record is saved to a shared sheet URL.

## Capabilities

### New Capabilities
- `ball-by-ball-scoring-ui`: Streamlit interface for entering over-wise delivery outcomes and maintaining a live score state.
- `team-roster-and-role-selection`: Team setup and roster-constrained selection of striker/non-striker and bowler roles.
- `cricket-run-attribution-and-strike-rules`: Rules engine for legal-ball counting, extras handling, batter run attribution, and strike rotation.
- `google-authenticated-sheet-persistence`: Google sign-in and append-only delivery persistence to a configured Google Sheet.

### Modified Capabilities
- None.

## Impact

- Affected code: Streamlit frontend, scoring state/rules module, and Google integration layer.
- External dependencies: Google OAuth flow/library, Google Sheets API client, and credential/config handling.
- Data model impact: Introduce team and player roster models plus structured per-delivery records (over.ball, batting team, bowling team, striker/non-striker, bowler, batter runs, extras, legal-ball flag, totals) for persistence.
- Google Sheet schema impact: Persist explicit delivery columns for `match_id`, `innings_no`, `over_no`, `ball_in_over_legal`, `delivery_seq`, `batting_team`, `bowling_team`, `striker`, `non_striker`, `bowler`, `batter_runs`, `extra_type`, `extra_runs`, `total_runs_on_ball`, `is_legal_ball`, `over_completed`, `team_total_runs`, `team_total_wickets`, `timestamp_utc`.
- Operational impact: Requires Google Cloud OAuth and Sheets API setup, plus secure management of OAuth client configuration.
