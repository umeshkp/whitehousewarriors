# google-authenticated-sheet-persistence Specification

## Purpose
TBD - created by archiving change streamlit-cricket-scoring-ui. Update Purpose after archive.
## Requirements
### Requirement: Google account authentication before scoring
The system SHALL require users to authenticate with a Google account before enabling score entry and persistence actions.

#### Scenario: Unauthenticated user is gated
- **WHEN** a user opens the scoring app without a valid authenticated session
- **THEN** the system displays a Google sign-in action and disables delivery submission

### Requirement: Shared Google Sheet target configuration
The system SHALL allow users to configure a shared Google Sheet URL and SHALL validate that the URL maps to an accessible sheet.

#### Scenario: User configures invalid sheet URL
- **WHEN** the user submits a malformed or inaccessible Google Sheet URL
- **THEN** the system shows an error and does not enable delivery persistence

### Requirement: Append-only ball record persistence
The system SHALL append one row per delivery to the configured Google Sheet including over-ball index, batting team, bowling team, bowler, striker, non-striker, batter runs, extras, legal-ball flag, and resulting totals.

#### Scenario: Delivery is written to sheet
- **WHEN** an authenticated user submits a valid delivery while sheet configuration is valid
- **THEN** the system appends exactly one row representing that delivery and confirms save success

### Requirement: Fixed Google Sheet scoring columns
The system SHALL create or validate the following header columns for persistent scoring data: `match_id`, `innings_no`, `over_no`, `ball_in_over_legal`, `delivery_seq`, `batting_team`, `bowling_team`, `striker`, `non_striker`, `bowler`, `batter_runs`, `extra_type`, `extra_runs`, `total_runs_on_ball`, `is_legal_ball`, `over_completed`, `team_total_runs`, `team_total_wickets`, `timestamp_utc`.

#### Scenario: Missing headers are initialized
- **WHEN** the configured sheet is writable but header row is missing or incomplete
- **THEN** the system writes the required fixed header columns before appending delivery rows

