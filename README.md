# Whitehouse Warriors

Streamlit-based cricket scoring interface with optional Google login and dual persistence modes.

## Features

- Streamlit UI for over-wise cricket scoring.
- Team setup for exactly two teams with roster-based player selection.
- Bowler must be selected from bowling team roster.
- Striker and non-striker must be selected from batting team roster.
- Extras (`wide`, `no-ball`) are tracked separately and are not legal balls.
- Automatic over rollover after 6 legal balls.
- New over blocks next delivery until bowler is selected.
- Popup-style Google account authentication (OAuth) with account chooser.
- Optional "Continue without login" local mode.
- Name-only signed-in identity display.
- Google-authenticated persistence to Google Sheets.
- Local CSV persistence fallback with browser CSV download.

## Google Sheet Columns

The app writes/validates this fixed header schema:

- `match_id`
- `innings_no`
- `over_no`
- `ball_in_over_legal`
- `delivery_seq`
- `batting_team`
- `bowling_team`
- `striker`
- `non_striker`
- `bowler`
- `batter_runs`
- `extra_type`
- `extra_runs`
- `total_runs_on_ball`
- `is_legal_ball`
- `over_completed`
- `team_total_runs`
- `team_total_wickets`
- `timestamp_utc`

## Local Setup

1. Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Install test/development tooling (optional):

```bash
pip install -r requirements-dev.txt
python3 -m playwright install
```

2. Configure environment variables (Google OAuth is optional):

```bash
export GOOGLE_OAUTH_CLIENT_CONFIG_JSON='<oauth-client-json>'
export GOOGLE_OAUTH_REDIRECT_URI='http://localhost:8501'
export GOOGLE_SHEET_URL='https://docs.google.com/spreadsheets/d/<sheet-id>/edit#gid=0'
```

3. Optional local bypass/development modes:

```bash
export AUTH_BYPASS=true
export USE_IN_MEMORY_SHEETS=true
export LOCAL_SCORING_DIR='.local_scoring'
```

4. Run Streamlit:

```bash
streamlit run app.py
```

## Quick Usage Flow

1. Click `Continue with Google` to authenticate, or click `Continue without login`.
2. Create Team 1 and Team 2 rosters.
3. Start innings by choosing batting team, striker, and non-striker.
4. If authenticated, validate the shared Google Sheet URL for sheet persistence.
5. Enter each delivery with bowler, runs, extras, and wicket flag.
6. In local mode, click `End Match` and download the generated CSV.

Behavior enforced by the app:
- 6 legal balls per over.
- `wide` and `no-ball` do not count as legal balls.
- Batter runs are attributed to striker only.
- Odd batter runs rotate strike; even runs keep strike.
- After over completion, the next over starts automatically and requires bowler selection.

Mode behavior:
- `google-authenticated`: writes deliveries to Google Sheets once sheet access is validated.
- `local-csv-fallback`: writes deliveries to local CSV (`.local_scoring/`) and enables CSV download at match end.
- Login state and local scoring snapshot persist across browser refresh and UI restarts.

## Google OAuth Notes

- Enable Google Sheets API in your Google Cloud project.
- Configure OAuth consent screen and add your redirect URI.
- Share the target Google Sheet with the authenticated Google account.
- All valid Google accounts are accepted (no domain allowlist restrictions).

## Troubleshooting

- `Google login is not configured`: use `Continue without login`, or set `GOOGLE_OAUTH_CLIENT_CONFIG_JSON` and `GOOGLE_OAUTH_REDIRECT_URI`.
- `OAuth state mismatch`: retry `Continue with Google` and complete login in one tab/window.
- If unauthenticated mode is active, scoring still works and is persisted locally to CSV.

## Tests

```bash
python3 -m pytest
```

If `pytest` is missing, install dependencies first:

```bash
pip install -r requirements.txt
```
