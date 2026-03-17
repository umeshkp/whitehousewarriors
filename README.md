# Whitehouse Warriors

Streamlit-based cricket scoring interface with Google-authenticated persistence to Google Sheets.

## Features

- Streamlit UI for over-wise cricket scoring.
- Team setup for exactly two teams with roster-based player selection.
- Bowler must be selected from bowling team roster.
- Striker and non-striker must be selected from batting team roster.
- Extras (`wide`, `no-ball`) are tracked separately and are not legal balls.
- Automatic over rollover after 6 legal balls.
- New over blocks next delivery until bowler is selected.
- Google account authentication (OAuth).
- Persistent append-only delivery logging to Google Sheets.

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

2. Configure environment variables:

```bash
export GOOGLE_OAUTH_CLIENT_CONFIG_JSON='<oauth-client-json>'
export GOOGLE_OAUTH_REDIRECT_URI='http://localhost:8501'
export GOOGLE_SHEET_URL='https://docs.google.com/spreadsheets/d/<sheet-id>/edit#gid=0'
```

3. Optional local bypass/development modes:

```bash
export AUTH_BYPASS=true
export USE_IN_MEMORY_SHEETS=true
```

4. Run Streamlit:

```bash
streamlit run app.py
```

## Quick Usage Flow

1. Sign in with Google (or enable local bypass mode).
2. Create Team 1 and Team 2 rosters.
3. Start innings by choosing batting team, striker, and non-striker.
4. Validate the shared Google Sheet URL.
5. Enter each delivery with bowler, runs, extras, and wicket flag.

Behavior enforced by the app:
- 6 legal balls per over.
- `wide` and `no-ball` do not count as legal balls.
- Batter runs are attributed to striker only.
- Odd batter runs rotate strike; even runs keep strike.
- After over completion, the next over starts automatically and requires bowler selection.

## Google OAuth Notes

- Enable Google Sheets API in your Google Cloud project.
- Configure OAuth consent screen and add your redirect URI.
- Share the target Google Sheet with the authenticated Google account.

## Tests

```bash
python3 -m pytest
```

If `pytest` is missing, install dependencies first:

```bash
pip install -r requirements.txt
```
