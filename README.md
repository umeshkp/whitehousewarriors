# whitehousewarriors

Whitehouse warrior cricket scoring interface.

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
python -m venv .venv
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

## Google OAuth Notes

- Enable Google Sheets API in your Google Cloud project.
- Configure OAuth consent screen and add your redirect URI.
- Share the target Google Sheet with the authenticated Google account.

## Tests

```bash
pytest
```
